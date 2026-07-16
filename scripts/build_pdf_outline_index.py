#!/usr/bin/env python3
"""
build_pdf_outline_index.py — deterministic PageIndex-shaped index from a PDF's
embedded outline (bookmarks). NO LLM, ~$0.

WHY THIS EXISTS
---------------
PageIndex's native PDF path *ignores* a PDF's embedded outline and re-infers a
table of contents with an LLM (expensive, and it drops section numbers and
over-segments — e.g. RFC 9110 -> 474 guessed nodes, ~$6 in TOC-repair loops).
But a well-produced PDF already carries its structure deterministically as an
outline (`fitz.get_toc()`). For RFC 9110 that outline is 311 entries, byte-for-
byte the same headings as the Markdown IDX-D tree, section numbers intact.

This tool turns that outline into a page-addressed index whose structure and
per-node text mirror the Markdown twin, so a Markdown-vs-PDF pairing isolates
ONLY the representation-inherent differences: addressing (line vs physical page)
and text fidelity (clean HTML-derived text vs PDF extraction). It is the honest
"deterministic PDF representation" arm, and the cheap answer to "can we derive
the IDX-D equivalent from the PDF?" — yes, from the outline.

GENERAL BY DESIGN
-----------------
Nothing here is RFC-specific. It works on any PDF that carries an embedded
outline; if the PDF has none, it exits with a clear message (the approach needs
a bookmarked PDF). Reproducibility is pinned to the PyMuPDF version (same PDF +
same version -> byte-identical index.json), mirroring scripts/build_paper_book.py.

USAGE
-----
  .venv/bin/python scripts/build_pdf_outline_index.py --pdf sources/rfc9110/rfc9110.pdf \
      --index-dir indexes/IDX-PDF-outline-rfc9110 --overwrite
  .venv/bin/python scripts/build_pdf_outline_index.py --self-test   # offline, no PDF
"""

from __future__ import annotations

import argparse
import bisect
import hashlib
import json
import re
import sys
import time
from pathlib import Path

EXPECTED_PYMUPDF = "1.26.4"   # reproducibility pin (override with --expected-pymupdf)

# --headings-from text: some born-digital PDFs (e.g. the EUR-Lex Official Journal
# rendition of an EU regulation) carry NO usable embedded outline — fitz.get_toc()
# returns a single title entry — yet their structure is perfectly regular in the
# text layer (a number line + a rubric line). A profile names, per structural kind,
# a MULTILINE regex whose group(1) is the item number and group(2) the rubric line.
# Articles nest under a Section when one is open in the current chapter, else
# directly under the chapter. Add profiles for other doc families here; nothing
# below is EU-specific.
KIND_LABEL = {"chapter": "Chapter", "section": "Section", "article": "Article"}

TEXT_PROFILES = {
    "eu-legislation": {
        "patterns": {
            "chapter": re.compile(r"(?m)^[ \t]*CHAPTER[ \t]+([IVXLC]+)\b[ \t]*\n[ \t]*(.+?)[ \t]*$"),
            "section": re.compile(r"(?m)^[ \t]*Section[ \t]+(\d+)\b[ \t]*\n[ \t]*(.+?)[ \t]*$"),
            "article": re.compile(r"(?m)^[ \t]*Article[ \t]+(\d+)\b[ \t]*\n[ \t]*(.+?)[ \t]*$"),
        },
        # Text before the first matched heading (citations + recitals) becomes a
        # leading level-1 node instead of being silently dropped.
        "preamble_title": "Recitals (Preamble)",
    },
}


# --------------------------------------------------------------------------
# Pure helpers (unit-tested offline, no PDF/LLM)
# --------------------------------------------------------------------------

def char_to_page(offset: int, page_starts: list[int]) -> int:
    """1-based physical page containing character `offset`, given the sorted
    start offsets of each page in the concatenated document text."""
    return bisect.bisect_right(page_starts, offset)


def locate_heading(text: str, title: str, from_offset: int) -> int | None:
    """First char offset of `title` in `text` at/after `from_offset`, tolerant
    of the whitespace differences between an outline title and the PDF text
    layer (collapsed runs, NBSPs, intra-title line breaks). Returns None if the
    heading cannot be located (caller falls back to page-range text)."""
    # Fast path: exact substring (the common case).
    idx = text.find(title, from_offset)
    if idx != -1:
        return idx
    # Whitespace-flexible: match the title's non-space tokens separated by \s+.
    tokens = [re.escape(t) for t in title.split()]
    if not tokens:
        return None
    pat = re.compile(r"\s+".join(tokens))
    m = pat.search(text, from_offset)
    return m.start() if m else None


def assign_node_ids(n: int) -> list[str]:
    """Pre-order 4-digit zero-padded ids ('0000', '0001', ...) — matches the
    convention in the repo's existing indexes."""
    return [f"{i:04d}" for i in range(n)]


def nest_by_level(flat: list[dict]) -> list[dict]:
    """Nest a flat, document-order list of entries (each carrying an integer
    `level` >= 1) into a tree, dropping the transient `level` key. A child is
    any subsequent entry with a strictly greater level than the open node."""
    roots: list[dict] = []
    stack: list[dict] = []   # path of currently-open ancestors
    for e in flat:
        level = e["level"]
        node = {k: v for k, v in e.items() if k != "level"}
        node["nodes"] = []
        while stack and stack[-1]["_level"] >= level:
            stack.pop()
        if stack:
            stack[-1]["nodes"].append(node)
        else:
            roots.append(node)
        node["_level"] = level
        stack.append(node)
    # strip helper key and any empty children lists
    def clean(ns: list[dict]) -> list[dict]:
        out = []
        for x in ns:
            x.pop("_level", None)
            kids = clean(x.get("nodes", []))
            if kids:
                x["nodes"] = kids
            else:
                x.pop("nodes", None)
            out.append(x)
        return out
    return clean(roots)


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def page_starts_of(pages: list[str]) -> list[int]:
    """Start char offset of each page in the ""-concatenated document text."""
    starts, cur = [], 0
    for p in pages:
        starts.append(cur)
        cur += len(p)
    return starts


def slice_entries(positions: list[int], titles: list[str], levels: list[int],
                  pages: list[str]) -> list[dict]:
    """Core slicer, shared by both heading sources. Given each heading's exact
    char offset (ascending, non-overlapping) plus its title and level, assign
    non-overlapping heading-to-next-heading text and physical page ranges. Text
    assignment mirrors md_to_tree: each entry owns the text from its own heading
    up to the next heading."""
    text = "".join(pages)
    page_starts = page_starts_of(pages)
    entries, n = [], len(positions)
    for i in range(n):
        start_char = positions[i]
        end_char = positions[i + 1] if i + 1 < n else len(text)
        body = text[start_char:end_char].strip()
        start_page = char_to_page(start_char, page_starts)
        end_page = char_to_page(max(start_char, end_char - 1), page_starts)
        entries.append({
            "level": levels[i],
            "title": titles[i].strip(),
            "start_index": start_page,
            "end_index": end_page,
            "text": body,
        })
    return entries


def build_flat_entries(toc: list, pages: list[str]) -> list[dict]:
    """Outline (bookmark) source: map `[(level, title, start_page), ...]` onto the
    text layer by locating each title, then slice. Titles are located scanning
    forward and monotonically (a section number can appear as a cross-reference
    earlier; anchoring at the outline's start page and never searching before the
    previous heading avoids false hits)."""
    page_starts = page_starts_of(pages)
    text = "".join(pages)
    positions: list[int] = []
    prev_end = 0
    for level, title, page in toc:
        page = max(1, min(page, len(pages)))
        start = max(page_starts[page - 1], prev_end)
        pos = locate_heading(text, title.strip(), start)
        if pos is None:
            pos = start                          # fallback: never move backwards
        positions.append(pos)
        prev_end = pos + len(title)
    titles = [t for _, t, _ in toc]
    levels = [l for l, _, _ in toc]
    return slice_entries(positions, titles, levels, pages)


def scan_text_headings(pages: list[str], profile: dict) -> list[tuple[int, int, str]]:
    """Text-layer source: find headings by regex when a PDF lacks a usable
    outline. Returns `[(char_offset, level, title), ...]` in document order.
    Levels: chapter=1, section=2, article=2 (or 3 when a section is open in the
    current chapter). An optional preamble node captures pre-heading text."""
    text = "".join(pages)
    page_starts = page_starts_of(pages)
    raw: list[tuple[int, str, str, str]] = []
    for kind, rx in profile["patterns"].items():
        for m in rx.finditer(text):
            raw.append((m.start(), kind, m.group(1), m.group(2).strip()))
    raw.sort(key=lambda h: h[0])

    hits: list[tuple[int, int, str]] = []
    section_open = False
    for off, kind, num, rubric in raw:
        if kind == "chapter":
            level, section_open = 1, False
        elif kind == "section":
            level, section_open = 2, True
        else:  # article
            level = 3 if section_open else 2
        title = f"{KIND_LABEL[kind]} {num}"
        if rubric:
            title = f"{title} — {rubric}"
        hits.append((off, level, title))

    pre = profile.get("preamble_title")
    if pre and hits and hits[0][0] > 0:
        hits.insert(0, (0, 1, pre))
    return hits


def page_text_reading_order(page) -> str:
    """Text of one page in reading order. PyMuPDF's default get_text() emits
    blocks in extraction order, which is NOT always document-linear (e.g. a
    running header or a References heading can surface before body content that
    visually precedes it). Sorting non-empty blocks by (y, x) restores top-to-
    bottom, left-to-right order for single-column body text — which is what
    heading-boundary slicing needs to be correct."""
    blocks = [b for b in page.get_text("blocks") if b[4].strip()]
    blocks.sort(key=lambda b: (round(b[1]), round(b[0])))
    return "".join(b[4] for b in blocks)


def build_index(pdf_path: Path, expected_pymupdf: str,
                headings_from: str = "outline", text_profile: str = "eu-legislation") -> dict:
    import fitz  # PyMuPDF
    ver = fitz.__version__.split()[0] if isinstance(fitz.__version__, str) else str(fitz.VersionBind)
    if ver != expected_pymupdf:
        raise SystemExit(
            f"ERROR: PyMuPDF {ver} != pinned {expected_pymupdf}; reproducibility "
            f"not guaranteed. Re-pin with --expected-pymupdf {ver} if intentional.")
    doc = fitz.open(str(pdf_path))
    pages = [page_text_reading_order(doc[i]) for i in range(doc.page_count)]

    if headings_from == "text":
        profile = TEXT_PROFILES.get(text_profile)
        if profile is None:
            raise SystemExit(f"unknown --text-profile {text_profile!r}; "
                             f"known: {', '.join(TEXT_PROFILES)}")
        hits = scan_text_headings(pages, profile)
        if not hits:
            raise SystemExit(
                f"ERROR: profile {text_profile!r} matched no headings in {pdf_path}. "
                f"Check the profile's regexes against the PDF text layer.")
        positions = [h[0] for h in hits]
        levels = [h[1] for h in hits]
        titles = [h[2] for h in hits]
        flat = slice_entries(positions, titles, levels, pages)
    else:
        toc = doc.get_toc()
        if not toc:
            raise SystemExit(
                f"ERROR: {pdf_path} has no embedded outline (fitz.get_toc() empty). "
                f"Either the PDF is bookmarked and this is a bug, or use "
                f"--headings-from text with a matching --text-profile to derive "
                f"structure from the text layer instead.")
        flat = build_flat_entries(toc, pages)
    node_ids = assign_node_ids(len(flat))
    for e, nid in zip(flat, node_ids):
        e["node_id"] = nid
    # order fields consistently, then nest
    ordered = [{"level": e["level"], "title": e["title"], "node_id": e["node_id"],
                "start_index": e["start_index"], "end_index": e["end_index"],
                "text": e["text"]} for e in flat]
    structure = nest_by_level(ordered)
    return {"doc_name": pdf_path.name, "structure": structure}


def count_nodes(structure: list[dict]) -> int:
    return sum(1 + count_nodes(x.get("nodes", [])) for x in structure)


# --------------------------------------------------------------------------
# Provenance
# --------------------------------------------------------------------------

def write_provenance(index_dir: Path, pdf_path: Path, index: dict,
                     expected_pymupdf: str, twin: str | None,
                     headings_from: str = "outline",
                     text_profile: str | None = None) -> None:
    node_fields = ["title", "node_id", "start_index", "end_index", "text"]
    if headings_from == "text":
        condition = (f"deterministic-pdf-text-headings (regex profile "
                     f"{text_profile!r}; no outline, no LLM)")
        description = (
            "Deterministic PageIndex-shaped index derived from the PDF's TEXT LAYER "
            "by a regular-heading regex profile, used because this PDF carries no "
            "usable embedded outline (fitz.get_toc() empty). Structure comes from the "
            "document's own regular numbering (e.g. CHAPTER / Section / Article), not "
            "from an LLM. Still the honest 'deterministic PDF representation' arm — the "
            "structure source is a parser rather than bookmarks.")
        gen_mode = "pdf-text-headings"
    else:
        condition = "deterministic-pdf-outline (embedded bookmarks; no LLM)"
        description = (
            "Deterministic PageIndex-shaped index derived from the PDF's embedded "
            "outline (fitz.get_toc()); per-node text sliced from the PDF text layer "
            "at heading boundaries. The honest 'PDF representation' arm: same section "
            "structure as the Markdown twin, differing only in addressing (physical "
            "page vs line) and text fidelity (PDF extraction vs HTML-derived).")
        gen_mode = "pdf-outline"
    prov = {
        "index_id": index_dir.name,
        "condition": condition,
        "description": description,
        "source": str(pdf_path),
        "source_pdf_sha256": sha256_file(pdf_path),
        "generation": {
            "tool": "scripts/build_pdf_outline_index.py",
            "mode": gen_mode,
            "text_profile": text_profile if headings_from == "text" else None,
            "uses_llm": False,
            "pymupdf_version": expected_pymupdf,
            "cost_usd": 0.0,
        },
        "node_count": count_nodes(index["structure"]),
        "node_fields": node_fields,
        "addressing": "physical page (start_index/end_index), NOT line numbers",
    }
    if twin:
        prov["markdown_twin"] = twin
        prov["twin_note"] = (
            f"Structure is intended to be identical to {twin} (its Markdown IDX-D "
            f"twin); the pair isolates representation. Verified at build time.")
    prov["generated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    (index_dir / "provenance.json").write_text(
        json.dumps(prov, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# Offline self-test (no PDF, no network)
# --------------------------------------------------------------------------

def self_test() -> None:
    failures = []

    def check(name, got, want):
        ok = got == want
        print(f"  {'PASS' if ok else 'FAIL'}: {name} (got {got!r}, want {want!r})")
        if not ok:
            failures.append(name)

    # char_to_page: offsets map to 1-based pages.
    ps = [0, 10, 25]  # page 1: [0,10), page 2: [10,25), page 3: [25,..)
    check("char_to_page start p1", char_to_page(0, ps), 1)
    check("char_to_page mid p2", char_to_page(12, ps), 2)
    check("char_to_page p3", char_to_page(30, ps), 3)

    # locate_heading: exact + whitespace-flexible + monotonic search.
    txt = "intro 15.4.2. 301 Moved Permanently \nbody about 301..."
    check("locate exact", locate_heading(txt, "15.4.2. 301 Moved Permanently", 0), 6)
    txt2 = "x 1.1.  Purpose\nbody"   # double space vs single in title
    check("locate flex whitespace", locate_heading(txt2, "1.1. Purpose", 0) is not None, True)
    check("locate respects from_offset", locate_heading("aa target bb target", "target", 5) > 5, True)
    check("locate miss returns None", locate_heading("no heading here", "15.4.2", 0), None)

    # nest_by_level: a level-2 then two level-3 children, then a new level-2.
    flat = [
        {"level": 2, "title": "15.4", "node_id": "0000"},
        {"level": 3, "title": "15.4.1", "node_id": "0001"},
        {"level": 3, "title": "15.4.2", "node_id": "0002"},
        {"level": 2, "title": "15.5", "node_id": "0003"},
    ]
    tree = nest_by_level([dict(e) for e in flat])
    check("nest root count", len(tree), 2)
    check("nest child count", len(tree[0]["nodes"]), 2)
    check("nest child id", tree[0]["nodes"][1]["node_id"], "0002")
    check("nest sibling has no children key", "nodes" in tree[1], False)
    check("nest dropped level key", "level" in tree[0], False)

    # build_flat_entries: non-overlapping heading-to-next-heading text on 2 pages.
    pages = ["A. First\nalpha text\n", "B. Second\nbeta text\n"]
    toc = [(1, "A. First", 1), (1, "B. Second", 2)]
    ents = build_flat_entries(toc, pages)
    check("flat count", len(ents), 2)
    check("flat[0] text is own section only", "beta" not in ents[0]["text"], True)
    check("flat[0] starts at its heading", ents[0]["text"].startswith("A. First"), True)
    check("flat[1] start page", ents[1]["start_index"], 2)

    check("assign_node_ids", assign_node_ids(3), ["0000", "0001", "0002"])

    # scan_text_headings: EU-style number-line + rubric-line, section-aware levels
    # and preamble capture. Two pages; a chapter with a bare article, then a
    # section whose article must drop to level 3.
    prof = TEXT_PROFILES["eu-legislation"]
    tpages = [
        "recital text here \nCHAPTER I \nGeneral provisions \nArticle 1 \nScope \nbody one \n",
        "CHAPTER II \nRights \nSection 1 \nAccess \nArticle 2 \nRight of access \nbody two \n",
    ]
    hits = scan_text_headings(tpages, prof)
    kinds = [t for _, _, t in hits]
    check("scan preamble first", hits[0][2], "Recitals (Preamble)")
    check("scan chapter title", "Chapter I — General provisions" in kinds, True)
    check("scan article rubric", "Article 1 — Scope" in kinds, True)
    lvl = {t: lv for _, lv, t in hits}
    check("scan bare article level 2", lvl["Article 1 — Scope"], 2)
    check("scan sectioned article level 3", lvl["Article 2 — Right of access"], 3)
    check("scan section level 2", lvl["Section 1 — Access"], 2)
    check("scan no cross-ref false hit", sum(k.startswith("Article") for k in kinds), 2)
    # end-to-end slice via the shared slicer
    ent = slice_entries([h[0] for h in hits], [h[2] for h in hits],
                        [h[1] for h in hits], tpages)
    check("scan preamble owns pre-heading text", ent[0]["text"].startswith("recital text"), True)
    check("scan article1 text isolated", "body one" in ent[2]["text"] and "body two" not in ent[2]["text"], True)
    check("scan article2 start page", ent[-1]["start_index"], 2)

    if failures:
        raise SystemExit(f"self-test FAILED: {failures}")
    print("self-test OK")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pdf", type=str, help="source PDF (must carry an embedded outline)")
    p.add_argument("--out", type=str, default=None,
                   help="raw index json (default results/<stem>-outline_structure.json)")
    p.add_argument("--index-dir", type=str, default=None,
                   help="curated index dir to also write index.json + provenance.json into")
    p.add_argument("--twin", type=str, default=None,
                   help="markdown IDX-D twin index id for provenance (e.g. IDX-D-rfc9110)")
    p.add_argument("--headings-from", choices=["outline", "text"], default="outline",
                   help="structure source: 'outline' = embedded bookmarks (default); "
                        "'text' = regex over the text layer (for PDFs with no outline)")
    p.add_argument("--text-profile", choices=sorted(TEXT_PROFILES), default="eu-legislation",
                   help="heading regex profile for --headings-from text")
    p.add_argument("--expected-pymupdf", type=str, default=EXPECTED_PYMUPDF,
                   help="pinned PyMuPDF version for reproducibility")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--self-test", action="store_true", help="offline checks; no PDF")
    args = p.parse_args()

    if args.self_test:
        self_test()
        return
    if not args.pdf:
        p.error("--pdf is required (or use --self-test)")

    pdf_path = Path(args.pdf)
    if not pdf_path.is_file():
        raise SystemExit(f"PDF not found: {pdf_path}")

    index = build_index(pdf_path, args.expected_pymupdf,
                        headings_from=args.headings_from, text_profile=args.text_profile)
    n = count_nodes(index["structure"])
    print(f"{args.headings_from} -> {n} nodes ({index['doc_name']})")

    out_path = Path(args.out) if args.out else Path("results") / f"{pdf_path.stem}-outline_structure.json"
    if out_path.exists() and not args.overwrite:
        raise SystemExit(f"{out_path} exists; pass --overwrite to replace it")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(index, indent=2, ensure_ascii=False) + "\n"
    out_path.write_text(payload, encoding="utf-8")
    print(f"raw index written: {out_path}")

    if args.index_dir:
        idx_dir = Path(args.index_dir)
        idx_dir.mkdir(parents=True, exist_ok=True)
        idx_file = idx_dir / "index.json"
        if idx_file.exists() and not args.overwrite:
            raise SystemExit(f"{idx_file} exists; pass --overwrite to replace it")
        idx_file.write_text(payload, encoding="utf-8")
        write_provenance(idx_dir, pdf_path, index, args.expected_pymupdf, args.twin,
                         headings_from=args.headings_from,
                         text_profile=args.text_profile if args.headings_from == "text" else None)
        print(f"curated index + provenance written: {idx_dir}")


if __name__ == "__main__":
    main()

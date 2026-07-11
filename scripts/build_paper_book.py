#!/usr/bin/env python3
"""Producer for corpus/paper-book-v1/: deterministic PDF -> normalized Markdown.

Unlike site-book-v1 (produced in the website repo and synced), this corpus is
built in-repo from the frozen source PDF pinned in config/paper-book-v1.yml.
Re-running against the same PDF, config, and PyMuPDF version yields a
byte-identical paper-book-v1.md and manifest.json (provenance.json carries the
only timestamp).

Outputs (gated by --overwrite):
  corpus/paper-book-v1/paper-book-v1.md
  corpus/paper-book-v1/paper-book-v1.manifest.json
  corpus/paper-book-v1/provenance.json
  reports/qc-paper-book-v1.md

Usage:
  python3 scripts/build_paper_book.py --overwrite
  python3 scripts/build_paper_book.py --out-root /tmp/somewhere --overwrite
"""

import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import fitz  # PyMuPDF
import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "paper-book-v1.yml"


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


# ---------------------------------------------------------------------------
# Extraction: PDF -> classified line elements
# ---------------------------------------------------------------------------

class QC:
    """Counters and issue lists surfaced in the QC report / manifest."""

    def __init__(self):
        self.glyph_subs = {}          # font -> count
        self.ligatures = 0
        self.diacritics = 0
        self.dehyphenations = []      # joined words (samples kept)
        self.dehyph_uncertain = []    # joined without vocabulary evidence
        self.hyphens_kept = []
        self.cross_page_joins = 0
        self.vocab = set()            # document vocabulary for hyphenation calls
        self.watermark_lines = 0
        self.running_head_lines = 0
        self.unmapped_symbol_chars = []   # (page, font, repr(char))
        self.inline_subscripts = []       # (page, text) letters kept inline
        self.notes = []


def apply_glyph_map(font, text, glyph_map, qc, page_no):
    mapping = glyph_map.get(font)
    if mapping is None:
        return text
    out = []
    for ch in text:
        if ch in mapping:
            out.append(mapping[ch])
            qc.glyph_subs[font] = qc.glyph_subs.get(font, 0) + 1
        else:
            if ch.strip() and (ord(ch) < 32 or font in ("AdvDM5", "AdvPi1", "AdvPi3")):
                qc.unmapped_symbol_chars.append((page_no, font, repr(ch)))
            out.append(ch)
    return "".join(out)


def apply_ligatures(text, ligature_map, qc):
    for lig, repl in ligature_map.items():
        n = text.count(lig)
        if n:
            qc.ligatures += n
            text = text.replace(lig, repl)
    return text


def apply_diacritics(text, diacritic_map, qc):
    for pair, repl in diacritic_map.items():
        n = text.count(pair)
        if n:
            qc.diacritics += n
            text = text.replace(pair, repl)
    return text


def extract_elements(doc, cfg, qc):
    """Return a list of classified line elements across the whole document.

    Element: dict(kind, page, y, x, text, spans) where kind is one of
    title|author|heading|abstract|keywords|frontnote|caption|table|equation|
    reference|footnote_pool|body.
    """
    glyph_map = cfg["glyph_map"]
    lig_map = cfg["ligature_map"]
    furn = cfg["furniture"]
    roles = cfg["roles"]
    heading_font = roles["heading"]["font"]
    heading_size = roles["heading"]["size"]
    table_page = cfg["table_1"]["page"]

    elements = []
    references_started = False
    refs_after = None  # (page, y) of REFERENCES heading

    for pno in range(doc.page_count):
        page = doc[pno]
        pnum = pno + 1
        blocks = page.get_text("dict")["blocks"]

        # Pre-scan: blocks that are figure captions (contain bold "Figure N." span)
        caption_blocks = set()
        for bi, b in enumerate(blocks):
            if b["type"] != 0:
                continue
            for ln in b["lines"]:
                for s in ln["spans"]:
                    if s["font"] == "AdvTRB" and round(s["size"], 1) == 8.0 \
                            and re.match(r"Figure \d+\.", s["text"].strip()):
                        caption_blocks.add(bi)

        for bi, b in enumerate(blocks):
            if b["type"] != 0:
                continue
            for li, ln in enumerate(b["lines"]):
                spans = []
                for s in ln["spans"]:
                    font, size = s["font"], round(s["size"], 1)
                    text = s["text"]
                    if not text:
                        continue
                    # --- furniture ---
                    if font == furn["watermark_font"]:
                        qc.watermark_lines += 1
                        continue
                    if font == furn["running_head_font"] and size in (8.0, 10.0) \
                            and s["bbox"][1] < furn["running_head_y_max"]:
                        qc.running_head_lines += 1
                        continue
                    text = apply_glyph_map(font, text, glyph_map, qc, pnum)
                    text = apply_ligatures(text, lig_map, qc)
                    text = apply_diacritics(text, cfg.get("diacritic_map", {}), qc)
                    spans.append({
                        "font": font, "size": size, "text": text,
                        "x": round(s["bbox"][0], 1), "y": round(s["bbox"][1], 1),
                    })
                if not spans:
                    continue

                y = round(ln["bbox"][1], 1)
                x = round(ln["bbox"][0], 1)
                sizes = {sp["size"] for sp in spans}
                fonts = {sp["font"] for sp in spans}

                # Build line text, converting inline superscripts.
                parts = []
                for sp in spans:
                    t = sp["text"]
                    if sp["font"] == "AdvTR" and sp["size"] == roles["inline_superscript_size"]:
                        if t.strip().isdigit():
                            t = "".join(f"[fn{c}]" if c.isdigit() else c for c in t)
                        else:
                            qc.inline_subscripts.append((pnum, t.strip()))
                    parts.append(t)
                text = "".join(parts).strip()
                if not text:
                    continue

                kind = None
                if any(sp["font"] == roles["title"]["font"] and sp["size"] == roles["title"]["size"]
                       for sp in spans):
                    kind = "title"
                elif pnum == roles["author"].get("page", 1) and \
                        any(sp["font"] == roles["author"]["font"] and sp["size"] == roles["author"]["size"]
                            for sp in spans):
                    kind = "author"
                elif any(sp["font"] == heading_font and sp["size"] == heading_size for sp in spans):
                    kind = "heading"
                elif roles["abstract_size"] in sizes and "AdvTR" in fonts:
                    kind = "abstract"
                elif roles["keywords_size"] in sizes:
                    kind = "keywords"
                elif pnum == table_page and (
                        roles["table_size"] in sizes or
                        any(sp["font"] == "AdvUX" and sp["size"] == 8.0 for sp in spans)):
                    kind = "table"
                elif bi in caption_blocks:
                    kind = "caption"
                elif pnum == 1 and (roles["small_size"] in sizes or "AdvPi3" in fonts):
                    kind = "frontnote"
                elif references_started and refs_after is not None and \
                        (pnum, y) > refs_after and roles["small_size"] in sizes:
                    kind = "reference"
                elif roles["footnote_marker_size"] in sizes or (
                        roles["small_size"] in sizes and pnum > 2 and not references_started):
                    # bottom-of-page footnote text (8.0) and its 5.6 marker
                    kind = "footnote_pool"
                else:
                    kind = "body"

                if kind == "heading":
                    letters = re.sub(r"[^A-Za-z]", "", text)
                    level = 2 if letters and letters == letters.upper() else 3
                    if level == 2 and text.strip() == "REFERENCES":
                        references_started = True
                        refs_after = (pnum, y)
                    elements.append({"kind": "heading", "page": pnum, "y": y, "x": x,
                                     "text": text, "level": level})
                else:
                    elements.append({"kind": kind, "page": pnum, "y": y, "x": x,
                                     "block": bi, "li": li,
                                     "text": text, "spans": spans})

    # Equation detection: display equations are body lines dominated by math
    # fonts; the equation number "(n)" is a separate right-aligned line.
    math_fonts = {"AdvTN", "AdvBM13", "AdvCS", "AdvP4C4E51", "AdvBMa1", "AdvDM5"}

    def math_ratio(el):
        tot = sum(len(sp["text"].strip()) for sp in el.get("spans", []))
        m = sum(len(sp["text"].strip()) for sp in el.get("spans", [])
                if sp["font"] in math_fonts)
        return m / tot if tot else 0.0

    eq_nums = [el for el in elements
               if el["kind"] == "body" and re.fullmatch(r"\(\d\)", el["text"].strip())
               and any(sp["font"] in math_fonts for sp in el["spans"])]
    for el in elements:
        if el["kind"] != "body" or el in eq_nums:
            continue
        if len(el["text"]) >= 6 and math_ratio(el) > 0.6:
            el["kind"] = "equation"
            el["n"] = None
            for num in eq_nums:
                if num["page"] == el["page"] and abs(num["y"] - el["y"]) < 10:
                    el["n"] = int(num["text"].strip()[1:-1])
    for num in eq_nums:
        num["kind"] = "drop"

    elements = [el for el in elements if el["kind"] != "drop"]
    elements.sort(key=lambda e: (e["page"], e["y"], e["x"]))
    return elements


# ---------------------------------------------------------------------------
# Assembly helpers
# ---------------------------------------------------------------------------

NO_SPACE_JOIN = ("–", "—", "=", "×", "+", "−")


def join_wrapped(lines, qc, note_cross_page=False):
    """Join wrapped physical lines into one logical line.

    Hyphens at line ends are resolved against the document vocabulary
    (qc.vocab): drop the hyphen when the merged word occurs elsewhere in the
    document; keep it when the hyphenated compound occurs elsewhere (e.g.
    target-present) or the continuation is itself hyphenated; otherwise drop
    and log as uncertain.
    """
    out = ""
    prev_page = None
    for el in lines:
        t = el["text"].strip()
        if not t:
            continue
        if not out:
            out = t
        else:
            if note_cross_page and prev_page is not None and el["page"] != prev_page:
                qc.cross_page_joins += 1
            if out.endswith("-") and t and (t[0].islower() or t[0].isdigit()):
                prev_word = out.split()[-1][:-1]
                m = re.match(r"[A-Za-z’'\-]+", t)
                nxt = m.group(0) if m else ""
                merged = (prev_word + nxt).lower()
                hyphenated = (prev_word + "-" + nxt).lower()
                if merged in qc.vocab and hyphenated not in qc.vocab:
                    qc.dehyphenations.append(prev_word + nxt)
                    out = out[:-1] + t
                elif hyphenated in qc.vocab or "-" in nxt:
                    qc.hyphens_kept.append(prev_word + "-" + nxt)
                    out = out + t
                elif merged in qc.vocab:
                    qc.dehyphenations.append(prev_word + nxt)
                    out = out[:-1] + t
                else:
                    qc.dehyph_uncertain.append(prev_word + "|" + nxt)
                    out = out[:-1] + t
            elif out.endswith("-"):
                qc.hyphens_kept.append(out.split()[-1] + t.split()[0])
                out = out + t
            elif out.endswith(NO_SPACE_JOIN):
                out = out + t
            else:
                out = out + " " + t
        prev_page = el["page"]
    return out


def build_vocab(elements):
    """Collect the document's word forms (used to adjudicate hyphen joins)."""
    vocab = set()
    for el in elements:
        text = el["text"]
        if text.endswith("-"):  # exclude the hyphenated line-final fragment
            text = text[: text.rfind(" ") + 1] if " " in text else ""
        for w in re.findall(r"[A-Za-z][A-Za-z’'\-]+[A-Za-z]", text):
            vocab.add(w.lower())
    return vocab


def assemble_paragraphs(body_els, headings, cfg, qc):
    """Group body line elements into paragraphs (indent- and gap-based)."""
    indent_thr = cfg["paragraph"]["indent_threshold"]
    gap_thr = cfg["paragraph"]["gap_threshold"]

    # per-page left margin of body text
    margins = {}
    for el in body_els:
        margins.setdefault(el["page"], []).append(el["x"])
    margins = {p: min(xs) for p, xs in margins.items()}

    heading_keys = sorted((h["page"], h["y"]) for h in headings)

    def heading_between(a, b):
        return any(a < hk < b for hk in heading_keys)

    paras = []
    cur = []
    prev = None
    for el in body_els:
        new = False
        if not cur:
            new = True
        elif el["x"] > margins[el["page"]] + indent_thr:
            new = True
        elif prev is not None and el["page"] == prev["page"] and (el["y"] - prev["y"]) > gap_thr * 1.6:
            new = True
        elif prev is not None and heading_between((prev["page"], prev["y"]), (el["page"], el["y"])):
            new = True
        if new and cur:
            paras.append(cur)
            cur = []
        cur.append(el)
        prev = el
    if cur:
        paras.append(cur)

    out = []
    for lines in paras:
        text = join_wrapped(lines, qc, note_cross_page=True)
        pages = sorted({l["page"] for l in lines})
        out.append({"kind": "para", "page": pages[0], "y": lines[0]["y"],
                    "text": text, "pages": pages})
    return out


def assemble_captions(caption_els, qc):
    """Group caption lines per (page, block) in natural document order.

    Full-page figures are rotated (landscape) in this PDF, so geometric y/x
    sorting scrambles caption lines; PyMuPDF's block-internal line order is
    the reading order.
    """
    figures = []
    groups = {}
    for el in caption_els:
        groups.setdefault((el["page"], el["block"]), []).append(el)
    for (page, _), g in sorted(groups.items()):
        g.sort(key=lambda e: e["li"])
        text = join_wrapped(g, qc)
        m = re.match(r"Figure (\d+)\.\s*(.*)", text)
        if not m:
            qc.notes.append(f"Unparsed caption block on PDF page {page}: {text[:60]}")
            continue
        figures.append({"kind": "figure", "n": int(m.group(1)), "page": page,
                        "y": min(e["y"] for e in g), "caption": m.group(2).strip()})
    return figures


def assemble_table(table_els, cfg, qc):
    """Rebuild Table 1 from positioned spans into a Markdown table element."""
    tc = cfg["table_1"]
    anchors = tc["column_anchors"]
    col_names = tc["numeric_col_names"]

    spans = []
    for el in table_els:
        for sp in el["spans"]:
            spans.append(sp)
    spans.sort(key=lambda s: (s["y"], s["x"]))

    # caption: AdvUX 8.0 spans above the header zone
    caption_parts = [s["text"].strip() for s in spans
                     if s["font"] == "AdvUX" and s["y"] <= 170]
    caption = " ".join(caption_parts)
    caption = re.sub(r"^TABLE (\d+)\s*", "", caption)

    # cluster remaining spans into rows by y
    rows = []
    for sp in spans:
        if sp["font"] == "AdvUX" and sp["y"] <= 170:
            continue
        if rows and abs(sp["y"] - rows[-1]["y"]) <= 5:
            rows[-1]["cells"].append(sp)
        else:
            rows.append({"y": sp["y"], "cells": [sp]})

    def nearest_anchor(x):
        return min(range(len(anchors)), key=lambda i: abs(anchors[i] - x))

    md_rows = []
    notes = []
    for row in rows:
        if row["y"] <= tc["header_y_max"]:
            continue  # column headers are supplied from config
        cells = sorted(row["cells"], key=lambda s: s["x"])
        label_parts = [c["text"].strip() for c in cells if c["x"] < anchors[1] - 30]
        nums = ["", "", ""]
        for c in cells:
            if c["x"] >= anchors[1] - 30:
                idx = nearest_anchor(c["x"]) - 1
                if 0 <= idx <= 2:
                    nums[idx] = c["text"].strip()
        label = " ".join(p for p in label_parts if p)
        if label.startswith("Note"):
            notes.append(join_wrapped(
                [{"text": " ".join([label] + [n for n in nums if n]), "page": tc["page"]}], qc))
            continue
        if not any(nums):
            if label and cells[0]["x"] < tc["section_x_max"]:
                md_rows.append({"section": label})
            elif label and md_rows and "label" in md_rows[-1]:
                md_rows[-1]["label"] += " " + label  # wrapped label continuation
            continue
        md_rows.append({"label": label, "nums": nums})

    lines = [f"| Condition | {col_names[0]} | {col_names[1]} | {col_names[2]} |",
             "| --- | --- | --- | --- |"]
    for r in md_rows:
        if "section" in r:
            lines.append(f"| **{r['section']}** |  |  |  |")
        else:
            lines.append(f"| {r['label']} | {r['nums'][0]} | {r['nums'][1]} | {r['nums'][2]} |")

    return {"kind": "table", "n": 1, "page": tc["page"], "y": 138.0,
            "caption": caption, "md_lines": lines, "notes": notes,
            "row_count": sum(1 for r in md_rows if "label" in r)}


def assemble_footnotes(pool_els, cfg, qc):
    """Split bottom-of-page small text into numbered footnotes."""
    marker_size = cfg["roles"]["footnote_marker_size"]
    by_page = {}
    for el in pool_els:
        by_page.setdefault(el["page"], []).append(el)

    footnotes = []
    for page in sorted(by_page):
        els = sorted(by_page[page], key=lambda e: (e["y"], e["x"]))
        cur = None
        for el in els:
            starts = None
            for sp in el["spans"]:
                if sp["size"] == marker_size and sp["text"].strip().isdigit():
                    starts = int(sp["text"].strip())
                    break
            text = "".join(sp["text"] for sp in el["spans"]
                           if sp["size"] != marker_size).strip()
            if starts is not None:
                if cur:
                    footnotes.append(cur)
                cur = {"n": starts, "page": page, "lines": []}
            if cur is None:
                qc.notes.append(
                    f"Small text on PDF page {page} before any footnote marker: {text[:60]}")
                continue
            if text:
                cur["lines"].append({"text": text, "page": page})
        if cur:
            footnotes.append(cur)

    for fn in footnotes:
        fn["text"] = join_wrapped(fn["lines"], qc)
        del fn["lines"]
    footnotes.sort(key=lambda f: f["n"])
    return footnotes


def assemble_references(ref_els, qc):
    """Group hanging-indent reference lines into one entry per line."""
    by_page = {}
    for el in ref_els:
        by_page.setdefault(el["page"], []).append(el)
    margins = {p: min(e["x"] for e in els) for p, els in by_page.items()}

    entries = []
    cur = []
    for el in sorted(ref_els, key=lambda e: (e["page"], e["y"])):
        if el["x"] <= margins[el["page"]] + 3:
            if cur:
                entries.append(cur)
            cur = []
        cur.append(el)
    if cur:
        entries.append(cur)

    out = []
    for lines in entries:
        out.append({"text": join_wrapped(lines, qc), "page": lines[0]["page"]})
    return out


# ---------------------------------------------------------------------------
# Emission
# ---------------------------------------------------------------------------

class Book:
    """Accumulates output lines with per-line PDF-page attribution.

    page attribution: int = PDF page, None = generated scaffolding.
    Blank separator lines inherit the attribution of the preceding line.
    """

    def __init__(self):
        self.lines = []   # (text, page)

    def emit(self, text, page):
        for part in text.split("\n"):
            self.lines.append((part, page))

    def blank(self):
        page = self.lines[-1][1] if self.lines else None
        if self.lines and self.lines[-1][0] == "":
            return
        self.lines.append(("", page))

    def line_no(self):
        return len(self.lines) + 1


def build_book(cfg, elements, qc):
    roles = cfg["roles"]
    qc.vocab = build_vocab(elements)

    titles = [e for e in elements if e["kind"] == "title"]
    authors = [e for e in elements if e["kind"] == "author"]
    p1_body = [e for e in elements if e["kind"] == "body" and e["page"] == 1]
    frontnotes = [e for e in elements if e["kind"] == "frontnote"]
    abstract = [e for e in elements if e["kind"] == "abstract"]
    keywords = [e for e in elements if e["kind"] == "keywords"]
    headings = [e for e in elements if e["kind"] == "heading"]
    captions = [e for e in elements if e["kind"] == "caption"]
    tables = [e for e in elements if e["kind"] == "table"]
    equations = [e for e in elements if e["kind"] == "equation"]
    references = [e for e in elements if e["kind"] == "reference"]
    fn_pool = [e for e in elements if e["kind"] == "footnote_pool"]
    body = [e for e in elements if e["kind"] == "body" and e["page"] > 1]

    title_text = join_wrapped(titles, qc)
    paras = assemble_paragraphs(body, headings, cfg, qc)
    figures = assemble_captions(captions, qc)
    table = assemble_table(tables, cfg, qc) if tables else None
    footnotes = assemble_footnotes(fn_pool, cfg, qc)
    ref_entries = assemble_references(references, qc)

    eq_els = []
    for i, eq in enumerate(sorted(equations, key=lambda e: (e["page"], e["y"])), 1):
        eq_els.append({"kind": "equation", "n": eq.get("n") or i, "page": eq["page"],
                       "y": eq["y"], "text": eq["text"].strip()})

    # ------- flow: headings + paragraphs + figures + table + equations -------
    flow = sorted(
        [{"sort": (h["page"], h["y"]), **h} for h in headings] +
        [{"sort": (p["page"], p["y"]), **p} for p in paras] +
        [{"sort": (f["page"], f["y"]), **f} for f in figures] +
        ([{"sort": (table["page"], table["y"]), **table}] if table else []) +
        [{"sort": (e["page"], e["y"]), **e} for e in eq_els],
        key=lambda e: e["sort"])

    book = Book()
    manifest_sections = []
    manifest_figures = []
    manifest_footnotes = []
    straddles = []

    # ---- H1 + preface (generated) ----
    src = cfg["source_pdf"]
    book.emit(f"# {title_text}", 1)
    book.blank()
    preface = [
        "## Corpus Preface",
        "",
        "Purpose: Derived experimental Markdown corpus (PDF-extracted representation) "
        "for PageIndex hierarchy and retrieval experiments.",
        f"Source: {src['citation']}",
        f"DOI: {src['doi']}",
        f"Source PDF SHA-256: `{src['sha256']}`",
        f"Producer: `scripts/build_paper_book.py` with `config/paper-book-v1.yml` (this repo).",
        "",
        "Conventions: `<!-- PDF PAGE n -->` comments mark physical page boundaries; "
        "figures, tables, and equations appear as labeled placeholders "
        "(`[FIGURE n: caption]`, `[TABLE n: caption]` with extracted rows, `[EQUATION n: text]`); "
        "`[fnN]` marks in-text footnote references, with footnote text collected in the "
        "Footnotes section; the Appendix maps every PDF page to book line ranges.",
        "This document is generated — never hand-edit; fix the pipeline and rebuild.",
    ]
    book.emit("\n".join(preface), None)
    book.blank()
    manifest_sections.append({"level": 2, "title": "Corpus Preface", "line": 3,
                              "page": None, "synthetic": True})

    current_page = 0

    def advance_page(p):
        nonlocal current_page
        while current_page < p:
            current_page += 1
            book.emit(f"<!-- PDF PAGE {current_page} -->", current_page)
            book.blank()

    # ---- Front matter ----
    advance_page(1)
    line = book.line_no()
    book.emit("## Front Matter", 1)
    manifest_sections.append({"level": 2, "title": "Front Matter", "line": line,
                              "page": 1, "synthetic": True})
    book.blank()
    book.emit("### Authors and Affiliations", 1)
    book.blank()
    p1_stream = sorted(authors + p1_body, key=lambda e: (e["y"], e["x"]))
    affiliation = []

    def flush_affiliation():
        if affiliation:
            book.emit(join_wrapped(affiliation, qc), 1)
            book.blank()
            affiliation.clear()

    for el in p1_stream:
        if el["kind"] == "author":
            flush_affiliation()
            book.emit(f"**{el['text']}**", 1)
            book.blank()
        else:
            affiliation.append(el)
    flush_affiliation()

    book.emit("### Publication Note", 1)
    book.blank()
    fn_groups = []
    prev = None
    for el in sorted(frontnotes, key=lambda e: (e["y"], e["x"])):
        standalone = el["text"].startswith(("©", "http", "DOI:"))
        if prev is None or (el["y"] - prev["y"]) > 16 or standalone:
            fn_groups.append([])
        fn_groups[-1].append(el)
        prev = None if standalone else el
    for g in fn_groups:
        book.emit(join_wrapped(g, qc), 1)
        book.blank()

    # ---- Abstract ----
    line = book.line_no()
    book.emit("## Abstract", 1)
    manifest_sections.append({"level": 2, "title": "Abstract", "line": line,
                              "page": 1, "synthetic": False})
    book.blank()
    abs_text = join_wrapped(sorted(abstract, key=lambda e: (e["page"], e["y"])), qc,
                            note_cross_page=True)
    book.emit(abs_text, 1)
    book.blank()
    kw_text = join_wrapped(sorted(keywords, key=lambda e: (e["page"], e["y"])), qc)
    kw_text = re.sub(r"^Key words:\s*", "", kw_text)
    advance_page(2)
    book.emit(f"**Key words:** {kw_text}", 2)
    book.blank()

    # ---- Synthetic sections (e.g. the unlabeled introduction) ----
    for s in cfg.get("synthetic_sections", []):
        line = book.line_no()
        book.emit(f"## {s['title']}", current_page)
        book.emit("<!-- SYNTHETIC HEADING: not present in the printed paper -->", None)
        manifest_sections.append({"level": 2, "title": s["title"], "line": line,
                                  "page": current_page, "synthetic": True})
        book.blank()

    # ---- Main flow ----
    references_line = None
    for el in flow:
        advance_page(el["page"])
        if el["kind"] == "heading":
            line = book.line_no()
            book.emit(f"{'#' * el['level']} {el['text']}", el["page"])
            manifest_sections.append({"level": el["level"], "title": el["text"],
                                      "line": line, "page": el["page"],
                                      "synthetic": False})
            if el["text"].strip() == "REFERENCES":
                references_line = line
            book.blank()
        elif el["kind"] == "para":
            line = book.line_no()
            book.emit(el["text"], el["page"])
            if len(el["pages"]) > 1:
                straddles.append({"line": line, "pages": el["pages"]})
            book.blank()
        elif el["kind"] == "figure":
            line = book.line_no()
            book.emit(f"[FIGURE {el['n']}: {el['caption']}]", el["page"])
            manifest_figures.append({"n": el["n"], "page": el["page"], "line": line,
                                     "caption_preview": el["caption"][:100]})
            book.blank()
        elif el["kind"] == "table":
            book.emit(f"[TABLE {el['n']}: {el['caption']}]", el["page"])
            book.blank()
            book.emit("\n".join(el["md_lines"]), el["page"])
            book.blank()
            for note in el["notes"]:
                book.emit(note, el["page"])
                book.blank()
        elif el["kind"] == "equation":
            book.emit(f"[EQUATION {el['n']}: {el['text']}]", el["page"])
            book.blank()

    # ---- References entries ----
    ref_start = book.line_no()
    for entry in ref_entries:
        advance_page(entry["page"])
        book.emit(f"- {entry['text']}", entry["page"])
    ref_end = book.line_no() - 1
    book.blank()

    # ---- Footnotes (generated section; entries attributed to their PDF page) ----
    line = book.line_no()
    book.emit("## Footnotes", None)
    manifest_sections.append({"level": 2, "title": "Footnotes", "line": line,
                              "page": None, "synthetic": True})
    book.blank()
    for fn in footnotes:
        line = book.line_no()
        book.emit(f"**Footnote {fn['n']}** (PDF page {fn['page']}): {fn['text']}",
                  fn["page"])
        manifest_footnotes.append({"n": fn["n"], "page": fn["page"], "line": line})
        book.blank()

    return (book, {
        "title": title_text,
        "sections": manifest_sections,
        "figures": manifest_figures,
        "table": {"n": 1, "page": table["page"], "caption": table["caption"],
                  "rows": table["row_count"]} if table else None,
        "equations": [{"n": e["n"], "page": e["page"], "text": e["text"]} for e in eq_els],
        "footnotes": manifest_footnotes,
        "references": {"count": len(ref_entries), "start_line": ref_start,
                       "end_line": ref_end, "line": references_line},
        "straddles": straddles,
    })


def append_page_map(book, page_count):
    """Compute page -> line-range map from attributions, append as appendix."""
    page_ranges = {}
    for idx, (_, page) in enumerate(book.lines, start=1):
        if page is None:
            continue
        ranges = page_ranges.setdefault(page, [])
        if ranges and ranges[-1][1] == idx - 1:
            ranges[-1][1] = idx
        else:
            ranges.append([idx, idx])

    appendix_start = book.line_no()
    book.emit("## Appendix: PDF Page Map", None)
    book.blank()
    book.emit("Every book line maps to a physical PDF page below; lines outside these "
              "ranges are generated scaffolding (preface, section markers, this appendix).",
              None)
    book.blank()
    book.emit("| PDF page | Book lines |", None)
    book.emit("| --- | --- |", None)
    for page in range(1, page_count + 1):
        ranges = page_ranges.get(page, [])
        pretty = ", ".join(f"L{a}–L{b}" if a != b else f"L{a}" for a, b in ranges)
        book.emit(f"| {page} | {pretty} |", None)
    book.emit("", None)

    generated = []
    for idx, (_, page) in enumerate(book.lines, start=1):
        if page is None:
            if generated and generated[-1][1] == idx - 1:
                generated[-1][1] = idx
            else:
                generated.append([idx, idx])
    return page_ranges, generated, appendix_start


# ---------------------------------------------------------------------------
# QC report
# ---------------------------------------------------------------------------

def render_qc_report(cfg, manifest, qc):
    src = cfg["source_pdf"]
    m = manifest
    lines = []
    a = lines.append
    a("# QC Report: paper-book-v1")
    a("")
    a("Generated by `scripts/build_paper_book.py` — regenerate with `--overwrite`; "
      "never hand-edit.")
    a("")
    a(f"Source: {src['citation']} (DOI {src['doi']})")
    a(f"Source PDF SHA-256: `{src['sha256']}` ({src['pages']} pages)")
    a(f"Corpus SHA-256: `{m['corpus_sha256']}` ({m['counts']['lines']} lines)")
    a("")
    a("## Section inventory")
    a("")
    a("| Level | Section | Book line | PDF page | Origin |")
    a("| --- | --- | --- | --- | --- |")
    for s in m["sections"]:
        origin = "synthetic/generated" if s["synthetic"] else "print heading"
        page = s["page"] if s["page"] is not None else "—"
        a(f"| H{s['level']} | {s['title']} | L{s['line']} | {page} | {origin} |")
    a("")
    a("## Figures")
    a("")
    a("| Figure | PDF page | Book line | Caption (start) |")
    a("| --- | --- | --- | --- |")
    for f in m["figures"]:
        a(f"| {f['n']} | {f['page']} | L{f['line']} | {f['caption_preview']} |")
    a("")
    a("## Table, equation, footnotes")
    a("")
    if m["table"]:
        a(f"- TABLE 1 (PDF page {m['table']['page']}): {m['table']['rows']} data rows "
          f"reconstructed from span coordinates — “{m['table']['caption']}”.")
    for e in m["equations"]:
        a(f"- EQUATION {e['n']} (PDF page {e['page']}): best-effort text "
          f"`{e['text']}` — math glyphs approximated, verify against print.")
    fn_pages = ", ".join(str(f["page"]) for f in m["footnotes"])
    a(f"- {len(m['footnotes'])} footnotes (PDF pages {fn_pages}) collected in the "
      f"Footnotes section; in-text markers rendered as `[fnN]`.")
    a("")
    a("## References boundary")
    a("")
    r = m["references"]
    a(f"- REFERENCES heading at L{r['line']}; {r['count']} entries, one per line, "
      f"L{r['start_line']}–L{r['end_line']}.")
    a("")
    a("## Extraction issues found (and how they were handled)")
    a("")
    subs = ", ".join(f"{font}: {n}" for font, n in sorted(m["qc"]["glyph_substitutions"].items()))
    a(f"1. **Symbol-font glyph corruption** — the published PDF encodes `<`, `=`, `−`, "
      f"`+`, `×`, `–`, `—`, `°`, `©`, `γ` in private symbol fonts that extract as wrong "
      f"or control characters (e.g. `p<.001` extracted as `pB.001`). Decoded via a "
      f"font-keyed glyph map in config. Substitutions applied: {subs}.")
    a(f"2. **Ligatures and diacritics** — {m['qc']['ligatures']} broken ligatures "
      f"(ﬁ, ﬂ, …) normalized to ASCII pairs; {m['qc']['diacritics_recombined']} "
      f"split diacritics recombined (ñ, ä).")
    a(f"3. **Line-break hyphenation** — {m['qc']['dehyphenations']} hyphenated line "
      f"breaks re-joined and {m['qc']['hyphens_kept']} compound hyphens kept, "
      f"adjudicated against the document's own vocabulary. Samples of joins: "
      f"{', '.join(m['qc']['dehyphenation_samples'][:8])}. "
      f"Joins with no vocabulary evidence (review these): "
      f"{', '.join(m['qc']['dehyphenations_uncertain']) or 'none'}.")
    a(f"4. **Header/footer bleed** — running heads/page numbers "
      f"({m['qc']['furniture_stripped']['running_heads']} spans) and the per-page "
      f"`Downloaded By: [Oliva, Aude]` watermark "
      f"({m['qc']['furniture_stripped']['watermark']} spans) stripped by font/position "
      f"rules.")
    a(f"5. **Cross-page joins** — {m['qc']['cross_page_joins']} logical lines "
      f"(paragraphs, the abstract, reference entries) were joined across a page "
      f"boundary; {len(m['straddles'])} body paragraphs straddle pages and are "
      f"attributed to their starting page in the page map (listed in the manifest).")
    a(f"6. **Inline sub/superscripts** — subscript letters (e.g. the S/T/C in "
      f"M_S, M_T, M_C) are kept inline without markup; footnote superscripts became "
      f"`[fnN]` markers.")
    a("7. **Italics dropped** — italic spans (journal names, emphasis) are emitted as "
      "plain text; no Markdown emphasis is generated.")
    if m["qc"]["unmapped_symbol_chars"]:
        a(f"8. **Unmapped symbol glyphs** (kept verbatim, review needed): "
          f"{m['qc']['unmapped_symbol_chars']}")
    a("")
    a("## Page map summary")
    a("")
    covered = m["counts"]["lines"] - m["counts"]["generated_lines"]
    a(f"- {m['counts']['lines']} total lines: {covered} attributed to PDF pages 1–"
      f"{src['pages']}, {m['counts']['generated_lines']} generated scaffolding "
      f"(preface, synthetic headings, appendix).")
    a(f"- {len(m['straddles'])} straddling paragraphs (text spanning a page boundary, "
      f"attributed to the starting page).")
    a("")
    a("## Known extraction warts (kept verbatim)")
    a("")
    for wart in cfg.get("known_extraction_warts", []):
        a(f"- {wart}")
    a("")
    a("## Open questions for Barbara")
    a("")
    for note in m["qc"]["notes"]:
        a(f"- {note}")
    a("- The paper's opening section has no printed heading; a synthetic "
      "`## Introduction` was inserted (marked with an HTML comment). OK?")
    a("- EQUATION 1's text is a best-effort rendering of mangled math fonts — please "
      "verify it reads correctly against the print version.")
    a("- Table 1 was rebuilt from raw span coordinates (PyMuPDF found no table object); "
      "please spot-check the numbers against the print table.")
    a("- Sub/superscript letters are flattened inline (e.g. `MS(x, y)` for M_S); "
      "acceptable for retrieval, or should the pipeline add explicit `_S` markers?")
    a("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def git_info():
    def run(*args):
        try:
            return subprocess.run(["git", *args], cwd=ROOT, capture_output=True,
                                  text=True, check=True).stdout.strip()
        except Exception:
            return None
    commit = run("rev-parse", "HEAD")
    dirty = bool(run("status", "--porcelain"))
    sub = run("rev-parse", "HEAD:vendor/PageIndex")
    return commit, dirty, sub


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--out-root", type=Path, default=ROOT,
                    help="root under which corpus/ and reports/ are written (tests)")
    ap.add_argument("--overwrite", action="store_true",
                    help="required to overwrite existing outputs")
    args = ap.parse_args()

    cfg = yaml.safe_load(CONFIG_PATH.read_text())
    src = cfg["source_pdf"]

    if fitz.__version__.split()[0] != str(cfg["extraction"]["expected_version"]):
        sys.exit(f"ERROR: PyMuPDF {fitz.__version__} != pinned "
                 f"{cfg['extraction']['expected_version']}; reproducibility not "
                 f"guaranteed. Update config deliberately if upgrading.")

    pdf_path = ROOT / src["path"]
    actual_sha = sha256_file(pdf_path)
    if actual_sha != src["sha256"]:
        sys.exit(f"ERROR: source PDF sha256 mismatch:\n  pinned {src['sha256']}\n"
                 f"  actual {actual_sha}")

    out_dir = args.out_root / cfg["output"]["corpus_dir"]
    qc_path = args.out_root / cfg["output"]["qc_report"]
    md_path = out_dir / "paper-book-v1.md"
    manifest_path = out_dir / "paper-book-v1.manifest.json"
    prov_path = out_dir / "provenance.json"

    for p in (md_path, manifest_path, prov_path, qc_path):
        if p.exists() and not args.overwrite:
            sys.exit(f"ERROR: {p} exists; pass --overwrite to regenerate.")

    doc = fitz.open(pdf_path)
    if doc.page_count != src["pages"]:
        sys.exit(f"ERROR: expected {src['pages']} pages, PDF has {doc.page_count}")

    qc = QC()
    elements = extract_elements(doc, cfg, qc)
    book, meta = build_book(cfg, elements, qc)
    page_ranges, generated, _ = append_page_map(book, src["pages"])

    md_text = "\n".join(t for t, _ in book.lines) + "\n"
    corpus_sha = sha256_text(md_text)

    exp = cfg["expected"]
    problems = []
    if len(meta["figures"]) != exp["figures"]:
        problems.append(f"figures: {len(meta['figures'])} != expected {exp['figures']}")
    if len(meta["footnotes"]) != exp["footnotes"]:
        problems.append(f"footnotes: {len(meta['footnotes'])} != expected {exp['footnotes']}")
    if len(meta["equations"]) != exp["equations"]:
        problems.append(f"equations: {len(meta['equations'])} != expected {exp['equations']}")
    got_h2 = [s["title"] for s in meta["sections"] if s["level"] == 2 and not s["synthetic"]]
    for want in exp["top_level_sections"]:
        if want not in got_h2:
            problems.append(f"missing top-level section: {want}")
    if problems:
        print("WARNING: expectation mismatches (build continues; review QC):",
              file=sys.stderr)
        for p in problems:
            print("  -", p, file=sys.stderr)

    manifest = {
        "corpus_version": cfg["corpus_version"],
        "title": meta["title"],
        "source_pdf_sha256": src["sha256"],
        "extraction_tool": cfg["extraction"]["tool"],
        "extraction_tool_version": fitz.__version__,
        "counts": {
            "pdf_pages": src["pages"],
            "lines": len(book.lines),
            "generated_lines": sum(b - a + 1 for a, b in generated),
            "sections": len(meta["sections"]),
            "figures": len(meta["figures"]),
            "tables": 1 if meta["table"] else 0,
            "equations": len(meta["equations"]),
            "footnotes": len(meta["footnotes"]),
            "references": meta["references"]["count"],
        },
        "sections": meta["sections"],
        "figures": meta["figures"],
        "table": meta["table"],
        "equations": meta["equations"],
        "footnotes": meta["footnotes"],
        "references": meta["references"],
        "page_map": [{"page": p, "ranges": page_ranges.get(p, [])}
                     for p in range(1, src["pages"] + 1)],
        "generated_line_ranges": generated,
        "straddles": meta["straddles"],
        "expectation_mismatches": problems,
        "qc": {
            "glyph_substitutions": qc.glyph_subs,
            "ligatures": qc.ligatures,
            "diacritics_recombined": qc.diacritics,
            "dehyphenations": len(qc.dehyphenations),
            "dehyphenation_samples": qc.dehyphenations[:20],
            "dehyphenations_uncertain": qc.dehyph_uncertain,
            "hyphens_kept": len(qc.hyphens_kept),
            "cross_page_joins": qc.cross_page_joins,
            "furniture_stripped": {"watermark": qc.watermark_lines,
                                   "running_heads": qc.running_head_lines},
            "unmapped_symbol_chars": [list(u) for u in qc.unmapped_symbol_chars],
            "inline_subscripts": sorted({t for _, t in qc.inline_subscripts}),
            "notes": qc.notes,
        },
        "corpus_sha256": corpus_sha,
    }
    manifest["qc"]["hyphens_kept_samples"] = qc.hyphens_kept[:10]
    manifest_text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"

    commit, dirty, sub = git_info()
    provenance = {
        "corpus_version": cfg["corpus_version"],
        "producer": "in-repo (scripts/build_paper_book.py) — unlike site-book-v1, "
                    "which is produced in the website repo and synced",
        "source_pdf_path": src["path"],
        "source_pdf_sha256": src["sha256"],
        "doi": src["doi"],
        "extraction_tool": cfg["extraction"]["tool"],
        "extraction_tool_version": fitz.__version__,
        "config_path": "config/paper-book-v1.yml",
        "config_sha256": sha256_file(CONFIG_PATH),
        "repo_commit": commit,
        "repo_dirty": dirty,
        "pageindex_commit": sub,
        "corpus_sha256": corpus_sha,
        "manifest_sha256": sha256_text(manifest_text),
        "built_at": datetime.datetime.now(datetime.timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    qc_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(md_text)
    manifest_path.write_text(manifest_text)
    prov_path.write_text(json.dumps(provenance, indent=2, ensure_ascii=False) + "\n")

    manifest_for_qc = dict(manifest)
    qc_path.write_text(render_qc_report(cfg, manifest_for_qc, qc))

    print(f"wrote {md_path} ({len(book.lines)} lines, sha256 {corpus_sha[:16]}…)")
    print(f"wrote {manifest_path}")
    print(f"wrote {prov_path}")
    print(f"wrote {qc_path}")
    if problems:
        print(f"{len(problems)} expectation mismatch(es) — see stderr/QC report")


if __name__ == "__main__":
    main()

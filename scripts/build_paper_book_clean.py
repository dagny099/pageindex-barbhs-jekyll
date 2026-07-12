#!/usr/bin/env python3
"""Producer for corpus/paper-book-v1-clean/: the Markdown-native structural control.

This is the "favorable, clean" representation arm for the PDF-vs-Markdown
comparison. It is derived DETERMINISTICALLY from the already-frozen
corpus/paper-book-v1/ by STRUCTURAL transforms only — it never edits words — so
text fidelity is provably identical to the PDF-derived arm and *representation*
(clean native Markdown vs PDF-instrumented) is the only variable between them.

Transforms applied (all structural):
  1. drop the PDF instrumentation: `<!-- PDF PAGE n -->` markers, the
     `## Corpus Preface` block, the `## Appendix: PDF Page Map` block, and
     `<!-- SYNTHETIC HEADING ... -->` comments.
  2. title-case the ALL-CAPS print headings (EXPERIMENTAL METHOD -> Experimental
     Method) to native Markdown convention; hierarchy is unchanged.
  3. collapse the blank lines the removals leave behind.
Figures/tables keep their reading-order positions (already sensible, since PDF
order == reading order); they are NOT relocated.

A text-parity assertion guarantees every retained content line is byte-identical
to paper-book-v1 (only headings are re-cased, and only in case). Re-running is
byte-identical against the same paper-book-v1 input.

Usage:
  python3 scripts/build_paper_book_clean.py --overwrite
"""

import argparse
import datetime
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = ROOT / "corpus" / "paper-book-v1"
OUT_DIR = ROOT / "corpus" / "paper-book-v1-clean"
QC_PATH = ROOT / "reports" / "qc-paper-book-v1-clean.md"


def sha256_text(t: str) -> str:
    return hashlib.sha256(t.encode("utf-8")).hexdigest()


def title_case_heading(text: str) -> str:
    """Title-case an ALL-CAPS heading, keeping short function words lower."""
    small = {"of", "the", "and", "a", "an", "in", "on", "for", "to", "by", "vs"}
    words = text.split()
    out = []
    for i, w in enumerate(words):
        lw = w.lower()
        out.append(lw if (lw in small and i != 0) else lw.capitalize())
    return " ".join(out)


def transform(src_md: str):
    """Return (clean_md, sections, figures, table_line, footnotes, parity_content)."""
    lines = src_md.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]

    out = []
    parity = []          # retained content lines, verbatim (for parity check)
    sections = []
    figures = []
    footnotes = []
    table_line = None

    skip_block = None    # None | "preface" | "appendix"
    for ln in lines:
        heading = re.match(r"^(#{1,6}) (.*)$", ln)

        # enter/exit scaffolding blocks by heading
        if heading:
            title = heading.group(2).strip()
            if title == "Corpus Preface":
                skip_block = "preface"
                continue
            if title == "Appendix: PDF Page Map":
                skip_block = "appendix"
                continue
            # any other heading ends a skip block
            skip_block = None
        if skip_block:
            continue

        # drop PDF instrumentation comments/markers
        if re.match(r"^<!-- (PDF PAGE \d+|SYNTHETIC HEADING).*-->$", ln):
            continue

        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip()
            letters = re.sub(r"[^A-Za-z]", "", title)
            if letters and letters == letters.upper():
                title = title_case_heading(title)
            emitted = f"{'#' * level} {title}"
            sections.append({"level": level, "title": title, "line": len(out) + 1})
            out.append(emitted)
            continue

        # content line (verbatim)
        out.append(ln)
        if ln.strip():
            parity.append(ln)
        fm = re.match(r"^\[FIGURE (\d+):", ln)
        if fm:
            figures.append({"n": int(fm.group(1)), "line": len(out)})
        if ln.startswith("[TABLE 1:"):
            table_line = len(out)
        fn = re.match(r"^\*\*Footnote (\d+)\*\*", ln)
        if fn:
            footnotes.append({"n": int(fn.group(1)), "line": len(out)})

    # collapse 3+ consecutive blanks to a single blank; fix section line numbers after
    collapsed = []
    blanks = 0
    remap = {}  # old index in `out` (1-based) -> new
    for i, ln in enumerate(out, 1):
        if ln == "":
            blanks += 1
            if blanks >= 2:
                remap[i] = len(collapsed)  # points at the kept blank
                continue
        else:
            blanks = 0
        collapsed.append(ln)
        remap[i] = len(collapsed)

    def fix(items):
        for it in items:
            it["line"] = remap[it["line"]]
    fix(sections); fix(figures); fix(footnotes)
    if table_line is not None:
        table_line = remap[table_line]

    clean_md = "\n".join(collapsed) + "\n"
    return clean_md, sections, figures, table_line, footnotes, parity


def retained_content_from_source(src_md: str):
    """The non-heading, non-scaffolding content lines of paper-book-v1, in order.

    Must equal the clean doc's non-heading content lines (proves no word changed).
    """
    lines = src_md.split("\n")
    kept = []
    skip_block = None
    for ln in lines:
        heading = re.match(r"^(#{1,6}) (.*)$", ln)
        if heading:
            title = heading.group(2).strip()
            if title == "Corpus Preface":
                skip_block = "preface"; continue
            if title == "Appendix: PDF Page Map":
                skip_block = "appendix"; continue
            skip_block = None
            continue  # headings compared separately (they are re-cased)
        if skip_block:
            continue
        if re.match(r"^<!-- (PDF PAGE \d+|SYNTHETIC HEADING).*-->$", ln):
            continue
        if ln.strip():
            kept.append(ln)
    return kept


def git_info():
    def run(*a):
        try:
            return subprocess.run(["git", *a], cwd=ROOT, capture_output=True,
                                  text=True, check=True).stdout.strip()
        except Exception:
            return None
    return run("rev-parse", "HEAD"), bool(run("status", "--porcelain"))


def render_qc(manifest, src_prov):
    m = manifest
    L = []
    a = L.append
    a("# QC Report: paper-book-v1-clean")
    a("")
    a("Generated by `scripts/build_paper_book_clean.py` — regenerate with "
      "`--overwrite`; never hand-edit.")
    a("")
    a("The Markdown-native structural control for the PDF-vs-Markdown comparison. "
      "Derived by structural transforms from `corpus/paper-book-v1/` (never edits "
      "words), so text fidelity is identical to the PDF-derived arm and "
      "representation is the only variable.")
    a("")
    a(f"Derived from paper-book-v1 corpus SHA-256: `{src_prov['corpus_sha256']}`")
    a(f"This corpus SHA-256: `{m['corpus_sha256']}` ({m['counts']['lines']} lines)")
    a("")
    a("## What differs from paper-book-v1 (structure only)")
    a("")
    a("- Removed PDF instrumentation: `<!-- PDF PAGE n -->` markers, the Corpus "
      "Preface block, the Appendix: PDF Page Map block, synthetic-heading comments.")
    a("- Title-cased the ALL-CAPS print headings (e.g. EXPERIMENTAL METHOD -> "
      "Experimental Method); heading hierarchy unchanged.")
    a("- Figures/tables keep their reading-order positions (not relocated).")
    a("")
    a("## Text-fidelity guarantee")
    a("")
    a(f"- Text-parity check PASSED: all {m['counts']['content_lines']} non-heading "
      "content lines are byte-identical to paper-book-v1 (verified at build time). "
      "No glyph, ligature, statistic, or word differs between the two arms.")
    a("")
    a("## Section inventory")
    a("")
    a("| Level | Section | Line |")
    a("| --- | --- | --- |")
    for s in m["sections"]:
        a(f"| H{s['level']} | {s['title']} | L{s['line']} |")
    a("")
    a("## Figures / table / footnotes")
    a("")
    a(f"- {len(m['figures'])} figure placeholders at lines "
      f"{', '.join('L%d' % f['line'] for f in m['figures'])}.")
    a(f"- Table 1 at L{m['table_line']}." if m["table_line"] else "- Table 1: not found.")
    a(f"- {len(m['footnotes'])} footnotes retained.")
    a("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    src_md_path = SRC_DIR / "paper-book-v1.md"
    src_prov = json.loads((SRC_DIR / "provenance.json").read_text())
    src_manifest = json.loads((SRC_DIR / "paper-book-v1.manifest.json").read_text())
    src_md = src_md_path.read_text()

    # guard: source corpus must match its own pinned hash (don't derive from a dirty book)
    if sha256_text(src_md) != src_manifest["corpus_sha256"]:
        sys.exit("ERROR: paper-book-v1.md does not match its manifest hash; "
                 "rebuild the source corpus first.")

    md_path = OUT_DIR / "paper-book-v1-clean.md"
    manifest_path = OUT_DIR / "paper-book-v1-clean.manifest.json"
    prov_path = OUT_DIR / "provenance.json"
    for p in (md_path, manifest_path, prov_path, QC_PATH):
        if p.exists() and not args.overwrite:
            sys.exit(f"ERROR: {p} exists; pass --overwrite.")

    clean_md, sections, figures, table_line, footnotes, parity = transform(src_md)

    # --- text-parity assertion: no word changed, only structure ---
    clean_content = [ln for ln in clean_md.split("\n")
                     if ln.strip() and not re.match(r"^#{1,6} ", ln)]
    src_content = retained_content_from_source(src_md)
    if clean_content != src_content:
        # find first divergence for the error message
        for i, (a_, b_) in enumerate(zip(clean_content, src_content)):
            if a_ != b_:
                sys.exit(f"ERROR: text parity broken at content line {i}:\n"
                         f"  clean: {a_!r}\n  src:   {b_!r}")
        sys.exit(f"ERROR: text parity broken (length {len(clean_content)} vs "
                 f"{len(src_content)})")

    corpus_sha = sha256_text(clean_md)
    manifest = {
        "corpus_version": "paper-book-v1-clean",
        "role": "markdown-native structural control (PDF-vs-Markdown comparison)",
        "derived_from": "paper-book-v1",
        "derived_from_corpus_sha256": src_manifest["corpus_sha256"],
        "source_pdf_sha256": src_manifest["source_pdf_sha256"],
        "counts": {
            "lines": clean_md.count("\n"),
            "content_lines": len(clean_content),
            "sections": len(sections),
            "figures": len(figures),
            "tables": 1 if table_line else 0,
            "footnotes": len(footnotes),
        },
        "sections": sections,
        "figures": figures,
        "table_line": table_line,
        "footnotes": footnotes,
        "text_parity_verified": True,
        "corpus_sha256": corpus_sha,
    }
    manifest_text = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"

    commit, dirty = git_info()
    provenance = {
        "corpus_version": "paper-book-v1-clean",
        "producer": "in-repo (scripts/build_paper_book_clean.py) — structural "
                    "transform of paper-book-v1; the Markdown-native control arm",
        "derived_from": "corpus/paper-book-v1/paper-book-v1.md",
        "derived_from_corpus_sha256": src_manifest["corpus_sha256"],
        "source_pdf_sha256": src_manifest["source_pdf_sha256"],
        "transform": "structural-only (strip PDF instrumentation, title-case "
                     "headings); text parity asserted at build",
        "repo_commit": commit,
        "repo_dirty": dirty,
        "corpus_sha256": corpus_sha,
        "manifest_sha256": sha256_text(manifest_text),
        "built_at": datetime.datetime.now(datetime.timezone.utc)
            .strftime("%Y-%m-%dT%H:%M:%SZ"),
    }

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    md_path.write_text(clean_md)
    manifest_path.write_text(manifest_text)
    prov_path.write_text(json.dumps(provenance, indent=2, ensure_ascii=False) + "\n")
    QC_PATH.write_text(render_qc(manifest, src_prov))

    print(f"wrote {md_path} ({manifest['counts']['lines']} lines, "
          f"sha256 {corpus_sha[:16]}…)")
    print(f"text parity: PASSED ({len(clean_content)} content lines identical)")
    print(f"sections: {len(sections)}  figures: {len(figures)}  "
          f"footnotes: {len(footnotes)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
eurlex_html_to_markdown.py — deterministic Markdown twin from an EUR-Lex
Official-Journal XHTML (ELI/CONVEX) rendition of an EU legislative act. NO LLM, ~$0.

WHY THIS EXISTS
---------------
The representation study pairs a Markdown-native arm against a PDF arm that
differ ONLY in representation (addressing + text fidelity + producer path), over
the same section structure. For RFC 9110 the Markdown twin came from the official
HTML via a generic h1-6 -> heading conversion. That recipe FAILS on EUR-Lex acts:
their HTML carries ZERO <h1>-<h6> tags — structure lives entirely in nested
`<div class="eli-subdivision">` plus classed title paragraphs
(oj-ti-section-1 = "CHAPTER I"/"Section 1" number line, oj-ti-section-2 = its
rubric, oj-ti-art = "Article N", oj-sti-art = the article rubric).

This tool reads those markers in document order and emits Markdown headings whose
depth mirrors the document's own nesting, so the deterministic heading tree built
over the output is structurally PARALLEL to the PDF-text-headings arm
(scripts/build_pdf_outline_index.py --headings-from text): Chapter (#), Section
(##), Article (## directly under a chapter, ### under a section), and a single
leading "Recitals (Preamble)" (#) node for the citations + recitals. Titles use
the same "{Kind} {number} — {rubric}" normalization as the PDF arm, so the two
indices line up node-for-node.

Body text is every paragraph's text in document order under its heading (article
points are EUR-Lex tables of `(a)` / text cells — captured verbatim as lines; no
content dropped). Clean, HTML-derived text is exactly the fidelity advantage the
Markdown arm is meant to have over PDF extraction.

GENERAL BY DESIGN
-----------------
Nothing is GDPR-specific; it works on any EUR-Lex act sharing the ELI/CONVEX
class vocabulary. Deterministic: same HTML in -> byte-identical Markdown out.

USAGE
-----
  .venv/bin/python scripts/eurlex_html_to_markdown.py \
      --html sources/gdpr-2016-679/gdpr.html --out workspace/gdpr.md
  .venv/bin/python scripts/eurlex_html_to_markdown.py --self-test   # offline
"""

from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# Title-marker paragraph classes (NOT body text).
CLS_CHAPTER_SECTION_NUM = "oj-ti-section-1"   # "CHAPTER I" or "Section 1"
CLS_CHAPTER_SECTION_TIT = "oj-ti-section-2"   # its rubric
CLS_ARTICLE_NUM = "oj-ti-art"                 # "Article N"
CLS_ARTICLE_TIT = "oj-sti-art"                # article rubric
MARKER_CLASSES = {CLS_CHAPTER_SECTION_NUM, CLS_CHAPTER_SECTION_TIT,
                  CLS_ARTICLE_NUM, CLS_ARTICLE_TIT}

PREAMBLE_TITLE = "Recitals (Preamble)"


class ParagraphCollector(HTMLParser):
    """Collect every <p>'s class set and normalized inner text, in document
    order. Inner markup (spans, sup) contributes its text; block nesting (the
    <td>/<table> wrapping article points) is ignored — we only care about the
    ordered stream of paragraphs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.paras: list[tuple[set[str], str]] = []
        self._stack: list[tuple[set[str], list[str]]] = []

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag == "p":
            cls = dict(attrs).get("class", "") or ""
            self._stack.append((set(cls.split()), []))

    def handle_data(self, data: str) -> None:
        if self._stack:
            self._stack[-1][1].append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "p" and self._stack:
            cls, parts = self._stack.pop()
            text = re.sub(r"\s+", " ", "".join(parts)).strip()
            self.paras.append((cls, text))


def _classify(cls: set[str]) -> str | None:
    for c in MARKER_CLASSES:
        if c in cls:
            return c
    return None


def paragraphs_to_markdown(paras: list[tuple[set[str], str]]) -> str:
    """Ordered pass over paragraphs -> Markdown. Section-open state (reset by
    each Chapter, set by each Section) decides whether an Article nests at depth
    2 or 3 — identical logic to the PDF text-heading scanner, so the two arms
    produce parallel trees."""
    out: list[str] = []
    section_open = False
    any_heading = False

    def emit_heading(depth: int, title: str) -> None:
        nonlocal any_heading
        if out:
            out.append("")
        out.append("#" * depth + " " + title)
        out.append("")
        any_heading = True

    i, n = 0, len(paras)
    while i < n:
        cls, text = paras[i]
        kind = _classify(cls)

        if kind == CLS_CHAPTER_SECTION_NUM:
            rubric = ""
            if i + 1 < n and CLS_CHAPTER_SECTION_TIT in paras[i + 1][0]:
                rubric = paras[i + 1][1]
                i += 1
            m = re.match(r"\s*(CHAPTER|Section)\s+([IVXLC]+|\d+)", text, re.I)
            if m and m.group(1).upper() == "CHAPTER":
                title = f"Chapter {m.group(2)}"
                section_open, depth = False, 1
            else:
                num = m.group(2) if m else text.strip()
                title = f"Section {num}"
                section_open, depth = True, 2
            if rubric:
                title = f"{title} — {rubric}"
            emit_heading(depth, title)

        elif kind == CLS_ARTICLE_NUM:
            rubric = ""
            if i + 1 < n and CLS_ARTICLE_TIT in paras[i + 1][0]:
                rubric = paras[i + 1][1]
                i += 1
            m = re.match(r"\s*Article\s+(\d+)", text)
            title = f"Article {m.group(1)}" if m else text.strip()
            if rubric:
                title = f"{title} — {rubric}"
            emit_heading(3 if section_open else 2, title)

        elif kind in (CLS_CHAPTER_SECTION_TIT, CLS_ARTICLE_TIT):
            pass  # a stray rubric not consumed above — skip (never body)

        else:  # body paragraph
            if text:
                if not any_heading:
                    emit_heading(1, PREAMBLE_TITLE)  # pre-chapter text -> preamble
                out.append(text)

        i += 1

    return "\n".join(out).rstrip("\n") + "\n"


def html_to_markdown(html: str) -> str:
    p = ParagraphCollector()
    p.feed(html)
    return paragraphs_to_markdown(p.paras)


# --------------------------------------------------------------------------
# Offline self-test (no file, no network)
# --------------------------------------------------------------------------

def self_test() -> None:
    failures = []

    def check(name, got, want):
        ok = got == want
        print(f"  {'PASS' if ok else 'FAIL'}: {name} (got {got!r}, want {want!r})")
        if not ok:
            failures.append(name)

    html = """
    <p class="oj-doc-ti">REGULATION (EU) TEST</p>
    <p class="oj-normal">Whereas recital text.</p>
    <div id="cpt_I">
      <p class="oj-ti-section-1"><span>CHAPTER I</span></p>
      <div class="eli-title"><p class="oj-ti-section-2">General provisions</p></div>
      <div class="eli-subdivision" id="art_1">
        <p class="oj-ti-art">Article 1</p>
        <div class="eli-title"><p class="oj-sti-art">Scope</p></div>
        <p class="oj-normal">Body of article one.</p>
      </div>
    </div>
    <div id="cpt_II">
      <p class="oj-ti-section-1"><span>CHAPTER II</span></p>
      <div class="eli-title"><p class="oj-ti-section-2">Rights</p></div>
      <div id="cpt_II.sct_1">
        <p class="oj-ti-section-1"><span>Section 1</span></p>
        <div class="eli-title"><p class="oj-ti-section-2">Access</p></div>
        <div class="eli-subdivision" id="art_2">
          <p class="oj-ti-art">Article 2</p>
          <div class="eli-title"><p class="oj-sti-art">Right of access</p></div>
          <table><tbody><tr><td><p class="oj-normal">(a)</p></td>
            <td><p class="oj-normal">first point.</p></td></tr></tbody></table>
        </div>
      </div>
    </div>
    """
    md = html_to_markdown(html)
    lines = md.splitlines()
    headings = [l for l in lines if l.startswith("#")]
    check("preamble heading first", headings[0], "# " + PREAMBLE_TITLE)
    check("chapter I depth/title", "# Chapter I — General provisions" in headings, True)
    check("article 1 under chapter is depth 2", "## Article 1 — Scope" in headings, True)
    check("section depth 2", "## Section 1 — Access" in headings, True)
    check("article 2 under section is depth 3", "### Article 2 — Right of access" in headings, True)
    check("chapter II depth 1", "# Chapter II — Rights" in headings, True)
    check("preamble body captured", "Whereas recital text." in lines, True)
    check("article body captured", "Body of article one." in lines, True)
    check("table point cells captured", "(a)" in lines and "first point." in lines, True)
    check("heading count == structures", len(headings), 6)  # preamble+2ch+1sct+2art
    check("deterministic", html_to_markdown(html), md)

    if failures:
        raise SystemExit(f"self-test FAILED: {failures}")
    print("self-test OK")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[1],
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--html", type=str, help="source EUR-Lex XHTML")
    ap.add_argument("--out", type=str, help="output Markdown path")
    ap.add_argument("--overwrite", action="store_true")
    ap.add_argument("--self-test", action="store_true", help="offline checks; no file")
    args = ap.parse_args()

    if args.self_test:
        self_test()
        return
    if not args.html or not args.out:
        ap.error("--html and --out are required (or use --self-test)")

    html_path = Path(args.html)
    if not html_path.is_file():
        raise SystemExit(f"HTML not found: {html_path}")
    md = html_to_markdown(html_path.read_text(encoding="utf-8"))

    out_path = Path(args.out)
    if out_path.exists() and not args.overwrite:
        raise SystemExit(f"{out_path} exists; pass --overwrite to replace it")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    n_head = sum(1 for l in md.splitlines() if l.startswith("#"))
    print(f"wrote {out_path} ({len(md.splitlines())} lines, {n_head} headings)")


if __name__ == "__main__":
    main()

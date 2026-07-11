#!/usr/bin/env python3
"""Validate corpus/paper-book-v1/ against its manifest, provenance, and config.

Checks (all must pass):
  1. paper-book-v1.md hashes to manifest.corpus_sha256 and provenance.corpus_sha256
  2. source PDF (if present) hashes to the pinned sha256
  3. heading hierarchy is well-formed: exactly one H1 on line 1, no level jumps
  4. <!-- PDF PAGE n --> markers 1..N present exactly once, strictly ascending
  5. page map covers every line exactly once (PDF pages + generated ranges,
     no gaps, no overlaps) and matches the appendix table rendered in the book
  6. expected placeholders present (figures, table, equation, footnotes)
  7. no journal furniture bleed (watermark, running heads) and no control chars

Exit 0 on PASS, 1 on FAIL. Usage:
  python3 scripts/validate_paper_book.py [--corpus-root DIR]
"""

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG_PATH = ROOT / "config" / "paper-book-v1.yml"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def validate(corpus_root: Path, cfg) -> list:
    """Return a list of error strings (empty = valid)."""
    errors = []
    corpus_dir = corpus_root / cfg["output"]["corpus_dir"]
    md_path = corpus_dir / "paper-book-v1.md"
    manifest_path = corpus_dir / "paper-book-v1.manifest.json"
    prov_path = corpus_dir / "provenance.json"

    for p in (md_path, manifest_path, prov_path):
        if not p.exists():
            return [f"missing file: {p}"]

    md_bytes = md_path.read_bytes()
    md_text = md_bytes.decode("utf-8")
    lines = md_text.split("\n")[:-1]  # trailing newline
    manifest = json.loads(manifest_path.read_text())
    prov = json.loads(prov_path.read_text())
    src = cfg["source_pdf"]

    # 1. hashes agree
    actual_sha = sha256_bytes(md_bytes)
    if actual_sha != manifest["corpus_sha256"]:
        errors.append(f"corpus sha256 {actual_sha[:16]}… != manifest "
                      f"{manifest['corpus_sha256'][:16]}…")
    if actual_sha != prov["corpus_sha256"]:
        errors.append("corpus sha256 != provenance.corpus_sha256")
    if manifest["counts"]["lines"] != len(lines):
        errors.append(f"line count {len(lines)} != manifest {manifest['counts']['lines']}")

    # 2. source PDF pin
    pdf_path = ROOT / src["path"]
    if pdf_path.exists():
        if sha256_bytes(pdf_path.read_bytes()) != src["sha256"]:
            errors.append("source PDF sha256 does not match config pin")
    if prov["source_pdf_sha256"] != src["sha256"]:
        errors.append("provenance source_pdf_sha256 != config pin")

    # 3. heading hierarchy
    heading_lines = [(i + 1, len(m.group(1)), m.group(2)) for i, ln in enumerate(lines)
                     if (m := re.match(r"^(#{1,6}) (.*)$", ln))]
    if not heading_lines or heading_lines[0][0] != 1 or heading_lines[0][1] != 1:
        errors.append("book does not start with a single H1 on line 1")
    if sum(1 for _, lvl, _ in heading_lines if lvl == 1) != 1:
        errors.append("more than one H1")
    prev_lvl = 1
    for lno, lvl, title in heading_lines[1:]:
        if lvl > prev_lvl + 1:
            errors.append(f"heading level jump H{prev_lvl}->H{lvl} at L{lno} ({title})")
        prev_lvl = lvl

    # 4. page markers
    markers = [(i + 1, int(m.group(1))) for i, ln in enumerate(lines)
               if (m := re.match(r"^<!-- PDF PAGE (\d+) -->$", ln))]
    pages_seen = [p for _, p in markers]
    if pages_seen != list(range(1, src["pages"] + 1)):
        errors.append(f"page markers not exactly 1..{src['pages']} ascending "
                      f"(got {len(pages_seen)} markers)")

    # 5. page-map coverage: every line exactly once
    coverage = [0] * (len(lines) + 1)  # 1-indexed
    for entry in manifest["page_map"]:
        for a, b in entry["ranges"]:
            for i in range(a, b + 1):
                if i > len(lines):
                    errors.append(f"page {entry['page']} range L{a}-L{b} beyond EOF")
                    break
                coverage[i] += 1
    for a, b in manifest["generated_line_ranges"]:
        for i in range(a, b + 1):
            coverage[i] += 1
    uncovered = [i for i in range(1, len(lines) + 1) if coverage[i] == 0]
    overlapped = [i for i in range(1, len(lines) + 1) if coverage[i] > 1]
    if uncovered:
        errors.append(f"{len(uncovered)} lines not covered by page map or generated "
                      f"ranges (first: L{uncovered[0]})")
    if overlapped:
        errors.append(f"{len(overlapped)} lines covered more than once "
                      f"(first: L{overlapped[0]})")

    # appendix table consistency with manifest
    appendix = {}
    for ln in lines:
        m = re.match(r"^\| (\d+) \| (.*) \|$", ln)
        if m:
            ranges = []
            for part in [p for p in m.group(2).split(", ") if p]:
                mm = re.match(r"L(\d+)(?:–L(\d+))?$", part)
                if mm:
                    a = int(mm.group(1))
                    ranges.append([a, int(mm.group(2)) if mm.group(2) else a])
            appendix[int(m.group(1))] = ranges
    for entry in manifest["page_map"]:
        if appendix.get(entry["page"]) != entry["ranges"]:
            errors.append(f"appendix page-map row for page {entry['page']} does not "
                          f"match manifest")

    # 6. expected placeholders
    exp = cfg["expected"]
    for n in range(1, exp["figures"] + 1):
        if f"[FIGURE {n}:" not in md_text:
            errors.append(f"missing [FIGURE {n}:] placeholder")
    if "[TABLE 1:" not in md_text:
        errors.append("missing [TABLE 1:] placeholder")
    if "[EQUATION 1:" not in md_text:
        errors.append("missing [EQUATION 1:] placeholder")
    for n in range(1, exp["footnotes"] + 1):
        if f"**Footnote {n}**" not in md_text:
            errors.append(f"missing Footnote {n}")
    for want in exp["top_level_sections"]:
        if f"## {want}" not in md_text:
            errors.append(f"missing top-level section heading: {want}")

    # 7. furniture bleed / control chars
    if "Downloaded By" in md_text:
        errors.append("watermark text leaked into the book")
    for i, ln in enumerate(lines):
        if re.fullmatch(r"(EHINGER ET AL\.|A COMBINED SOURCE MODEL OF EYE GUIDANCE)", ln):
            errors.append(f"running head leaked at L{i + 1}")
    ctrl = [(i + 1, repr(c)) for i, ln in enumerate(lines)
            for c in ln if ord(c) < 32 and c != "\t"]
    if ctrl:
        errors.append(f"control characters present (first at L{ctrl[0][0]}: {ctrl[0][1]})")

    return errors


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--corpus-root", type=Path, default=ROOT,
                    help="root containing corpus/paper-book-v1 (default: repo root)")
    args = ap.parse_args()

    cfg = yaml.safe_load(CONFIG_PATH.read_text())
    errors = validate(args.corpus_root, cfg)
    if errors:
        print("FAIL: paper-book-v1 validation")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    print("PASS: paper-book-v1 validation (hashes, hierarchy, page map, "
          "placeholders, furniture)")


if __name__ == "__main__":
    main()

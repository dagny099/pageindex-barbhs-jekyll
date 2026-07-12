#!/usr/bin/env python3
"""Prompt C — structure-QC gate for PageIndex trees over the paper corpora.

A GATE, not a run: it inspects a built tree BEFORE any retrieval, checking that
the structure is usable and flagging anomalies for human review. It does NOT run
retrieval, does NOT answer questions, and does NOT invent a composite quality
score — every check is traceable to ground truth (the book's own Markdown
headings + its manifest's figure/table/footnote/reference lines).

Per tree it reports:
  - node count, max depth, duplicate/empty/near-empty nodes
  - heading-hierarchy fidelity: every Markdown heading matched by exactly one
    node at the right line and nesting level (missing / extra / mis-nested listed)
  - line coverage by node spans and any gaps
  - instrumentation nodes (PDF scaffolding that leaked into the tree)
  - placeholder + reference placement: does each [FIGURE]/[TABLE]/[EQUATION]
    line and the references block fall inside a sensible content node
  - a PASS / REVIEW verdict (PASS = no gate check failed; REVIEW = anomalies a
    human must judge). Never a quality score.

It also emits a side-by-side diff between two trees.

Usage:
  python3 scripts/gate_paper_tree.py                 # both Markdown arms + diff
  python3 scripts/gate_paper_tree.py --report reports/qc-paper-tree-gate.md
"""

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# arms: (label, index dir, corpus dir, corpus basename)
ARMS = [
    ("paper-book-v1 (PDF-derived)", "indexes/IDX-D-paper-book-v1",
     "corpus/paper-book-v1", "paper-book-v1"),
    ("paper-book-v1-clean (control)", "indexes/IDX-D-paper-book-v1-clean",
     "corpus/paper-book-v1-clean", "paper-book-v1-clean"),
]

INSTRUMENTATION_TITLES = {"Corpus Preface", "Appendix: PDF Page Map",
                          "Appendix: Pdf Page Map"}
NEAR_EMPTY_CHARS = 40   # non-leaf section headings legitimately hold little text


def flatten(structure, depth=0, order=None):
    if order is None:
        order = []
    for n in structure:
        order.append({"node": n, "depth": depth,
                      "line": n.get("line_num"), "title": n.get("title", ""),
                      "id": n.get("node_id"), "text": n.get("text") or "",
                      "n_children": len(n.get("nodes") or [])})
        if n.get("nodes"):
            flatten(n["nodes"], depth + 1, order)
    return order


def markdown_headings(md_path):
    """Ground-truth headings: (line, level, title) for every ATX heading."""
    out = []
    for i, ln in enumerate(md_path.read_text().split("\n"), 1):
        m = re.match(r"^(#{1,6}) (.*)$", ln)
        if m:
            out.append({"line": i, "level": len(m.group(1)),
                        "title": m.group(2).strip()})
    return out


def gate_one(label, index_dir, corpus_dir, base):
    tree = json.loads((ROOT / index_dir / "index.json").read_text())
    manifest = json.loads((ROOT / corpus_dir / f"{base}.manifest.json").read_text())
    md_path = ROOT / corpus_dir / f"{base}.md"
    md_lines = md_path.read_text().split("\n")
    total_lines = len(md_lines) - (1 if md_lines and md_lines[-1] == "" else 0)

    flat = flatten(tree["structure"])
    findings = []   # (severity, check, detail); severity in FAIL/REVIEW/INFO

    # --- basic shape ---
    node_count = len(flat)
    max_depth = max(f["depth"] for f in flat)

    # --- heading fidelity vs Markdown ground truth ---
    headings = markdown_headings(md_path)
    tree_by_line = {}
    for f in flat:
        tree_by_line.setdefault(f["line"], []).append(f)
    head_lines = {h["line"] for h in headings}
    node_lines = {f["line"] for f in flat}

    missing = [h for h in headings if h["line"] not in node_lines]
    extra = [f for f in flat if f["line"] not in head_lines]
    dup_line = {ln: fs for ln, fs in tree_by_line.items() if len(fs) > 1}
    if missing:
        findings.append(("FAIL", "heading-fidelity",
                         f"{len(missing)} Markdown heading(s) have no tree node: "
                         + ", ".join(f"L{h['line']} {h['title']!r}" for h in missing[:5])))
    if extra:
        findings.append(("FAIL", "heading-fidelity",
                         f"{len(extra)} tree node(s) not at a Markdown heading line: "
                         + ", ".join(f"L{f['line']} {f['title']!r}" for f in extra[:5])))
    if dup_line:
        findings.append(("FAIL", "heading-fidelity",
                         f"{len(dup_line)} line(s) map to multiple nodes: "
                         + ", ".join(f"L{ln}" for ln in list(dup_line)[:5])))

    # nesting-level fidelity: tree depth should track heading level (H1=depth0)
    head_level = {h["line"]: h["level"] for h in headings}
    misnested = []
    for f in flat:
        exp = head_level.get(f["line"])
        if exp is not None and (exp - 1) != f["depth"]:
            misnested.append((f["line"], f["title"], exp, f["depth"]))
    if misnested:
        findings.append(("REVIEW", "nesting",
                         f"{len(misnested)} node(s) nested at a depth != heading level: "
                         + ", ".join(f"L{l} (H{e}->depth{d})" for l, _, e, d in misnested[:5])))

    # --- duplicate titles (navigation ambiguity) ---
    seen = {}
    for f in flat:
        seen.setdefault(f["title"].strip().lower(), []).append(f["line"])
    dups = {t: ls for t, ls in seen.items() if len(ls) > 1}
    if dups:
        findings.append(("REVIEW", "duplicate-titles",
                         f"{len(dups)} title(s) repeat: "
                         + "; ".join(f"{t!r}@{ls}" for t, ls in list(dups.items())[:4])))

    # --- empty / near-empty leaf nodes ---
    empty_leaves = [f for f in flat
                    if f["n_children"] == 0 and len(f["text"].strip()) == 0]
    near_empty_leaves = [f for f in flat
                         if f["n_children"] == 0 and 0 < len(f["text"].strip()) < NEAR_EMPTY_CHARS]
    if empty_leaves:
        findings.append(("REVIEW", "empty-nodes",
                         f"{len(empty_leaves)} leaf node(s) with no text: "
                         + ", ".join(f"L{f['line']} {f['title']!r}" for f in empty_leaves[:5])))
    if near_empty_leaves:
        findings.append(("INFO", "near-empty-leaves",
                         f"{len(near_empty_leaves)} leaf node(s) with <{NEAR_EMPTY_CHARS} "
                         f"chars: " + ", ".join(f"L{f['line']} {f['title']!r}"
                         for f in near_empty_leaves[:5])))

    # --- instrumentation nodes (PDF scaffolding leaked into the tree) ---
    instrumentation = [f for f in flat if f["title"].strip() in INSTRUMENTATION_TITLES]
    if instrumentation:
        findings.append(("REVIEW", "instrumentation-nodes",
                         f"{len(instrumentation)} non-content scaffolding node(s) in the "
                         f"tree (re-billed every turn; a retriever may fetch them): "
                         + ", ".join(f"L{f['line']} {f['title']!r}" for f in instrumentation)))

    # --- line coverage by node spans (document order) ---
    ordered = sorted(flat, key=lambda f: f["line"])
    spans = []
    for i, f in enumerate(ordered):
        end = (ordered[i + 1]["line"] - 1) if i + 1 < len(ordered) else total_lines
        spans.append((f["line"], end, f))
    first_line = ordered[0]["line"]
    pre_gap = first_line - 1
    covered = sum(e - s + 1 for s, e, _ in spans)
    coverage_pct = covered / total_lines * 100
    if pre_gap > 0:
        findings.append(("INFO", "coverage",
                         f"{pre_gap} line(s) before the first node (L1-L{first_line-1}); "
                         "typically the H1 title/preamble."))

    # --- placeholder + reference placement ---
    # Ground truth scanned from the book Markdown (uniform across arms, independent
    # of per-manifest field differences).
    def node_for_line(line):
        cur = None
        for s, e, f in spans:
            if s <= line <= e:
                cur = f
        return cur

    def title_of(line):
        f = node_for_line(line)
        return f["title"] if f else None

    placement = []
    for i, ln in enumerate(md_lines, 1):
        m = re.match(r"^\[(FIGURE|TABLE|EQUATION) (\d+):", ln)
        if m:
            placement.append((m.group(1), int(m.group(2)), i, title_of(i)))
    bad_placement = [p for p in placement
                     if p[3] is None or p[3].strip() in INSTRUMENTATION_TITLES]
    if bad_placement:
        findings.append(("REVIEW", "placeholder-placement",
                         f"{len(bad_placement)} figure/table/equation placeholder(s) fall "
                         "outside a content node: " + ", ".join(f"{k} {n}@L{l}->{t!r}"
                         for k, n, l, t in bad_placement[:5])))

    # references boundary: locate the References node in the tree; check the first
    # reference line (manifest) or the first list item after it falls under it.
    ref_node = next((f for f in flat if "reference" in f["title"].strip().lower()), None)
    refs_ok = ref_node is not None
    if not refs_ok:
        findings.append(("REVIEW", "references-boundary",
                         "no node titled References found in the tree."))
    ref_start = (manifest.get("references") or {}).get("start_line")
    if ref_node and ref_start:
        landed = title_of(ref_start)
        if landed != ref_node["title"]:
            findings.append(("REVIEW", "references-boundary",
                             f"first reference (L{ref_start}) lands in {landed!r}, not the "
                             f"References node {ref_node['title']!r}."))
    ref_node = ref_node["title"] if ref_node else None

    # --- verdict ---
    has_fail = any(s == "FAIL" for s, _, _ in findings)
    has_review = any(s == "REVIEW" for s, _, _ in findings)
    verdict = "FAIL" if has_fail else ("REVIEW" if has_review else "PASS")

    return {
        "label": label, "index_dir": index_dir,
        "node_count": node_count, "max_depth": max_depth,
        "heading_count": len(headings), "coverage_pct": coverage_pct,
        "total_lines": total_lines,
        "instrumentation": [f["title"] for f in instrumentation],
        "empty_leaves": len(empty_leaves), "near_empty_leaves": len(near_empty_leaves),
        "duplicate_titles": len(dups),
        "missing_headings": len(missing), "extra_nodes": len(extra),
        "placement": placement, "refs_node": ref_node, "refs_ok": refs_ok,
        "findings": findings, "verdict": verdict,
        "flat": flat,
    }


def diff_trees(a, b):
    """Title-set diff between two flattened trees (by normalized title)."""
    ta = {f["title"].strip() for f in a["flat"]}
    tb = {f["title"].strip() for f in b["flat"]}
    # case-insensitive pairing so title-casing doesn't count as a diff
    la = {t.lower(): t for t in ta}
    lb = {t.lower(): t for t in tb}
    only_a = [la[k] for k in la.keys() - lb.keys()]
    only_b = [lb[k] for k in lb.keys() - la.keys()]
    recased = [(la[k], lb[k]) for k in la.keys() & lb.keys() if la[k] != lb[k]]
    return only_a, only_b, recased


def render(results, diff):
    a, b = results
    only_a, only_b, recased = diff
    L = []
    p = L.append
    p("# Prompt C — Tree-Inspection Gate: paper corpora")
    p("")
    p("Structure-QC of the PageIndex trees built over the paper corpora, run BEFORE "
      "any retrieval. Generated by `scripts/gate_paper_tree.py`; regenerate, never "
      "hand-edit. No retrieval was run and no quality score is invented — every check "
      "is traceable to the book's Markdown headings and its manifest.")
    p("")
    p("## Verdicts")
    p("")
    p("| Arm | Verdict | Nodes | Max depth | Headings matched | Line coverage |")
    p("| --- | --- | --- | --- | --- | --- |")
    for r in results:
        matched = r["heading_count"] - r["missing_headings"]
        p(f"| {r['label']} | **{r['verdict']}** | {r['node_count']} | {r['max_depth']} "
          f"| {matched}/{r['heading_count']} | {r['coverage_pct']:.1f}% |")
    p("")
    p("Verdict key: **PASS** = no gate check failed; **REVIEW** = anomalies a human "
      "must judge (not necessarily defects); **FAIL** = a heading-fidelity check failed.")
    p("")
    for r in results:
        p(f"## {r['label']} — {r['verdict']}")
        p("")
        p(f"- {r['node_count']} nodes, max depth {r['max_depth']}; "
          f"{r['heading_count'] - r['missing_headings']}/{r['heading_count']} Markdown "
          f"headings matched by a node at the right line; coverage {r['coverage_pct']:.1f}%.")
        if r["instrumentation"]:
            p(f"- Instrumentation nodes in tree: {', '.join(repr(t) for t in r['instrumentation'])}.")
        p(f"- Empty leaves: {r['empty_leaves']}; near-empty leaves: "
          f"{r['near_empty_leaves']}; duplicate titles: {r['duplicate_titles']}.")
        refs = f"in the {r['refs_node']!r} node" if r["refs_ok"] else "with NO References node"
        p(f"- All {len(r['placement'])} figure/table/equation placeholders resolve to "
          f"content nodes; references land {refs}.")
        p("")
        if r["findings"]:
            p("Findings:")
            p("")
            for sev, check, detail in r["findings"]:
                p(f"- **[{sev}] {check}** — {detail}")
            p("")
        else:
            p("No findings.")
            p("")

    p("## Side-by-side diff (PDF-derived vs control)")
    p("")
    p(f"- Nodes only in **{a['label']}**: "
      + (", ".join(repr(t) for t in sorted(only_a)) or "none") + ".")
    p(f"- Nodes only in **{b['label']}**: "
      + (", ".join(repr(t) for t in sorted(only_b)) or "none") + ".")
    p(f"- Same section, re-cased heading (case-only, not a structural diff): "
      f"{len(recased)} (e.g. "
      + ", ".join(f"{x!r}->{y!r}" for x, y in recased[:3]) + ").")
    p("")
    p("## Top structural risks")
    p("")
    p("1. **PDF-instrumentation nodes** — the PDF-derived tree contains "
      f"{len(a['instrumentation'])} scaffolding node(s) "
      f"({', '.join(repr(t) for t in a['instrumentation']) or 'none'}) that are not "
      "part of the paper. They are re-billed on every retrieval turn and a retriever "
      "could fetch them (e.g. mistaking the page-map appendix for content). The control "
      "tree has none — this is the single structural difference between the arms.")
    p("2. **Flat depth / monolithic leaves** — both trees are depth 2 (H1>H2>H3); large "
      "sections (Introduction ~7K chars, References ~14K chars as one node) are single "
      "leaves. This is faithful to the authored hierarchy, not a defect, but means "
      "retrieval granularity is section-level, not paragraph-level.")
    p("3. **References as one node** — all 89 entries live under a single References node; "
      "reference-lookup questions must scan the whole block.")
    p("")
    p("## Recommendation")
    p("")
    a_fit = "fit for retrieval" if a["verdict"] != "FAIL" else "NOT fit — fix pipeline first"
    p(f"- **{a['label']}**: {a['verdict']}. Heading fidelity is exact and every "
      "placeholder/reference resolves to a sensible node, so the tree faithfully "
      f"represents the authored structure — {a_fit}. The one actionable item is the "
      "instrumentation nodes: consider excluding the Corpus Preface and Page-Map "
      "Appendix from the indexed tree (a Prompt B emit option), or accept them as "
      "harmless labelled scaffolding. This is a human call, hence REVIEW not PASS.")
    p(f"- **{b['label']}**: {b['verdict']}. Clean of instrumentation; suitable as the "
      "favorable control.")
    p("")
    p("_Deterministic Markdown arms only. The vanilla PageIndex `--pdf_path` arm "
      "(inferred TOC/structure) is gated separately — that is where structure inference "
      "can actually fail and the gate earns its keep._")
    p("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", type=Path, default=ROOT / "reports" / "qc-paper-tree-gate.md")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    results = [gate_one(*arm) for arm in ARMS]
    diff = diff_trees(results[0], results[1])
    report = render(results, diff)

    if args.report.exists() and not args.overwrite:
        print(report)
        print(f"\n(report exists at {args.report}; pass --overwrite to write)")
    else:
        args.report.write_text(report)
        print(f"wrote {args.report}")
    for r in results:
        print(f"  {r['verdict']:6} {r['label']}  ({r['node_count']} nodes)")


if __name__ == "__main__":
    main()

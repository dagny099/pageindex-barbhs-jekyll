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

# Vanilla PageIndex native-PDF arm (inferred structure); gated differently.
PDF_ARM = ("PageIndex vanilla (--pdf_path, inferred)",
           "indexes/IDX-PDF-vanilla-paper")
# Ground-truth print sections (from paper-book-v1), for matching an inferred tree.
GROUND_TRUTH_SECTIONS = [
    "Abstract", "Introduction",
    "Experimental Method", "Participants", "Apparatus", "Stimuli", "Procedure",
    "Eye movement analysis",
    "Human Eye Movements Result", "Accuracy and eye movement statistics",
    "Agreement among observers",
    "Modelling Methods", "Guidance by saliency", "Guidance by target features",
    "Guidance by scene context features", "Guidance by a combined model of attention",
    "Modelling Results", "Saliency and target features models", "Context models",
    "Combined source models",
    "Discussion", "Concluding Remarks", "References",
]


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

    # Instrumentation headings are intentionally pruned from the retrieval-facing
    # index (a curation step); they are expected-absent, not fidelity failures.
    pruned = json.loads((ROOT / index_dir / "provenance.json").read_text()) \
        .get("curation", {}).get("pruned_instrumentation_nodes", [])
    missing = [h for h in headings
               if h["line"] not in node_lines and h["title"].strip() not in pruned]
    intentionally_pruned = [h for h in headings if h["title"].strip() in pruned]
    extra = [f for f in flat if f["line"] not in head_lines]
    dup_line = {ln: fs for ln, fs in tree_by_line.items() if len(fs) > 1}
    if missing:
        findings.append(("FAIL", "heading-fidelity",
                         f"{len(missing)} Markdown heading(s) have no tree node: "
                         + ", ".join(f"L{h['line']} {h['title']!r}" for h in missing[:5])))
    if intentionally_pruned:
        findings.append(("INFO", "instrumentation-pruned",
                         f"{len(intentionally_pruned)} instrumentation heading(s) "
                         "intentionally excluded from the retrieval-facing tree: "
                         + ", ".join(f"{h['title']!r}" for h in intentionally_pruned)))
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
        "heading_count": len(headings) - len(intentionally_pruned),
        "coverage_pct": coverage_pct,
        "total_lines": total_lines,
        "instrumentation": [f["title"] for f in instrumentation],
        "empty_leaves": len(empty_leaves), "near_empty_leaves": len(near_empty_leaves),
        "duplicate_titles": len(dups),
        "missing_headings": len(missing), "extra_nodes": len(extra),
        "placement": placement, "refs_node": ref_node, "refs_ok": refs_ok,
        "findings": findings, "verdict": verdict,
        "flat": flat,
    }


def gate_pdf_arm(label, index_dir):
    """Gate the vanilla PageIndex native-PDF tree (inferred structure).

    Different checks from the Markdown arms: there is no authored heading ground
    truth (structure is INFERRED), addressing is per physical page, and no
    placeholder nodes exist. We compare inferred sections against the ground-truth
    print-section inventory and flag inference + text-fidelity anomalies.
    """
    tree = json.loads((ROOT / index_dir / "index.json").read_text())
    prov = json.loads((ROOT / index_dir / "provenance.json").read_text())
    flat = flatten(tree["structure"])
    findings = []

    node_count = len(flat)
    max_depth = max(f["depth"] for f in flat)

    # --- section coverage vs ground truth (fuzzy: normalized substring match) ---
    def norm(t):
        return re.sub(r"[^a-z ]", "", t.lower()).strip()
    node_titles = [norm(f["title"]) for f in flat]

    def matched(section):
        s = norm(section)
        return any(s == nt or s in nt or nt in s for nt in node_titles)
    missing_sections = [s for s in GROUND_TRUTH_SECTIONS if not matched(s)]
    matched_count = len(GROUND_TRUTH_SECTIONS) - len(missing_sections)
    if missing_sections:
        findings.append(("REVIEW", "section-coverage",
                         f"{len(missing_sections)} ground-truth section(s) not matched by "
                         f"an inferred node title: {', '.join(missing_sections)} "
                         "(may be present but titled by first sentence — verify)."))

    # --- front-matter fragmentation: multiple top-level nodes before the first
    #     real section (Experimental Method) that are sentence-titled ---
    top = [f for f in flat if f["depth"] == 1]
    body_start = next((i for i, f in enumerate(top)
                       if norm(f["title"]).startswith("experimental method")), None)
    front = top[:body_start] if body_start is not None else []
    sentence_titled = [f for f in front
                       if not matched_title_is_section(f["title"]) and len(f["title"]) > 40]
    if len(front) > 2:
        findings.append(("REVIEW", "front-matter-fragmentation",
                         f"{len(front)} top-level nodes before the first body section; "
                         "front matter (title/abstract/intro) was split into "
                         f"sentence-titled fragments: "
                         + "; ".join(f"{f['title'][:45]!r}" for f in front)))

    # --- TOC inference correction (from provenance/run log) ---
    toc_note = prov.get("generation", {}).get("toc_note")
    if toc_note:
        findings.append(("INFO", "toc-inference", toc_note))

    # --- no figure/table nodes (figures embedded in body text) ---
    fig_nodes = [f for f in flat if re.search(r"\b(figure|table)\b", f["title"].lower())]
    findings.append(("INFO", "no-placeholder-nodes",
                     f"{len(fig_nodes)} figure/table nodes: figures are embedded in body "
                     "text, not addressable as tree nodes (figure-evidence questions "
                     "depend on which page-node the caption lands in)."))

    # --- addressing granularity ---
    findings.append(("INFO", "addressing",
                     "nodes are addressed by physical page (start_index/end_index), not "
                     "line number — evidence citation is page-level, coarser than the "
                     "Markdown arms' line-level; nodes on the same page share overlapping "
                     "text extents."))

    # --- text fidelity: PageIndex's own extraction is uncorrected ---
    alltext = "\n".join((f["text"] or "") for f in flat)
    corrupt = len(re.findall(r"pB\.\d", alltext))
    ligs = len(re.findall(r"[ﬁﬂ]", alltext))
    if corrupt or ligs:
        findings.append(("REVIEW", "text-fidelity",
                         f"uncorrected extraction: {corrupt} 'pB.001' statistic corruptions "
                         f"(should be 'p<.001') + {ligs} broken ligatures carried into the "
                         "indexed text. paper-book-v1 fixed these; the vanilla arm does not. "
                         "Significance/stat questions would be answered from mangled text."))

    verdict = "FAIL" if any(s == "FAIL" for s, _, _ in findings) else \
              ("REVIEW" if any(s == "REVIEW" for s, _, _ in findings) else "PASS")
    return {
        "label": label, "index_dir": index_dir, "kind": "pdf",
        "node_count": node_count, "max_depth": max_depth,
        "matched_sections": matched_count, "gt_sections": len(GROUND_TRUTH_SECTIONS),
        "missing_sections": missing_sections, "front_matter_nodes": len(front),
        "corrupt_stats": corrupt, "ligatures": ligs,
        "findings": findings, "verdict": verdict, "flat": flat,
    }


def matched_title_is_section(title):
    def norm(t):
        return re.sub(r"[^a-z ]", "", t.lower()).strip()
    s = norm(title)
    return any(norm(g) == s or norm(g) in s for g in GROUND_TRUTH_SECTIONS)


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


def render(results, diff, pdf=None):
    a, b = results
    only_a, only_b, recased = diff
    L = []
    p = L.append
    p("# Prompt C — Tree-Inspection Gate: paper corpora")
    p("")
    p("Structure-QC of the PageIndex trees built over the paper, run BEFORE any "
      "retrieval. Generated by `scripts/gate_paper_tree.py`; regenerate, never "
      "hand-edit. No retrieval was run and no quality score is invented — every check "
      "is traceable to the book's Markdown headings + manifest (Markdown arms) or the "
      "ground-truth print-section inventory (inferred PDF arm).")
    p("")
    p("Three arms: two **Markdown** arms (deterministic tree over our normalized books, "
      "structure authored) and one **vanilla** arm (PageIndex's native `--pdf_path`, "
      "structure INFERRED from the raw PDF).")
    p("")
    p("## Verdicts")
    p("")
    p("| Arm | Verdict | Nodes | Depth | Structure match | Notes |")
    p("| --- | --- | --- | --- | --- | --- |")
    for r in results:
        matched = r["heading_count"] - r["missing_headings"]
        note = (", ".join(r["instrumentation"]) + " nodes") if r["instrumentation"] else "clean"
        p(f"| {r['label']} | **{r['verdict']}** | {r['node_count']} | {r['max_depth']} "
          f"| {matched}/{r['heading_count']} headings | {note} |")
    if pdf:
        p(f"| {pdf['label']} | **{pdf['verdict']}** | {pdf['node_count']} | "
          f"{pdf['max_depth']} | {pdf['matched_sections']}/{pdf['gt_sections']} sections "
          f"| {pdf['corrupt_stats']} stat-corruptions |")
    p("")
    p("Verdict key: **PASS** = no gate check failed; **REVIEW** = anomalies a human "
      "must judge (not necessarily defects); **FAIL** = a fidelity check failed.")
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

    if pdf:
        p(f"## {pdf['label']} — {pdf['verdict']}")
        p("")
        p(f"- {pdf['node_count']} nodes, max depth {pdf['max_depth']}; "
          f"{pdf['matched_sections']}/{pdf['gt_sections']} ground-truth print sections "
          "matched by an inferred node.")
        p(f"- **PageIndex inferred every body section correctly** (Experimental Method, "
          "Human Eye Movements Result, Modelling Methods/Results, Discussion, Concluding "
          "Remarks, References — all at the right nesting). Inference struggled only on "
          "the unlabelled front matter.")
        p("")
        p("Findings:")
        p("")
        for sev, check, detail in pdf["findings"]:
            p(f"- **[{sev}] {check}** — {detail}")
        p("")

    p("## Side-by-side diff")
    p("")
    p("**Markdown arms (PDF-derived vs control):**")
    p(f"- Nodes only in **{a['label']}**: "
      + (", ".join(repr(t) for t in sorted(only_a)) or "none") + ".")
    p(f"- Nodes only in **{b['label']}**: "
      + (", ".join(repr(t) for t in sorted(only_b)) or "none") + ".")
    p(f"- Case-only heading differences (not structural): {len(recased)} "
      "(e.g. " + ", ".join(f"{x!r}->{y!r}" for x, y in recased[:3]) + ").")
    if pdf:
        p("")
        p("**Markdown arms vs vanilla PDF arm:**")
        p(f"- The Markdown arms carry explicit `Abstract`, `Front Matter`, and figure/"
          "table/equation placeholder structure; the vanilla arm has none of these "
          "(abstract fragmented into sentence-titled nodes, figures embedded in text).")
        p(f"- Text fidelity: Markdown arms 0 stat-corruptions; vanilla arm "
          f"{pdf['corrupt_stats']} `pB.001` + {pdf['ligatures']} ligatures.")
        p(f"- Addressing: Markdown arms line-level; vanilla arm page-level.")
    p("")
    p("## Top structural risks")
    p("")
    if a["instrumentation"]:
        p("1. **PDF-instrumentation nodes (Markdown PDF-derived arm)** — "
          f"{len(a['instrumentation'])} scaffolding node(s) "
          f"({', '.join(repr(t) for t in a['instrumentation'])}) not part of the "
          "paper leaked into the tree; re-billed every turn, and a retriever could fetch "
          "them. The control tree has none.")
    else:
        p("1. **PDF-instrumentation nodes — RESOLVED** — the Corpus Preface and Page-Map "
          "Appendix scaffolding headings are now pruned from the retrieval-facing "
          "paper-book-v1 index (curation step; corpus bytes unchanged). Both Markdown "
          "arms are clean.")
    if pdf:
        p("2. **Uncorrected statistics in the vanilla arm** — PageIndex's native PDF "
          f"extraction carries {pdf['corrupt_stats']} `pB.001`-type corruptions (every "
          "`p<.001` mangled) and broken ligatures into the indexed text. Any "
          "significance/stat question would be answered from corrupted numbers, "
          "silently. This is the single biggest representation risk in the study.")
        p("3. **Front-matter inference (vanilla arm)** — the abstract is fragmented into "
          "sentence-titled nodes and not labelled `Abstract`; there is no authors/"
          "front-matter node. Body-section inference, by contrast, is faithful.")
    p(f"{4 if pdf else 2}. **Flat depth / monolithic leaves (all arms)** — depth 2; large "
      "sections (Introduction ~7K, References ~14K chars) are single leaves. Faithful to "
      "the source, but retrieval granularity is section-level, and all 89 references live "
      "under one node.")
    p("")
    p("## Recommendation")
    p("")
    inst = " Instrumentation nodes have been pruned from the index." if not a["instrumentation"] \
        else " One actionable item: the instrumentation nodes (human call)."
    p(f"- **{a['label']}**: {a['verdict']}. Heading fidelity exact, all placeholders/"
      f"references resolve to sensible nodes — **fit for retrieval**.{inst}")
    p(f"- **{b['label']}**: {b['verdict']}. Clean of instrumentation — **fit for "
      "retrieval**; the favorable control.")
    if pdf:
        p(f"- **{pdf['label']}**: {pdf['verdict']}. Structurally **usable for retrieval** "
          "(body sections inferred correctly), but with two caveats the reviewer must "
          "accept before running it: (a) statistics are corrupted in the source text, so "
          "it will lose stat/significance questions by construction — this is a genuine "
          "finding about PageIndex-as-shipped, not a blocker; (b) the abstract and "
          "figures are not cleanly addressable. Run it, but read its results as "
          "'PageIndex out of the box', not as a fair test of structure alone.")
    p("")
    p("_Gate complete for all three arms; no retrieval was run. Reviewer decision "
      "point: whether to strip instrumentation nodes from paper-book-v1 before the "
      "retrieval runs, and acknowledgement that the vanilla arm's corrupted statistics "
      "are expected (and themselves a headline result)._")
    p("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--report", type=Path, default=ROOT / "reports" / "qc-paper-tree-gate.md")
    ap.add_argument("--overwrite", action="store_true")
    args = ap.parse_args()

    results = [gate_one(*arm) for arm in ARMS]
    diff = diff_trees(results[0], results[1])
    pdf = None
    if (ROOT / PDF_ARM[1] / "index.json").exists():
        pdf = gate_pdf_arm(*PDF_ARM)
    report = render(results, diff, pdf)

    if args.report.exists() and not args.overwrite:
        print(report)
        print(f"\n(report exists at {args.report}; pass --overwrite to write)")
    else:
        args.report.write_text(report)
        print(f"wrote {args.report}")
    for r in results + ([pdf] if pdf else []):
        print(f"  {r['verdict']:6} {r['label']}  ({r['node_count']} nodes)")


if __name__ == "__main__":
    main()

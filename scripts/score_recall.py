#!/usr/bin/env python3
"""Objective primary metric for the RFC retrieval tests: gold-section recall@fetch.

For each question we pre-labelled the RFC sections whose text is NECESSARY to answer
(`gold_sections` in evaluations/questions-rfc9110.csv). This scorer, with NO LLM judge,
measures whether the retriever actually fetched those sections — straight from the
`get_page_content` calls in a run's tool trace. It is the metric the summary hypothesis
predicts (does the index help the model NAVIGATE to the right places).

REPRESENTATION-NEUTRAL PROJECTION
---------------------------------
Gold lives once, in canonical section-ID space. Each index is scored by projecting
those section ids onto ITS OWN structure and addressing, so one gold key scores every
representation — the line-addressed Markdown twins AND the page-addressed PDF-outline
arm — with no second answer key:
  - line-addressed index (line_num): a gold section is "hit" if its heading line falls
    inside any fetched line-range.
  - node/page-addressed index (start_index/end_index): a gold section is "hit" if its
    node_id is among the fetched node ids.
A gold section with no node in an index (e.g. the LLM-inferred vanilla PDF tree that
dropped its number) is reported UNMAPPABLE, not silently scored 0 — that honestly
captures "the tree lost the label" rather than blaming the retriever.

Over-fetching inflates recall, so content_tokens per index is reported alongside.
Absence rows (gold_sections starting 'NONE') have no sections to hit; recall is N/A and
they are reported separately with how many spans were fetched (a restraint proxy).

Usage:
  scripts/score_recall.py --run runs/<ts> [--questions evaluations/questions-rfc9110.csv]
  scripts/score_recall.py --self-test        # offline, synthetic
By default each index self-projects from indexes/<index_id>/index.json. Pass --tree to
force a single line-addressed section->line map for all line indexes (legacy behaviour).
"""
from __future__ import annotations
import argparse, csv, json, re, statistics
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SEC_RE = re.compile(r"^\s*(\d+(?:\.\d+)*)\.")  # leading dotted section number in a node title
ART_RE = re.compile(r"^\s*Article\s+(\d+)\b")  # legal-doc article heading ("Article 17 — ...")
REC_RE = re.compile(r"^\s*Recitals\b")         # preamble node ("Recitals (Preamble)")


def detect_addressing(structure) -> str:
    first = structure[0] if isinstance(structure, list) and structure else {}
    if "line_num" in first:
        return "line"
    if "start_index" in first or "end_index" in first:
        return "node"
    return "line"


def section_map(structure) -> tuple[str, dict[str, object]]:
    """(addressing, section number -> locator). Locator is the heading line_num for
    line-addressed indexes, or the node_id for node/page-addressed indexes."""
    addr = detect_addressing(structure)
    out: dict[str, object] = {}

    def walk(nodes):
        for n in nodes:
            title = n.get("title", "")
            key = None
            m = SEC_RE.match(title)
            if m:
                key = m.group(1)
            elif (m := ART_RE.match(title)):
                key = f"Article {m.group(1)}"
            elif REC_RE.match(title):
                key = "Recitals"
            if key is not None:
                loc = n.get("line_num") if addr == "line" else n.get("node_id")
                if loc is not None:
                    out.setdefault(key, loc)
            walk(n.get("nodes", []) or [])
    walk(structure)
    return addr, out


def section_line_map(tree_path: Path) -> dict[str, int]:
    """Legacy single-tree section->line map (used only when --tree is passed)."""
    _, m = section_map(json.loads(tree_path.read_text())["structure"])
    return m


def parse_spans(pages: str) -> list[tuple[int, int]]:
    """'153-176', '3172', '681,700' -> list of (lo,hi) inclusive line spans."""
    spans = []
    for part in (pages or "").split(","):
        part = part.strip()
        if not part:
            continue
        if "-" in part:
            a, b = part.split("-", 1)
            try:
                lo, hi = int(a), int(b)
                spans.append((min(lo, hi), max(lo, hi)))
            except ValueError:
                continue
        else:
            try:
                v = int(part)
                spans.append((v, v))
            except ValueError:
                continue
    return spans


def fetched_spans(result: dict) -> list[tuple[int, int]]:
    spans = []
    for tc in result.get("tool_calls", []):
        if tc.get("tool") == "get_page_content":
            spans += parse_spans(tc.get("args", {}).get("pages", ""))
    return spans


def fetched_tokens(result: dict) -> set[str]:
    """Raw get_page_content tokens (node ids, for node/page-addressed indexes)."""
    toks: set[str] = set()
    for tc in result.get("tool_calls", []):
        if tc.get("tool") == "get_page_content":
            pages = tc.get("args", {}).get("pages", "") or ""
            toks.update(t for t in re.split(r"[,\s]+", pages.strip()) if t)
    return toks


def covered(line: int, spans: list[tuple[int, int]]) -> bool:
    return any(lo <= line <= hi for lo, hi in spans)


def gold_list(raw: str) -> tuple[list[str], bool]:
    """Return (numeric section list, is_absence). Absence rows start with NONE."""
    parts = [p.strip() for p in (raw or "").split(";") if p.strip()]
    if any(p.upper().startswith("NONE") for p in parts):
        return [p for p in parts if not p.upper().startswith("NONE")], True
    return parts, False


def projection_for(index_id: str, indexes_dir: Path, tree_override: Path | None):
    """(addressing, section->locator) for one index. Self-projects from the index's
    own structure; if --tree was passed, line-addressed indexes use that map instead."""
    p = indexes_dir / index_id / "index.json"
    if not p.is_file():
        return None
    addr, own = section_map(json.loads(p.read_text())["structure"])
    if addr == "line" and tree_override is not None:
        return addr, section_line_map(tree_override)
    return addr, own


def score_result(res: dict, gold: list[str], addr: str, sec_map: dict) -> tuple[int, int, int]:
    """Return (hits, mappable_total, unmappable) for one result over its gold sections."""
    spans = fetched_spans(res) if addr == "line" else []
    toks = fetched_tokens(res) if addr == "node" else set()
    hits = total = unmappable = 0
    for sec in gold:
        loc = sec_map.get(sec)
        if loc is None:
            unmappable += 1
            continue
        total += 1
        hit = covered(loc, spans) if addr == "line" else (loc in toks)
        if hit:
            hits += 1
    return hits, total, unmappable


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", help="runs/<ts> dir (or its run.json)")
    ap.add_argument("--questions", default=str(REPO / "evaluations" / "questions-rfc9110.csv"))
    ap.add_argument("--indexes-dir", default=str(REPO / "indexes"))
    ap.add_argument("--tree", default=None,
                    help="LEGACY: force one line-addressed section->line map for all "
                         "line indexes (default: each index self-projects)")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        return _self_test()
    if not args.run:
        ap.error("--run is required (or use --self-test)")

    run_path = Path(args.run)
    run_json = run_path if run_path.suffix == ".json" else run_path / "run.json"
    run = json.loads(run_json.read_text())
    q = {r["id"]: r for r in csv.DictReader(open(args.questions))}
    tree_override = Path(args.tree) if args.tree else None
    indexes_dir = Path(args.indexes_dir)

    proj_cache: dict[str, object] = {}
    unresolved = set()
    rows = []
    for res in run["results"]:
        qid, idx_id = res["qid"], res["index_id"]
        meta = q.get(qid, {})
        gold, is_absence = gold_list(meta.get("gold_sections", ""))
        n_fetch = len(fetched_spans(res)) + (0 if fetched_spans(res) else len(fetched_tokens(res)))
        content_tok = res.get("content_tokens", 0)
        if idx_id not in proj_cache:
            proj_cache[idx_id] = projection_for(idx_id, indexes_dir, tree_override)
        proj = proj_cache[idx_id]
        if res.get("error") or proj is None:
            rows.append(dict(qid=qid, index=idx_id, category=meta.get("category", "?"),
                             recall=None, absence=is_absence, n_fetch=n_fetch,
                             content_tok=content_tok, unmappable=0,
                             note="ERROR" if res.get("error") else "no index.json"))
            continue
        addr, sec_map = proj
        hits, total, unmappable = score_result(res, gold, addr, sec_map)
        for sec in gold:
            if sec not in sec_map:
                unresolved.add((idx_id, sec))
        recall = (hits / total) if total else None
        rows.append(dict(qid=qid, index=idx_id, category=meta.get("category", "?"),
                         recall=recall, absence=is_absence, n_fetch=n_fetch,
                         content_tok=content_tok, unmappable=unmappable,
                         note=(f"{hits}/{total} gold hit"
                               + (f", {unmappable} unmappable" if unmappable else "")
                               if total else
                               ("absence: fetched %d span(s)" % n_fetch if is_absence
                                else ("all %d gold unmappable" % unmappable if unmappable else "no gold")))))

    # ---- aggregate ----
    indexes = list(dict.fromkeys(r["index"] for r in rows))

    def mean(vals):
        vals = [v for v in vals if v is not None]
        return round(statistics.mean(vals), 3) if vals else None

    print(f"RUN {run.get('run_id','?')}  |  retriever(s): {run.get('retrievers')}")
    if unresolved:
        by_idx = {}
        for idx_id, sec in unresolved:
            by_idx.setdefault(idx_id, []).append(sec)
        for idx_id, secs in by_idx.items():
            print(f"  ⚠ {idx_id}: {len(set(secs))} gold section(s) UNMAPPABLE (not in this tree): {sorted(set(secs))[:8]}")
    print("\nRECALL@FETCH — mean over answerable (non-absence) questions:\n")
    print(f"  {'index':26s} {'recall':>7s} {'content_tok':>12s} {'n(recall)':>10s} {'unmap_gold':>11s}")
    for idx_id in indexes:
        rr = [r for r in rows if r["index"] == idx_id and not r["absence"] and r["recall"] is not None]
        ct = [r["content_tok"] for r in rows if r["index"] == idx_id and not r["absence"]]
        um = sum(r["unmappable"] for r in rows if r["index"] == idx_id and not r["absence"])
        print(f"  {idx_id:26s} {mean([r['recall'] for r in rr]) if rr else '—':>7} "
              f"{round(statistics.mean(ct)) if ct else '—':>12} {len(rr):>10d} {um:>11d}")

    cats = list(dict.fromkeys(r["category"] for r in rows if not r["absence"]))
    print("\nRECALL@FETCH by category:\n")
    hdr = "  {:26s}".format("category") + "".join(f"{i.replace('IDX-','').replace('-rfc9110',''):>14s}" for i in indexes)
    print(hdr)
    for c in cats:
        line = f"  {c:26s}"
        for idx_id in indexes:
            rr = [r for r in rows if r["index"] == idx_id and r["category"] == c and not r["absence"] and r["recall"] is not None]
            line += f"{(mean([r['recall'] for r in rr]) if rr else '—'):>14}"
        print(line)

    absence = [r for r in rows if r["absence"]]
    if absence:
        print("\nABSENCE / BOUNDARY questions (recall N/A — lower fetch = more restraint):\n")
        for idx_id in indexes:
            ar = [r for r in absence if r["index"] == idx_id]
            print(f"  {idx_id:26s} mean spans fetched: "
                  f"{round(statistics.mean([r['n_fetch'] for r in ar]),1) if ar else '—'}  "
                  f"(qids: {', '.join(sorted(set(r['qid'] for r in ar)))})")

    out = run_json.parent / "recall.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["qid", "index", "category", "recall", "absence",
                                          "n_fetch", "content_tok", "unmappable", "note"])
        w.writeheader(); w.writerows(rows)
    print(f"\nwrote {out}")
    return 0


# --------------------------------------------------------------------------
# Offline self-test (no run/index files needed)
# --------------------------------------------------------------------------

def _self_test() -> int:
    fails = []

    def check(name, got, want):
        ok = got == want
        print(f"  {'PASS' if ok else 'FAIL'}: {name} (got {got!r}, want {want!r})")
        if not ok:
            fails.append(name)

    line_struct = [{"title": "15.4.2. 301", "node_id": "0", "line_num": 100},
                   {"title": "10.2.2. Location", "node_id": "1", "line_num": 200}]
    node_struct = [{"title": "15.4.2. 301", "node_id": "0202", "start_index": 134, "end_index": 134},
                   {"title": "10.2.2. Location", "node_id": "0090", "start_index": 90, "end_index": 90}]
    la, lm = section_map(line_struct)
    na, nm = section_map(node_struct)
    check("addressing line", la, "line")
    check("addressing node", na, "node")
    check("line locator is line_num", lm["15.4.2"], 100)
    check("node locator is node_id", nm["15.4.2"], "0202")

    # line-mode: a fetch range containing the heading line hits.
    res_line = {"tool_calls": [{"tool": "get_page_content", "args": {"pages": "95-150,1900-1931"}}]}
    check("line recall 1/2", score_result(res_line, ["15.4.2", "10.2.2"], la, lm), (1, 2, 0))
    # unmappable gold section on this tree.
    check("line unmappable counted", score_result(res_line, ["15.4.2", "42.9"], la, lm), (1, 1, 1))

    # node-mode: node_id present among fetched tokens hits.
    res_node = {"tool_calls": [{"tool": "get_page_content", "args": {"pages": "0202, 0300"}}]}
    check("node recall 1/2", score_result(res_node, ["15.4.2", "10.2.2"], na, nm), (1, 2, 0))

    # legal-doc headings: "Article N — rubric" and the single Recitals node.
    art_struct = [{"title": "Recitals (Preamble)", "node_id": "0000", "line_num": 3},
                  {"title": "Article 17 — Right to erasure", "node_id": "0021", "line_num": 700},
                  {"title": "Article 4 — Definitions", "node_id": "0007", "line_num": 400}]
    aa, am = section_map(art_struct)
    check("article key mapped", am["Article 17"], 700)
    check("recitals key mapped", am["Recitals"], 3)
    res_art = {"tool_calls": [{"tool": "get_page_content", "args": {"pages": "690-720"}}]}
    check("article recall 1/2", score_result(res_art, ["Article 17", "Article 4"], aa, am),
          (1, 2, 0))

    check("gold drops NONE", gold_list("15.4.2; NONE-for-freshness; 9.2.3"),
          (["15.4.2", "9.2.3"], True))
    check("gold pure absence", gold_list("NONE"), ([], True))
    check("parse spans", parse_spans("100-150,3172"), [(100, 150), (3172, 3172)])
    check("fetched tokens", fetched_tokens(res_node), {"0202", "0300"})

    if fails:
        raise SystemExit(f"self-test FAILED: {fails}")
    print("self-test OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

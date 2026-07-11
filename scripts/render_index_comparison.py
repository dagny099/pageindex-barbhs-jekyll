#!/usr/bin/env python3
"""Render the V1 Index Comparison Explorer.

Reads the three curated V1 indexes (IDX-D / IDX-C / IDX-O), the frozen corpus,
and the corpus manifest, then emits:

  - a single self-contained offline HTML explorer (three-pane inspection UI),
  - one Markdown outline per index condition,
  - a Markdown alignment report.

The explorer is a derived inspection artifact. The frozen corpus and the
original index JSON files remain authoritative. No LLM is called; all
review signals are conservative deterministic heuristics, not verdicts.

Usage:
    python scripts/render_index_comparison.py            # repo-default paths
    python scripts/render_index_comparison.py --overwrite
    python scripts/render_index_comparison.py \
        --idx-d indexes/IDX-D/index.json \
        --idx-c indexes/IDX-C/index.json \
        --idx-o indexes/IDX-O/index.json \
        --corpus corpus/site-book-v1/site-book-v1.md \
        --output reports/V1_INDEX_COMPARISON.html
"""

from __future__ import annotations

import argparse
import datetime as _dt
import hashlib
import html
import json
import re
import statistics
import subprocess
import sys
import unicodedata
from pathlib import Path

SCRIPT_VERSION = "1.0.0"
CONDITIONS = ("D", "C", "O")
CONDITION_LABELS = {
    "D": "IDX-D · Deterministic",
    "C": "IDX-C · Cloud-assisted",
    "O": "IDX-O · Ollama-assisted",
}

REPO_ROOT = Path(__file__).resolve().parent.parent

STOPWORDS = set(
    """the a an and or of to in for on with by is are was were be been being
    this that these those it its as at from about into over under their his
    her they them we you i he she which who whom what when where how why not
    no nor but if then than so such can could may might will would shall
    should do does did done have has had having more most other some any each
    all both few own same s t don now""".split()
)

STATUS_TERMS = {
    "production", "deployed", "deployment", "complete", "completed",
    "launched", "live", "shipped", "finished", "operational",
}

GENERIC_PHRASES = (
    "this section", "provides an overview", "offers an overview",
    "provides a summary", "key aspects", "a range of", "various aspects",
    "serves as", "highlights the importance", "in summary", "overall,",
    "delves into", "explores the", "sheds light on",
)

# ---------------------------------------------------------------------------
# Loading and traversal
# ---------------------------------------------------------------------------


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_index(path: Path) -> dict:
    """Load a PageIndex index JSON. Returns dict with at least 'structure'."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        data = {"structure": data}
    if "structure" not in data:
        raise ValueError(f"{path}: no 'structure' key in index JSON")
    struct = data["structure"]
    if isinstance(struct, dict):
        data["structure"] = [struct]
    return data


def flatten(structure: list, parent: int | None = None, depth: int = 0,
            out: list | None = None, path: tuple = ()) -> list:
    """Pre-order flatten. Each entry: dict with node ref + derived fields."""
    if out is None:
        out = []
    for node in structure:
        title = node.get("title") or ""
        entry = {
            "i": len(out),
            "node": node,
            "id": node.get("node_id") or "",
            "title": title,
            "depth": depth,
            "parent": parent,
            "path": path + (title,),
            "children": [],
        }
        out.append(entry)
        if parent is not None:
            out[parent]["children"].append(entry["i"])
        flatten(node.get("nodes") or [], entry["i"], depth + 1, out,
                entry["path"])
    return out


# ---------------------------------------------------------------------------
# Normalization and alignment
# ---------------------------------------------------------------------------

_MD_LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")


def normalize_title(title: str) -> str:
    """Conservative normalization for comparison: NFC, link syntax stripped,
    whitespace collapsed. Punctuation and numbers are preserved."""
    t = unicodedata.normalize("NFC", title or "")
    t = _MD_LINK.sub(r"\1", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def norm_path(path: tuple) -> tuple:
    return tuple(normalize_title(p) for p in path)


def review_key(entry: dict) -> str:
    """Stable review key: node_id plus a short hash of the normalized heading
    path, so exported flags survive cosmetic regeneration but do not silently
    reattach to a different heading."""
    h = hashlib.sha256("␟".join(norm_path(entry["path"])).encode()).hexdigest()[:8]
    return f"{entry['id']}·{h}"


def align(flat_by_cond: dict) -> tuple[dict, list]:
    """Align the three flattened trees conservatively.

    Primary key is node_id (verified against normalized heading path and
    line_num). Nodes whose node_id is absent from a condition are retried by
    normalized heading path. Returns (per-node status for the reference
    (IDX-D) tree, list of extra nodes present only in non-reference trees).

    Statuses: exact / probable / divergent / ambiguous / unmatched.
    """
    ref = flat_by_cond["D"]
    others = {c: flat_by_cond[c] for c in ("C", "O")}

    by_id = {}
    by_path = {}
    ambiguous_ids = set()
    for cond, flat in others.items():
        ids = {}
        paths = {}
        for e in flat:
            if e["id"] in ids:
                ambiguous_ids.add((cond, e["id"]))
            ids.setdefault(e["id"], e)
            paths.setdefault(norm_path(e["path"]), e)
        by_id[cond] = ids
        by_path[cond] = paths

    statuses = []
    matched = {c: set() for c in others}
    for e in ref:
        st = {"status": "exact", "match": {}, "notes": []}
        for cond in others:
            m = by_id[cond].get(e["id"])
            how = "id"
            if m is not None and norm_path(m["path"]) != norm_path(e["path"]):
                # same id, different heading path: suspicious; try path match
                pm = by_path[cond].get(norm_path(e["path"]))
                if pm is not None:
                    m, how = pm, "path"
                else:
                    st["notes"].append(f"IDX-{cond}: node_id {e['id']} has a "
                                       f"different heading path")
                    st["status"] = "divergent"
            if m is None:
                m = by_path[cond].get(norm_path(e["path"]))
                how = "path"
            if m is None:
                st["match"][cond] = None
                st["status"] = "unmatched"
                st["notes"].append(f"IDX-{cond}: no matching node")
                continue
            if (cond, m["id"]) in ambiguous_ids:
                st["status"] = "ambiguous"
                st["notes"].append(f"IDX-{cond}: duplicate node_id {m['id']}")
            st["match"][cond] = m["i"]
            matched[cond].add(m["i"])
            if how == "path" and st["status"] == "exact":
                st["status"] = "probable"
                st["notes"].append(f"IDX-{cond}: matched by heading path, "
                                   f"not node_id")
            if normalize_title(m["title"]) != normalize_title(e["title"]):
                st["status"] = "divergent"
                st["notes"].append(f"IDX-{cond}: title differs: "
                                   f"{m['title']!r}")
            if m["node"].get("line_num") != e["node"].get("line_num"):
                if st["status"] == "exact":
                    st["status"] = "probable"
                st["notes"].append(
                    f"IDX-{cond}: line_num {m['node'].get('line_num')} vs "
                    f"{e['node'].get('line_num')}")
        statuses.append(st)

    extras = []
    for cond, flat in others.items():
        for e in flat:
            if e["i"] not in matched[cond]:
                extras.append({"cond": cond, "id": e["id"],
                               "title": e["title"],
                               "path": " → ".join(e["path"]),
                               "line_num": e["node"].get("line_num")})
    return statuses, extras


# ---------------------------------------------------------------------------
# Spans, boundary checks, source documents
# ---------------------------------------------------------------------------


def compute_spans(flat: list, line_count: int) -> None:
    """Attach 1-based inclusive line spans to each entry of the reference
    tree: own_end (up to next node) and span_end (end of subtree)."""
    starts = [e["node"].get("line_num") or 0 for e in flat]
    for idx, e in enumerate(flat):
        start = starts[idx]
        e["start"] = start
        e["own_end"] = line_count
        e["span_end"] = line_count
        for j in range(idx + 1, len(flat)):
            if e["own_end"] == line_count and starts[j] > 0:
                e["own_end"] = max(start, starts[j] - 1)
            if flat[j]["depth"] <= e["depth"] and starts[j] > 0:
                e["span_end"] = max(start, starts[j] - 1)
                break
        else:
            e["span_end"] = line_count
        if e["own_end"] > e["span_end"]:
            e["own_end"] = e["span_end"]


def check_text_boundaries(flat: list, corpus_lines: list) -> list:
    """Verify each node's embedded text matches the corpus slice implied by
    its line span. Returns a list of mismatch dicts."""
    mismatches = []
    for e in flat:
        text = (e["node"].get("text") or "")
        if not text.strip() or not e.get("start"):
            continue
        slice_ = "\n".join(corpus_lines[e["start"] - 1:e["own_end"]])
        if _squash(text) != _squash(slice_):
            mismatches.append({
                "id": e["id"], "title": e["title"],
                "lines": f"{e['start']}–{e['own_end']}",
                "text_len": len(text), "slice_len": len(slice_),
            })
            e.setdefault("warn", []).append("text-mismatch")
            e["embedded_text"] = text  # keep authoritative text for display
    return mismatches


def _squash(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def doc_for_line(docs: list, line: int) -> int | None:
    for i, d in enumerate(docs):
        if d["start"] <= line <= d["end"]:
            return i
    return None


def load_manifest_docs(path: Path | None) -> list:
    if path is None or not path.exists():
        return []
    m = json.loads(path.read_text(encoding="utf-8"))
    docs = []
    for d in m.get("documents", []):
        docs.append({
            "title": d.get("source_title") or d.get("source_path") or "?",
            "path": d.get("source_path") or "",
            "url": d.get("canonical_url") or "",
            "group": d.get("group") or "",
            "start": d.get("output_start_line") or 0,
            "end": d.get("output_end_line") or 0,
        })
    docs.sort(key=lambda d: d["start"])
    return docs


# ---------------------------------------------------------------------------
# Review-signal heuristics (deterministic; produce signals, not verdicts)
# ---------------------------------------------------------------------------

_NUM = re.compile(r"\d[\d,]*(?:\.\d+)?%?")
_ENTITY = re.compile(r"\b(?:[A-Z][A-Za-z0-9+./-]*[ \t]+){1,3}[A-Z][A-Za-z0-9+./-]*\b")


def content_words(text: str) -> set:
    return {w for w in re.findall(r"[a-z0-9']+", text.lower())
            if len(w) > 3 and w not in STOPWORDS}


def summary_signals(summary: str, source: str, context: str) -> list:
    """Signals for one summary against its source section.

    `source` is the node's own text; `context` is the wider subtree span
    (used to avoid false positives for parent-node summaries that legitimately
    cover child content)."""
    signals = []
    ctx_norm = context.replace(",", "")

    # strip list-enumerator numbers ("1." / "2)" at line start) before
    # extracting numbers — they are formatting, not claims about the source
    body = re.sub(r"(?m)^\s*(?:\*\*)?\d{1,2}[.)]\s", " ", summary)
    nums = sorted({n.replace(",", "") for n in _NUM.findall(body)})
    missing_nums = [n for n in nums if n not in ctx_norm]
    if missing_nums:
        signals.append({"kind": "numbers-not-in-source",
                        "detail": ", ".join(missing_nums[:6])})

    ctx_lower = context.lower()
    sum_words = set(re.findall(r"[a-z]+", summary.lower()))
    missing_status = sorted(t for t in STATUS_TERMS
                            if t in sum_words and t not in ctx_lower)
    if missing_status:
        signals.append({"kind": "status-term-not-in-source",
                        "detail": ", ".join(missing_status)})

    ents = sorted({e.strip() for e in _ENTITY.findall(summary)})
    missing_ents = [e for e in ents
                    if e.lower() not in ctx_lower and len(e) > 6][:5]
    if missing_ents:
        signals.append({"kind": "entity-not-in-source",
                        "detail": "; ".join(missing_ents)})

    cw = content_words(summary)
    if cw:
        overlap = len(cw & content_words(context)) / len(cw)
        if overlap < 0.25:
            signals.append({"kind": "low-source-overlap",
                            "detail": f"{overlap:.0%} of summary content "
                                      f"words appear in source"})

    lower = summary.lower()
    generic_hits = [p for p in GENERIC_PHRASES if p in lower]
    if len(generic_hits) >= 2:
        signals.append({"kind": "generic-language",
                        "detail": ", ".join(f"“{p}”" for p in generic_hits[:4])})
    return signals


def boilerplate_openings(entries: list, cond: str, top: int = 5) -> list:
    """Most common 3-word summary openings within a condition. Reported once
    in the alignment report (a systematic prompt artifact is not worth a
    per-node signal)."""
    counts = {}
    for e in entries:
        s = e["conds"].get(cond, {}).get("summary") or ""
        words = s.split()
        if len(words) >= 3:
            k = " ".join(words[:3])
            counts[k] = counts.get(k, 0) + 1
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:top]


def cross_summary_signals(entries: list, cond: str) -> None:
    """Length outliers and near-duplicate summaries within one condition.
    Mutates entries[i]['conds'][cond]['signals']."""
    items = [(e, e["conds"][cond]) for e in entries
             if e["conds"].get(cond, {}).get("summary")]
    if not items:
        return
    lengths = [len(c["summary"]) for _, c in items]
    med = statistics.median(lengths)
    toks = [content_words(c["summary"]) for _, c in items]
    for idx, (e, c) in enumerate(items):
        n = len(c["summary"])
        if med and n < 0.35 * med:
            c["signals"].append({"kind": "unusually-short",
                                 "detail": f"{n} chars vs median {med:.0f}"})
        elif med and n > 2.5 * med:
            c["signals"].append({"kind": "unusually-long",
                                 "detail": f"{n} chars vs median {med:.0f}"})
        dups = []
        for jdx, (e2, _) in enumerate(items):
            if jdx == idx or not toks[idx] or not toks[jdx]:
                continue
            jac = len(toks[idx] & toks[jdx]) / len(toks[idx] | toks[jdx])
            if jac >= 0.75:
                dups.append(e2["id"])
        if dups:
            c["signals"].append({"kind": "near-duplicate-summary",
                                 "detail": "similar to node(s) " +
                                           ", ".join(sorted(dups)[:5])})


# ---------------------------------------------------------------------------
# Assembly
# ---------------------------------------------------------------------------


def build_model(paths: dict, title: str) -> dict:
    """Load everything and compute the full data model used by all outputs."""
    corpus_text = paths["corpus"].read_text(encoding="utf-8")
    corpus_lines = corpus_text.split("\n")
    docs = load_manifest_docs(paths.get("manifest"))

    indexes = {c: load_index(paths[c]) for c in CONDITIONS}
    flat = {c: flatten(indexes[c]["structure"]) for c in CONDITIONS}
    statuses, extras = align(flat)

    ref = flat["D"]
    compute_spans(ref, len(corpus_lines))
    mismatches = check_text_boundaries(ref, corpus_lines)

    entries = []
    for e, st in zip(ref, statuses):
        own_text = "\n".join(corpus_lines[e["start"] - 1:e["own_end"]]) \
            if e.get("start") else (e["node"].get("text") or "")
        span_text = "\n".join(corpus_lines[e["start"] - 1:e["span_end"]]) \
            if e.get("start") else own_text
        conds = {"D": {"textlen": len(e["node"].get("text") or "")}}
        for c in ("C", "O"):
            mi = st["match"].get(c)
            node = flat[c][mi]["node"] if mi is not None else None
            summary = (node.get("summary") or "").strip() if node else ""
            prefix = (node.get("prefix_summary") or "").strip() if node else ""
            cd = {"summary": summary,
                  "prefix": bool(prefix) and not summary,
                  "textlen": len((node.get("text") or "")) if node else 0,
                  "signals": []}
            if summary:
                cd["signals"] = summary_signals(summary, own_text, span_text)
            conds[c] = cd
        warns = list(e.get("warn", []))
        cs, os_ = conds["C"]["summary"], conds["O"]["summary"]
        if bool(cs) != bool(os_):
            warns.append("summary-missing-in-one-condition")
        if cs and os_:
            ratio = max(len(cs), len(os_)) / max(1, min(len(cs), len(os_)))
            if ratio >= 3:
                warns.append("summary-length-disparity")
        entry = {
            "i": e["i"], "id": e["id"], "key": review_key(e),
            "title": e["title"], "depth": e["depth"], "parent": e["parent"],
            "children": e["children"], "path": list(e["path"]),
            "start": e.get("start", 0), "own_end": e.get("own_end", 0),
            "span_end": e.get("span_end", 0),
            "doc": doc_for_line(docs, e.get("start", 0)),
            "status": st["status"], "align_notes": st["notes"],
            "warns": warns, "conds": conds,
        }
        if "embedded_text" in e:
            entry["embedded_text"] = e["embedded_text"]
        entries.append(entry)

    for c in ("C", "O"):
        cross_summary_signals(entries, c)

    # repeated-title stats (informative: how much ancestry matters)
    title_counts = {}
    for e in entries:
        title_counts.setdefault(normalize_title(e["title"]), []).append(e["id"])
    repeated = {t: ids for t, ids in sorted(title_counts.items())
                if len(ids) > 1}

    def prov(cond):
        p = paths[cond]
        pj = p.parent / "provenance.json"
        extra = {}
        if pj.exists():
            try:
                pdata = json.loads(pj.read_text())
                extra = {"model": pdata.get("generation", {}).get("model"),
                         "pageindex_commit": pdata.get("pageindex_commit")}
            except (json.JSONDecodeError, OSError):
                pass
        return {"path": _rel(p), "sha256": sha256_file(p), **extra}

    repo_commit = None
    try:
        repo_commit = subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT,
            capture_output=True, text=True, timeout=10).stdout.strip() or None
    except OSError:
        pass

    model = {
        "meta": {
            "title": title,
            "script_version": SCRIPT_VERSION,
            "generated_at": _dt.datetime.now(_dt.timezone.utc)
                .strftime("%Y-%m-%dT%H:%M:%SZ"),
            "repo_commit": repo_commit,
            "corpus": {"path": _rel(paths["corpus"]),
                       "sha256": sha256_file(paths["corpus"]),
                       "lines": len(corpus_lines)},
            "indexes": {c: prov(c) for c in CONDITIONS},
            "doc_description": {
                c: indexes[c].get("doc_description") or "" for c in ("C", "O")},
            "condition_labels": CONDITION_LABELS,
        },
        "corpus_text": corpus_text,
        "docs": docs,
        "nodes": entries,
        "extras": extras,
        "boundary_mismatches": mismatches,
        "repeated_titles": repeated,
    }
    return model


def _rel(p: Path) -> str:
    try:
        return str(p.resolve().relative_to(REPO_ROOT))
    except ValueError:
        return str(p)


# ---------------------------------------------------------------------------
# Markdown outlines
# ---------------------------------------------------------------------------


def build_outline(model: dict, cond: str) -> str:
    meta = model["meta"]
    idx = meta["indexes"][cond]
    lines = [
        f"# {CONDITION_LABELS[cond]} — Index Outline",
        "",
        f"Derived from `{idx['path']}` (sha256 `{idx['sha256'][:12]}…`) over "
        f"corpus `{meta['corpus']['path']}`.",
        "Generated by `scripts/render_index_comparison.py` "
        f"v{meta['script_version']}. Node text omitted by design.",
        "",
    ]
    docs = model["docs"]
    for e in model["nodes"]:
        pad = "  " * e["depth"]
        cd = e["conds"].get(cond, {})
        bits = [f"`{e['id']}`", f"lines {e['start']}–{e['span_end']}"]
        if e["children"]:
            bits.append(f"children {len(e['children'])}")
        if e["doc"] is not None and docs:
            bits.append(f"doc: {docs[e['doc']]['title']}")
        lines.append(f"{pad}- **{e['title']}** — " + " · ".join(bits))
        if cond != "D":
            if cd.get("summary"):
                one = re.sub(r"\s+", " ", cd["summary"]).strip()
                lines.append(f"{pad}  - Summary: {one}")
            elif cd.get("prefix"):
                lines.append(f"{pad}  - (prefix summary: verbatim node text, "
                             "below summary token threshold)")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Alignment report
# ---------------------------------------------------------------------------


def build_alignment_report(model: dict) -> str:
    meta = model["meta"]
    nodes = model["nodes"]
    by_status = {}
    for e in nodes:
        by_status.setdefault(e["status"], []).append(e)
    signal_counts = {}
    signal_nodes = {"C": 0, "O": 0}
    for e in nodes:
        for c in ("C", "O"):
            sigs = e["conds"][c].get("signals", [])
            if sigs:
                signal_nodes[c] += 1
            for s in sigs:
                signal_counts[(c, s["kind"])] = \
                    signal_counts.get((c, s["kind"]), 0) + 1
    warn_counts = {}
    for e in nodes:
        for w in e["warns"]:
            warn_counts[w] = warn_counts.get(w, 0) + 1

    L = []
    L.append("# V1 Index Alignment Report")
    L.append("")
    L.append(f"Generated by `scripts/render_index_comparison.py` "
             f"v{meta['script_version']} on {meta['generated_at']}.")
    L.append("")
    L.append("> **Scope:** this report evaluates *representational alignment* "
             "between the three index conditions — whether they describe the "
             "same document map. It says nothing about retrieval quality.")
    L.append("")
    L.append("## Inputs")
    L.append("")
    L.append("| Artifact | Path | SHA-256 (first 12) |")
    L.append("|---|---|---|")
    L.append(f"| Corpus | `{meta['corpus']['path']}` | "
             f"`{meta['corpus']['sha256'][:12]}` |")
    for c in CONDITIONS:
        idx = meta["indexes"][c]
        L.append(f"| {CONDITION_LABELS[c]} | `{idx['path']}` | "
                 f"`{idx['sha256'][:12]}` |")
    L.append("")
    L.append("## Alignment result")
    L.append("")
    L.append(f"- Nodes in reference tree (IDX-D): **{len(nodes)}**")
    for st in ("exact", "probable", "divergent", "ambiguous", "unmatched"):
        n = len(by_status.get(st, []))
        L.append(f"- {st.capitalize()} matches: **{n}**")
    L.append(f"- Nodes present only in IDX-C/IDX-O (unmatched extras): "
             f"**{len(model['extras'])}**")
    L.append("")
    if len(by_status.get("exact", [])) == len(nodes) and not model["extras"]:
        L.append("**All three indexes share an identical structure** — same "
                 "node IDs, normalized titles, and line numbers in the same "
                 "pre-order. IDX-C and IDX-O differ from IDX-D only in their "
                 "`summary` / `prefix_summary` fields. Review effort should "
                 "therefore focus on summary quality, not structure.")
        L.append("")
    for st in ("probable", "divergent", "ambiguous", "unmatched"):
        entries = by_status.get(st, [])
        if entries:
            L.append(f"### {st.capitalize()} nodes")
            L.append("")
            for e in entries:
                notes = "; ".join(e["align_notes"]) or "—"
                L.append(f"- `{e['id']}` **{e['title']}** "
                         f"(lines {e['start']}–{e['own_end']}): {notes}")
            L.append("")
    if model["extras"]:
        L.append("### Extra nodes (present only in a non-reference index)")
        L.append("")
        for x in model["extras"]:
            L.append(f"- IDX-{x['cond']} `{x['id']}` **{x['title']}** "
                     f"(line {x['line_num']}) — {x['path']}")
        L.append("")

    L.append("## Boundary verification")
    L.append("")
    mm = model["boundary_mismatches"]
    L.append(f"Each node's embedded `text` was compared (whitespace-"
             f"normalized) against the corpus slice implied by its line span. "
             f"Mismatches: **{len(mm)}**.")
    L.append("")
    for m in mm:
        L.append(f"- `{m['id']}` **{m['title']}** (lines {m['lines']}): "
                 f"embedded text {m['text_len']} chars vs corpus slice "
                 f"{m['slice_len']} chars")
    if mm:
        L.append("")

    L.append("## Summary coverage")
    L.append("")
    for c in ("C", "O"):
        n_sum = sum(1 for e in nodes if e["conds"][c].get("summary"))
        n_pre = sum(1 for e in nodes if e["conds"][c].get("prefix"))
        L.append(f"- IDX-{c}: {n_sum} generated summaries, {n_pre} prefix "
                 f"(verbatim-text) nodes")
    L.append("")

    L.append("## Repeated titles")
    L.append("")
    rep = model["repeated_titles"]
    L.append(f"{len(rep)} normalized titles occur on more than one node; "
             "alignment therefore always considers full heading ancestry, "
             "never bare titles. Most repeated:")
    L.append("")
    top = sorted(rep.items(), key=lambda kv: (-len(kv[1]), kv[0]))[:10]
    for t, ids in top:
        L.append(f"- “{t}” × {len(ids)}")
    L.append("")

    L.append("## Review signals (deterministic heuristics)")
    L.append("")
    L.append("These are conservative *signals for human review*, *not* "
             "confirmed errors. Counts by condition:")
    L.append("")
    L.append("| Signal | IDX-C | IDX-O |")
    L.append("|---|---|---|")
    kinds = sorted({k for (_, k) in signal_counts})
    for k in kinds:
        L.append(f"| {k} | {signal_counts.get(('C', k), 0)} | "
                 f"{signal_counts.get(('O', k), 0)} |")
    L.append("")
    L.append(f"Nodes with at least one signal — IDX-C: "
             f"**{signal_nodes['C']}**, IDX-O: **{signal_nodes['O']}**.")
    L.append("")
    L.append("### Most common summary openings (systematic prompt artifacts)")
    L.append("")
    for c in ("C", "O"):
        tops = boilerplate_openings(nodes, c)
        if tops:
            L.append(f"- IDX-{c}: " + "; ".join(
                f"“{k}…” × {v}" for k, v in tops))
    L.append("")
    if warn_counts:
        L.append("Node-level warnings:")
        L.append("")
        for w in sorted(warn_counts):
            L.append(f"- {w}: {warn_counts[w]}")
        L.append("")
    L.append("---")
    L.append("")
    L.append("*This explorer is a derived inspection artifact. The frozen "
             "corpus and original index JSON files remain authoritative.*")
    L.append("")
    return "\n".join(L)


# ---------------------------------------------------------------------------
# HTML
# ---------------------------------------------------------------------------


def esc(s: str) -> str:
    return html.escape(str(s), quote=True)


def embed_json(model: dict) -> str:
    """Serialize the model for embedding inside a <script> tag."""
    payload = json.dumps(model, ensure_ascii=False, sort_keys=True,
                         separators=(",", ":"))
    return payload.replace("</", "<\\/")


def build_html(model: dict) -> str:
    tpl = _HTML_TEMPLATE
    meta = model["meta"]
    return (tpl
            .replace("%%TITLE%%", esc(meta["title"]))
            .replace("%%GENERATED%%", esc(meta["generated_at"]))
            .replace("%%VERSION%%", esc(meta["script_version"]))
            .replace("%%DATA%%", embed_json(model)))


# The template is long but deliberately dependency-free: system fonts,
# no external assets, all data embedded.
_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%%TITLE%%</title>
<style>
:root{
  --paper:#fffdf8; --panel:#ffffff; --soft:#f3efe4; --line:#e4ddcc;
  --ink:#2b302b; --muted:#687069; --green:#3e6b4f; --green-soft:#e8efe9;
  --blue:#3d5a80; --blue-soft:#e3ebf3; --amber:#a06a1d; --amber-soft:#fff3d8;
  --red:#8b3f2f; --red-soft:#f7e4df;
  --r:10px; --shadow:0 2px 10px rgba(35,40,35,.07);
  --sans:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;
  --mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;
}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{font:14px/1.5 var(--sans);color:var(--ink);background:var(--paper);display:flex;flex-direction:column}
button{font:inherit;color:inherit;background:var(--panel);border:1px solid var(--line);border-radius:7px;padding:4px 10px;cursor:pointer}
button:hover{border-color:var(--muted)}
button:focus-visible,a:focus-visible,input:focus-visible,select:focus-visible,textarea:focus-visible,[tabindex]:focus-visible{outline:2px solid var(--blue);outline-offset:1px}
button.primary{background:var(--green);border-color:var(--green);color:#fff}
input[type=text],input[type=search],select,textarea{font:inherit;border:1px solid var(--line);border-radius:7px;padding:4px 8px;background:#fff;color:var(--ink)}
h1,h2,h3{margin:0;font-weight:600}
.small{font-size:12px;color:var(--muted)}
code,.mono{font-family:var(--mono);font-size:12px}
mark{background:var(--amber-soft);color:inherit;border-radius:3px;padding:0 2px}
mark.ok{background:var(--green-soft)}
@media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important;scroll-behavior:auto!important}}

header.app{display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:8px 14px;background:var(--panel);border-bottom:1px solid var(--line);position:sticky;top:0;z-index:20}
header.app h1{font-size:15px;margin-right:6px}
#search{flex:1 1 220px;max-width:420px}
.counts{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.chip{display:inline-flex;align-items:center;gap:4px;border:1px solid var(--line);border-radius:999px;padding:1px 9px;font-size:12px;background:var(--soft)}
.chip b{font-weight:600}

#legend{display:flex;flex-wrap:wrap;gap:10px;padding:6px 14px;font-size:12px;color:var(--muted);background:var(--soft);border-bottom:1px solid var(--line)}
.dot{display:inline-block;width:9px;height:9px;border-radius:50%;margin-right:4px;vertical-align:baseline}
.dot.exact{background:var(--green)} .dot.probable{background:var(--amber)}
.dot.divergent,.dot.ambiguous{background:var(--amber);outline:2px solid var(--red)}
.dot.unmatched{background:var(--red)}
.dot.signal{background:#fff;border:2px solid var(--amber)}
.dot.flagged{background:var(--blue)}

main{flex:1;display:grid;grid-template-columns:330px minmax(340px,1fr) minmax(320px,480px);gap:10px;padding:10px 14px;min-height:0}
.pane{background:var(--panel);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--shadow);display:flex;flex-direction:column;min-height:0;overflow:hidden}
.pane>.body{overflow:auto;flex:1;min-height:0}
.pane>.head{padding:8px 12px;border-bottom:1px solid var(--line);display:flex;flex-wrap:wrap;gap:6px;align-items:center;background:linear-gradient(#fff,#fbf9f2)}
.pane>.head h2{font-size:13px;color:var(--muted);text-transform:uppercase;letter-spacing:.04em}

/* Tree */
#treeControls{display:flex;flex-wrap:wrap;gap:6px;padding:8px 10px;border-bottom:1px solid var(--line);font-size:12px;align-items:center}
#treeControls select{font-size:12px;max-width:150px}
#tree{padding:4px 4px 20px;font-size:13px}
.trow{display:flex;align-items:center;gap:4px;padding:2px 6px;border-radius:6px;cursor:pointer;border:1px solid transparent}
.trow:hover{background:var(--soft)}
.trow.sel{background:var(--blue-soft);border-color:var(--blue)}
.trow .caret{width:16px;flex:none;text-align:center;color:var(--muted);font-size:10px}
.trow .t{flex:1;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.trow .meta{flex:none;color:var(--muted);font-size:11px;display:flex;gap:5px;align-items:center}
.trow .fdot{width:8px;height:8px;border-radius:50%;flex:none}
#results{padding:6px}
.rrow{padding:6px 8px;border:1px solid var(--line);border-radius:8px;margin-bottom:6px;cursor:pointer;background:#fff}
.rrow:hover{border-color:var(--blue)}
.rrow .path{font-size:11px;color:var(--muted)}
.rrow .fields{font-size:11px;color:var(--blue)}
.empty{padding:24px 16px;color:var(--muted);text-align:center}

/* Center */
#crumb{font-size:12px;color:var(--muted);padding:0 0 4px}
#crumb a{color:var(--blue);text-decoration:none;cursor:pointer}
#nodeTitle{font-size:17px}
.metachips{display:flex;flex-wrap:wrap;gap:6px;margin:8px 0}
.badge{display:inline-flex;gap:4px;align-items:center;font-size:11px;border-radius:999px;padding:1px 8px;border:1px solid var(--line);background:var(--soft)}
.badge.exact{background:var(--green-soft);border-color:var(--green);color:var(--green)}
.badge.probable,.badge.divergent,.badge.ambiguous,.badge.warn{background:var(--amber-soft);border-color:var(--amber);color:var(--amber)}
.badge.unmatched{background:var(--red-soft);border-color:var(--red);color:var(--red)}
.badge.sig{background:var(--amber-soft);border-color:var(--amber);color:#6b4a12}
.sumcard{border:1px solid var(--line);border-radius:var(--r);margin:10px 0;background:#fff}
.sumcard.active{border-color:var(--blue);box-shadow:0 0 0 2px var(--blue-soft)}
.sumcard .chead{display:flex;flex-wrap:wrap;gap:6px;align-items:center;padding:7px 12px;border-bottom:1px solid var(--line);background:var(--soft);border-radius:var(--r) var(--r) 0 0}
.sumcard .chead .cname{font-weight:600;font-size:13px}
.sumcard .ctext{padding:10px 12px;white-space:pre-wrap}
.sumcard .ctext.none{color:var(--muted);font-style:italic}
.flagrow{display:flex;flex-wrap:wrap;gap:5px;padding:8px 12px;border-top:1px dashed var(--line)}
.flagbtn{font-size:11px;border-radius:999px;padding:2px 9px}
.flagbtn[aria-pressed="true"]{background:var(--blue);border-color:var(--blue);color:#fff}
#noteWrap{margin:10px 0}
#noteWrap textarea{width:100%;min-height:52px;resize:vertical}
.dnote{border:1px dashed var(--line);border-radius:var(--r);padding:8px 12px;color:var(--muted);margin:10px 0;background:var(--soft)}

/* Right */
.tabs{display:flex;gap:2px;padding:6px 8px 0}
.tabs button{border-radius:8px 8px 0 0;border-bottom:none;background:var(--soft)}
.tabs button[aria-selected="true"]{background:#fff;font-weight:600;border-color:var(--line)}
.tabbody{border-top:1px solid var(--line);overflow:auto;flex:1;min-height:0;padding:10px 12px}
#src{font-family:var(--mono);font-size:12px;line-height:1.5;white-space:pre-wrap;word-break:break-word}
#src .ln{color:#b0a98f;user-select:none;display:inline-block;width:44px;text-align:right;padding-right:10px}
#src .own{background:var(--green-soft)}
.kv{display:grid;grid-template-columns:auto 1fr;gap:2px 12px;font-size:12px}
.kv dt{color:var(--muted)} .kv dd{margin:0;font-family:var(--mono);word-break:break-all}
details{border:1px solid var(--line);border-radius:8px;padding:6px 10px;margin:8px 0;background:#fff}
details summary{cursor:pointer;color:var(--blue);font-size:12px}
pre.raw{overflow:auto;font-size:11px;background:var(--soft);padding:8px;border-radius:8px}

/* Overlays */
#overlay{position:fixed;inset:0;background:rgba(43,48,43,.35);display:flex;align-items:flex-start;justify-content:center;z-index:50;padding:30px 14px;overflow:auto}
#overlay.hidden,.hidden{display:none!important}
#helpCard{background:var(--paper);border:1px solid var(--line);border-radius:14px;box-shadow:0 16px 40px rgba(35,40,35,.25);max-width:760px;padding:22px 26px}
#helpCard h2{font-size:17px;margin-bottom:6px}
#helpCard h3{font-size:14px;margin:14px 0 4px;color:var(--green)}
#helpCard ul{margin:4px 0;padding-left:20px}
#helpCard kbd{font-family:var(--mono);font-size:11px;border:1px solid var(--line);border-bottom-width:2px;border-radius:4px;padding:0 5px;background:#fff}
#toast{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);background:var(--ink);color:#fff;border-radius:8px;padding:8px 16px;z-index:60;font-size:13px}

footer.app{padding:6px 14px;border-top:1px solid var(--line);font-size:11px;color:var(--muted);display:flex;gap:14px;flex-wrap:wrap}
footer.app a{color:var(--blue)}

@media (max-width:1100px){
  main{grid-template-columns:280px 1fr}
  #rightPane{grid-column:1/-1;max-height:50vh}
}
@media (max-width:760px){
  main{grid-template-columns:1fr;padding:8px}
  .pane{max-height:70vh}
  #leftPane{max-height:45vh}
}
@media print{header.app,#legend,footer.app{display:none}}
</style>
</head>
<body>
<header class="app">
  <h1>%%TITLE%%</h1>
  <input id="search" type="search" placeholder="Search titles, paths, summaries, source, node IDs…" aria-label="Search all indexed fields">
  <div class="counts" id="counts" title="Review progress (nodes with generated summaries)"></div>
  <button id="btnHelp" title="How to use this view">How to use this view</button>
  <button id="btnExport" title="Download review flags as JSON">Export flags</button>
  <button id="btnImport" title="Import review flags from a JSON file">Import</button>
  <button id="btnClear" title="Clear all locally stored review flags">Clear</button>
  <input id="importFile" type="file" accept="application/json" class="hidden" aria-hidden="true">
</header>

<div id="legend" aria-label="Legend">
  <span><span class="dot exact"></span>exact alignment</span>
  <span><span class="dot probable"></span>probable / divergent / ambiguous</span>
  <span><span class="dot unmatched"></span>unmatched</span>
  <span><span class="dot signal"></span>review signal (heuristic, not a verdict)</span>
  <span><span class="dot flagged"></span>has your review flag</span>
  <span>“Signals only” filters the tree to nodes needing attention.</span>
</div>

<main>
  <section class="pane" id="leftPane" aria-label="Document tree">
    <div class="head"><h2>Document map</h2>
      <span class="small" id="treeCount"></span>
    </div>
    <div id="treeControls">
      <button id="btnExpand" title="Expand every branch">Expand all</button>
      <button id="btnCollapse" title="Collapse to top level">Collapse</button>
      <button id="btnReveal" title="Expand to the selected node">Reveal selected</button>
      <label><input type="checkbox" id="fltSignals"> Signals only</label>
      <label><input type="checkbox" id="fltSummaries"> With summaries</label>
      <label><input type="checkbox" id="fltFlagged"> Flagged</label>
      <select id="fltDoc" aria-label="Filter by source document"><option value="">All documents</option></select>
      <select id="fltDepth" aria-label="Filter by depth"><option value="">Any depth</option></select>
    </div>
    <div class="body">
      <div id="tree" role="tree" aria-label="Index hierarchy"></div>
      <div id="results" class="hidden" aria-live="polite"></div>
    </div>
  </section>

  <section class="pane" id="centerPane" aria-label="Node comparison">
    <div class="head"><h2>Node comparison</h2><span class="small">press <b>c</b>/<b>o</b> to pick a card, <b>1–6</b> to flag</span></div>
    <div class="body" id="center"><div class="empty">Select a node in the tree (or search) to compare conditions.</div></div>
  </section>

  <section class="pane" id="rightPane" aria-label="Source and inspection">
    <div class="tabs" role="tablist">
      <button role="tab" id="tabSrc" aria-selected="true" data-tab="src">Source text</button>
      <button role="tab" id="tabInspect" aria-selected="false" data-tab="inspect">Summary inspection</button>
      <button role="tab" id="tabRaw" aria-selected="false" data-tab="raw">Raw metadata</button>
    </div>
    <div class="tabbody" id="tabbody"><div class="empty">Node details appear here.</div></div>
  </section>
</main>

<footer class="app">
  <span>Generated %%GENERATED%% · script v%%VERSION%%</span>
  <span>This explorer is a derived inspection artifact — the frozen corpus and index JSON files remain authoritative.</span>
  <a id="provLink" href="#" role="button">Provenance</a>
</footer>

<div id="overlay" class="hidden" role="dialog" aria-modal="true" aria-labelledby="helpTitle">
  <div id="helpCard">
    <h2 id="helpTitle">V1 Index Comparison Explorer</h2>
    <p class="small">One frozen corpus, three index conditions. <b>IDX-D</b> is the deterministic
    Markdown-heading tree (no generated summaries — by design). <b>IDX-C</b> adds summaries from a
    cloud model; <b>IDX-O</b> adds summaries from a local Ollama model. Structure was verified at
    build time: <span id="helpAlign"></span>. Your job here is judging the <i>summaries</i>:
    are they faithful, specific, and boundary-respecting?</p>
    <h3>Workflow</h3>
    <ul>
      <li>Pick a node in the tree, or search (<kbd>/</kbd>). The center shows IDX-C and IDX-O summaries; the right pane shows the Markdown source for the node's lines.</li>
      <li>Flag each summary: Faithful · Too generic · Misleading · Missing distinction · Boundary problem · Needs review. Flags save to this browser's <code>localStorage</code> — <b>export to JSON</b> before clearing browser data.</li>
      <li><b>Signals only</b> filters to nodes where deterministic heuristics found something worth a look (numbers or entities absent from source, near-duplicate or generic phrasing, …). Signals are <i>prompts for review, not verdicts</i>.</li>
    </ul>
    <h3>Keyboard</h3>
    <ul>
      <li><kbd>j</kbd>/<kbd>k</kbd> next / previous node · <kbd>n</kbd> next unreviewed summary · <kbd>e</kbd> expand/collapse</li>
      <li><kbd>c</kbd>/<kbd>o</kbd> choose condition card · <kbd>1</kbd>–<kbd>6</kbd> toggle flags · <kbd>/</kbd> search · <kbd>?</kbd> this help</li>
    </ul>
    <h3>Alignment states</h3>
    <ul>
      <li><b>exact</b> — node ID, title, and line range agree across all three indexes.</li>
      <li><b>probable</b> — matched with minor differences (e.g. by heading path, or line drift).</li>
      <li><b>divergent / ambiguous</b> — matched but titles differ, or duplicate IDs made the match uncertain.</li>
      <li><b>unmatched</b> — no counterpart found; never silently dropped.</li>
    </ul>
    <details id="provPanel"><summary>Provenance</summary><dl class="kv" id="provList"></dl></details>
    <p style="text-align:right;margin-bottom:0"><button class="primary" id="btnCloseHelp">Start reviewing</button></p>
  </div>
</div>

<script type="application/json" id="data">%%DATA%%</script>
<script>
(function(){
"use strict";
var DATA = JSON.parse(document.getElementById("data").textContent);
var NODES = DATA.nodes, META = DATA.meta, DOCS = DATA.docs;
var LINES = DATA.corpus_text.split("\n");
var FLAG_NAMES = ["Faithful","Too generic","Misleading","Missing distinction","Boundary problem","Needs review"];
var LS_KEY = "piV1Review::" + META.corpus.sha256.slice(0,12);
var LS_HELP = LS_KEY + "::helpDismissed";
var $ = function(id){ return document.getElementById(id); };

/* ---------- state ---------- */
var sel = null;                 // selected node index
var activeCond = "C";           // card targeted by keyboard flags
var expanded = {};              // node i -> bool
var store = loadStore();
var searchMode = false;

function loadStore(){
  try{
    var raw = localStorage.getItem(LS_KEY);
    if(raw){ var s = JSON.parse(raw); if(s && s.flags) return s; }
  }catch(e){}
  return {version:1, corpus_sha256:META.corpus.sha256, flags:{}};
}
function saveStore(){
  try{ localStorage.setItem(LS_KEY, JSON.stringify(store)); }
  catch(e){ toast("Could not save to localStorage: " + e.message); }
  renderCounts();
}
function nodeFlags(n){ return store.flags[n.key] || null; }
function condFlags(n,c){ var f = nodeFlags(n); return (f && f[c]) || []; }

/* ---------- helpers ---------- */
function el(tag, attrs, kids){
  var e = document.createElement(tag);
  if(attrs) for(var k in attrs){
    if(k === "text") e.textContent = attrs[k];
    else if(k === "html") e.innerHTML = attrs[k];
    else if(k.slice(0,2) === "on") e.addEventListener(k.slice(2), attrs[k]);
    else e.setAttribute(k, attrs[k]);
  }
  (kids||[]).forEach(function(c){ e.appendChild(c); });
  return e;
}
function escHtml(s){ return String(s).replace(/[&<>"]/g, function(c){
  return {"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]; }); }
function toast(msg){
  var t = $("toastEl"); if(t) t.remove();
  t = el("div",{id:"toastEl"}); t.id="toast"; t.textContent = msg;
  document.body.appendChild(t); setTimeout(function(){ t.remove(); }, 3200);
}
function hasSignals(n){
  return n.warns.length>0 || n.status!=="exact" ||
    (n.conds.C.signals||[]).length>0 || (n.conds.O.signals||[]).length>0;
}
function hasSummary(n){ return !!(n.conds.C.summary || n.conds.O.summary); }
function isReviewed(n){
  var f = nodeFlags(n); if(!f) return false;
  return (f.C&&f.C.length) || (f.O&&f.O.length) || (f.note&&f.note.trim());
}
function isFlaggedBad(n){
  var f = nodeFlags(n); if(!f) return false;
  function bad(a){ return (a||[]).some(function(x){ return x!=="Faithful"; }); }
  return bad(f.C) || bad(f.O);
}

/* ---------- counts ---------- */
function renderCounts(){
  var total=0, reviewed=0, flagged=0;
  NODES.forEach(function(n){
    if(hasSummary(n)){ total++; if(isReviewed(n)) reviewed++; }
    if(isFlaggedBad(n)) flagged++;
  });
  $("counts").innerHTML =
    '<span class="chip">reviewed <b>'+reviewed+"</b>/"+total+"</span>"+
    '<span class="chip">flagged <b>'+flagged+"</b></span>"+
    '<span class="chip">unresolved <b>'+(total-reviewed)+"</b></span>";
}

/* ---------- tree ---------- */
function visibleByFilters(n){
  if($("fltSignals").checked && !hasSignals(n)) return false;
  if($("fltSummaries").checked && !hasSummary(n)) return false;
  if($("fltFlagged").checked && !isReviewed(n)) return false;
  var d = $("fltDoc").value; if(d!=="" && String(n.doc)!==d) return false;
  var dep = $("fltDepth").value; if(dep!=="" && n.depth>+dep) return false;
  return true;
}
function computeShown(){
  // a node is shown if it or any descendant passes filters
  var shown = new Array(NODES.length).fill(false);
  for(var i=NODES.length-1;i>=0;i--){
    var n = NODES[i];
    shown[i] = visibleByFilters(n) ||
      n.children.some(function(c){ return shown[c]; });
  }
  return shown;
}
function renderTree(){
  var tree = $("tree"); tree.innerHTML = "";
  var shown = computeShown(); var count = 0;
  function rows(list, container){
    list.forEach(function(i){
      if(!shown[i]) return;
      var n = NODES[i]; count++;
      var open = !!expanded[i];
      var row = el("div",{class:"trow"+(sel===i?" sel":""), role:"treeitem",
        tabindex:"0", "aria-expanded": n.children.length? String(open):null,
        "data-i":String(i),
        onclick:function(ev){ if(ev.target.classList.contains("caret")) toggle(i); else select(i); },
        onkeydown:function(ev){ if(ev.key==="Enter"||ev.key===" "){ ev.preventDefault(); select(i);} }});
      row.style.paddingLeft = (6+n.depth*14)+"px";
      row.appendChild(el("span",{class:"caret",text:n.children.length?(open?"▾":"▸"):"•"}));
      row.appendChild(el("span",{class:"t",text:n.title,title:n.path.join(" → ")}));
      var meta = el("span",{class:"meta"});
      if(n.children.length) meta.appendChild(el("span",{text:String(n.children.length),title:n.children.length+" children"}));
      meta.appendChild(el("span",{text:"L"+n.start,title:"lines "+n.start+"–"+n.span_end}));
      if(n.status!=="exact") meta.appendChild(el("span",{class:"fdot dot "+n.status,title:"alignment: "+n.status}));
      if((n.conds.C.signals||[]).length || (n.conds.O.signals||[]).length || n.warns.length)
        meta.appendChild(el("span",{class:"fdot dot signal",title:"has review signals"}));
      if(isReviewed(n)) meta.appendChild(el("span",{class:"fdot dot flagged",title:"you flagged/reviewed this"}));
      row.appendChild(meta);
      container.appendChild(row);
      if(n.children.length && open){
        n.children.forEach(function(){});
        rows(n.children, container);
      }
    });
  }
  var roots = NODES.filter(function(n){ return n.parent===null; }).map(function(n){ return n.i; });
  rows(roots, tree);
  if(count===0) tree.appendChild(el("div",{class:"empty",text:"No nodes match the current filters. Uncheck a filter to see more."}));
  $("treeCount").textContent = count + " / " + NODES.length + " nodes";
}
function toggle(i){ expanded[i] = !expanded[i]; renderTree(); }
function expandAncestors(i){
  var p = NODES[i].parent;
  while(p!==null && p!==undefined){ expanded[p]=true; p=NODES[p].parent; }
}
function select(i, fromTree){
  sel = i; searchMode=false; $("results").classList.add("hidden");
  $("tree").classList.remove("hidden");
  expandAncestors(i); renderTree(); renderCenter(); renderRight();
  try{ history.replaceState(null,"","#node="+encodeURIComponent(NODES[i].id)); }catch(e){}
  var row = document.querySelector('.trow[data-i="'+i+'"]');
  if(row && !fromTree) row.scrollIntoView({block:"nearest"});
}

/* ---------- center ---------- */
function badge(cls, text, title){ return '<span class="badge '+cls+'" title="'+escHtml(title||"")+'">'+escHtml(text)+"</span>"; }
function renderCenter(){
  var c = $("center");
  if(sel===null){ c.innerHTML = '<div class="empty">Select a node to compare conditions.</div>'; return; }
  var n = NODES[sel];
  var docName = (n.doc!==null && DOCS[n.doc]) ? DOCS[n.doc].title : null;
  var crumb = n.path.slice(0,-1).map(function(t,idx){
    return '<a data-up="'+(n.path.length-1-idx)+'">'+escHtml(t)+"</a>";
  }).join(" → ");
  var h = [];
  h.push('<div id="crumb">'+(crumb||"(root)")+"</div>");
  h.push('<h3 id="nodeTitle">'+escHtml(n.title)+"</h3>");
  h.push('<div class="metachips">');
  h.push(badge("", "id "+n.id, "PageIndex node_id (identical across conditions)"));
  h.push(badge("", "lines "+n.start+"–"+n.span_end, "own text ends at line "+n.own_end));
  h.push(badge("", "depth "+n.depth));
  h.push(badge("", n.children.length+" children"));
  if(docName) h.push(badge("", docName, "source document (from corpus manifest)"));
  h.push(badge(n.status, n.status, (n.align_notes||[]).join("; ") || "node ID, title and lines agree in all three indexes"));
  n.warns.forEach(function(w){ h.push(badge("warn","⚠ "+w,"node-level warning")); });
  h.push("</div>");
  if(n.align_notes && n.align_notes.length)
    h.push('<div class="dnote">Alignment notes: '+escHtml(n.align_notes.join("; "))+"</div>");

  h.push('<div class="dnote"><b>IDX-D</b> — deterministic condition: no generated summary, by design. '+
         "Hierarchy and boundaries above come from the authored Markdown headings.</div>");

  ["C","O"].forEach(function(cond){
    var cd = n.conds[cond];
    var flags = condFlags(n,cond);
    h.push('<div class="sumcard'+(activeCond===cond?" active":"")+'" data-cond="'+cond+'">');
    h.push('<div class="chead"><span class="cname">'+escHtml(META.condition_labels[cond])+"</span>");
    var model = (META.indexes[cond]||{}).model;
    if(model) h.push('<span class="small">'+escHtml(model)+"</span>");
    if(cd.summary) h.push('<span class="small">'+cd.summary.length+" chars</span>");
    (cd.signals||[]).forEach(function(s){
      h.push(badge("sig","◌ "+s.kind, "Review signal (heuristic): "+s.detail));
    });
    h.push("</div>");
    if(cd.summary) h.push('<div class="ctext">'+escHtml(cd.summary)+"</div>");
    else if(cd.prefix) h.push('<div class="ctext none">No generated summary — node was below the summary token threshold; the index stores the node’s verbatim text instead (see Source tab).</div>');
    else h.push('<div class="ctext none">No summary present for this node in this condition.</div>');
    if(cd.summary){
      h.push('<div class="flagrow" role="group" aria-label="Review flags for IDX-'+cond+'">');
      FLAG_NAMES.forEach(function(f,fi){
        var on = flags.indexOf(f)>=0;
        h.push('<button class="flagbtn" aria-pressed="'+on+'" data-cond="'+cond+'" data-flag="'+escHtml(f)+'" title="Toggle ('+(fi+1)+' when card is active)">'+escHtml(f)+"</button>");
      });
      h.push("</div>");
    }
    h.push("</div>");
  });

  var note = (nodeFlags(n)||{}).note || "";
  h.push('<div id="noteWrap"><label class="small" for="noteBox">Reviewer note (saved locally)</label>'+
    '<textarea id="noteBox" placeholder="Optional note about this node…">'+escHtml(note)+"</textarea></div>");
  c.innerHTML = h.join("");

  c.querySelectorAll("#crumb a").forEach(function(a){
    a.addEventListener("click", function(){
      var up = +a.getAttribute("data-up"); var t = sel;
      for(var k=0;k<up;k++){ t = NODES[t].parent; }
      if(t!==null) select(t);
    });
  });
  c.querySelectorAll(".flagbtn").forEach(function(b){
    b.addEventListener("click", function(){
      toggleFlag(NODES[sel], b.getAttribute("data-cond"), b.getAttribute("data-flag"));
    });
  });
  c.querySelectorAll(".sumcard").forEach(function(card){
    card.addEventListener("click", function(){ setActiveCond(card.getAttribute("data-cond")); });
  });
  var nb = $("noteBox"); var noteTimer=null;
  nb.addEventListener("input", function(){
    clearTimeout(noteTimer);
    noteTimer = setTimeout(function(){
      var n2 = NODES[sel];
      var f = store.flags[n2.key] || (store.flags[n2.key]={});
      f.note = nb.value; if(!nb.value.trim()) delete f.note;
      if(!f.C && !f.O && !f.note) delete store.flags[n2.key];
      saveStore(); renderTree();
    }, 400);
  });
}
function setActiveCond(c){
  activeCond = c;
  document.querySelectorAll(".sumcard").forEach(function(card){
    card.classList.toggle("active", card.getAttribute("data-cond")===c);
  });
}
function toggleFlag(n, cond, flag){
  var f = store.flags[n.key] || (store.flags[n.key]={});
  var arr = f[cond] || (f[cond]=[]);
  var at = arr.indexOf(flag);
  if(at>=0) arr.splice(at,1); else arr.push(flag);
  arr.sort();
  if(!arr.length) delete f[cond];
  if(!f.C && !f.O && !f.note) delete store.flags[n.key];
  saveStore(); renderCenter(); renderTree();
}

/* ---------- right pane ---------- */
var curTab = "src";
function setTab(t){
  curTab = t;
  document.querySelectorAll('.tabs [role="tab"]').forEach(function(b){
    b.setAttribute("aria-selected", String(b.getAttribute("data-tab")===t));
  });
  renderRight();
}
function renderRight(){
  var body = $("tabbody");
  if(sel===null){ body.innerHTML = '<div class="empty">Node details appear here.</div>'; return; }
  var n = NODES[sel];
  if(curTab==="src") body.innerHTML = renderSource(n);
  else if(curTab==="inspect") body.innerHTML = renderInspect(n);
  else body.innerHTML = renderRaw(n);
}
function renderSource(n){
  if(!n.start) return '<div class="empty">No line range available for this node; source cannot be shown.</div>';
  var end = Math.min(n.span_end, LINES.length);
  if(n.start > LINES.length) return '<div class="empty">This node’s line range ('+n.start+"–"+n.span_end+") extends beyond the corpus ("+LINES.length+" lines). Its provenance may be stale.</div>";
  var out = ['<div class="small" style="margin-bottom:6px">Corpus lines '+n.start+"–"+end+
    ' — <span style="background:var(--green-soft);padding:0 4px;border-radius:3px">highlighted</span> = the node’s own text (before its first child).</div>'];
  if(n.embedded_text) out.push('<div class="dnote">⚠ The embedded node text differs from this corpus slice (see alignment report); the corpus is shown here, the embedded text in Raw metadata.</div>');
  out.push('<div id="src">');
  for(var ln=n.start; ln<=end; ln++){
    var own = ln <= n.own_end;
    out.push('<span class="ln">'+ln+"</span>"+
      '<span class="'+(own?"own":"")+'">'+escHtml(LINES[ln-1]===""?" ":LINES[ln-1])+"</span>\n");
  }
  out.push("</div>");
  return out.join("");
}
function markTerms(summary, sourceLower){
  // highlight numbers, status terms, capitalized entities; green if in source, amber if not
  var patterns = /(\d[\d,]*(?:\.\d+)?%?)|((?:[A-Z][A-Za-z0-9+.\/-]*[ \t]+){1,3}[A-Z][A-Za-z0-9+.\/-]*)|(\b(?:production|deployed|deployment|complete|completed|launched|live|shipped|finished|operational)\b)/g;
  return escHtml(summary).replace(patterns, function(m){
    var probe = m.replace(/,/g,"").toLowerCase();
    var okSrc = sourceLower.indexOf(probe)>=0 || sourceLower.indexOf(m.toLowerCase())>=0;
    return '<mark class="'+(okSrc?"ok":"")+'" title="'+(okSrc?"found in source section":"NOT found in source section — verify")+'">'+m+"</mark>";
  });
}
function renderInspect(n){
  var srcLower = LINES.slice(n.start-1, n.span_end).join("\n").replace(/,/g,"").toLowerCase();
  var out = ['<div class="small" style="margin-bottom:8px"><mark class="ok">green</mark> = number/entity/status term found in the source section · <mark>amber</mark> = not found (verify against source). Heuristics are review prompts, not verdicts.</div>'];
  var any=false;
  ["C","O"].forEach(function(cond){
    var cd = n.conds[cond];
    out.push("<h3 style='font-size:13px;margin:10px 0 4px'>"+escHtml(META.condition_labels[cond])+"</h3>");
    if(!cd.summary){
      out.push('<div class="dnote">'+(cd.prefix?"Prefix (verbatim-text) node — nothing generated to inspect.":"No summary in this condition.")+"</div>");
      return;
    }
    any=true;
    out.push('<div style="white-space:pre-wrap;border:1px solid var(--line);border-radius:8px;padding:8px 10px;background:#fff">'+markTerms(cd.summary, srcLower)+"</div>");
    out.push('<div class="small" style="margin:4px 0 8px">'+cd.summary.length+" chars");
    (cd.signals||[]).forEach(function(s){ out.push(" · ◌ "+escHtml(s.kind)+": "+escHtml(s.detail)); });
    out.push("</div>");
  });
  if(!any && !n.conds.C.summary && !n.conds.O.summary)
    out.push('<div class="empty">Neither condition generated a summary for this node (below token threshold — expected, not an error).</div>');
  return out.join("");
}
function renderRaw(n){
  var subset = {node_id:n.id, review_key:n.key, title:n.title, depth:n.depth,
    parent_path:n.path.slice(0,-1).join(" → "),
    lines:{start:n.start, own_end:n.own_end, span_end:n.span_end},
    alignment:{status:n.status, notes:n.align_notes},
    warnings:n.warns,
    source_document:(n.doc!==null&&DOCS[n.doc])?DOCS[n.doc].path:null,
    conditions:{
      "IDX-D":{text_chars:n.conds.D.textlen, summary:null},
      "IDX-C":{text_chars:n.conds.C.textlen, summary_chars:(n.conds.C.summary||"").length||null, prefix_only:n.conds.C.prefix||undefined, signals:n.conds.C.signals},
      "IDX-O":{text_chars:n.conds.O.textlen, summary_chars:(n.conds.O.summary||"").length||null, prefix_only:n.conds.O.prefix||undefined, signals:n.conds.O.signals}
    }};
  var out = ['<div class="small">Compact node metadata (full summaries are in the center pane; node text is derived from corpus lines and shown in Source).</div>'];
  out.push('<pre class="raw">'+escHtml(JSON.stringify(subset,null,2))+"</pre>");
  var full = {node_id:n.id, title:n.title, line_num:n.start,
    text:"(see Source tab — verified identical to corpus lines "+n.start+"–"+n.own_end+")",
    summary_C:n.conds.C.summary||null, summary_O:n.conds.O.summary||null};
  if(n.embedded_text) full.text = n.embedded_text;
  out.push('<details><summary>Show raw node JSON (debug)</summary><pre class="raw">'+
    escHtml(JSON.stringify(full,null,2))+"</pre></details>");
  return out.join("");
}

/* ---------- search ---------- */
var searchTimer = null;
function doSearch(q){
  var results = $("results");
  q = q.trim().toLowerCase();
  if(!q){ searchMode=false; results.classList.add("hidden"); $("tree").classList.remove("hidden"); return; }
  searchMode = true;
  var hits = [];
  for(var i=0;i<NODES.length && hits.length<60;i++){
    var n = NODES[i]; var fields = [];
    if(n.title.toLowerCase().indexOf(q)>=0) fields.push("title");
    else if(n.path.join(" → ").toLowerCase().indexOf(q)>=0) fields.push("path");
    if(n.id.toLowerCase().indexOf(q)>=0) fields.push("node id");
    if((n.conds.C.summary||"").toLowerCase().indexOf(q)>=0) fields.push("IDX-C summary");
    if((n.conds.O.summary||"").toLowerCase().indexOf(q)>=0) fields.push("IDX-O summary");
    if(n.doc!==null && DOCS[n.doc] && (DOCS[n.doc].title+" "+DOCS[n.doc].path).toLowerCase().indexOf(q)>=0) fields.push("source doc");
    if(!fields.length && n.start){
      var body = LINES.slice(n.start-1, n.own_end).join("\n").toLowerCase();
      if(body.indexOf(q)>=0) fields.push("source text");
    }
    if(fields.length) hits.push({i:i, fields:fields});
  }
  $("tree").classList.add("hidden"); results.classList.remove("hidden");
  results.innerHTML = "";
  if(!hits.length){
    results.appendChild(el("div",{class:"empty",text:"No matches for “"+q+"”. Try a shorter term — search covers titles, paths, summaries, source text, node IDs and document names."}));
    return;
  }
  hits.forEach(function(h){
    var n = NODES[h.i];
    var r = el("div",{class:"rrow",tabindex:"0",role:"button",
      onclick:function(){ select(h.i); $("search").value=""; },
      onkeydown:function(ev){ if(ev.key==="Enter"){ select(h.i); $("search").value=""; }}});
    r.appendChild(el("div",{text:n.title}));
    r.appendChild(el("div",{class:"path",text:n.path.slice(0,-1).join(" → ")||"(root)"}));
    r.appendChild(el("div",{class:"fields",text:"matched: "+h.fields.join(", ")}));
    results.appendChild(r);
  });
}

/* ---------- export / import ---------- */
function exportFlags(){
  var payload = {
    format:"pageindex-v1-review-flags", version:1,
    corpus_sha256:META.corpus.sha256,
    exported_at:new Date().toISOString(),
    flag_vocabulary:FLAG_NAMES,
    note:"Keys are node_id·pathhash review keys, stable across regeneration.",
    flags:store.flags};
  var blob = new Blob([JSON.stringify(payload,null,2)],{type:"application/json"});
  var a = el("a",{href:URL.createObjectURL(blob),download:"v1-review-flags.json"});
  document.body.appendChild(a); a.click(); a.remove();
  toast("Exported "+Object.keys(store.flags).length+" flagged node(s).");
}
function importFlags(file){
  var rd = new FileReader();
  rd.onload = function(){
    try{
      var p = JSON.parse(rd.result);
      if(!p || typeof p.flags!=="object") throw new Error("no 'flags' object found");
      if(p.corpus_sha256 && p.corpus_sha256!==META.corpus.sha256 &&
         !confirm("These flags were exported against a different corpus version. Import anyway?")) return;
      var known = {}; NODES.forEach(function(n){ known[n.key]=true; });
      var merged=0, unknown=0;
      Object.keys(p.flags).forEach(function(k){
        if(known[k]){ store.flags[k]=p.flags[k]; merged++; } else unknown++;
      });
      saveStore(); renderTree(); renderCenter();
      toast("Imported "+merged+" node(s)"+(unknown?(", "+unknown+" unknown key(s) skipped"):"")+".");
    }catch(e){ toast("Import failed: "+e.message+" — file unchanged."); }
  };
  rd.readAsText(file);
}

/* ---------- keyboard ---------- */
function visibleSequence(){
  var seq=[]; document.querySelectorAll("#tree .trow").forEach(function(r){ seq.push(+r.getAttribute("data-i")); });
  return seq;
}
function move(delta){
  var seq = visibleSequence(); if(!seq.length) return;
  var at = seq.indexOf(sel);
  var next = at<0 ? seq[0] : seq[Math.max(0,Math.min(seq.length-1,at+delta))];
  select(next);
}
function nextUnreviewed(){
  var start = sel===null? -1 : sel;
  for(var k=1;k<=NODES.length;k++){
    var i=(start+k)%NODES.length; var n=NODES[i];
    if(hasSummary(n) && !isReviewed(n)){ select(i); return; }
  }
  toast("All summary-bearing nodes reviewed 🎉");
}
document.addEventListener("keydown", function(ev){
  var tag = (ev.target.tagName||"").toLowerCase();
  if(tag==="input"||tag==="textarea"||tag==="select"){
    if(ev.key==="Escape") ev.target.blur();
    return;
  }
  if(ev.metaKey||ev.ctrlKey||ev.altKey) return;
  if(ev.key==="/"){ ev.preventDefault(); $("search").focus(); return; }
  if(ev.key==="?"){ toggleHelp(); return; }
  if(ev.key==="j"){ move(1); return; }
  if(ev.key==="k"){ move(-1); return; }
  if(ev.key==="n"){ nextUnreviewed(); return; }
  if(ev.key==="e" && sel!==null){ toggle(sel); return; }
  if(ev.key==="c"){ setActiveCond("C"); return; }
  if(ev.key==="o"){ setActiveCond("O"); return; }
  if(sel!==null && ev.key>="1" && ev.key<="6"){
    var n = NODES[sel];
    if(n.conds[activeCond].summary) toggleFlag(n, activeCond, FLAG_NAMES[+ev.key-1]);
    else toast("IDX-"+activeCond+" has no summary here to flag.");
  }
});

/* ---------- help & provenance ---------- */
function fillProvenance(){
  var kv = $("provList"); kv.innerHTML="";
  function row(k,v){ kv.appendChild(el("dt",{text:k})); kv.appendChild(el("dd",{text:v||"—"})); }
  row("Corpus", META.corpus.path+" ("+META.corpus.lines+" lines)");
  row("Corpus SHA-256", META.corpus.sha256);
  ["D","C","O"].forEach(function(c){
    row("IDX-"+c, META.indexes[c].path + (META.indexes[c].model? "  ·  "+META.indexes[c].model : ""));
    row("IDX-"+c+" SHA-256", META.indexes[c].sha256);
  });
  row("Generated", META.generated_at);
  row("Script", "render_index_comparison.py v"+META.script_version);
  row("Repo commit", META.repo_commit);
  row("PageIndex commit", (META.indexes.C||{}).pageindex_commit);
  var exact = NODES.filter(function(n){ return n.status==="exact"; }).length;
  $("helpAlign").textContent = exact+" of "+NODES.length+
    " nodes align exactly across all three indexes"+
    (exact===NODES.length? " (identical structure)":"");
}
function toggleHelp(force){
  var ov = $("overlay");
  var show = force!==undefined? force : ov.classList.contains("hidden");
  ov.classList.toggle("hidden", !show);
  if(!show){ try{ localStorage.setItem(LS_HELP,"1"); }catch(e){} }
}

/* ---------- filters init ---------- */
function initControls(){
  DOCS.forEach(function(d,i){
    $("fltDoc").appendChild(el("option",{value:String(i),text:d.title}));
  });
  var maxd = Math.max.apply(null, NODES.map(function(n){ return n.depth; }));
  for(var d=0;d<=maxd;d++) $("fltDepth").appendChild(el("option",{value:String(d),text:"≤ "+d}));
  ["fltSignals","fltSummaries","fltFlagged","fltDoc","fltDepth"].forEach(function(id){
    $(id).addEventListener("change", renderTree);
  });
  document.querySelectorAll('.tabs [role="tab"]').forEach(function(b){
    b.addEventListener("click", function(){ setTab(b.getAttribute("data-tab")); });
  });
  $("btnExpand").addEventListener("click", function(){ NODES.forEach(function(n){ if(n.children.length) expanded[n.i]=true; }); renderTree(); });
  $("btnCollapse").addEventListener("click", function(){ expanded={}; NODES.forEach(function(n){ if(n.depth===0) expanded[n.i]=true; }); renderTree(); });
  $("btnReveal").addEventListener("click", function(){ if(sel!==null) select(sel); });
  $("search").addEventListener("input", function(){
    clearTimeout(searchTimer);
    var v = this.value;
    searchTimer = setTimeout(function(){ doSearch(v); }, 160);
  });
  $("btnHelp").addEventListener("click", function(){ toggleHelp(true); });
  $("btnCloseHelp").addEventListener("click", function(){ toggleHelp(false); });
  $("provLink").addEventListener("click", function(ev){ ev.preventDefault(); toggleHelp(true); $("provPanel").open = true; });
  $("overlay").addEventListener("click", function(ev){ if(ev.target===this) toggleHelp(false); });
  $("btnExport").addEventListener("click", exportFlags);
  $("btnImport").addEventListener("click", function(){ $("importFile").click(); });
  $("importFile").addEventListener("change", function(){ if(this.files[0]) importFlags(this.files[0]); this.value=""; });
  $("btnClear").addEventListener("click", function(){
    if(confirm("Clear ALL locally stored review flags for this corpus? Export first if you want to keep them.")){
      store = {version:1, corpus_sha256:META.corpus.sha256, flags:{}};
      saveStore(); renderTree(); renderCenter(); toast("Local review flags cleared.");
    }
  });
}

/* ---------- boot ---------- */
initControls();
NODES.forEach(function(n){ if(n.depth<2) expanded[n.i]=true; });
fillProvenance();
renderCounts();
renderTree();
var deepLink = null;
var hm = /[#&]node=([^&]+)/.exec(location.hash||"");
if(hm){
  var want = decodeURIComponent(hm[1]);
  NODES.some(function(n){ if(n.id===want||n.key===want){ deepLink=n.i; return true; } return false; });
}
var tm = /[#&]tab=(src|inspect|raw)/.exec(location.hash||"");
if(tm) setTab(tm[1]);
if(deepLink!==null) select(deepLink);
var helpSeen = deepLink!==null;
try{ helpSeen = helpSeen || localStorage.getItem(LS_HELP)==="1"; }catch(e){}
if(!helpSeen) toggleHelp(true);
})();
</script>
</body>
</html>
"""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def discover_index(cond: str) -> Path:
    """Repo-default discovery: fail safely if zero or multiple candidates."""
    canonical = REPO_ROOT / "indexes" / f"IDX-{cond}" / "index.json"
    if canonical.exists():
        return canonical
    candidates = sorted((REPO_ROOT / "indexes").glob(f"IDX-{cond}*/index.json"))
    if len(candidates) == 1:
        return candidates[0]
    listing = "\n  ".join(str(c) for c in candidates) or "(none found)"
    raise SystemExit(
        f"Cannot unambiguously discover the IDX-{cond} index. "
        f"Pass --idx-{cond.lower()} explicitly. Candidates:\n  {listing}")


def parse_args(argv: list | None = None) -> argparse.Namespace:
    ap = argparse.ArgumentParser(
        description="Render the V1 Index Comparison Explorer "
                    "(HTML + outlines + alignment report).")
    ap.add_argument("--idx-d", type=Path, help="Path to IDX-D index.json")
    ap.add_argument("--idx-c", type=Path, help="Path to IDX-C index.json")
    ap.add_argument("--idx-o", type=Path, help="Path to IDX-O index.json")
    ap.add_argument("--corpus", type=Path,
                    default=REPO_ROOT / "corpus/site-book-v1/site-book-v1.md")
    ap.add_argument("--manifest", type=Path, default=None,
                    help="Corpus manifest JSON (default: alongside corpus)")
    ap.add_argument("--output", type=Path,
                    default=REPO_ROOT / "reports/V1_INDEX_COMPARISON.html")
    ap.add_argument("--outline-dir", type=Path,
                    default=REPO_ROOT / "reports/index-outlines")
    ap.add_argument("--alignment-report", type=Path,
                    default=REPO_ROOT / "reports/V1_INDEX_ALIGNMENT_REPORT.md")
    ap.add_argument("--title", default="PageIndex V1 — Index Comparison Explorer")
    ap.add_argument("--overwrite", action="store_true",
                    help="Allow overwriting existing outputs")
    return ap.parse_args(argv)


def main(argv: list | None = None) -> int:
    args = parse_args(argv)
    paths = {
        "D": args.idx_d or discover_index("D"),
        "C": args.idx_c or discover_index("C"),
        "O": args.idx_o or discover_index("O"),
        "corpus": args.corpus,
    }
    manifest = args.manifest
    if manifest is None:
        cand = args.corpus.parent / (args.corpus.stem + ".manifest.json")
        manifest = cand if cand.exists() else None
    paths["manifest"] = manifest

    for key in ("D", "C", "O", "corpus"):
        if not paths[key].exists():
            raise SystemExit(f"Input not found: {paths[key]}")

    outputs = [args.output, args.alignment_report] + [
        args.outline_dir / f"IDX-{c}.md" for c in CONDITIONS]
    if not args.overwrite:
        existing = [str(p) for p in outputs if p.exists()]
        if existing:
            raise SystemExit(
                "Refusing to overwrite existing outputs (pass --overwrite):\n  "
                + "\n  ".join(existing))

    model = build_model(paths, args.title)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.outline_dir.mkdir(parents=True, exist_ok=True)
    args.alignment_report.parent.mkdir(parents=True, exist_ok=True)

    args.output.write_text(build_html(model), encoding="utf-8")
    for c in CONDITIONS:
        (args.outline_dir / f"IDX-{c}.md").write_text(
            build_outline(model, c), encoding="utf-8")
    args.alignment_report.write_text(build_alignment_report(model),
                                     encoding="utf-8")

    nodes = model["nodes"]
    exact = sum(1 for e in nodes if e["status"] == "exact")
    size = args.output.stat().st_size
    print(f"Wrote {args.output} ({size/1024:.0f} KB)")
    print(f"  nodes: {len(nodes)}  exact: {exact}  "
          f"unmatched extras: {len(model['extras'])}")
    print(f"Wrote outlines to {args.outline_dir}/IDX-{{D,C,O}}.md")
    print(f"Wrote {args.alignment_report}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

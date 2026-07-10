#!/usr/bin/env python3
"""Merge several retrieval runs into one combined comparison table.

Useful when the full (index x retriever) grid is split across run folders — e.g. a
retriever that failed (quota/error) in one run but succeeded (as a different condition)
in another. Rows are keyed by (index, retriever, question); when the same cell appears
more than once, a NON-error row wins over an error row, and the newest wins otherwise.

Usage:
  python3 scripts/compare_runs.py runs/<tsA> runs/<tsB> runs/<tsC>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main(dirs: list[str]) -> int:
    cells: dict[tuple, dict] = {}
    for d in dirs:
        rj = Path(d) / "run.json"
        if not rj.exists():
            print(f"skip {d} (no run.json)"); continue
        rec = json.loads(rj.read_text())
        for r in rec["results"]:
            key = (r.get("index_id"), r["retriever"], r["qid"])
            prev = cells.get(key)
            # prefer a non-error row; otherwise keep first seen
            if prev is None or (prev.get("error") and not r.get("error")):
                cells[key] = r

    combos: dict[tuple, list] = {}
    for (idx, ret, _qid), r in cells.items():
        combos.setdefault((idx, ret), []).append(r)

    print("| Index | Retriever | n_ok | n_err | tools | struct_tok | content_tok | total_tok | $ | s |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    for (idx, ret) in sorted(combos):
        rows = combos[(idx, ret)]
        ok = [r for r in rows if not r.get("error")]
        n_err = len(rows) - len(ok)
        if not ok:
            print(f"| {idx} | {ret.split('/')[-1]} | 0 | {n_err} | — | — | — | — | — | — |"); continue
        n = len(ok)
        avg = lambda k: round(sum(r[k] for r in ok) / n, 1)
        tt = round(sum(r["usage"].get("total_tokens", 0) for r in ok) / n)
        cost = round(sum(r["est_cost_usd"] or 0 for r in ok), 4)
        print(f"| {idx} | {ret.split('/')[-1]} | {n} | {n_err} | {avg('n_tool_calls')} | "
              f"{avg('structure_tokens')} | {avg('content_tokens')} | {tt} | {cost} | {avg('latency_seconds')} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

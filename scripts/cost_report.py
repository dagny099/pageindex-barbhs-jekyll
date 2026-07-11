#!/usr/bin/env python3
"""cost_report.py — read runs/usage_log.jsonl and report per-call token cost.

Two views, both driven off the per-call rows written by usage_logging.record_usage:

  1. Per-condition totals (index x retriever): full-price input / cache_read /
     cache_write / output tokens and USD. This is where the "caching cut cost by
     X%" number comes from — compare a caching-ON run to a caching-OFF run.
  2. Re-send amplification: for each question thread, input tokens by call_idx.
     The index TREE is a tool result that persists in context and is re-billed as
     input every turn, so input_tokens CLIMBS across call_idx — until caching is
     on, at which point cache_read_tokens picks it up instead. This view makes
     that dynamic visible per call rather than hidden in an aggregate.

Also reconciles: it recomputes each row's cost from its own tokens (via
usage_logging.cost_for) and flags any drift from the logged cost_usd, so the
report can't silently disagree with the JSONL.

Usage:
  python3 scripts/cost_report.py                          # all rows in runs/usage_log.jsonl
  python3 scripts/cost_report.py --run 20260710T120000Z   # one run only
  python3 scripts/cost_report.py --log path/to/log.jsonl --no-amplify
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))  # so `import usage_logging` works
from usage_logging import cost_for

REPO = Path(__file__).resolve().parents[1]
DEFAULT_LOG = REPO / "runs" / "usage_log.jsonl"


def load_rows(log_path: Path, run_id: str | None) -> list[dict]:
    if not log_path.exists():
        raise SystemExit(f"No usage log at {log_path}. Run a retrieval first (scripts/run_retrieval.py).")
    rows = []
    for i, line in enumerate(log_path.read_text().splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError as e:
            print(f"  [warn] skipping malformed line {i}: {e}", file=sys.stderr)
            continue
        if run_id and rec.get("run_id") != run_id:
            continue
        rows.append(rec)
    if not rows:
        raise SystemExit(f"No rows{' for run ' + run_id if run_id else ''} in {log_path}.")
    return rows


def _c(n) -> str:
    """Comma-group an int for readability."""
    return f"{int(n):,}"


def per_condition(rows: list[dict]) -> None:
    # Group by (index, retriever). Track distinct questions and per-call sums.
    agg: dict[tuple, dict] = defaultdict(lambda: {
        "calls": 0, "qids": set(),
        "input": 0, "cache_read": 0, "cache_write": 0, "output": 0, "cost": 0.0,
    })
    for r in rows:
        a = agg[(r["index"], r["retriever"])]
        a["calls"] += 1
        a["qids"].add(r["qid"])
        a["input"] += r.get("input_tokens", 0)
        a["cache_read"] += r.get("cache_read_tokens", 0)
        a["cache_write"] += r.get("cache_creation_tokens", 0)
        a["output"] += r.get("output_tokens", 0)
        a["cost"] += r.get("cost_usd", 0.0)

    hdr = f"{'index':<7} {'retriever':<32} {'qs':>3} {'calls':>5} " \
          f"{'input':>12} {'cache_read':>12} {'cache_write':>12} {'output':>10} {'cost_usd':>10}"
    print("=== Per-condition totals (index × retriever) ===")
    print(hdr)
    print("-" * len(hdr))
    grand = 0.0
    for (index, retr), a in sorted(agg.items()):
        grand += a["cost"]
        print(f"{index:<7} {retr:<32} {len(a['qids']):>3} {a['calls']:>5} "
              f"{_c(a['input']):>12} {_c(a['cache_read']):>12} {_c(a['cache_write']):>12} "
              f"{_c(a['output']):>10} {'$'+format(a['cost'],'.4f'):>10}")
    print("-" * len(hdr))
    print(f"{'TOTAL':<7} {'':<32} {'':>3} {sum(a['calls'] for a in agg.values()):>5} "
          f"{'':>12} {'':>12} {'':>12} {'':>10} {'$'+format(grand,'.4f'):>10}")
    print()


def amplification(rows: list[dict]) -> None:
    # Group rows into question threads: (run_id, index, retriever, qid) -> [rows by call_idx].
    threads: dict[tuple, list[dict]] = defaultdict(list)
    for r in rows:
        threads[(r["run_id"], r["index"], r["retriever"], r["qid"])].append(r)

    print("=== Re-send amplification (input tokens by call_idx) ===")
    print("Input climbs as the tree is re-sent each turn; cache_read replaces it once caching is on.\n")
    for (run_id, index, retr, qid), thread in sorted(threads.items()):
        thread.sort(key=lambda r: r.get("call_idx", 0))
        print(f"[{run_id} | {index} | {retr} | {qid}]")
        print(f"  {'call':>4} {'phase':<13} {'input':>10} {'cache_read':>11} {'cache_write':>11} {'cost_usd':>10}")
        for r in thread:
            print(f"  {r.get('call_idx',0):>4} {r.get('phase',''):<13} "
                  f"{_c(r.get('input_tokens',0)):>10} {_c(r.get('cache_read_tokens',0)):>11} "
                  f"{_c(r.get('cache_creation_tokens',0)):>11} "
                  f"{'$'+format(r.get('cost_usd',0.0),'.5f'):>10}")
        print()


def reconcile(rows: list[dict]) -> None:
    """Recompute each row's cost from its own tokens and flag drift vs logged cost."""
    logged = sum(r.get("cost_usd", 0.0) for r in rows)
    recomputed = 0.0
    mismatches = 0
    for r in rows:
        try:
            c = cost_for(r["retriever"], r.get("input_tokens", 0), r.get("output_tokens", 0),
                         r.get("cache_read_tokens", 0), r.get("cache_creation_tokens", 0))
        except KeyError:
            # Unpriced model in the log — can't reconcile this row; note and skip.
            print(f"  [warn] no price for {r['retriever']!r}; row not reconciled", file=sys.stderr)
            recomputed += r.get("cost_usd", 0.0)
            continue
        recomputed += c
        if abs(round(c, 6) - r.get("cost_usd", 0.0)) > 1e-6:
            mismatches += 1
            if mismatches <= 5:
                print(f"  [drift] {r['run_id']}/{r['index']}/{r['retriever']}/{r['qid']} "
                      f"call {r.get('call_idx')}: logged ${r.get('cost_usd')} vs recomputed ${round(c,6)}",
                      file=sys.stderr)
    tick = "✓" if abs(round(logged, 4) - round(recomputed, 4)) < 1e-4 and mismatches == 0 else "✗"
    print(f"Reconciliation: logged ${logged:.4f} vs recomputed ${recomputed:.4f}  "
          f"[{mismatches} row mismatch(es)] {tick}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--log", type=Path, default=DEFAULT_LOG, help="path to usage_log.jsonl")
    ap.add_argument("--run", default=None, help="filter to one run_id")
    ap.add_argument("--no-amplify", action="store_true", help="skip the per-call amplification view")
    args = ap.parse_args()

    rows = load_rows(args.log, args.run)
    print(f"Loaded {len(rows)} call rows from {args.log}"
          f"{' (run ' + args.run + ')' if args.run else ''}\n")
    per_condition(rows)
    if not args.no_amplify:
        amplification(rows)
    reconcile(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

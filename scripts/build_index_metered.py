#!/usr/bin/env python3
"""
build_index_metered.py — metered PageIndex tree generation (PDF or Markdown).

WHY THIS EXISTS
---------------
runs/usage_log.jsonl only captured RETRIEVAL (scripts/run_retrieval.py); index
GENERATION — the dominant spend on long documents — was a telemetry blind spot.
This driver closes it: it wraps litellm.completion / litellm.acompletion (the
two functions every vendored PageIndex LLM call goes through —
vendor/PageIndex/pageindex/utils.py:33,63) and records one usage_logging row per
call with phase="index_build". The vendor submodule is never modified.

WHY A WRAPPER, NOT A LITELLM CALLBACK
-------------------------------------
LiteLLM fires async success callbacks as fire-and-forget tasks; page_index_main
closes its own event loop (asyncio.run at page_index.py:1102), so tail rows
would be lost — the exact failure mode documented in run_retrieval.py's
make_litellm_usage_collector. Wrapping captures usage synchronously inside the
await chain: lossless, and per-call latency comes for free. Only SUCCESSFUL
calls are recorded; a call that errors after generating tokens is invisible
(rare, and PageIndex's own retry loop hides it from every layer).

PRE-FLIGHT DISCIPLINE (brief §4.2 — reports/project-brief-2026-07-13-long-doc-corpora.md)
------------------------------------------------------------------------------------------
Before spending, the script prints a cost estimate and asks for confirmation
(skip with --yes). Markdown estimates are near-exact (summary calls = nodes over
--summary-token-threshold, computed deterministically); PDF estimates use the
2-4x input-pass rule of thumb. During the run, spend is compared to an abort
bound (default 2x the high estimate); crossing it raises KeyboardInterrupt,
which PageIndex's `except Exception` retry loops cannot swallow.

USAGE (from the repo root, so dotenv finds .env)
------------------------------------------------
  .venv/bin/python scripts/build_index_metered.py --pdf_path sources/rfc9110/rfc9110.pdf
  .venv/bin/python scripts/build_index_metered.py --md_path corpus/paper-book-v1-clean/paper-book-v1-clean.md \
      --if-add-node-summary yes --summary-token-threshold 0 --index-label IDX-C0-paper
  .venv/bin/python scripts/build_index_metered.py --self-test    # offline, no API calls

Output tree goes to results/<stem>_structure.json (gitignored scratch) unless
--out is given; curate keepers into indexes/IDX-*/ by hand as usual. Afterwards:
  python3 scripts/cost_report.py --run <run_id>
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import threading
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))            # usage_logging
sys.path.insert(0, str(REPO / "vendor" / "PageIndex"))  # pageindex (vendored)

from usage_logging import PRICES, cost_for, from_litellm_usage, normalize_model, record_usage

DEFAULT_LOG = REPO / "runs" / "usage_log.jsonl"
SUMMARY_PROMPT_OVERHEAD = 60   # tokens of instruction wrapping around node text
SUMMARY_OUTPUT_TOKENS = 80     # typical generated-summary length


# --------------------------------------------------------------------------
# Metering: wrap litellm at the module level (vendor code looks the functions
# up at call time, so patching the attributes is sufficient and reversible).
# --------------------------------------------------------------------------

class Meter:
    """Accumulates per-call usage; writes one usage_logging row per LLM call."""

    def __init__(self, *, run_id: str, qid: str, index: str, fallback_model: str,
                 log_path: str, abort_usd: float | None):
        self.run_id, self.qid, self.index = run_id, qid, index
        self.fallback_model = fallback_model
        self.log_path = log_path
        self.abort_usd = abort_usd
        self.rows = []
        self.total_usd = 0.0
        self._lock = threading.Lock()  # sync calls may arrive from worker threads

    def capture(self, response, model: str | None, latency_s: float) -> None:
        try:
            usage = from_litellm_usage(getattr(response, "usage", None) or {})
            with self._lock:
                row = record_usage(
                    usage, run_id=self.run_id, qid=self.qid, index=self.index,
                    retriever=model or self.fallback_model, call_idx=len(self.rows),
                    phase="index_build", latency_s=round(latency_s, 3),
                    log_path=self.log_path, source="litellm",
                )
                self.rows.append(row)
                self.total_usd += row.cost_usd
                total = self.total_usd
        except Exception as e:  # never let logging break a build
            print(f"  [usage-log] capture failed ({type(e).__name__}: {e})")
            return
        if self.abort_usd and total > self.abort_usd:
            # KeyboardInterrupt (a BaseException) escapes PageIndex's
            # `except Exception` retry loops; a normal exception would be
            # retried up to 10 times and then swallowed.
            print(f"\n!! ABORT: metered spend ${total:.2f} exceeded bound "
                  f"${self.abort_usd:.2f} after {len(self.rows)} calls. "
                  f"Partial usage rows are in {self.log_path} (run_id {self.run_id}).")
            raise KeyboardInterrupt("cost abort bound exceeded")

    def summary(self) -> dict:
        f = lambda name: sum(getattr(r, name) for r in self.rows)
        return {
            "calls": len(self.rows),
            "input_tokens": f("input_tokens"),
            "output_tokens": f("output_tokens"),
            "cache_read_tokens": f("cache_read_tokens"),
            "cache_creation_tokens": f("cache_creation_tokens"),
            "cost_usd": round(self.total_usd, 4),
        }


def install_meter(litellm_module, meter: Meter) -> None:
    orig_sync = litellm_module.completion
    orig_async = litellm_module.acompletion

    def completion(*args, **kwargs):
        t0 = time.perf_counter()
        resp = orig_sync(*args, **kwargs)
        meter.capture(resp, kwargs.get("model"), time.perf_counter() - t0)
        return resp

    async def acompletion(*args, **kwargs):
        t0 = time.perf_counter()
        resp = await orig_async(*args, **kwargs)
        meter.capture(resp, kwargs.get("model"), time.perf_counter() - t0)
        return resp

    litellm_module.completion = completion
    litellm_module.acompletion = acompletion


# --------------------------------------------------------------------------
# Pre-flight estimation (brief §4.2)
# --------------------------------------------------------------------------

def _encoding(model: str):
    import tiktoken
    try:
        return tiktoken.encoding_for_model(normalize_model(model))
    except KeyError:
        return tiktoken.get_encoding("o200k_base")


def estimate_md(md_text: str, threshold: int, model: str,
                summaries: bool) -> dict:
    """Near-exact: PageIndex's markdown structure pass is deterministic (free);
    only nodes whose text reaches `threshold` tokens trigger a summary call
    (page_index_md.get_node_summary — below it, text is copied verbatim)."""
    enc = _encoding(model)
    sections, current = [], []
    for line in md_text.splitlines():
        if line.startswith("#"):
            sections.append("\n".join(current))
            current = []
        current.append(line)
    sections.append("\n".join(current))
    tok = [len(enc.encode(s)) for s in sections if s.strip()]
    if not summaries:
        return {"kind": "md", "calls": 0, "in_low": 0, "in_high": 0,
                "out_low": 0, "out_high": 0, "doc_tokens": sum(tok)}
    over = [t for t in tok if t >= threshold]
    calls = len(over)
    est_in = sum(over) + calls * SUMMARY_PROMPT_OVERHEAD
    return {"kind": "md", "calls": calls, "doc_tokens": sum(tok),
            "in_low": est_in, "in_high": est_in,
            "out_low": calls * SUMMARY_OUTPUT_TOKENS,
            "out_high": calls * SUMMARY_OUTPUT_TOKENS}


def estimate_pdf(pdf_path: str, model: str) -> dict:
    """Rule of thumb (calibrate with metered pilots): TOC detection +
    verification + node-text re-send for summaries pass the document through
    as input ~2-4x; output runs ~10-20% of input."""
    import fitz
    enc = _encoding(model)
    doc = fitz.open(pdf_path)
    doc_tokens = sum(len(enc.encode(p.get_text())) for p in doc)
    return {"kind": "pdf", "calls": None, "doc_tokens": doc_tokens,
            "in_low": 2 * doc_tokens, "in_high": 4 * doc_tokens,
            "out_low": int(0.10 * 2 * doc_tokens),
            "out_high": int(0.20 * 4 * doc_tokens)}


def priced(model: str, in_tok: int, out_tok: int) -> float | None:
    try:
        return cost_for(model, in_tok, out_tok)
    except KeyError:
        return None


# --------------------------------------------------------------------------
# Build
# --------------------------------------------------------------------------

def run_build(args) -> None:
    import litellm
    from pageindex.page_index import page_index_main
    from pageindex.page_index_md import md_to_tree
    from pageindex.utils import ConfigLoader

    src = Path(args.pdf_path or args.md_path)
    if not src.is_file():
        raise SystemExit(f"source file not found: {src}")

    user_opt = {k: v for k, v in {
        "model": args.model,
        "toc_check_page_num": args.toc_check_pages,
        "max_page_num_each_node": args.max_pages_per_node,
        "max_token_num_each_node": args.max_tokens_per_node,
        "if_add_node_id": args.if_add_node_id,
        "if_add_node_summary": args.if_add_node_summary,
        "if_add_doc_description": args.if_add_doc_description,
        "if_add_node_text": args.if_add_node_text,
    }.items() if v is not None}
    opt = ConfigLoader().load(user_opt)
    model = opt.model
    summaries_on = opt.if_add_node_summary == "yes"

    # ---- pre-flight estimate (free, deterministic) ----
    if args.pdf_path:
        est = estimate_pdf(args.pdf_path, model)
    else:
        est = estimate_md(src.read_text(encoding="utf-8"),
                          args.summary_token_threshold, model, summaries_on)
    lo = priced(model, est["in_low"], est["out_low"])
    hi = priced(model, est["in_high"], est["out_high"])

    out_path = Path(args.out) if args.out else REPO / "results" / f"{src.stem}_structure.json"
    if out_path.exists() and not args.overwrite:
        raise SystemExit(f"{out_path} exists; pass --overwrite to replace it")

    run_id = args.run_id or time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    print(f"run_id: {run_id}")
    print(f"source: {src}  ({est['doc_tokens']:,} tokens)")
    print(f"model:  {model}   summaries: {opt.if_add_node_summary}   "
          f"doc-description: {opt.if_add_doc_description}")
    if est["kind"] == "md":
        print(f"estimate (near-exact): {est['calls']} summary calls, "
              f"~{est['in_high']:,} input / ~{est['out_high']:,} output tokens")
    else:
        print(f"estimate (2-4x rule of thumb): {est['in_low']:,}-{est['in_high']:,} input / "
              f"{est['out_low']:,}-{est['out_high']:,} output tokens")
    if hi is not None:
        print(f"estimated cost: ${lo:.2f} - ${hi:.2f}")
    else:
        print(f"estimated cost: UNKNOWN — {normalize_model(model)!r} is not in "
              f"usage_logging.PRICES; rows will fail to cost. Add it first.")
        if not args.yes:
            raise SystemExit("refusing to run an unpriceable model without --yes")

    if args.abort_over == -1:
        abort_usd = round(2 * hi, 2) if hi else None
    else:
        abort_usd = args.abort_over or None
    print(f"abort bound: {'$%.2f' % abort_usd if abort_usd else 'DISABLED'}")

    if not args.yes:
        if input("Proceed with the paid build? [y/N] ").strip().lower() != "y":
            raise SystemExit("aborted before any spend")

    # ---- metered build ----
    meter = Meter(run_id=run_id, qid=src.stem, index=args.index_label,
                  fallback_model=model, log_path=str(args.log),
                  abort_usd=abort_usd)
    install_meter(litellm, meter)

    t0 = time.perf_counter()
    if args.pdf_path:
        result = page_index_main(str(src), opt)
    else:
        result = asyncio.run(md_to_tree(
            md_path=str(src),
            if_thinning=args.if_thinning.lower() == "yes",
            min_token_threshold=args.thinning_threshold,
            if_add_node_summary=opt.if_add_node_summary,
            summary_token_threshold=args.summary_token_threshold,
            model=opt.model,
            if_add_doc_description=opt.if_add_doc_description,
            if_add_node_text=opt.if_add_node_text,
            if_add_node_id=opt.if_add_node_id,
        ))
    elapsed = time.perf_counter() - t0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    # ---- reconcile against the estimate ----
    s = meter.summary()
    print(f"\ntree written to: {out_path}")
    print(f"build time: {elapsed:.1f}s   LLM calls: {s['calls']}")
    print(f"tokens: {s['input_tokens']:,} in / {s['output_tokens']:,} out"
          + (f" / {s['cache_read_tokens']:,} cache-read" if s["cache_read_tokens"] else "")
          + (f" / {s['cache_creation_tokens']:,} cache-write" if s["cache_creation_tokens"] else ""))
    print(f"metered cost: ${s['cost_usd']:.4f}")
    if hi and hi > 0:
        print(f"realized/estimated(high): {s['cost_usd'] / hi:.2f} "
              f"(brief §4.2 step 5: scale up only if <= ~1.5; record this ratio)")
    print(f"rows appended to {args.log} — verify with: "
          f"python3 scripts/cost_report.py --run {run_id}")


# --------------------------------------------------------------------------
# Offline self-test (no API calls, no network)
# --------------------------------------------------------------------------

def self_test() -> None:
    import tempfile
    from types import SimpleNamespace as NS

    failures = []

    def check(name, got, want):
        ok = got == want
        print(f"  {'PASS' if ok else 'FAIL'}: {name} (got {got!r}, want {want!r})")
        if not ok:
            failures.append(name)

    # 1. Meter.capture writes a correctly costed row from a litellm-shaped usage.
    with tempfile.TemporaryDirectory() as td:
        log = str(Path(td) / "log.jsonl")
        meter = Meter(run_id="TEST", qid="doc", index="IDX-TEST",
                      fallback_model="gpt-4o-2024-11-20", log_path=log, abort_usd=None)
        usage = NS(prompt_tokens=1000, completion_tokens=100,
                   prompt_tokens_details=NS(cached_tokens=0))
        meter.capture(NS(usage=usage), "gpt-4o-2024-11-20", 0.5)
        row = json.loads(Path(log).read_text().splitlines()[0])
        check("row input_tokens", row["input_tokens"], 1000)
        check("row phase", row["phase"], "index_build")
        check("row cost", row["cost_usd"], round((1000 * 2.50 + 100 * 10.00) / 1e6, 5))

        # 2. Abort bound raises KeyboardInterrupt (escapes vendor retry loops).
        meter.abort_usd = 0.004
        try:
            meter.capture(NS(usage=usage), "gpt-4o-2024-11-20", 0.5)
            check("abort raised", False, True)
        except KeyboardInterrupt:
            check("abort raised", True, True)

    # 3. Wrapper intercepts sync and async litellm entry points losslessly.
    fake = NS(usage=NS(prompt_tokens=10, completion_tokens=2,
                       prompt_tokens_details=NS(cached_tokens=0)))
    lite = NS(completion=lambda **kw: fake,
              acompletion=None)
    async def _acomp(**kw):
        return fake
    lite.acompletion = _acomp
    with tempfile.TemporaryDirectory() as td:
        log = str(Path(td) / "log.jsonl")
        meter = Meter(run_id="TEST", qid="doc", index="IDX-TEST",
                      fallback_model="gpt-4o-2024-11-20", log_path=log, abort_usd=None)
        install_meter(lite, meter)
        lite.completion(model="gpt-4o-2024-11-20", messages=[])
        asyncio.run(lite.acompletion(model="gpt-4o-2024-11-20", messages=[]))
        check("wrapper captured both calls", len(meter.rows), 2)
        check("call_idx increments", meter.rows[1].call_idx, 1)

    # 4. Markdown estimator: only over-threshold sections cost a call.
    md = "# Big\n" + ("word " * 400) + "\n## Small\ntiny\n"
    est = estimate_md(md, threshold=200, model="gpt-4o-2024-11-20", summaries=True)
    check("md estimator call count", est["calls"], 1)
    est_off = estimate_md(md, threshold=200, model="gpt-4o-2024-11-20", summaries=False)
    check("md estimator summaries-off", est_off["calls"], 0)

    if failures:
        raise SystemExit(f"self-test FAILED: {failures}")
    print("self-test OK")


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[1],
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--pdf_path", type=str, help="Path to the PDF file")
    p.add_argument("--md_path", type=str, help="Path to the Markdown file")
    p.add_argument("--model", type=str, default=None, help="Overrides config.yaml")
    p.add_argument("--toc-check-pages", type=int, default=None)
    p.add_argument("--max-pages-per-node", type=int, default=None)
    p.add_argument("--max-tokens-per-node", type=int, default=None)
    p.add_argument("--if-add-node-id", type=str, default=None)
    p.add_argument("--if-add-node-summary", type=str, default=None)
    p.add_argument("--if-add-doc-description", type=str, default=None)
    p.add_argument("--if-add-node-text", type=str, default=None)
    p.add_argument("--if-thinning", type=str, default="no", help="markdown only")
    p.add_argument("--thinning-threshold", type=int, default=5000, help="markdown only")
    p.add_argument("--summary-token-threshold", type=int, default=200,
                   help="markdown only; 0 = LLM summary for every node")
    p.add_argument("--index-label", type=str, default=None,
                   help="`index` column in usage rows (default BUILD-<stem>)")
    p.add_argument("--run-id", type=str, default=None, help="default: UTC timestamp")
    p.add_argument("--out", type=str, default=None,
                   help="output JSON (default results/<stem>_structure.json)")
    p.add_argument("--overwrite", action="store_true")
    p.add_argument("--yes", action="store_true", help="skip the pre-flight confirmation")
    p.add_argument("--abort-over", type=float, default=-1,
                   help="hard-stop the build past this USD spend; "
                        "-1 = auto (2x high estimate), 0 = disabled")
    p.add_argument("--log", type=str, default=str(DEFAULT_LOG))
    p.add_argument("--self-test", action="store_true",
                   help="offline checks of metering, abort, and estimators")
    args = p.parse_args()

    if args.self_test:
        self_test()
        return
    if bool(args.pdf_path) == bool(args.md_path):
        p.error("exactly one of --pdf_path / --md_path is required")
    if args.index_label is None:
        args.index_label = f"BUILD-{Path(args.pdf_path or args.md_path).stem}"
    run_build(args)


if __name__ == "__main__":
    main()

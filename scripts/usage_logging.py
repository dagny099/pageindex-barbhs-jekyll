"""
usage_logging.py — per-call token & cost capture for the PageIndex experiment.

WHY THIS EXISTS
---------------
Agentic retrieval makes N LLM calls per question (get_document_structure ->
reason -> get_page_content -> ... -> answer). The dominant cost is the index
TREE, which is a tool result that stays in context and is re-billed as INPUT
on every subsequent turn. `content_tokens` in the current logs captures only
the fetched payload, not this re-sent navigation context — so it undercounts
the bill by an order of magnitude and can't be split into input/output.

The fix is not a better estimator. Every provider already returns exact usage
on each response. Capture it per call, tagged with the run identity, and cost
becomes exact AND granular (you can see the amplification turn by turn).

PROVIDER TOKEN SEMANTICS (the subtle, load-bearing part)
--------------------------------------------------------
The two providers define the input-token field DIFFERENTLY, so a single naive
`billable = input - cache_read` is wrong for one of them:

  - OpenAI (Chat Completions `prompt_tokens`, and the OpenAI-Responses /
    Agents-SDK `input_tokens`): the input count is the TOTAL, and `cached_tokens`
    (nested under `*_tokens_details`) is a SUBSET of it.
    Full-price input = input_total - cached.
  - Anthropic (`input_tokens`): already the UNCACHED remainder —
    `cache_read_input_tokens` and `cache_creation_input_tokens` are reported
    SEPARATELY and are NOT included in `input_tokens`. Full-price input =
    `input_tokens` as-is (subtracting cache_read again double-counts the
    discount — the original draft did exactly that and under-billed Anthropic).

`record_usage()` discriminates by field shape (a top-level
`cache_read_input_tokens` / `cache_creation_input_tokens` => Anthropic remainder
convention; otherwise nested `cached_tokens` => OpenAI total convention) and
normalizes both into one canonical shape before costing.

CACHE WRITE PREMIUM
-------------------
The first turn WRITES the ~40K-token tree to cache. Anthropic bills that write
at 1.25x input (5-min TTL) / 2x (1h). OpenAI charges no write premium (the write
is just normal input tokens; only reads are discounted). `cache_creation_tokens`
is logged separately and priced at `cache_write`; ignoring it undercounts the
single most expensive event in the run. See reports/COST_NOTES.md.

DESIGN NOTES (maintainability)
------------------------------
- PRICES is the single source of truth. Update it in one place.
- Model names are normalized (litellm prefixes like `anthropic/`,
  `ollama_chat/` stripped) so retriever strings key into PRICES.
- The log is append-only JSONL — safe to tail during a run, trivial to load
  into pandas afterwards, and never rewrites prior rows.
- `python3 scripts/usage_logging.py` runs an offline self-test of the
  provider-semantics normalization and the cache-write pricing (no API calls).
"""

from __future__ import annotations
import json, os, time
from dataclasses import dataclass, asdict
from typing import Any

# --- Single source of truth: USD per 1e6 tokens (verified 2026-07-10) ---------
# cache_read : discounted reuse rate  (OpenAI cached input = 0.5x in; Anthropic cache read = 0.1x in)
# cache_write: FIRST-write premium    (OpenAI none -> = in; Anthropic 5-min TTL = 1.25x in, 1h = 2x)
PRICES = {
    # The three V1 conditions carry explicit cache rates (used with prompt caching).
    "gpt-4o-2024-11-20":          {"in": 2.50, "out": 10.00, "cache_read": 1.25, "cache_write": 2.50},
    "claude-sonnet-4-5":          {"in": 3.00, "out": 15.00, "cache_read": 0.30, "cache_write": 3.75},
    # local / self-hosted: no API charge. Latency is the real cost — logged separately.
    "qwen2.5-7b-instruct-ctx32k": {"in": 0.00, "out": 0.00,  "cache_read": 0.00, "cache_write": 0.00},
    # Other retrievers the harness may run. `in`/`out` only: cache_read / cache_write
    # fall back to full input price (no discount) — set them explicitly if a model
    # is ever run *with* caching so cache accounting stays exact.
    "gpt-4o":                     {"in": 2.50, "out": 10.00, "cache_read": 1.25, "cache_write": 2.50},
    "gpt-4o-mini":                {"in": 0.15, "out": 0.60},
    "gpt-4.1":                    {"in": 2.00, "out": 8.00},
    "gpt-4.1-mini":               {"in": 0.40, "out": 1.60},
    "claude-3-5-sonnet-latest":   {"in": 3.00, "out": 15.00, "cache_read": 0.30, "cache_write": 3.75},
}

# litellm prefixes the model with its provider (e.g. "anthropic/claude-sonnet-4-5",
# "ollama_chat/qwen2.5-7b-instruct-ctx32k"); strip it so the string keys into PRICES.
_LITELLM_PROVIDER_PREFIXES = (
    "anthropic/", "openai/", "ollama_chat/", "ollama/",
    "gemini/", "vertex_ai/", "bedrock/", "azure/",
)

LOG_PATH = os.environ.get("USAGE_LOG", "runs/usage_log.jsonl")


def normalize_model(name: str) -> str:
    """Strip a leading litellm provider prefix so `anthropic/claude-sonnet-4-5`
    and `ollama_chat/qwen2.5-...` resolve to their PRICES keys."""
    for pre in _LITELLM_PROVIDER_PREFIXES:
        if name.startswith(pre):
            return name[len(pre):]
    return name


@dataclass
class CallUsage:
    run_id: str            # one experiment run (index x retriever)
    qid: str               # question id, e.g. "CS6"
    index: str             # IDX-D / IDX-C / IDX-O
    retriever: str         # model string as invoked (may carry a litellm prefix)
    call_idx: int          # 0-based position in the agentic loop
    phase: str             # "structure" | "page_content" | "answer" | "other"
    input_tokens: int          # FULL-PRICE (uncached) input; total prompt = input + cache_read + cache_creation
    output_tokens: int
    cache_read_tokens: int     # served from cache (billed at cache_read)
    cache_creation_tokens: int # written to cache this call (billed at cache_write; ~always the tree, turn 0)
    latency_s: float
    cost_usd: float


def _get(u: Any, *names, default=0) -> int:
    """Read the first present attribute/key from a usage object or dict."""
    for n in names:
        if isinstance(u, dict) and n in u and u[n] is not None:
            return int(u[n])
        if hasattr(u, n) and getattr(u, n) is not None:
            return int(getattr(u, n))
    return default


def _nested_cached(u: Any) -> int:
    """OpenAI reports cache hits as `cached_tokens` nested under
    `prompt_tokens_details` (Chat Completions) or `input_tokens_details`
    (Responses / Agents SDK). Read either shape, attr or dict."""
    for attr in ("prompt_tokens_details", "input_tokens_details"):
        details = getattr(u, attr, None)
        if details is None and isinstance(u, dict):
            details = u.get(attr)
        if details is not None:
            c = _get(details, "cached_tokens")
            if c:
                return c
    return 0


def cost_for(retriever: str, input_tokens: int, output_tokens: int,
             cache_read_tokens: int = 0, cache_creation_tokens: int = 0) -> float:
    """Cost from CANONICAL, already-normalized token counts:
    `input_tokens` is the full-price (uncached) input — do NOT pass a total that
    still includes cached tokens (record_usage does the splitting)."""
    p = PRICES.get(normalize_model(retriever))
    if not p:
        raise KeyError(f"No price for {retriever!r} (normalized {normalize_model(retriever)!r}); add it to PRICES.")
    return (input_tokens * p["in"]
            + cache_creation_tokens * p.get("cache_write", p["in"])
            + cache_read_tokens * p.get("cache_read", p["in"])
            + output_tokens * p["out"]) / 1e6


def record_usage(response: Any, *, run_id: str, qid: str, index: str,
                 retriever: str, call_idx: int, phase: str,
                 latency_s: float, log_path: str = LOG_PATH) -> CallUsage:
    """
    Call this once per LLM response inside the retrieval loop. Accepts either an
    object with a `.usage` attribute, or a bare usage object/dict. Normalizes
    OpenAI-style (total input) and Anthropic-style (remainder input) usage into
    the canonical CallUsage shape, then costs it.
    """
    u = getattr(response, "usage", None)
    if u is None:
        u = response  # allow passing a bare usage object / dict
    u = u or {}

    out = _get(u, "output_tokens", "completion_tokens")

    a_cache_read = _get(u, "cache_read_input_tokens")
    a_cache_create = _get(u, "cache_creation_input_tokens")
    if a_cache_read or a_cache_create:
        # Anthropic remainder convention: input_tokens already excludes cache.
        input_tokens = _get(u, "input_tokens", "prompt_tokens")
        cache_read = a_cache_read
        cache_create = a_cache_create
    else:
        # OpenAI / Agents-SDK total convention: input is total incl. cached.
        total_input = _get(u, "input_tokens", "prompt_tokens")
        cache_read = _nested_cached(u)
        cache_create = 0
        input_tokens = max(total_input - cache_read, 0)

    rec = CallUsage(
        run_id=run_id, qid=qid, index=index, retriever=retriever,
        call_idx=call_idx, phase=phase,
        input_tokens=input_tokens, output_tokens=out,
        cache_read_tokens=cache_read, cache_creation_tokens=cache_create,
        latency_s=round(latency_s, 3),
        cost_usd=round(cost_for(retriever, input_tokens, out, cache_read, cache_create), 6),
    )
    os.makedirs(os.path.dirname(log_path) or ".", exist_ok=True)
    with open(log_path, "a") as f:
        f.write(json.dumps(asdict(rec)) + "\n")
    return rec


# --- Optional: a timing context manager so you never hand-compute latency -----
class timed:
    def __enter__(self):
        self._t = time.perf_counter(); return self
    def __exit__(self, *exc):
        self.latency_s = time.perf_counter() - self._t


# --- Usage sketch (drop into the harness where completions are made) ----------
# With the OpenAI Agents SDK the loop runs inside Runner.run(), so per-call usage
# is read post-hoc from result.raw_responses (one ModelResponse per LLM turn):
#
#   for k, mr in enumerate(result.raw_responses):
#       record_usage(mr, run_id=run_id, qid=qid, index=index_id,
#                    retriever=model_name, call_idx=k, phase=phase_for(mr),
#                    latency_s=0.0)   # latency is per-run here, not per-call
#
# Afterwards:
#   import pandas as pd
#   df = pd.read_json("runs/usage_log.jsonl", lines=True)
#   # Per-call rows show the tree re-send: input_tokens climbs each call_idx,
#   # and cache_read_tokens picks it up once caching is on.


def _selftest() -> None:
    """Offline check: the two providers' differing input-token semantics
    normalize to the SAME canonical split, and the cache-write premium is
    priced. No API calls."""
    import tempfile
    log = os.path.join(tempfile.mkdtemp(), "selftest.jsonl")

    # OpenAI-style: prompt_tokens is the TOTAL (10000), cached (8000) is a subset.
    oai = record_usage(
        {"prompt_tokens": 10000, "completion_tokens": 500,
         "prompt_tokens_details": {"cached_tokens": 8000}},
        run_id="t", qid="q", index="IDX-C", retriever="gpt-4o-2024-11-20",
        call_idx=1, phase="page_content", latency_s=0.0, log_path=log)
    assert oai.input_tokens == 2000, oai.input_tokens        # 10000 total - 8000 cached
    assert oai.cache_read_tokens == 8000
    assert oai.cache_creation_tokens == 0
    # (2000*2.50 + 8000*1.25 + 500*10) / 1e6
    assert abs(oai.cost_usd - 0.020000) < 1e-9, oai.cost_usd

    # Anthropic-style: input_tokens (2000) is ALREADY the uncached remainder;
    # cache_read (8000) is reported separately. The old draft did
    # max(2000-8000,0)=0 here and under-billed — assert we bill the full 2000.
    ant = record_usage(
        {"input_tokens": 2000, "output_tokens": 500,
         "cache_read_input_tokens": 8000, "cache_creation_input_tokens": 0},
        run_id="t", qid="q", index="IDX-C", retriever="anthropic/claude-sonnet-4-5",
        call_idx=1, phase="page_content", latency_s=0.0, log_path=log)
    assert ant.input_tokens == 2000, ant.input_tokens        # NOT double-subtracted
    assert ant.cache_read_tokens == 8000
    # (2000*3.00 + 8000*0.30 + 500*15) / 1e6
    assert abs(ant.cost_usd - 0.015900) < 1e-9, ant.cost_usd

    # Anthropic turn 0: the tree is WRITTEN to cache (40000 tokens at 1.25x).
    ant0 = record_usage(
        {"input_tokens": 2000, "output_tokens": 500,
         "cache_read_input_tokens": 0, "cache_creation_input_tokens": 40000},
        run_id="t", qid="q", index="IDX-C", retriever="anthropic/claude-sonnet-4-5",
        call_idx=0, phase="structure", latency_s=0.0, log_path=log)
    assert ant0.cache_creation_tokens == 40000
    # (2000*3.00 + 40000*3.75 + 500*15) / 1e6  -> the write dominates
    assert abs(ant0.cost_usd - 0.163500) < 1e-9, ant0.cost_usd

    # litellm prefix resolves to a PRICES key.
    assert normalize_model("anthropic/claude-sonnet-4-5") == "claude-sonnet-4-5"
    assert normalize_model("ollama_chat/qwen2.5-7b-instruct-ctx32k") == "qwen2.5-7b-instruct-ctx32k"
    assert normalize_model("gpt-4o-2024-11-20") == "gpt-4o-2024-11-20"

    print("usage_logging self-test OK "
          f"(openai=${oai.cost_usd}, anthropic=${ant.cost_usd}, anthropic-write=${ant0.cost_usd})")


if __name__ == "__main__":
    _selftest()

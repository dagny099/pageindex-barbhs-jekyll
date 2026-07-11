# Cost & token notes — PageIndex website experiment

Companion to `cost_enriched_per_run.csv` and `cost_summary_by_condition.csv`.
Prices verified 2026-07-10; USD per 1e6 tokens.

| model | input | output | note |
|---|---|---|---|
| gpt-4o-2024-11-20 | $2.50 | $10.00 | |
| claude-sonnet-4-5 | $3.00 | $15.00 | 200K-context tier; runs stayed well under |
| qwen2.5-7b (local) | $0.00 | $0.00 | self-hosted; latency is the real cost |

## Two numbers, and why they differ

**Floor cost** (in the enriched CSV) charges only what the logs directly
support: `content_tokens` as input + answer text as output (output tokens
approximated at ~chars/4, since the runs did not record completion tokens).
Across all 98 runs this totals **~$1.29**. It is a true lower bound.

**Navigation-inclusive estimate** adds the cost the floor ignores: the index
tree is a tool result that persists in context and is re-billed as **input on
every subsequent turn**. Modeled as `S x n_tool_calls + content_tokens` with a
single measured anchor `S = 43,730` (the structure qwen read on IDX-C), the
total is **~$35 — about 27x the floor**, and it scales with `n_tool_calls`.

### Caveat on the estimate
`S` is measured once, for IDX-C, and applied to all indices. IDX-D (headings
only) and IDX-O (local summaries) almost certainly differ. The *magnitude* and
the *direction* (navigation dominates; cost tracks tool-call count) are robust;
the exact dollar figure is not. Per-index structure size is the single missing
measurement — which is exactly what `usage_logging.py` captures going forward.

## The highest-value lever: prompt caching

This workload re-sends an identical tree prefix on every turn — the ideal case
for prompt caching. Cache reads bill at ~10% of input (Anthropic) / 50%
(OpenAI cached input). Enabling caching on the navigation prefix would cut the
dominant input cost by up to ~90%. It is both the biggest optimization and a
clean thing to measure and publish (cached vs uncached cost per question).

## What the data already shows (defensible without better logging)

- Output tokens are an **inverse** quality signal here: qwen writes the most
  (mean ~670, max 1402) and scores worst; a collapsed retrieval produced 915
  output tokens having fetched nothing.
- On cross-section synthesis, answer completeness tracks **exploration depth**
  (`n_tool_calls`), which is also the cost driver — a real recall/cost tradeoff
  that a terse retriever hides behind a confident partial answer.
- Retriever capability, not index sophistication, is the binding constraint for
  cross-section questions: bare deterministic headings (IDX-D) + Sonnet beat
  LLM-summarized IDX-C + qwen decisively.

## Caching & per-call cost logging — design decisions (V3A / PROMPT A)

This is the record of *why* the per-call logging + caching harness looks the way
it does, so the choices are auditable later. Built: `scripts/usage_logging.py`
(schema + prices + costing), per-call instrumentation in `scripts/run_retrieval.py`
(`runs/usage_log.jsonl`), `scripts/cost_report.py`, and a `--cache {off,on}` flag.

**1. Exact per-call usage, read post-hoc from the SDK — not a wrapped call.**
The retriever runs its whole agentic loop *inside* the OpenAI Agents SDK
(`Runner.run`), so there is no raw completion call in our code to wrap. Per-call
granularity comes from `RunResult.raw_responses` (one `ModelResponse` per LLM
turn, each with its own `.usage`). `phase` (structure / page_content / answer /
other) is **inferred** from the tool call(s) present in each `ModelResponse.output`
— a heuristic, confirmed correct on live data (`other → structure → page_content
→ answer`).

**2. The cache-write premium is a first-class cost.** Turn 0 *writes* the ~40K-token
tree to cache. Anthropic bills that write at **1.25× input (5-min TTL) / 2× (1h)**;
OpenAI charges no write premium (only reads discount, at 0.5×). The original draft
had no `cache_write` rate and never read `cache_creation_input_tokens`, so it
undercounted the single most expensive event in the run. Now logged as its own
`cache_creation_tokens` column and priced at `cache_write`.

**3. The two providers define the input-token field DIFFERENTLY — normalize before
costing.** OpenAI's `prompt_tokens` / Agents-SDK `input_tokens` is the **TOTAL**
(cached is a subset). Anthropic's `input_tokens` is the **uncached remainder**
(cache read/creation reported separately, *not* included). A single
`billable = input − cache_read` double-subtracts on Anthropic (the draft's bug: it
computed `max(2000−8000,0)=0` and billed zero full-price input). `record_usage()`
now discriminates by field shape and normalizes both into
`{full-price input, cache_read, cache_creation, output}`; `cost_for()` is one
formula over those canonical fields. Prices live in **one** place
(`usage_logging.PRICES`); model names are normalized to strip litellm prefixes
(`anthropic/`, `ollama_chat/`).

**4. Empirical: OpenAI auto-caching yields ZERO hits in the current message
layout.** Live 2-question baseline (IDX-D / gpt-4o): `cached_tokens = 0` on every
turn (the field *is* read correctly — verified). The tree arrives as a
*mid-conversation tool result*, not a stable leading prefix, and the loop is too
short for best-effort automatic caching to engage; across questions the per-question
text precedes the tree, so nothing is a reusable prefix either. **Implication:** an
OpenAI caching win requires restructuring the tree into a stable *leading* cached
prefix (the "tree as cached system-prefix" variant) — which *changes what the model
sees*, so it is a **separate experiment arm** with its own parity baseline, not part
of the default tool-result layout.

**5. Anthropic caching honors the "don't change what the model sees" constraint.**
Anthropic caching is explicit (breakpoint-driven), and the tree tool-result *does*
persist across turns, so an in-place `cache_control` breakpoint yields cache reads
without touching content. We reach it through litellm's `cache_control_injection_points`
(passed via `ModelSettings.extra_args`, forwarded by the Agents SDK's `LitellmModel`),
targeting `index: -1` — a **single** breakpoint on the latest message each turn
(under Anthropic's 4-block cap; caches the whole prefix incl. the tree). Verified
offline that this injects `cache_control` onto the tree block and leaves all content
byte-identical. `cache_control` is request **metadata, not content** — the prompt the
model reasons over is identical to caching OFF, so it affects cost/latency only.

**6. TTL implication.** Default cache TTL is **5 minutes**. Caching only spans
questions within a run if consecutive questions start within ~5 min; a slow sweep
lets the tree cache expire and silently re-pays the write. The 1-hour TTL fixes that
but **doubles** the write premium (2× vs 1.25×), so it pays off only across enough
reads.

**7. Parity is really a determinism check.** Both providers define caching as a pure
compute optimization (identical results, hit or miss); for OpenAI the request is
unchanged, and for Anthropic the only delta is a `cache_control` annotation (content
proven identical). So output-neutrality holds *by construction*. The empirical ON-vs-OFF
check therefore pins `temperature=0` and treats **`fetched_ranges` (the tool-call
trajectory) as the primary invariant**, answer text as secondary — because any real
divergence would be sampling nondeterminism, not caching, and exact answer text can
wobble on a rerun for reasons unrelated to the cache.

**Validation status (2026-07-10).** Cost model: self-test ✓ (`python3
scripts/usage_logging.py`). Instrumentation, phase inference, amplification
(input climbs `344 → 408 → 9,363 → 14,023` as the tree enters context), cost
reconciliation: confirmed on a **live** OpenAI baseline ✓. Anthropic
`cache_control` injection: mechanism proven **offline** ✓. **Blocked:** the live
Anthropic `cache_read > 0` confirmation and the Anthropic ON-vs-OFF parity check —
the Anthropic API returned *"credit balance is too low"* (no account credits).
Resume both once Anthropic billing is topped up:
`scripts/run_retrieval.py --indexes IDX-D --retrievers anthropic/claude-sonnet-4-5
--questions DL3 DL4 --cache on` (then `--cache off`, and diff `fetched_ranges`).

**Sources (verified 2026-07):** OpenAI automatic prefix caching (50% cached-input
discount, ≥1024-token prefix, 128-token increments) —
<https://openai.com/index/api-prompt-caching/>,
<https://developers.openai.com/api/docs/guides/prompt-caching>. Anthropic prompt
caching (cache read ~0.1×, write 1.25×/2×, 5-min/1-h TTL, ≤4 breakpoints) — see the
`claude-api` skill's `shared/prompt-caching.md`.

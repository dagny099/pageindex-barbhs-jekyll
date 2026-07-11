# PageIndex V1 — Findings Handoff

Purpose: a reference for Barbara (or an agent) to understand the most robust and
most interesting take-aways from the V1 Index/Retriever comparison, stated at the
narrowest level the evidence supports. Every claim separates **observation** from
**interpretation** and carries a **confidence** rating. Use this to write the V1
closing memo or a publication — do not exceed the claims stated here without new
evidence.

Source data: `evaluations/questions.csv` (14 questions) and
`responses-review.csv` (98 runs, with human scores `my_retrieval` / `my_answer`,
0–5). Cost figures from the enriched analysis (`cost_enriched_per_run.csv`,
`COST_NOTES.md`).

---

## 0. How to use this document

- **Do** lift the finding statements verbatim; they are pre-checked against the data.
- **Do** preserve the null and mixed results — they are the point, not filler.
- **Do not** upgrade a "moderate" or "low" confidence claim to a headline.
- **Do not** average qwen (RET-OLL) into cross-model comparisons — see §5.
- If an agent writes the memo: this file supplies the verified conclusions;
  the agent's job is documentation and trace citation, **not** discovering new findings.

---

## 1. Experiment reconstructed (verify the starred items before publishing)

Corpus: frozen `site-book-v1.md`, 26 website documents stitched into one book with
an **authored Markdown hierarchy**. This is the single most important caveat: the
structure PageIndex navigated was hand-authored, not inferred (see §8, §10).

Conditions actually run (98 = 14 questions × 7 cells):

| Index | How built | Retrievers run on it |
|---|---|---|
| IDX-D | Deterministic — authored MD headings, **no** model summaries | gpt-4o, Sonnet, qwen |
| IDX-C | Same hierarchy **+ cloud-model summaries** | gpt-4o, Sonnet, qwen |
| IDX-O | Same hierarchy **+ local Ollama summaries** | gpt-4o only |

Retriever (navigator) models: `gpt-4o-2024-11-20`, `claude-sonnet-4-5`,
`qwen2.5-7b-instruct-ctx32k` (local).

**\*Confirm from `config/` before publishing:** exact model that built IDX-C;
exact model + quantization + context that built IDX-O; that all cells share the
same PageIndex commit, node-text/node-ID/thinning settings, retrieval prompt,
tool interface, max retrieval steps, and answer format. If any differ, weaken the
corresponding conclusion.

**Fixed navigator for the Index Comparison:** use `gpt-4o-2024-11-20` — it is the
only retriever run on all three indices (D, C, O), so it is the one clean control
for IDX-D vs IDX-C vs IDX-O.

---

## 2. Primary finding (confidence: MODERATE)

> On a corpus with an authored Markdown hierarchy, **the retrieval model — not the
> index-construction method — determined retrieval and answer quality.** Adding
> model-generated summaries to the authored hierarchy produced no meaningful gain.

- **Observed.** Holding the navigator fixed, IDX-C minus IDX-D mean Δ(answer) was
  **+0.00 for Sonnet** (identical score on all 14 questions) and **−0.07 for
  gpt-4o**. Holding the index fixed, navigators differed sharply: mean answer
  score **Sonnet 3.93, gpt-4o ~3.25, qwen 0.89** (0–5). IDX-O (local summaries)
  was marginally the weakest index for gpt-4o (answer 3.00 vs 3.29 on IDX-D).
- **Why it matters.** The pre-registered V1 hypothesis was that summaries improve
  retrieval beyond the authored hierarchy. On this corpus they did not. The
  variance that does exist lives almost entirely in the navigator.
- **Conclusion it supports.** For a well-structured corpus, invest in the
  navigator, not in enriching an already-good map. Summaries did not earn their
  added indexing cost here.
- **Alternative explanations.** (a) The authored hierarchy was already so good
  that summaries had no headroom — plausible, and exactly why V3 (PDF, inferred
  structure) is the needed follow-up. (b) The 0–5 rubric is too coarse to detect a
  small summary benefit. (c) n=14, single rater, single run.
- **What would change it.** A corpus where structure must be inferred (PDF);
  a finer rubric; category-level power; blind or multi-rater scoring.

---

## 3. Secondary finding 1 — the navigator advantage is two mechanisms (confidence: MODERATE / LOW-MODERATE)

> Sonnet's edge over gpt-4o is **question-dependent** and comes from two separable
> behaviors, only one of which shows up in tool-call counts.

- **Observed.** On direct-location the two are indistinguishable (tool calls 3.0
  vs 3.0; answer 3.88 vs 4.00). The gap appears on harder categories. Δ(tool
  calls, Sonnet−gpt-4o) by category: cross-section +1.3, evidence-gap +1.6,
  reflective +0.6, direct-location 0.0, consistency −0.5. Δ(answer score):
  cross-section +1.00, reflective +1.00, evidence-gap +0.50, direct-location
  +0.12, **consistency +1.25 despite fewer tool calls**.
- **Interpretation.** (a) *Adaptive search depth* — on scattered-evidence
  questions Sonnet explores more and scores higher (CS6: 11 tool calls, hit 3 of 4
  canonical evidence bands, 4/5; gpt-4o: 4 calls, 0 bands, 2/5). (b) *Faithful
  synthesis of conflicting evidence at equal retrieval* — on CN4 (the "13 vs 14
  years of data" question) both fetched near-identical ranges, but Sonnet surfaced
  the discrepancy (4/5) while gpt-4o smoothed it into one number (3/5).
- **Confidence.** Moderate for mechanism (a) — the category pattern is consistent.
  Low-moderate for mechanism (b) — it rests on CN4 plus the consistency aggregate,
  and there are only 2 consistency questions.
- **Alternative explanation.** The tool-call difference could be a stopping-
  criterion artifact of the shared prompt rather than a stable model trait; check
  whether `max_retrieval_steps` was ever binding for either model.

---

## 4. Secondary finding 2 — even the best navigator did not reach the ceiling on evidence-gap (confidence: LOW-MODERATE, but the most *interesting* result)

> On evidence-gap questions the correct answer has two parts — confirm an absence
> **and** surface oblique traces — and the retrievers split the labor rather than
> either completing it.

- **Observed (EG4: "Is there a Resume Explorer project page, and where is the work
  described?").** Ground truth: no page; two oblique traces (a GraphRAG-post
  mention ~L2317–2337 and the resume-schema resource ~L3717+). gpt-4o confirmed the
  absence by bulk-scanning the portfolio (its largest fetch of the experiment,
  14,241 content tokens) and found **0** traces (3/5). Sonnet skipped the scan and
  found the resume-schema trace (4/5). **Neither found the GraphRAG trace.**
- **Interpretation.** "More tokens fetched" ≠ better retrieval: gpt-4o fetched the
  most and found the fewest traces, because it grabbed one contiguous block instead
  of hunting scattered evidence. Evidence-gap questions decompose into two sub-tasks
  that neither navigator's search strategy completed.
- **Why it matters.** This is the "the interesting result isn't who won" finding —
  it motivates hybrid/better retrieval more persuasively than a leaderboard, and it
  is directly on-thesis for knowledge legibility (the map was legible; complete
  reading of it was not achieved).
- **Confidence.** Low-moderate — compelling trace, but one question; treat as an
  illustrative mechanism, not a measured rate.

---

## 5. qwen (RET-OLL) — a segregated failure regime, never averaged in (confidence: HIGH)

- **Observed.** The local 7B navigator collapsed in **15 of 28 runs** (read the
  index tree, called `get_page_content` zero times, emitted a fluent generic
  corpus overview). Mean answer score **0.89/5**; latency **60–536 s** (mean 150 s).
  On IDX-C it scored 0.00 across the board.
- **Handling.** Report Sonnet vs gpt-4o quantitatively (both are competent tool-
  callers → a fair comparison). Treat qwen as a **qualitative "collapse regime"** —
  a weak tool-caller that fails *ungracefully*, producing confident, fluent,
  ungrounded output. Do **not** fold it into cross-model averages; doing so is what
  would make the whole comparison look noisy.
- **Why it's worth keeping.** The collapse mode (verbosity as the tell of a
  non-retrieval) is itself on-thesis for the judgment-gap argument.

---

## 6. Cost — what the logs support, and the caching question

- **Floor (defensible).** Charging only content fetched as input + answer text as
  output (output ≈ chars/4, since completion tokens were not logged), all 98 runs
  cost **~$1.29**. This is a true lower bound. Prices (verified 2026-07-10, USD/1M):
  gpt-4o-2024-11-20 $2.50/$10.00; claude-sonnet-4-5 $3.00/$15.00; qwen local $0.
- **Realistic (illustrative, LOW confidence).** The index tree is a tool result
  that persists in context and is re-billed as **input on every subsequent turn**.
  Using one measured anchor (a 43,730-token structure), the realistic total is
  **~$35 — ~27× the floor** — and it scales with `n_tool_calls`, not with the
  answer. Exact per-index tree sizes were not logged; that is the single missing
  measurement (fix in V3 with `usage_logging.py`).
- **Output-token volume is an inverse quality signal here:** qwen wrote the most
  (mean ~670, max 1402) and scored worst; a collapsed run produced 915 output
  tokens having fetched nothing.

### Would prompt caching help? (yes, with conditions — do not overclaim)

- **Mechanism.** Within one question's loop the ~43K-token tree is byte-identical on
  every turn — the ideal cacheable prefix. A cache **read** bills at ~10% of input
  (Anthropic) / ~50% (OpenAI cached input). For a question with *k* tool calls, you
  pay one write (~1.25×) + *k* reads (~0.1×) instead of full price *k*+1 times →
  **~70% off the dominant cost term.**
- **Conditions.** (1) The tree must sit as a stable prefix. In a tool-use loop it
  arrives as a `tool_result` mid-conversation, which still caches from turn 2 onward
  *within* a question; to cache it *across* the 14 questions, inject it as a fixed
  system-block prefix ahead of the per-question text. (2) Cache TTL is short (5-min
  default) — run questions in a tight batch. (3) Prefix must be exact-match (no
  per-turn timestamps/nondeterminism).
- **What it does NOT do.** It changes cost and latency only — **not** the tokens
  processed or the answers — so it cannot distort quality measurements. It does not
  reduce the many-sequential-calls latency inherent to agentic tree search.
- **Honest caveat for V1.** At $1–35 total, the dollars are trivial. Caching is worth
  doing (a) as a measurable, publishable "how to make PageIndex affordable" result,
  and (b) because V3's larger PDF trees make the amplification real. It is a V3
  priority, not a V1 rescue.

---

## 7. Limitations (state these wherever a conclusion appears)

Small question set (n=14; 2–4 per category → category-level claims are
underpowered); single corpus; author-created ground truth; single-rater, non-blind
scoring; single run (no repeats → no variance estimate); no conventional retrieval
baseline (BM25 / dense / long-context); no PDF representation; authored Markdown
hierarchy is a **favorable** input; per-call token/cost not logged; exact IDX-C /
IDX-O build models to be confirmed from config.

---

## 8. Guardrails — what NOT to claim

- Not "PageIndex beats vector RAG" — no baseline was run.
- Not "summaries are useless" — claim only "no measurable benefit **on this
  authored-hierarchy corpus**, at this rubric granularity and sample size."
- Not "Sonnet is a better model" — claim "Sonnet's navigation was better on
  scattered-evidence and conflicting-evidence questions **on this corpus**; on
  direct lookup the two tied."
- Not "gpt-4o is unreliable" — it was cheap and solid; its weakness was early
  stopping on hard synthesis, not error.
- Not any category-level rate as if powered — flag n per cell.

---

## 9. Narrowest defensible V1 claim (for the abstract / LinkedIn)

**Primary.** On a website corpus with an authored hierarchy, retrieval quality was
governed by the navigator, not the index: model-generated summaries added no
measurable benefit over authored Markdown headings (Sonnet identical on all 14
questions; gpt-4o −0.07 mean), while navigators differed substantially, and the
difference concentrated on scattered- and conflicting-evidence questions.

**Secondary (optional).** On evidence-gap questions, no navigator reached the
ceiling: the correct answer required both confirming an absence and surfacing
oblique traces, and the models split those sub-tasks — token volume did not
predict retrieval quality.

**Cautionary sentence.** These results describe one small, author-scored,
single-run study on a corpus whose structure was hand-authored; the summary null in
particular may not survive a corpus where PageIndex must infer structure — which is
exactly what V3 tests.

---

## 10. What V1 motivates for V3A (pointer, not a design)

The summary null is only interpretable because the hierarchy was authored. The
obvious next test removes that gift: **the same knowledge as a PDF, where structure
must be inferred** (TOC detection, page mapping, heading inference). Carry gpt-4o
(workhorse control) **and** Sonnet (the behavior contrast); drop qwen. Inspect the
generated tree **before** running retrieval, so a bad tree is not blamed on the
navigator. Weight evidence-gap questions up. Instrument per-call cost from run 1.

The V3A design belongs in a separate, frozen `V3A_PREREGISTRATION.md` written
**after** the paper and 8-question set are chosen — not in this results document.

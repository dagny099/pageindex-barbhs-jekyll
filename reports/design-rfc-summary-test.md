# Design: Do generated summaries help retrieval? — the RFC 9110 stress test

## Why this test exists (the weakness it fixes)

Every prior attempt to answer *"do LLM-generated node summaries improve retrieval over a
plain heading tree?"* has been **uninformative**, for the same reasons each time:

- **Ceiling.** The website (26 short, well-titled docs) and the 2009 paper (14 pages,
  self-contained) are both easy to navigate by headings alone. A strong retriever scores
  near-max on `IDX-D`, leaving no headroom for summaries to show a benefit. A null there
  can't distinguish *"summaries are useless"* from *"nothing left to improve."*
- **Subjective endpoint.** The verdict rested on a single rater's 0–4 answer score on
  n=14 — exactly the judgment calls the effect lived in. → *"n=14, one judge, within noise."*
- **Confounds.** The paper's "PDF vs Markdown" arms also varied summaries; its
  extraction "corruptions" turned out to be recoverable notation, not data
  (see `reports/qc-paper-tree-gate.md` and the retrieval run) — so it never isolated
  summaries at all.

This test removes all three: a **hard-to-navigate** corpus (so there is headroom), an
**objective primary metric** computed from the tool trace (no judge), and a **clean
single-variable manipulation** (identical tree, summaries on vs off), with
**pre-registered predictions** so the result is confirmatory, not a fishing expedition.

## Hypothesis and pre-registered predictions

> **H.** On a deep, cross-referential document, real generated summaries improve the
> retriever's ability to *navigate to the sections that hold the evidence* — the benefit
> concentrates on multi-hop / scattered questions and is ~absent on single-section lookups.

Pre-registered, **before running**:

| # | Prediction | If TRUE → | If FALSE → |
|---|---|---|---|
| P1 | On **multi-hop / cross-ref / enumeration** questions, `IDX-C0` gold-section **recall** exceeds `IDX-D` by a meaningful margin (target Δrecall ≥ 0.15). | summaries earn their cost on hard docs | — |
| P2 | On **single-hop lookup** controls, `IDX-C0` ≈ `IDX-D` (both high). | effect is navigation-specific, not global | if C0 also wins here, benefit is trivial/uniform (weaker claim) |
| P3 | Any C0 advantage is **larger for a weak retriever** (qwen) than a strong one (gpt-4o). | summaries are a crutch for weak navigators | if equal, benefit is retriever-independent |

**Decision rule (all outcomes are publishable):**
- **P1 holds, P2 holds** → "Generated summaries measurably improve retrieval navigation on
  deep/scattered documents; they don't help easy lookups." (positive, scoped)
- **P1 fails (C0 ≈ D on hard buckets too)** → a **strong, replicated null on the hardest fair
  venue**: "even on a 311-node spec, summaries don't improve navigation — invest in the
  retriever and the ingest path, not index enrichment." (negative, and credible *because*
  the venue was built to give summaries their best chance)
- **P3 pattern** → "summaries help weak local models, not strong cloud ones" — a concrete
  cost/quality lever for anyone running PageIndex locally.

## Conditions (one variable)

| Index | Tree | Summaries | Build cost |
|---|---|---|---|
| `IDX-D-rfc9110` | deterministic Markdown headings (311 nodes) | none | **$0** (already built) |
| `IDX-C0-rfc9110` | **same 311-node tree** | real gpt-4o summary per node (`--summary-token-threshold 0`) | ~$2 est (per-node calls only; the Markdown path does **not** trigger the PDF `toc_item_index_fixer`, so no $4 blow-up) |

Held fixed across conditions: byte-identical corpus text, retriever model, system prompt,
tool interface, `max_turns`, `temperature=0`, the question set, and the gold-section labels.
**The only thing that changes is whether `get_document_structure` carries summaries.** (The
harness already exposes summaries in the line-mode structure view and strips node text, so
no harness change is needed.)

Retriever: **`gpt-4o-2024-11-20`** (primary). Optional second arm **`qwen2.5-7b-instruct-ctx32k`**
(local, $0) to test P3 — worth including because the primary metric is objective and needs
no extra grading.

## Scope boundary — indexes that are NOT comparators here (verified 2026-07-15)

This test compares ONLY the line-addressed Markdown twins built from the same HTML→Markdown
source (all share `corpus_sha256 d034ec…`): **`IDX-D-rfc9110`**, **`IDX-C0-rfc9110`**, and
**`IDX-O0-rfc9110`** (once built). They share a byte-identical 311-node tree and differ
*solely* in the summary field, so any retrieval difference is attributable to summaries alone.

**`IDX-PDF-vanilla-rfc9110` is excluded.** It is a different derivation of RFC 9110 (native
PDF ingestion of `rfc9110.pdf`, sha `60b30e…`, built in a separate session): **474**
LLM-inferred nodes, **physical-page** addressing, summaries but **no inline node text**.
Folding it in would confound four variables at once — representation (PDF extraction vs
HTML→MD), structure inference (LLM-inferred vs deterministic), addressing (page vs line),
and granularity (474 vs 311 nodes). Concretely, the `gold_sections` labels and
`score_recall.py` are defined against the 311-node **line**-addressed tree and cannot score a
page-addressed index without re-labeling. Mixing is *mechanically* safe (the harness stamps
each result with its own index's provenance) but *analytically* invalid. The vanilla PDF
index belongs to a separate question — PDF-native vs Markdown ingestion (cost + structure +
fidelity) — not the summary test.

## Why RFC 9110 is the right stressor

- **Deep** (h2→h5, depth ~5) and **large** (311 nodes) — the retriever must choose among
  many similarly-named sections.
- **Terse, numeric headings** ("7.8 Upgrade", "15.5.22 426 Upgrade Required") give weak
  navigational signal on their own — the exact case where a summary could add value.
- **Densely cross-referential** — methods ↔ status codes ↔ header fields ↔ conditional
  requests ↔ ranges. Real questions have evidence genuinely *scattered* across distant
  sections. This is the opposite of the self-contained paper.

## Question set

**Schema** (`evaluations/questions-rfc9110.csv`):
`id, category, question, gold_sections, required_facts, difficulty, status, notes`
- `gold_sections` — the RFC section numbers whose text is *necessary* to answer, mapped to
  node line-ranges in the built tree. **This is the objective ground truth** for the recall
  metric.
- `required_facts` — a short checklist (2–4 atomic facts) the answer must contain, for
  blind checklist grading (not a vibe score).

**Difficulty gate (kills the ceiling problem at authoring time):** exclude any question
whose answer sits in a *single* section whose heading already contains the question's
keyword — those are ceiling for both arms and waste power. Every non-control question must
require ≥2 sections OR a section whose heading does *not* name the concept.

**Categories & target counts (n≈24):**

| Category | n | Purpose | Summary benefit expected? |
|---|---|---|---|
| A. single-hop lookup | 4 | control / ceiling anchor | no (P2) |
| B. multi-hop synthesis | 6 | precedence/interaction rules across sections | **yes (P1)** |
| C. cross-reference resolution | 5 | one concept defined-here, consequence-there | **yes (P1)** |
| D. scattered enumeration | 5 | "find *all* sections about X" | **yes (P1)** |
| E. boundary / absence | 4 | is it even in 9110, or in 9111/9112? honesty | objective |

**Example questions (verified answerable in RFC 9110; gold sections shown):**

- **A1 (lookup).** Which status code means the target moved permanently, and which field
  carries the new URI? — *gold: §15.4.2 (301), §10.2.2 (Location)*
- **B3 (multi-hop).** In what precedence order does a server evaluate If-Match,
  If-Unmodified-Since, If-None-Match, If-Modified-Since, and If-Range on one request? —
  *gold: §13.2.2 (precedence) + §13.1.1–13.1.5*
- **B2 (multi-hop).** Which standard methods are both *safe* and *cacheable* by default, and
  what makes a method cacheable? — *gold: §9.2.1, §9.2.3, §9.3.1/9.3.2*
- **C1 (cross-ref).** If a server can't satisfy Accept, what status *may* it return, and what
  alternative does the spec explicitly permit instead? — *gold: §12.5.1, §15.5.7 (406 "MAY disregard")*
- **D1 (enumeration).** List every 4xx status specifically about authentication/authorization
  and where each is defined. — *gold: §15.5.2 (401), §15.5.4 (403), §15.5.8 (407), §11*
- **D2 (enumeration).** Which header fields does 9110 define for HTTP authentication, and which
  are request vs response? — *gold: §11.6.1–11.6.4 (WWW-Authenticate, Authorization, Authentication-Info, Proxy-*)*
- **E1 (boundary).** Does 9110 define how to calculate cache *freshness lifetime*? If not, where? —
  *gold: none in 9110 → RFC 9111 (correct answer states the absence)*

Author the full 24 against the spec; every `gold_sections` entry is verified by reading the
cited RFC section (the RFC's own cross-references make this checkable, not subjective).

## Metrics

1. **PRIMARY — gold-section recall@fetch (objective, no judge).** For each question,
   recall = (gold sections whose text the retriever actually fetched via `get_page_content`)
   / (total gold sections). Computed by `scripts/score_recall.py` from `run.json` fetched
   line-ranges vs the gold node ranges. Report mean recall per condition **per category**.
   *This is the metric the hypothesis actually predicts, and it can't be gamed by a grader.*
2. **SECONDARY — answer correctness (blind checklist).** Fraction of `required_facts`
   present in the answer, graded with the **index label hidden** (D/C0 shuffled) to remove
   allegiance bias. A checklist, not a 0–4 feel.
3. **TERTIARY — navigation efficiency.** `n_tool_calls`, `structure_tokens`,
   `content_tokens`, latency, $ — the cost side of any benefit (summaries make the structure
   dump bigger; does the recall gain justify the extra navigate-tokens?).

## Build & run

```bash
# 1. Curate the already-built deterministic tree into an index (with provenance)
#    from results/rfc9110_structure.json  ->  indexes/IDX-D-rfc9110/
# 2. Build the summarized twin (bounded per-node summary calls; no toc-fixer on md path)
.venv/bin/python scripts/build_index_metered.py --md_path workspace/rfc9110.md \
  --if-add-node-summary yes --summary-token-threshold 0 --if-add-doc-description yes \
  --index-label BUILD-rfc9110-c0 --abort-over 4 --overwrite      # confirm the ~$2 preflight first
#    curate  ->  indexes/IDX-C0-rfc9110/
# 3. Run both arms, same questions, temp 0
.venv/bin/python scripts/run_retrieval.py \
  --questions-file evaluations/questions-rfc9110.csv \
  --indexes IDX-D-rfc9110 IDX-C0-rfc9110 \
  --retrievers gpt-4o-2024-11-20 --temperature 0
#    optional weak-retriever arm for P3:
#    --retrievers ollama_chat/qwen2.5-7b-instruct-ctx32k
# 4. Objective scoring (no judge)
.venv/bin/python scripts/score_recall.py --run runs/<ts> --questions evaluations/questions-rfc9110.csv
```

New tooling required: `scripts/score_recall.py` (maps fetched line-ranges → gold node ranges,
emits recall per question/category/condition). Small, offline, testable.

## Threats to validity & mitigations

- **Author bias in gold labels.** Mitigate: gold sections are the RFC's *own* normative
  locations, verified against the text; labels fixed **before** running.
- **Weak power (n≈24).** This is a case study, not a powered trial. Credibility comes from
  the objective primary metric + pre-registration + the effect being *predicted to
  concentrate* in specific buckets (a uniform or absent effect is itself clean).
- **Retriever masking.** gpt-4o may answer despite poor navigation (as it did on the paper);
  that's why **recall**, not answer score, is primary — and why the qwen arm matters.
- **Summary quality.** Threshold-0 guarantees a real generated summary per node (not the
  verbatim-copy branch that hit `IDX-C`); if summaries are low quality, that's a finding
  about PageIndex defaults, stated as such.

## Effort / next step

The bottleneck is **authoring 24 spec-checked questions with gold-section labels** (needs
care, not compute). Build (~$2) and run (cheap) are quick; `score_recall.py` is ~an hour.
I can draft the first 8 (2A / 3B / 2C+D / 1E) with verified gold sections for your review,
then we scale to 24 and run.

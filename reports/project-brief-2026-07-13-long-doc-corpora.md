# Project Brief — Long-Document Corpora for PageIndex Exploration (FAA pair + RFC)

**Date:** 2026-07-13
**Status:** Planning (no corpus built yet; sources verified and pinned below)
**Purpose of this file:** Standalone context for future sessions. Explains *why* these
document sets were chosen, records verified canonical sources with hashes, and states
the cost-telemetry discipline to follow before/while/after running anything.

---

## 1. Motivation

The existing experiment compares PageIndex index conditions (IDX-D/C/O) over small
corpora: `site-book-v1` (website snapshot) and `paper-book-v1` (34-page academic PDF,
~17K tokens). Two threads motivate scaling up:

1. **Section-length sensitivity.** We found the open-source markdown pipeline
   (`vendor/PageIndex/pageindex/page_index_md.py:10`) copies node text verbatim as the
   "summary" for nodes under `--summary-token-threshold` (default 200 tokens), while
   the PDF pipeline (`pageindex/utils.py:590`) always LLM-generates summaries and
   ignores that flag entirely (`run_pageindex.py:116` passes it only to `md_to_tree`).
   See `reports/findings-summary-threshold.md`. Documents with contrasting section
   lengths turn this from an incidental observation into a designed experiment.
2. **Hands-on capability exploration.** Long "complicated manuals" exercise tree
   depth, TOC detection, retrieval navigation cost, and prompt-cache behavior in ways
   a 34-page paper cannot.

## 2. Study design: two sets + a representation twin

| Set | Profile | Document | Stresses |
|---|---|---|---|
| **A** | Long doc, **long prose sections** | FAA Pilot's Handbook of Aeronautical Knowledge (PHAK) | Real LLM summarization quality & cost; deep rich TOC |
| **B** | Long doc, **short numbered sections** | FAA Aeronautical Information Manual (AIM) | The <200-token verbatim-summary branch; TOC-from-text detection |
| **C** | Medium doc, short sections, **same-source PDF/HTML/TXT triplet** | RFC 9110 (HTTP Semantics) | Representation comparison with airtight provenance |

**Why the FAA pair specifically:** same publisher, same domain, same era, same
typography — so the long-vs-short-section contrast is not confounded by style. This
mirrors the discipline of the existing PDF-vs-Markdown arms ("differ only in
representation"); here the arms differ (mostly) only in *section granularity*.

**Why RFC 9110:** the RFC Editor publishes canonical PDF, HTML, and plain text of the
*same content from the same source* — the cleanest possible extension of the
representation study (`paper-book-v1` vs `paper-book-v1-clean`), because the Markdown
arm need not be derived from the PDF at all.

**A designed asymmetry discovered during verification:** PHAK's embedded PDF outline
is extremely rich (7,689 entries, max depth 12) while the AIM's is shallow (80
entries, depth 3) relative to its true paragraph-numbered hierarchy. So Set A tests
"PageIndex with a gift-wrapped TOC" and Set B tests "PageIndex must infer structure
from body text." Report this contrast explicitly in any findings.

## 3. Verified canonical sources (2026-07-13)

All three downloaded and verified with the repo's pinned PyMuPDF: born-digital
(machine text, not scans), embedded TOC present, token counts via tiktoken
`o200k_base`. Scratch copies live outside the repo; **when adopting a document,
re-download from the canonical URL into `sources/<name>/` and pin the SHA-256 in a
config, following the `sources/paper-2009/` + `config/paper-book-v1.yml` pattern.**

### Set A — FAA-H-8083-25C, Pilot's Handbook of Aeronautical Knowledge (2023 edition)
- Landing page: <https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/phak>
- Full-book PDF: <https://www.faa.gov/regulations_policies/handbooks_manuals/aviation/faa-h-8083-25c.pdf>
- 77,598,564 bytes · **522 pages** · ~410K tokens · TOC: 7,689 entries, depth 12
- SHA-256: `247929cace0ab56b376e683eba540cc4c8f39f199ab35414e8b604e24f395cb7`
- No official HTML twin (chapter pages on faa.gov are just PDF links). PDF-arm only.
- Per-chapter PDFs also exist on the landing page — useful for a cheap pilot run
  (e.g., Ch. 4 "Principles of Flight" as its own pinned source).

### Set B — FAA AIM, Basic with Changes 1–3, effective 2026-07-09
- Publications page: <https://www.faa.gov/air_traffic/publications>
- PDF: <https://www.faa.gov/air_traffic/publications/media/AIM_Basic_w_Chg_1_and_2_and_3_dtd_7-9-26.pdf>
- Official HTML twin: <https://www.faa.gov/air_traffic/publications/atpubs/aim_html/index.html>
- 42,727,799 bytes · **781 pages** · ~554K tokens · TOC: 80 entries, depth 3 (shallow
  vs. its actual chapter → section → numbered-paragraph hierarchy)
- SHA-256: `aa64a8be658f54a2f6d7fbb4b0d3ae222942446ad200926e5c88d8afca39dc8b`
- ⚠ The AIM is amended ~every 6 months and the PDF filename carries the date —
  provenance must record edition ("Basic w/ Chg 1–3 dtd 7-9-26"), not just "AIM".

### Set C — RFC 9110, HTTP Semantics (June 2022, Internet Standard / STD 97)
- PDF: <https://www.rfc-editor.org/rfc/rfc9110.pdf>
- HTML twin: <https://www.rfc-editor.org/rfc/rfc9110.html> · Text twin: <https://www.rfc-editor.org/rfc/rfc9110.txt>
- 2,858,365 bytes · **194 pages** · ~112K tokens · TOC: 311 entries, depth 5
- SHA-256 (PDF): `60b30efa1048900833d1758440247fe8ac85a3134f2327388dcb24e07d814c89`
- RFCs are immutable once published — ideal provenance. **194 pages also fits inside
  the PageIndex hosted free trial (200 credits / 200 active pages)**, so RFC 9110 is
  the designated document for any hosted Chat-API experiment; PHAK/AIM do not fit
  the trial.

All three are US-government / IETF-published — public domain or freely
redistributable, safe to commit under `sources/` with provenance.

## 4. Practical guardrails (READ BEFORE RUNNING ANYTHING)

Scale context: these documents are **6× (RFC), 24× (PHAK), 32× (AIM)** the token count
of `paper-book-v1`. Costs that were pocket change will not stay pocket change.

### 4.1 What the cost telemetry does and does not cover

- **Instrumented:** retrieval runs. `scripts/run_retrieval.py` records every LLM call
  to `runs/usage_log.jsonl` via `scripts/usage_logging.py:record_usage` (exact
  provider-reported tokens, cache-aware, per-call rows). Report with
  `python3 scripts/cost_report.py [--run <run_id>]`, which also **reconciles** each
  row's logged `cost_usd` against recomputation and flags drift.
- **NOT instrumented: index generation.** Tree building in `vendor/PageIndex/` makes
  its own OpenAI calls (TOC detection, structure verification, per-node summaries)
  and writes nothing to `usage_log.jsonl`. On a 34-page paper that blind spot was
  cents; on a 522/781-page manual it is the *dominant* spend. Until a logging shim
  exists, bracket every index build with a manual reading of the OpenAI usage
  dashboard (before/after) and record the delta in the run notes / commit message.
- **The shim EXISTS (built 2026-07-13): `scripts/build_index_metered.py`.** Every
  PageIndex LLM call goes through `litellm.completion` / `litellm.acompletion`
  (`vendor/PageIndex/pageindex/utils.py:33,63`); the driver wraps those two module
  attributes (vendor untouched) and records one
  `usage_logging.from_litellm_usage → record_usage` row per call with
  `phase: "index_build"`, real per-call latency, and an `index` label of
  `BUILD-<stem>`. A wrapper was chosen over a LiteLLM success callback because
  `page_index_main` closes its own event loop (`asyncio.run`), which drops
  fire-and-forget async callback rows at the tail. The script also enforces the
  §4.2 pre-flight (estimate + confirm, `--yes` to skip) and hard-aborts past a
  spend bound (default 2× high estimate) via KeyboardInterrupt, which PageIndex's
  `except Exception` retry loops cannot swallow. Offline checks:
  `--self-test` and `tests/test_build_index_metered.py` (no API calls). Use this
  for every index build; known gap: calls that error after generating tokens are
  not recorded (PageIndex retries hide them from every layer).
- **Prices** live in one place: `scripts/usage_logging.py:PRICES`
  (gpt-4o-2024-11-20: $2.50/M in, $10/M out, cache read $1.25/M, cache write $2.50/M).

### 4.2 Estimate before you run (pre-flight procedure)

Never start a paid run without steps 1–4 written down; never scale up without step 5.

1. **State the value.** One sentence: what decision does this run inform? If no
   decision changes based on the outcome, don't run it.
2. **Measure the document (free, deterministic).** Token count via tiktoken over
   extracted text; node-count proxy = PDF outline entries or Markdown heading count;
   for Markdown arms, count nodes whose text exceeds `--summary-token-threshold` —
   that is the *exact* number of summary LLM calls (the rest hit the verbatim-copy
   branch and are free).
3. **Predict tokens per phase.**
   - *Markdown arm:* structure is deterministic (free). Cost = summaries only:
     input ≈ total text of over-threshold nodes; output ≈ (#calls × ~80 tokens).
     This estimate is near-exact.
   - *PDF arm:* TOC detection + verification ≈ 1.5–2× doc tokens as input, plus
     summaries (input ≈ 1× doc tokens, output ≈ #nodes × ~80), plus 1 doc-description
     call. Overall rule of thumb: input 2–4× doc tokens, output 10–20% of input.
4. **Price and bound it.** `cost = in/1e6×$2.50 + out/1e6×$10` (PRICES is the source
   of truth). Multiply by a **2× safety factor** — that's the abort threshold; if the
   metered spend crosses it mid-run, stop and investigate. Reference points at one
   full input pass: RFC ≈ $0.28 · PHAK ≈ $1.02 · AIM ≈ $1.38; ballpark full builds
   with summaries: **RFC $1–2, PHAK $3–8, AIM $4–10 per condition**.
5. **Pilot before scaling.** Run the smallest unit (RFC 9110, or one PHAK chapter)
   with metering on; compute `realized / estimated`. Only proceed to the full
   document if the ratio ≤ ~1.5; otherwise fix the estimate first. Record the ratio
   in the run notes so the multiplier in step 3 improves over time.
6. **Confidence rule:** any run estimated above ~$5 requires a metered pilot that
   validated the multiplier for that document class first.

### 4.3 Retrieval amplification will be much larger here

The dominant retrieval cost is the tree re-billed as input every agent turn
(see `reports/COST_NOTES.md`). The site-book tree is ~9K tokens; a PHAK tree built
from a 7,689-entry outline could be an order of magnitude larger. Consequences:
1. **Thinning matters** (`min_token_threshold` / tree-thinning options) — an
   unthinned PHAK tree may not even fit comfortably in context.
2. **Prompt caching stops being optional.** These runs are also the first realistic
   chance to capture a live `cache_creation_tokens > 0` row (the cache-write premium
   has never been observed live — see the cache-write accounting backlog).
3. The 3-way 14-question run on the *small* paper cost **$6.78** (165 calls). Assume
   a multiple of that per condition here; run `cost_report.py --run <id>` after the
   first 2–3 questions and extrapolate before committing to the full question set.

### 4.4 Sequencing (cheap → expensive)

1. **Deterministic first, always.** `--md_path` with summaries off (IDX-D style) is
   free; for PDFs there is no zero-LLM mode, so start PDF work on the *smallest*
   unit (RFC 9110, or a single PHAK chapter PDF) before full books.
2. **RFC 9110 is the pilot document** for every new mechanism (it's the cheapest and
   has the best provenance), then PHAK, then AIM.
3. One index condition at a time; check telemetry between conditions, not after all.
4. Hosted API experiments: RFC only (fits the 200-credit trial); Chat API is billed
   per query (token-based credits) — it is not free beyond the trial.

### 4.5 Reporting discipline

- Every run gets a `run_id` (UTC timestamp, e.g. `20260712T180445Z`); telemetry rows
  carry it; commit the `usage_log.jsonl` rows for keeper runs (precedent: commit
  `47b31ba`) and reference the run_id in findings docs.
- Findings must quote costs from `cost_report.py` output (reconciled), never from
  memory or estimates. Estimates belong in *pre-run* notes, clearly labeled.
- New corpora follow the frozen-corpus discipline: build scripts in `scripts/`,
  config in `config/`, pinned source in `sources/`, provenance JSON with hashes,
  QC report in `reports/`, never hand-edit outputs.

## 5. Proposed next steps

1. Pin RFC 9110 (`sources/rfc9110/` + config), build a PDF-arm and text/HTML-derived
   Markdown-arm corpus; run the tree gate pattern from the paper study.
2. Pilot PHAK Chapter 4 (single-chapter PDF) end-to-end to shake out the pipeline
   and calibrate the cost rule of thumb.
3. Decide thinning/summary-threshold settings for full PHAK + AIM builds using the
   pilot numbers; only then build full-book indexes.
4. Draft evaluation questions per set (reuse the Prompt-D question-design approach).
5. (Backlog) Index-build telemetry shim; upstream issue for the markdown/PDF summary
   inconsistency (see `reports/findings-summary-threshold.md`).

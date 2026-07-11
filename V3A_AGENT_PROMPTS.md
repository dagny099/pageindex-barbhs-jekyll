# V3A Coding-Agent Prompts

Four self-contained prompts, one per agent session. Run in dependency order:
**A (independent) → B → C → D** (C and D both depend on B; they can run in parallel).
Each prompt is scoped to a single task, mirrors the existing repo conventions
(frozen `corpus/` with `manifest.json` + `provenance.json`, `vendor/PageIndex`
submodule, `indexes/IDX-*`, `runs/`, `scripts/`, `CLAUDE.md` re-sync workflow),
and ends with a "report back" section so you can review before merging.

Paper under study (freeze one canonical PDF): **Ehinger, K. A., Hidalgo-Sotelo, B.,
Torralba, A., & Oliva, A. (2009). "Modelling Search for People in 900 Scenes: A
Combined Source Model of Eye Guidance." *Visual Cognition* 17(6–7), 945–978.
DOI 10.1080/13506280902834720.** Recommended canonical PDF: the published-layout
version (journal furniture present) — it is the harder, more honest structure-inference test.

---

## PROMPT A — Harness instrumentation: prompt caching + per-call cost tracking

You are working in the PageIndex website-experiment repository. Do ONE task:
add per-call token/cost logging and prompt caching to the retrieval harness,
WITHOUT changing what the model sees or produces.

Context:
- The retriever runs an agentic loop (get_document_structure → get_page_content →
  … → answer). The index tree is a tool result that persists in context and is
  re-billed as input on every subsequent turn — this is the dominant, currently
  untracked cost.
- A drafted logger, `usage_logging.py` (CallUsage schema, PRICES table,
  `record_usage`, `cost_for`), already exists. Use it as the single source of truth
  for prices and the log schema; extend it only if needed.

Task:
1. Instrument every LLM call in the retrieval loop (OpenAI, Anthropic, and Ollama
   paths) to append a `CallUsage` row to `runs/usage_log.jsonl`, tagged with
   run_id, qid, index, retriever, call_idx, and phase (structure/page_content/answer).
   Read exact usage from the provider response (OpenAI prompt/completion +
   prompt_tokens_details.cached_tokens; Anthropic input/output +
   cache_read_input_tokens).
2. Enable prompt caching on the index-tree prefix:
   - Anthropic: set a `cache_control` breakpoint on the tree block.
   - OpenAI: rely on automatic prefix caching; ensure the tree prefix is byte-stable
     across turns (no per-turn nondeterminism).
   - Add a config flag to optionally inject the tree as a cached system-prefix so
     caching spans questions within one run (document the TTL implication).
3. Add `scripts/cost_report.py` that reads the JSONL and prints per-condition
   input / output / cache_read tokens and cost, plus a per-call view showing input
   tokens climbing across call_idx (the re-send amplification).

Hard constraints:
- Do NOT change retrieval logic, prompts, tool interface, max steps, or answer
  format. Caching must affect cost and latency ONLY.
- Keep prices in one place. Do not touch `corpus/` or `indexes/`.

Acceptance criteria (must demonstrate):
- A 2-question smoke run shows `cache_read_tokens > 0` on turns ≥ 2 (Anthropic) and
  cached-prefix hits (OpenAI).
- **Parity check:** for those 2 questions, final `answer` text and `fetched_ranges`
  are identical with caching ON vs OFF (proves caching did not alter results).
- `cost_report.py` totals reconcile with the JSONL rows.

Report back: files changed; how caching was wired per provider; the parity-check
result; a sample cost report; anything that required a judgment call.

---

## PROMPT B — PDF → normalized Markdown ingestion (paper-book-v1)

You are producing a new frozen corpus for the PageIndex experiment: a normalized
Markdown "book" derived from one academic PDF, following the SAME producer pattern
as the existing site-book (frozen snapshot, provenance-pinned, never hand-edited).

Paper: Ehinger, Hidalgo-Sotelo, Torralba & Oliva (2009), Visual Cognition 17(6–7),
945–978. Use the single canonical PDF placed at `sources/paper-2009/paper.pdf`
(confirm its SHA-256; do not fetch a different version).

Task:
1. Build a deterministic, reproducible pipeline (scripts + config) that converts the
   PDF into `corpus/paper-book-v1/paper-book-v1.md`, normalized with the SAME
   conventions as the site-book: explicit heading hierarchy, a stable line-numbering
   scheme so `expected_evidence` can cite `Lxxx`, and a **page-map table**
   (PDF page → line range) so retrieval fetches can be traced back to physical pages.
2. Represent figures, tables, and equations as **labeled placeholders** with their
   captions (e.g. `[FIGURE 3: caption…]`) — never silently drop them; they are the
   representation-sensitive content.
3. Emit `manifest.json`, `provenance.json` (source PDF sha256, extraction tool +
   version, pageindex_commit), and a `reports/qc-paper-book-v1.md` that enumerates
   every section, figure, table, the references boundary, and any extraction issues
   (broken ligatures, hyphenation, header/footer bleed, column/reading-order errors).

Hard constraints:
- Reproducible: re-running yields a byte-identical `.md` (same sha256).
- Preserve the PDF↔line page-map at 100% line coverage.
- Do not hand-edit outputs; fix the pipeline instead. Mirror the site-book repo layout.

Acceptance criteria:
- `paper-book-v1.md` rebuilds to the same sha256; QC report lists every figure/table/
  section with line ranges; a validation script confirms the heading hierarchy is
  well-formed and the page-map covers all lines.

Report back: what structure was preserved vs. had to be inferred; the extraction
issues found; the page-map summary; and open questions for Barbara (e.g. ambiguous
section boundaries, figures that resisted extraction).

---

## PROMPT C — Tree-inspection gate (structure QC before any retrieval)

You are validating that PageIndex built a usable structural tree BEFORE any
retrieval is run. This is a gate, not a run.

Context: On the website corpus the hierarchy was authored; on this PDF-derived corpus
the structure must be INFERRED (TOC detection, section boundaries, page mapping).
A bad tree silently poisons retrieval results, so it must be inspected first.

Task:
1. Using the fixed index config, generate the PageIndex tree for BOTH representations:
   the PDF-derived `paper-book-v1` and (as the favorable control) a Markdown-native
   version of the same paper.
2. For each tree, emit a structure-quality report: node count, max depth,
   TOC-detection success, % of lines covered and any gaps, empty / duplicate /
   collapsed / mis-nested nodes, figure/table nodes, and whether section boundaries
   match `reports/qc-paper-book-v1.md` from Prompt B.
3. Emit a side-by-side **PDF-tree vs Markdown-tree diff** and a PASS / REVIEW verdict
   per representation.

Hard constraints:
- Do NOT run retrieval or answer any questions.
- Report metrics and flag anomalies; do not invent a quality score. Where judgment is
  needed, surface it for human review rather than deciding.

Acceptance criteria: a reviewer can decide in under 10 minutes whether the PDF tree is
fit for retrieval, from the report alone.

Report back: the diff, the top structural risks, and an explicit recommendation on
whether the PDF tree is fit for retrieval or needs a pipeline fix (Prompt B) first.

---

## PROMPT D — Candidate question generation (propose; Barbara disposes)

You are drafting CANDIDATE evaluation questions for a representation comparison
(PDF vs Markdown) on a paper Barbara co-authored and knows expertly. She will cut
your list down to 6–8, so over-produce and flag uncertainty.

Context & schema: reuse the existing `evaluations/questions.csv` schema (`id`,
`category`, `question`, `expected_evidence`, `ground_truth`, `why_strategic`,
`difficulty`). Categories: direct-location, cross-section-synthesis, consistency,
evidence-gap, reflective-discovery — plus, for a paper, add methods/procedural and
figure-or-table-evidence. Read `corpus/paper-book-v1/paper-book-v1.md`.

Task:
1. Propose 12–16 candidate questions spanning the categories, weighting evidence-gap
   UP (it was the most discriminating category in V1).
2. Deliberately include 2–3 **representation-sensitive** questions (figure/table
   content, cross-page reasoning, reference-list lookup) designed to expose PDF-vs-
   Markdown extraction differences.
3. For each: `question`, `category`, `expected_evidence` (with `Lxxx` locations in
   the book), a DRAFT `ground_truth`, `why_strategic`, `difficulty`, and a new
   `representation_sensitivity` tag (none / low / high).

Hard constraints (critical — this is the highest-judgment task):
- `ground_truth` is a DRAFT for Barbara to verify. Attach a `confidence` field and
  EXPLICITLY flag any answer you are not certain is correct. Do NOT state a confident
  ground truth you cannot ground in the text — fabricated ground truth is the exact
  failure this study exists to detect.
- Only propose questions whose `expected_evidence` you can locate in the book, and
  prefer evidence locatable in BOTH representations.

Acceptance criteria: `evaluations/candidate_questions.csv` (schema-compatible) plus a
short rationale note; every `ground_truth` cites specific evidence lines; low-confidence
items are clearly flagged.

Report back: the candidate set; which are representation-sensitive; and a ranked list
of which ground truths most need Barbara's verification (highest-risk first).

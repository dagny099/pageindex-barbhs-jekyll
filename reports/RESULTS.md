# PageIndex Experiment — Consolidated Results

*Compiled 2026-07-16 from the 13 retrieval runs in `runs/` (2026-07-09 → 2026-07-16), the
curated indexes in `indexes/`, and the scoring artifacts in `evaluations/` and
`runs/*/{scores,recall,answer_facts}.csv`. This is the detailed results reference for the
public write-up; every number below is traceable to a committed artifact (provenance table
in §9). The experimental design and its evolution are documented in
`reports/experimental-brief-lab-notebook.html`; mechanism deep-dives live in
`reports/findings-summary-threshold.md`, `evaluations/V1_FINDINGS_HANDOFF.md`, and
`reports/design-rfc-summary-test.md`.*

---

## 0. What was tested, in one paragraph

[PageIndex](https://github.com/VectifyAI/PageIndex) (vendored, unmodified, pinned at
`f413c66`) is "vectorless" reasoning-based RAG: build a hierarchical tree over a document,
then let an LLM agent navigate that tree instead of doing embedding search. We did not try
to improve it — we built a measurement harness around it that decomposes the pipeline into
independently inspectable stages (**representation → tree → navigation → synthesis**) and
asked: **how much value comes from the hierarchical tree itself, and how much more from
model-generated node summaries — and what does each cost?** Four corpora of increasing
navigation difficulty, three ways of obtaining the tree (deterministic from authored
structure, LLM-inferred, deterministic-plus-generated-summaries), retrieval always by an
agent over the tree, scored by human/agent rubric (website corpus) and by two objective
trace-based metrics (RFC 9110 and GDPR).

### Headline findings

1. **The navigator mattered more than the index** on well-structured corpora: switching
   retriever model moved answer quality by ~10× more than switching index condition (§2.1).
2. **PageIndex's "add summaries" is mostly a no-op at its default setting**: on the website
   corpus ~80% of node "summaries" were verbatim copies of node text (an undocumented
   200-token threshold, Markdown path only), which quadrupled per-question cost while adding
   ≈0 quality (§2.2).
3. **Real summaries (threshold 0) earned their cost on the website corpus** — strictly
   better *and* cheaper than the shipped default — **but the benefit did not generalize**:
   on RFC 9110, the corpus designed to give summaries their best chance, they *reduced*
   gold-section recall (0.92 → 0.69) at 4.6× the cost (§4.1).
4. **Deterministic structure extraction matched LLM-inferred structure at ~$0.** The PDF's
   embedded outline reproduced the Markdown tree almost exactly (311/311 titles); PageIndex's
   native PDF path ignored that outline and spent $6.44 inferring a noisier 474-node tree
   that dropped the section numbers the gold labels need (§3, §4.2).
5. **The dominant retrieval cost is invisible in the demo**: the tree is re-sent as input on
   every agent turn, so index enrichment multiplies *every* question's cost by the tree size
   — 4–5× for summary-bearing trees (§6).
6. **The summary result replicated on a second hard corpus (GDPR), and mostly survived a
   fairness check**: on EU law the summarized arm again came last and opened half the source
   text; when we reran the questions stripped of the article numbers that had been giving the
   deterministic arms free directions, the gap against summaries more than halved — but
   summaries reached only *parity*, never an advantage, at 3–5× the cost (§5).

---

## 1. Materials: corpora, indexes, questions

### 1.1 Corpora (frozen, provenance-pinned)

| Corpus | Source | Size | Structure | Question set |
|---|---|---|---|---|
| `site-book-v1` | 26 pages of barbhs.com, stitched Markdown "site book" (built in the website repo, synced by SHA) | ~27.7K words | authored Markdown headings, 339 tree nodes | 14 Q, 5 categories (`evaluations/questions.csv`) |
| `paper-book-v1` (+ `-clean` control) | Ehinger, Hidalgo-Sotelo, Torralba & Oliva (2009), *Visual Cognition* — PDF→Markdown built in-repo, glyph-corruption decoded via font-keyed map | ~10.8K words | 28 nodes | 8 Q, 6 categories (`evaluations/questions-paper-book-v1.csv`) |
| `rfc9110-book-v1` | RFC 9110 (HTTP Semantics), 194-page PDF/HTML/TXT triplet | 311 numbered sections | deep, cross-referential | 24 Q, 5 categories, gold section labels (`evaluations/questions-rfc9110.csv`) |
| `gdpr-md-v1` | GDPR (EU Regulation 2016/679), the EUR-Lex PDF — which has **no embedded outline** | 126 nodes (Articles + Recitals) | deep, cross-referential EU law | 24 Q, 5 categories, gold Article labels (`evaluations/questions-gdpr.csv`; paraphrase twin `questions-gdpr-paraphrase.csv`) |

The corpora ladder is deliberate: the website is *easy* to navigate by headings (authored
structure), the paper is small and self-contained, and RFC 9110 is the *hard* venue —
deep, scattered, cross-referential — chosen specifically so an index enrichment would have
headroom to show a benefit (`reports/design-rfc-summary-test.md`).

### 1.2 Index conditions

Two knobs, deliberately kept separate: **how the tree is obtained** and **whether nodes
carry generated summaries**.

| Condition | Tree obtained by | Summaries | Build cost | Built for |
|---|---|---|---|---|
| `IDX-D*` | deterministic — authored Markdown headings | none | **$0** (no LLM) | all three corpora |
| `IDX-C` | same headings | gpt-4o, **default threshold 200** → ~80% verbatim copies | ~$1 | site |
| `IDX-O` | same headings | local qwen2.5-7b, default threshold → same defect | $0 (local) | site |
| `IDX-C0*` | same headings | gpt-4o, **threshold 0** → real summary on every node | site ~$1 / RFC $0.70 | site, RFC |
| `IDX-PDF-vanilla-*` | **LLM-inferred** from the PDF (PageIndex native path) | always generated (PDF path has no threshold) | paper ~$1 / RFC **$6.44** | paper, RFC |
| `IDX-PDF-outline-*` | deterministic — the PDF's **embedded outline** (`fitz.get_toc()`), our `scripts/build_pdf_outline_index.py` | none | **$0** | RFC |
| `IDX-PDF-textheadings-*` | deterministic — headings recovered from the PDF's **text layer** (for PDFs with no embedded outline, e.g. GDPR's EUR-Lex file); `--headings-from text --text-profile eu-legislation` | none | **$0** | GDPR |

Retriever (navigator) held at `gpt-4o-2024-11-20` for every index comparison; the retriever
comparison (§2.1) instead held the index fixed and varied the navigator
(gpt-4o / claude-sonnet-4-5 / local qwen2.5-7b).

### 1.3 Metrics

- **Answer score, 0–5 rubric** (website corpus): correctness/completeness/grounding, scored
  per answer against pre-written expected evidence + ground truth. Judges: human + agent
  first-pass for the 98-cell V1 grid (`evaluations/scores-master.csv`); single agent judge
  for the D/C/C0 run (`runs/20260712T180445Z/scores.csv`). *Subjective, n=1 per cell —
  directional, not statistical.*
- **Recall@fetch** (RFC 9110 / GDPR) — *did the retriever open the right pages?* Objective,
  judge-free. Ahead of time, by hand, we label the sections whose text is actually needed to
  answer each question (the "gold sections"). Recall@fetch is the fraction of those gold
  sections the agent actually fetched while answering. It measures **navigation, not answer
  quality** — like an open-book exam where we've marked which pages hold the answer and check
  whether the student turned to them, not what they wrote down. Gold IDs live once in
  canonical section-ID space and are projected onto each index's own addressing (line ranges
  vs page nodes), then hit-tested against the agent's `get_page_content` calls
  (`scripts/score_recall.py`, `runs/*/recall.csv`). Opening *every* page would trivially
  score 1.0, so `content_tokens` fetched is reported alongside as a restraint check.
- **Fact-score** (RFC 9110 / GDPR) — *was the final answer actually correct?* The fraction of
  a question's pre-registered **required facts** that appear in the answer — concrete,
  checkable atoms (status codes, header-field names, RFC numbers), matched by regex, with
  **no LLM judge** (`scripts/score_answer_facts.py`, `runs/*/answer_facts.csv`). This grades
  the *outcome*, where Recall@fetch grades the *process*.

  **Worked example — RA1.** *"Which status code indicates the target resource has been
  assigned a new permanent URI, and what header field does the server use to convey that
  URI?"* The needed text lives in two RFC sections: **§15.4.2** (301 Moved Permanently) and
  **§10.2.2** (the Location header) — those are the gold sections. The required facts are the
  two atoms **`301`** and **`Location`**. On **IDX-D** the agent fetched both gold sections
  (**recall 1.0**) and its answer named both atoms (**fact-score 1.0**). On the coarser
  page-addressed **PDF-outline** arm the same question scored **recall 0.5** — not because it
  answered worse, but because that arm's physical-page nodes bundle neighbouring sections, so
  only one of the two gold locations registers as a distinct fetch. That gap is a
  *representation artifact*, which is exactly what the study is trying to see.

  Because one grades finding and the other grades correctness, **the two can diverge** — and
  that divergence is informative: an agent can navigate perfectly yet answer poorly (high
  recall, low fact-score), or answer correctly from a tight snippet or a node summary without
  ever opening the labelled sections (low recall, high fact-score). Reporting both separates
  *"looked in the right place"* from *"got it right."*
- **Telemetry** (all runs): tool calls, structure tokens re-sent per turn, content tokens
  fetched, latency, estimated $ per question (`runs/*/run.json`, `runs/usage_log.jsonl`).

---

## 2. Part 1 — Website corpus (`site-book-v1`)

### 2.1 The navigator dominated the index (runs 20260710T060453Z / 062406Z / 065513Z)

98 scored cells: 14 questions × {IDX-D, IDX-C, IDX-O} × {gpt-4o, claude-sonnet-4-5,
qwen2.5-7b} (IDX-O run with gpt-4o only; one gpt-4o cell lost to an API-quota outage).
Mean scores (0–5), from `evaluations/scores-master.csv`:

| | IDX-D (headings only) | IDX-C (default summaries) | IDX-O (local summaries) |
|---|---|---|---|
| **claude-sonnet-4-5** | ret 4.00 / ans 3.92 | ret 4.00 / ans 3.93 | — |
| **gpt-4o-2024-11-20** | ret 3.43 / ans 3.29 | ret 3.36 / ans 3.21 | ret 3.14 / ans 3.00 |
| **qwen2.5-7b (local)** | ret 2.21 / ans 1.79 | ret 0.00 / ans 0.00 | — |

- Holding the navigator fixed, adding summaries changed the answer score by **+0.00
  (Sonnet — identical on all 14 questions) and −0.07 (gpt-4o)**. Holding the index fixed,
  changing the navigator moved it by **~0.6–2 points**.
- Sonnet's edge concentrated on scattered-evidence questions (adaptive search depth: e.g.
  CS6, 11 tool calls vs 4) and on faithful synthesis of conflicting evidence (CN4: surfaced
  the "13 vs 14 years" discrepancy that gpt-4o smoothed over).
- **qwen collapse regime**: the local 7B navigator read the tree, then called
  `get_page_content` zero times in 15/28 runs and emitted a fluent, generic, ungrounded
  overview (mean 0.89/5; 60–536 s latency). It is reported separately and never averaged
  into cross-model numbers. Verbose output was the tell of a non-retrieval.
- On evidence-gap questions no navigator reached the ceiling: EG4 required confirming an
  absence *and* surfacing two oblique traces; gpt-4o bulk-scanned 14K tokens and found 0
  traces, Sonnet found 1 without scanning. Token volume did not predict retrieval quality.

Full claim-by-claim treatment with confidence ratings: `evaluations/V1_FINDINGS_HANDOFF.md`.

### 2.2 The summary-threshold discovery (mechanism finding)

Inspecting IDX-C/IDX-O revealed that PageIndex's Markdown path only generates a real
summary when a node's text exceeds `--summary-token-threshold` (default **200 tokens**;
the CLI `--help` marks the flag "markdown only", but the verbatim-copy behavior itself is
documented nowhere); below that it **copies the node text verbatim** into `summary`. The
PDF path always generates real summaries and ignores the flag. On this heading-dense corpus:

| | IDX-C | IDX-O |
|---|---|---|
| Nodes with verbatim "summary" | **273/339 (80.5%)** | 272/339 (80.2%) |

Downstream, the retriever's tree dump strips `text` "to save tokens" — defeated when
`summary == text`. The re-sent tree: **IDX-D 8,934 tokens vs IDX-C 43,730 (4.9×)**, billed
as input on every agent turn. Full mechanism + upstream/ours boundary:
`reports/findings-summary-threshold.md`.

### 2.3 The threshold-0 counterfactual: IDX-C0 (run 20260712T180445Z)

`IDX-C0` = same tree, real gpt-4o summary on every node. Three-way run, gpt-4o navigator,
14 questions, judge claude-fable-5 (0–5, n=1/cell — directional):

| Category | IDX-D | IDX-C | IDX-C0 |
|---|---|---|---|
| direct-location | 4.75 | 4.88 | 5.00 |
| evidence-gap | 4.33 | **3.67** | 4.50 |
| cross-section-synthesis | 2.33 | 3.33 | 3.83 |
| reflective-discovery | 2.75 | 4.75 | 5.00 |
| consistency | 4.50 | 3.75 | 4.25 |
| **mean** | **3.82** | **4.11** | **4.54** |
| tree re-sent/turn (tok) | 8,934 | 43,730 | 35,516 |
| **cost, 14 Q** | **$0.80** | **$3.29** | **$2.69** |

- **IDX-C0 strictly dominated IDX-C**: better on every summary-sensitive category *and* 18%
  cheaper. The shipped default was the worst value on the board.
- Summaries helped exactly where navigation is hard (cross-section, reflective-discovery);
  on direct-location all three tie near ceiling.
- Verbatim summaries actively **hurt** evidence-gap: on EG6, IDX-C laundered three bracketed
  placeholders as "actual numbers" — the failure that category exists to detect. IDX-D and
  IDX-C0 both caught it.
- Honest revision from the counterfactual: fixing the threshold recovered only ~8K of the
  ~35K-token tree excess. **A properly summarized tree is still ~4× the headings tree** —
  that cost is inherent to summarizing a heading-dense document, not an artifact of the bug.

---

## 3. Part 2 — Paper corpus (`paper-book-v1`): representation, first pass

Three arms over the same 2009 paper, gpt-4o navigator, 8 questions, **two replicate runs**
(20260715T002754Z, 20260715T003239Z):

| Arm | Tree | Nodes | Mean $/8Q (rep1 / rep2) | Struct tok/turn |
|---|---|---|---|---|
| `IDX-PDF-vanilla-paper` | LLM-inferred from source PDF | 25 | $0.31 / $0.31 | 4,515 |
| `IDX-D-paper-book-v1` | deterministic, PDF-derived Markdown | 28 | $0.28 / $0.13 | ~500–700 |
| `IDX-D-paper-book-v1-clean` | deterministic, cleaned Markdown control | 28 | $0.12 / $0.21 | ~500–700 |

What this run pair established:

- **Tree-quality gate first, retrieval second** (`reports/qc-paper-tree-gate.md`): the
  vanilla PDF arm inferred every body section correctly but carried **39 glyph-corrupted
  statistics (`p<.001` extracted as `pB.001`) and 57 ligature artifacts**, fragmented the
  abstract, and produced no figure/table nodes. The two Markdown arms passed clean. This is
  the extraction-layer failure made visible *before* it could be misattributed to retrieval.
- The vanilla arm's per-question cost ran ~1.5–2.5× the deterministic arms, driven by its
  ~4.5K-token always-summarized tree vs ~0.5K for headings — the same re-send mechanism as
  §2.2, at small-document scale.
- The replicate pair shows **within-arm run-to-run variance** (e.g. the D vs D-clean cost
  ordering flips between reps) — a caution against reading single-run cost deltas of this
  size as real.
- **Not yet measured:** answer quality was not formally scored for these runs (the paper
  question set has no gold-section labels, and the 0–5 judge pass wasn't run). Qualitative
  read of the transcripts: all three arms answered the direct questions correctly; the
  interesting differences are upstream, in the tree. This corpus mainly served to prove out
  the representation methodology that RFC 9110 then tested properly. A confound worth
  naming: the vanilla arm differs from the D arms in *both* tree inference and summaries,
  so it cannot isolate either — that isolation is what §4 was designed for.

---

## 4. Part 3 — RFC 9110: the two clean single-variable tests

RFC 9110 was selected because every prior venue was too easy: a strong retriever scores
near-ceiling from headings alone, so a summary benefit had nowhere to show up. 24 questions
with **gold section labels** (objective recall@fetch scoring, no judge), 4 single-hop
controls + 20 hard (multi-hop, cross-reference, scattered-enumeration, boundary-absence).

### 4.1 Do real summaries help navigation? — **No; they reduced recall at 4.6× cost** (run 20260715T051258Z)

Pre-registered design (`reports/design-rfc-summary-test.md`): identical 311-node tree,
summaries on (`IDX-C0-rfc9110`, real gpt-4o summary per node, built for $0.70) vs off
(`IDX-D-rfc9110`), gpt-4o navigator, temperature 0. Prediction P1: recall on hard
categories improves by ≥ +0.15 if summaries earn their cost.

| Recall@fetch by category (n) | IDX-D | IDX-C0 | Δ |
|---|---|---|---|
| single-hop-lookup (4) | 1.000 | 0.875 | −0.13 |
| multi-hop-synthesis (6) | 0.881 | 0.631 | −0.25 |
| cross-reference-resolution (5) | 0.800 | 0.550 | −0.25 |
| scattered-enumeration (5) | 1.000 | 0.680 | −0.32 |
| boundary-absence (1 scorable) | 1.000 | 1.000 | 0 |
| **overall (21)** | **0.918** | **0.687** | **−0.23** |
| answer fact-score (23) | 0.946 | 0.948 | ≈0 |
| tree re-sent/turn (tok) | 6,793 | 39,303 | 5.8× |
| **cost, 24 Q** | **$1.30** | **$6.01** | **4.6×** |

- **P1 failed with the sign reversed**: on the venue built to give summaries their best
  chance, every hard category's recall *dropped*, most on scattered-enumeration — exactly
  where summaries were predicted to help most.
- **The fact-scores tie is the mechanism clue**: answers stayed equally correct because the
  agent increasingly answered *from the summaries in the tree* instead of fetching the
  primary text (lower fetch-recall, same facts). That trades verifiable grounding in the
  spec's normative text for trust in generated paraphrases — an unfavorable trade for a
  normative document, and you pay 4.6× for it.
- Combined with §2.3, the summary question now has a two-sided answer: real summaries
  helped subjective answer quality on a small, discursive corpus, and hurt objective
  navigation recall on a large, precise one. "Add summaries" is not a general upgrade; it
  is a corpus-dependent trade.
- Prediction P3 (summaries as a crutch for weak local navigators) remains untested — the
  qwen arm was not run.

### 4.2 Does representation (PDF vs Markdown) matter when structure is held equal? — **Barely** (run 20260715T174748Z)

The reframe that made this test clean: **"PDF vs Markdown" is the wrong axis — the real
variable is how structure is obtained.** `rfc9110.pdf` carries an embedded outline of 311
entries byte-for-byte matching the Markdown heading tree. `scripts/build_pdf_outline_index.py`
extracts it deterministically for $0, yielding a page-addressed twin of the line-addressed
Markdown index.

| | IDX-D-rfc9110 (Markdown, line-addressed) | IDX-PDF-outline (PDF, page-addressed) |
|---|---|---|
| Nodes / struct tok per turn | 311 / 6,793 | 311 / 6,873 |
| Recall@fetch overall (21) | 0.906 | 0.821 |
| — single-hop (4) | 1.000 | 0.875 |
| — multi-hop (6) | 0.839 | 0.756 |
| — cross-reference (5) | 0.800 | 0.800 |
| — scattered-enumeration (5) | 1.000 | 0.840 |
| Mean content tok fetched/Q | 3,476 | 1,400 |
| **Cost, 24 Q** | **$1.27** | **$1.24** |

- With structure held identical, the representation gap is **−0.09 recall at cost parity** —
  small compared to the −0.23 summaries inflicted (§4.1). Page-level addressing is coarser:
  a page node bundles neighboring sections, so some fetches technically miss the gold
  section while still delivering its text (RA1: PDF-outline recall 0.5, answer still fully
  correct). The recall gap therefore *overstates* the practical difference.
- The IDX-D arm's overall recall replicated across the two independent runs (0.918 in §4.1
  vs 0.906 here) — the objective metric is stable.
- **The contrast that matters is with PageIndex's native PDF path**: it ignores the embedded
  outline and LLM-infers a 474-node tree for **$6.44** (metered; ~3× its own estimate,
  inflated by TOC-repair loops) that drops the section numbers gold labels key on and
  duplicates nodes. Deterministic outline extraction produced a strictly cleaner tree for
  $0. This is a finding about the tool's ingestion path, not about PDFs.

---

## 5. Part 4 — GDPR (EU law): does the RFC result replicate, and does it survive fair questions?

RFC 9110 showed summaries *hurt* navigation (§4.1). The open question was whether that is a
fact about summaries or a fact about one hard document. GDPR is the second hard venue, chosen
to be as different from RFC as possible while staying difficult: EU law rather than a network
protocol, numbered **Articles and Recitals** rather than sections, and — usefully — an
official EUR-Lex PDF with **no embedded outline**, so the free deterministic tree had to be
rebuilt from the PDF's text layer (`IDX-PDF-textheadings-gdpr`, 126 nodes, $0). All three arms
share that identical 126-node tree, so they differ only in *how the tree was obtained* and
*whether nodes carry summaries*:

- **IDX-D-gdpr** — deterministic Markdown headings, no summaries ($0).
- **IDX-PDF-textheadings-gdpr** — the deterministic PDF-text-heading twin, no summaries ($0).
- **IDX-C0-gdpr** — the same tree plus a real gpt-4o summary on every node ($0.33 to build).

Navigator gpt-4o, 24 questions with hand-labeled gold Articles, scored the same judge-free way
as RFC: **recall@fetch** (did it open the right Articles?) and **fact-score** (was the answer
right?) — both defined in §1.3. Recall uses span mode (`--line-hit span`, decided before the
run) because GDPR Articles are long.

### 5.1 The replication (original questions) — the RFC direction holds

| Arm (all share the 126-node tree) | Recall@fetch | Fact-score | Source text opened | Tree re-sent/turn | Cost, 24 Q |
|---|---|---|---|---|---|
| IDX-D (Markdown headings) | 0.958 | 0.920 | 71.1K tok | 2,853 | $0.72 |
| IDX-PDF-textheadings (PDF text layer) | **1.000** | **0.944** | 102.9K tok | 2,891 | $0.83 |
| IDX-C0 (real summaries) | **0.917** | **0.875** | **37.4K tok** | 15,272 | $2.27 |

The summarized arm came **last on both metrics**, and it opened barely half the source text
(37K vs 71K tokens) — the same tell as RFC: the agent answered from the summaries sitting in
the tree instead of fetching the Article itself. The two deterministic arms tied or beat it for
a third of the cost, and the summary tree is **5.4× larger to re-send every turn** (15,272 vs
2,853 tokens). So the RFC finding is not a one-document fluke: it replicates in a second,
unrelated hard corpus.

### 5.2 The paraphrase fair-test — the null softens but survives

One objection could explain the whole result away (§5.3, bias #1). These questions were written
while looking at the Article structure, and several named their target outright — the original
GC1 literally read *"Article 17(1)(c) permits erasure where the data subject objects 'pursuant
to Article 21(1)'…"*. When the question hands over the address, plain heading navigation is
trivially enough and a summary has nothing to add. So we reran the **same 24 questions with
byte-identical gold**, but every Article number and structural cue stripped out — phrased the
way a real user would ask (*"If a person objects to a company using their data, when can the
company refuse to stop?"*). $3.49, `evaluations/questions-gdpr-paraphrase.csv`.

| Arm | Recall: original → paraphrased | Fact-score: original → paraphrased |
|---|---|---|
| IDX-D (Markdown headings) | 0.958 → 0.840 | 0.920 → 0.861 |
| IDX-PDF-textheadings | 1.000 → 0.840 | 0.944 → **0.899** |
| IDX-C0 (real summaries) | 0.917 → 0.819 | 0.875 → **0.861** |
| **C0's gap to the best deterministic arm** | **−0.083 → −0.021** | **−0.069 → −0.038** |

Two things happened. First, the rewrite worked as intended: **recall fell on every arm** once
the prompts stopped naming targets — direct proof the deterministic arms had been riding the
free addresses. Second, the fair-test result: **the penalty against summaries more than halved,
but did not disappear.** C0's gap to the best deterministic arm shrank from −0.083 to −0.021 on
recall and from −0.069 to −0.038 on facts. The reason is *resilience* — C0's answer-correctness
barely moved (−0.014) while the deterministic arms fell three to four times as far, so on
realistic questions **C0 ties the Markdown-heading arm exactly on answer correctness (0.861
each)**, though the PDF-heading arm still leads (0.899). The token gap closed as well: with no
address to aim at, the deterministic arms fetched *less* and answered slightly worse, converging
on C0's roughly-flat fetch volume.

The honest reading: paraphrasing gives summaries their best chapter yet — they buy robustness to
vaguely-phrased questions, enough to reach *parity* on the outcome that matters — but not enough
to beat a $0 structural index, and not enough to justify their 3–5× re-send cost. **A tie,
bought at triple the price.**

### 5.3 Known biases of the GDPR evaluation

Four caveats bound the reading above. They don't overturn it; they mark where it is soft.

1. **The original questions were navigation-friendly by construction.** Written while looking at
   the Article structure, several named their target in the prompt. When the question hands the
   agent the address, heading navigation is trivially sufficient — and summaries exist precisely
   for the case where titles *don't* telegraph the answer. This was the most serious bias, which
   is why we ran the paraphrase test in §5.2; it shrank the anti-summary result but did not
   reverse it.

2. **Recall@fetch is stacked against summaries by definition.** It rewards opening the primary
   text — but *not needing to open it* is the whole point of a summary tree, and the fact-scores
   essentially tied. So the fair objective statement is not "summaries made retrieval worse" but
   "summaries delivered equal answers at 3–5× the cost, while shifting the grounding from the
   source text to a paraphrase." The cost half is certain; calling the grounding shift "worse"
   is a reasonable judgment for law and specs, not a universal fact.

3. **Two questions rest on a contestable answer key.** GE2 (deceased persons) and GE4 (anonymous
   information) are addressed only in the GDPR's *Recitals* — the preamble, which is interpretive
   context, not binding law. Our answer key treated the Recital as the authoritative location; a
   lawyer could argue that reasoning from the binding definition of "personal data" is the
   stronger answer, with the Recital as support. The effect is real but "failure" overstates two
   questions under one navigator.

4. **One answer key was changed after seeing the results — a "forking-paths" move** (choosing an
   analysis rule after glimpsing the data, the thing pre-registration exists to prevent). GC3's
   gold was narrowed after the run from {Article 46, Article 47} to {Article 47}, because all
   three arms answered fully from Article 47 alone and demanding a fetch of the *citing* Article
   penalized everyone equally. The reasoning is sound and documented in
   `evaluations/questions-gdpr.csv`, but it is labeled here as **post-hoc**, not "a correction."
   (The span-mode recall rule, by contrast, was fixed before the run and is clean.)

Caveats on the numbers themselves: n=24, one judge, one navigator; four questions (GB2, GC5,
GD1, GE3) were fuzzy-matched by the fact-scorer and flagged for manual confirmation; and the two
Recital questions (bias #3) sit at 0.5 recall across all three arms — the single biggest drag on
the paraphrased scores.

---

## 6. Cost: the re-send amplification is the whole story

The demo-invisible mechanism: the tree dump is a tool result that persists in the agent's
context and is **re-billed as input on every subsequent turn**. Index enrichment therefore
multiplies every question's cost, forever, by the tree size:

| Corpus | Headings tree ($/14 or 24 Q) | Summary tree | Multiplier |
|---|---|---|---|
| site-book (14 Q) | IDX-D $0.80 | IDX-C0 $2.69 / IDX-C $3.29 | 3.4–4.1× |
| RFC 9110 (24 Q) | IDX-D $1.30 | IDX-C0 $6.01 | 4.6× |
| GDPR (24 Q) | IDX-D $0.72 | IDX-C0 $2.27 | 3.2× (tree size 5.4×) |

The GDPR row shows the two multipliers can diverge: the summary *tree* is 5.4× larger to
re-send, but the per-question *cost* multiplier is only 3.2× here because GDPR's shorter
answers ran fewer agent turns, so the enlarged tree was re-billed fewer times.

Other cost facts worth keeping:

- **Total spend ≈ $60**: run-level estimates across all 13 retrieval runs sum to $43.13
  (`est_cost_usd` in `runs/*/run.json`; the two GDPR runs added $3.82 + $3.49), plus ~$14 of
  metered index builds (dominated by the LLM-inferred RFC PDF tree: $6.44 final resumable
  build plus earlier aborted/variant attempts; the GDPR summary index added $0.33), plus a
  few dollars of un-metered early site/paper index builds. The **per-call ledger**
  (`runs/usage_log.jsonl`, live since 2026-07-11, and where the GDPR runs are fully logged)
  captured the instrumented portion. Either way: the entire study cost less than a nice dinner.
- Index builds are now **metered and resumable** (`scripts/build_index_metered.py`,
  content-addressed LLM cache): an aborted build replays for $0. Calibration finding: the
  "2–4× input tokens" rule of thumb under-predicts TOC-repair-heavy PDF builds by ~3×.
- Anthropic **prompt caching** was wired in and verified for parity (cache ON vs OFF runs
  2026-07-11; logged −36%, ≈−24% net of the write premium). The exact cache-write premium
  was never captured on the corrected logging path — still open.
- Output-token volume was an *inverse* quality signal: qwen's collapsed non-retrievals
  produced the longest answers.

---

## 7. What we now claim (and won't)

Defensible claims, at the narrowest level the evidence supports:

1. On a corpus with authored structure, **retrieval quality was governed by the navigator,
   not the index** (moderate confidence; n=14, single-run cells).
2. **PageIndex's default "add summaries" on Markdown is largely a no-op that costs 4×**:
   ~80% verbatim copies, the verbatim semantics undocumented, and behavior inconsistent
   with the PDF path (high confidence; mechanism verified in upstream code, and confirmed
   unchanged on upstream `main` — which equals our pinned `f413c66` — on 2026-07-15).
3. **Properly generated summaries are a corpus-dependent trade, not an upgrade**: +0.7 mean
   rubric score on the discursive website corpus; **−0.23 objective recall at 4.6× cost** on
   the deep technical spec, with answers propped up by the summaries themselves. This
   **replicated on a second hard corpus (GDPR)**: summaries again came last, and even after
   the questions were rewritten to remove the article numbers that favored the deterministic
   arms, summaries reached only parity — never advantage — at 3–5× cost (§5). (Moderate-high
   confidence; the RFC and GDPR results are objective, but single-run and single-navigator.)
4. **Deterministic structure beats paid inference where authored structure exists** —
   Markdown headings or a PDF's embedded outline give an equal-or-better tree for $0
   vs $6.44 (high confidence for this document class: born-digital, well-bookmarked).
5. **Representation (PDF vs Markdown) mattered far less than structure-acquisition method
   and summary regime** (−0.09 recall at cost parity, partly a scoring-granularity artifact).

Guardrails — do **not** claim: PageIndex vs vector RAG (no baseline was run); "summaries
are useless" (they helped the website corpus); "Sonnet is better than gpt-4o" in general
(scoped to navigation behavior on this corpus); any category-level rate as statistically
powered (2–6 questions per cell); generalization of the $0-deterministic-tree result to
**scanned or image-only PDFs** (for GDPR's outline-less EUR-Lex PDF we recovered headings
from its *text layer* — still $0, and it matched or beat the summary arm, §5 — but a scanned
PDF has no text layer to recover, so that route would not apply).

Known weaknesses of the evidence: subjective 0–5 scoring is n=1 per cell with non-blind
judges (website corpus); most runs are single-shot (the paper pair and the twice-replicated
IDX-D RFC arm are the exceptions); all ground truth author-written; one navigator family
(gpt-4o) carried every index comparison. The GDPR evaluation carries four additional,
corpus-specific biases — question wording that telegraphed targets, a metric stacked against
summaries, two contestable recital answer keys, and one post-hoc answer-key change — all
detailed in §5.3.

---

## 8. Figures

| Figure | Shows |
|---|---|
| `figures/results-tree-tax.svg` | Tree tokens re-sent per agent turn, by index condition and corpus (incl. GDPR) — the amplification mechanism |
| `figures/results-website-quality-cost.svg` | Website corpus: answer quality vs cost for IDX-D / IDX-C / IDX-C0 — C0 dominates C; headings are the value baseline |
| `figures/results-rfc-recall.svg` | RFC 9110 recall@fetch by category: summaries hurt (D vs C0); representation barely matters (D vs PDF-outline) |
| `figures/results-gdpr-paraphrase.svg` | GDPR: recall + fact-score for all three arms, original vs paraphrased questions — the summary gap narrows but doesn't close |

All four are generated by `scripts/render_results_figures.py --overwrite` from numbers
verified against `runs/`; regenerate them after any results change (they are derived
artifacts, never hand-edited).

---

## 9. Provenance: the 13 runs

| # | Run | Corpus | Index arm(s) | Navigator(s) | Q | Purpose | Est. $ |
|---|---|---|---|---|---|---|---|
| 1 | `20260709T202248Z` | site | IDX-D | gpt-4o | 3 | harness validation | n/a (pre-instrumentation) |
| 2 | `20260709T205438Z` | site | IDX-D | gpt-4o-mini, sonnet-4-5 | 1 | retriever smoke test | $0.10 |
| 3 | `20260709T222631Z` | site | IDX-D | gpt-4o, qwen2.5-7b | 3 | retriever pilot | $0.18 |
| 4 | `20260710T060453Z` | site | IDX-D, IDX-C, IDX-O | gpt-4o | 14 | index comparison | $7.52 |
| 5 | `20260710T062406Z` | site | IDX-C | sonnet-4-5, qwen (gpt-4o quota-failed) | 14 | retriever comparison | $7.17 |
| 6 | `20260710T065513Z` | site | IDX-D | sonnet-4-5, qwen (gpt-4o quota-failed) | 14 | retriever comparison | $2.89 |
| 7 | `20260712T180445Z` | site | IDX-D, IDX-C, IDX-C0 | gpt-4o | 14 | threshold-0 counterfactual (scored) | $6.78 |
| 8 | `20260715T002754Z` | paper | PDF-vanilla, D, D-clean | gpt-4o | 8 | representation, rep 1 | $0.71 |
| 9 | `20260715T003239Z` | paper | PDF-vanilla, D, D-clean | gpt-4o | 8 | representation, rep 2 | $0.65 |
| 10 | `20260715T051258Z` | rfc9110 | IDX-D, IDX-C0 | gpt-4o | 24 | summary stress test (recall + facts) | $7.31 |
| 11 | `20260715T174748Z` | rfc9110 | IDX-D, IDX-PDF-outline | gpt-4o | 24 | representation study (recall) | $2.51 |
| 12 | `20260716T055341Z` | gdpr | IDX-D, IDX-PDF-textheadings, IDX-C0 | gpt-4o | 24 | summary + representation, original Qs (recall + facts) | $3.82 |
| 13 | `20260716T195845Z` | gdpr | IDX-D, IDX-PDF-textheadings, IDX-C0 | gpt-4o | 24 | paraphrased Qs — fair test for bias #1 (recall + facts) | $3.49 |

Every run folder carries `run.json` (full tool traces, per-question telemetry) and `run.md`
(human-readable). Corpus and index integrity are pinned by SHA-256 in each
`corpus/*/provenance.json` and `indexes/IDX-*/provenance.json`; PageIndex submodule at
`f413c66` throughout. Scoring artifacts: `evaluations/scores-master.csv` (runs 4–6),
`runs/20260712T180445Z/scores.csv` (run 7), `runs/20260715T051258Z/{recall,answer_facts}.csv`
(run 10), `runs/20260715T174748Z/recall.csv` (run 11),
`runs/20260716T055341Z/{recall,answer_facts}.csv` (run 12, telegraphed GDPR),
`runs/20260716T195845Z/{recall,answer_facts}.csv` (run 13, paraphrased GDPR).
Analysis notebooks (read-only layer) consume these directly — the two GDPR runs are already
in `runs/usage_log.jsonl` and carry `recall.csv`/`answer_facts.csv`, so `notebooks/*.ipynb`
pick them up with no code change (point notebooks 1–2's gold-set variable at
`evaluations/questions-gdpr.csv`).

### What's next

- **GDPR replication — done** (§5). Optional extension still open: an HTML-derived twin of the
  GDPR tree (a third representation, alongside Markdown and PDF-text-layer).
- **IDX-O0** (local threshold-0 summaries) and the P3 weak-navigator prediction.
- Repeatable multi-judge scoring (`scripts/score_run.py`) and n>1 for the subjective grid.
- Live capture of the prompt-cache write premium.
- Upstream issue **filed** ([VectifyAI/PageIndex#355](https://github.com/VectifyAI/PageIndex/issues/355),
  2026-07-15): the verbatim-copy summary semantics and the Markdown/PDF path divergence.
  Verified unchanged on upstream `main` (= `f413c66`) at filing; no prior report existed.
  Archived body: `reports/upstream-issue-draft.md`.

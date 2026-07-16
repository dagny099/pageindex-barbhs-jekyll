# PageIndex Website Experiment

An experiment harness for running [PageIndex](https://github.com/VectifyAI/PageIndex) —
an open-source, *vectorless, reasoning-based* RAG tool that builds a hierarchical
table-of-contents-style tree over a document (no chunking, no vector DB) — against a
frozen Markdown snapshot of the [barbhs.com](https://barbhs.com) website.

**Research question:** How do source structure, index-generation model, and retrieval
model affect what an AI system can accurately recover, connect, and explain about a
curated body of professional work? The design deliberately separates two frequently
conflated tasks: **building a map of knowledge** and **reasoning over that map**.

The full experimental brief, question set, evaluation rubric, and run log live in the
interactive lab notebook: [`reports/experimental-brief-lab-notebook.html`](reports/experimental-brief-lab-notebook.html)
(open it in a browser; notes save to `localStorage`).

> **Cheat sheet:** [RUNBOOK.md](RUNBOOK.md) — every command for building conditions,
> running retrieval, and analyzing results, with what each does for you.

## How it works

The website is flattened into a single derived Markdown "book" (`site-book-v1.md`),
PageIndex reads that book and emits a nested tree of nodes, and we curate the raw
output into named index variants for evaluation.

```
website source  →  corpus/site-book-v1.md  →  PageIndex  →  results/  →  indexes/IDX-*
   (barbhs.com)      (derived corpus)          (tree gen)    (raw run)   (curated variants)
```

## Corpus source & authority

Two frozen corpora, two producers — but the same discipline for both: **never hand-edit
`corpus/`**; fix the producer pipeline and rebuild.

**site-book-v1 (website corpus) is produced elsewhere.** It is built by a pipeline in the
website repo at `dagny099.github.io/experiments/pageindex/` (build/validate scripts,
selection config, normalization tests, and the QC/normalization reports). That repo is the
**authoritative producer**; the original website source files remain authoritative over the
corpus. This repo pins the exact snapshot it consumes in
[`corpus/site-book-v1/provenance.json`](corpus/site-book-v1/provenance.json): source repo,
source path, `website_commit`, `pageindex_commit`, and SHA256s of the corpus and manifest.
**To change it, fix the pipeline in the website repo, then re-sync here.** See
[CLAUDE.md](CLAUDE.md) for the re-sync workflow.

**paper-book-v1 (paper corpus) is produced in this repo** — a deliberate exception, since
its source is not website content but a frozen academic PDF (Ehinger, Hidalgo-Sotelo,
Torralba, & Oliva, 2009, *Visual Cognition*, DOI 10.1080/13506280902834720) pinned by
SHA-256 at `sources/paper-2009/`. The deterministic producer is
[`scripts/build_paper_book.py`](scripts/build_paper_book.py) with all extraction rules in
[`config/paper-book-v1.yml`](config/paper-book-v1.yml); rebuilding yields a byte-identical
book against the pinned PyMuPDF version. Extraction issues and open questions are
enumerated in [`reports/qc-paper-book-v1.md`](reports/qc-paper-book-v1.md).

```bash
# Rebuild the paper book (refuses to overwrite without the flag)
.venv/bin/python scripts/build_paper_book.py --overwrite

# Validate hashes, heading hierarchy, page map, placeholders, furniture
.venv/bin/python scripts/validate_paper_book.py
python3 -m pytest tests/test_build_paper_book.py
```

## Experimental design

Two axes, held one-at-a-time (not a full factorial to start):

**Index-generation conditions** — how the tree over the corpus is built:

| Condition | Index model | Summaries | Purpose |
|-----------|-------------|-----------|---------|
| **IDX-D** | None — Markdown headings (**D**eterministic) | No | Source-structure baseline |
| **IDX-C** | A capable **C**loud model | Yes | Generated summaries over a fixed hierarchy |
| **IDX-O** | A local **O**llama model | Yes | Local viability, JSON reliability, speed |

**Retrieval / answer-generation conditions** — which model navigates the index:
`RET-OAI` (OpenAI), `RET-ANT` (Anthropic), `RET-OLL` (Ollama, tool-capable).

Evaluated against a frozen **14-question set** across 5 categories (direct location ×4,
cross-section synthesis ×3, consistency ×2, evidence gap ×3, reflective discovery ×2),
scored on a 5-layer rubric (preprocessing / index / retrieval / answer / operational).
The frozen set — with per-question `expected_evidence` and `ground_truth` — lives in
[`evaluations/questions.csv`](evaluations/questions.csv) and is read directly by the
retrieval harness (`scripts/run_retrieval.py`).

### What the two objective metrics mean

The long-document arms (RFC 9110, GDPR) add two **judge-free** metrics that pull apart
*finding* from *being right*:

- **Recall@fetch — did the retriever open the right pages?** We pre-label, by hand, the
  sections that actually contain each answer; recall is the fraction the agent fetched while
  answering. It grades **navigation, not the answer** — an open-book exam where we marked the
  pages and check whether the student turned to them.
- **Fact-score — was the answer actually correct?** The fraction of a question's required
  facts (concrete atoms like status codes and header names) present in the final answer.

*Example (RA1):* *"Which status code marks a new permanent URI, and what header conveys it?"*
The answer must contain **`301`** and **`Location`** (fact-score), and that text lives in RFC
**§15.4.2** and **§10.2.2** (recall). The two can diverge — a model can answer correctly from
a summary without opening those sections, or open them yet answer poorly — which is why both
are reported. Full definitions and the worked example are in
[`reports/RESULTS.md` §1.3](reports/RESULTS.md).

## Layout

| Path | What it is |
|------|------------|
| `corpus/site-book-v1/` | Frozen input corpus (Markdown book stitched from 26 website documents) + `manifest.json` + `provenance.json`. Consumed, not produced here. |
| `corpus/paper-book-v1/` | Frozen paper corpus (Markdown book derived from the 2009 *Visual Cognition* PDF) + manifest + provenance. Produced **in this repo** by `scripts/build_paper_book.py`. |
| `sources/paper-2009/` | The frozen source PDF, pinned by SHA-256 in `config/paper-book-v1.yml`. |
| `indexes/IDX-<letter>/index.json` | Curated, evaluated index variants — one per index condition, each with its own `provenance.json`. Includes the deterministic (`IDX-D-*`), cloud-summary (`IDX-C`/`IDX-C0-*`), and PDF-derived (`IDX-PDF-outline-*`, `IDX-PDF-textheadings-*`) arms across all four corpora. |
| `results/` | Raw PageIndex run output (gitignored scratch). |
| `reports/` | Experimental brief / lab notebook, the consolidated results (`RESULTS.md`), figures, the Index Comparison Explorer (`V1_INDEX_COMPARISON.html`), index outlines, alignment report. (Corpus QC & normalization reports live in the website repo.) |
| `tests/` | pytest suite for repo tooling (paper-book build, explorer generator). Run with `python -m pytest`. |
| `notebooks/` | Read-only **analysis** notebooks (cost dashboard, cross-condition explorer, gold validator, single-run analysis) — numbered by lifecycle. See [`notebooks/README.md`](notebooks/README.md). |
| `vendor/PageIndex/` | The PageIndex tool, pinned as a git submodule. |
| `config/` | Build/run configs (corpus builders, index conditions, Ollama Modelfiles). |
| `evaluations/` | Frozen question sets (one CSV per corpus) + scoring artifacts. |
| `runs/` | One folder per retrieval run (`run.json`, `recall.csv`, `answer_facts.csv`) + the `usage_log.jsonl` cost ledger. |
| `scripts/` | The tested producer layer: corpus builders, index builders, the retrieval harness, and the scorers. |

## Index Comparison Explorer (V1 inspection tool)

**Open [`reports/V1_INDEX_COMPARISON.html`](reports/V1_INDEX_COMPARISON.html) directly in a
browser** — no server, no network, no framework; everything (data, corpus text, CSS, JS) is
embedded in the one file.

**What it is for:** the qualitative half of the V1 question — reading the IDX-C and IDX-O
summaries beside their Markdown source sections and judging whether generated summaries are
faithful, specific, and boundary-respecting. It is an *inspection* tool over the frozen
artifacts, **not** a results dashboard and **not** a retrieval system, and it never calls a
model — all automatic "review signals" are deterministic heuristics (numbers/entities/status
terms in a summary that don't appear in the source, near-duplicate or outlier-length
summaries), surfaced as *prompts for review, never verdicts*.

**How alignment works:** the three indexes were verified at build time to share an identical
339-node structure (same node IDs, titles, line ranges), so nodes align **exact** by node ID —
see [`reports/V1_INDEX_ALIGNMENT_REPORT.md`](reports/V1_INDEX_ALIGNMENT_REPORT.md) for the
evidence. The generator still handles drifted inputs conservatively (heading-path fallback →
`probable`; title/ID conflicts → `divergent`/`ambiguous`; no counterpart → `unmatched`, shown,
never silently dropped) so it stays honest if an index is ever regenerated.

**Review flags** (Faithful / Too generic / Misleading / Missing distinction / Boundary
problem / Needs review) attach per summary — a node's IDX-C and IDX-O summaries are flagged
independently — plus an optional free-text note per node. Flags live in the browser's
`localStorage`, keyed to the corpus SHA-256 so stale flags never silently reattach after a
corpus change. **Export flags → JSON** (header button) before clearing browser data; the
export identifies nodes by stable `node_id·path-hash` review keys and can be re-imported
later. Keyboard-driven review loop: `j`/`k` move, `n` = next unreviewed summary, `c`/`o` pick
a condition card, `1`–`6` toggle flags, `/` search, `?` help. `#node=0081` deep-links a node.

**Suggested first review:**

1. Open the HTML; read the onboarding panel and legend.
2. Check "Signals only" to see the nodes the heuristics flagged (~30 per condition).
3. Inspect a few on the **Summary inspection** tab — green marks are terms found in the
   source section, amber marks are not (verify those against the source).
4. Search (`/`) for one known project or article and compare IDX-C vs IDX-O against source.
5. Flag misleading or generic summaries as you go (`1`–`6`); add notes for anything subtle.
6. **Export flags** before clearing browser storage or switching machines.

**Regenerate after an index or corpus change** (also refreshes the outlines in
`reports/index-outlines/` and the alignment report):

```bash
python scripts/render_index_comparison.py --overwrite
# explicit paths (defaults shown); discovery fails safely if candidates are ambiguous
python scripts/render_index_comparison.py \
  --idx-d indexes/IDX-D/index.json --idx-c indexes/IDX-C/index.json \
  --idx-o indexes/IDX-O/index.json \
  --corpus corpus/site-book-v1/site-book-v1.md \
  --output reports/V1_INDEX_COMPARISON.html --overwrite
python -m pytest tests/test_render_index_comparison.py   # sanity-check the generator
```

**Explorer roadmap (deferred by design, in likely priority order):**

- **Question overlays** — project the 14 frozen evaluation questions onto the tree: which
  nodes hold each question's `expected_evidence`, so index quality can be read against the
  question set.
- **Retrieval-trace visualization** — overlay actual `runs/<timestamp>/` retrieval paths on
  the document map to connect summary quality to retrieval behavior (the quantitative half).
- **Flag aggregation** — a small script summarizing exported review-flag JSON into per-
  condition faithfulness tables for the lab notebook.
- **C-vs-O phrase diff** — deliberately dropped from V1: two independently generated
  paragraphs differ at nearly every word, so a textual diff is noise; targeted term
  highlighting (implemented) replaced it. Revisit only with a smarter semantic alignment.
- **LLM-assisted faithfulness checks** — excluded on principle from report generation;
  if added ever, as a separate, clearly-labeled offline pass, never inline.

## Running PageIndex

Prereqs: Python 3.12 (`.venv/` is checked out locally), the PageIndex submodule, and an LLM API key.

```bash
# 1. Fetch the pinned PageIndex submodule (first checkout only)
git submodule update --init --recursive

# 2. Activate the environment
source .venv/bin/activate

# 3. (Only for model-based conditions — IDX-D below needs no key.)
#    Provide an API key: cp .env.example .env  and fill it in.
#    The repo-root .env is auto-loaded (python-dotenv walk-up); see .env.example.

# 4. Generate the deterministic (IDX-D) tree from the corpus
#    (built purely from Markdown headings — no LLM call, no API key needed)
cd vendor/PageIndex
python3 run_pageindex.py --md_path ../../corpus/site-book-v1/site-book-v1.md \
  --if-add-node-summary no --if-add-doc-description no --if-add-node-text yes
# → writes results/site-book-v1_structure.json inside vendor/PageIndex/results/
```

Generation behavior (model, summaries, node IDs, thinning) is controlled by
`vendor/PageIndex/pageindex/config.yaml` and overridable via CLI flags. The default
model is `gpt-4o-2024-11-20`. Raw runs land in `results/`; curated variants are saved
to `indexes/IDX-<letter>/index.json`.

### Summary threshold experiments

For Markdown input, PageIndex does **not** call the model for every node by default.
When `--if-add-node-summary yes` is set, nodes whose text is below
`--summary-token-threshold` are copied verbatim into `summary` / `prefix_summary`;
only nodes at or above the threshold get an LLM-generated summary. The current
IDX-C / IDX-O runs used the default threshold of `200`.

**Measured impact:** at the default threshold, ~80% of summaries end up as verbatim
copies of node text (273/339 nodes in IDX-C, 272/339 in IDX-O), and because the
retriever's tree dump keeps `summary` after stripping `text`, the tree re-sent on every
turn is ~4.9× the heading-only baseline (~43.7K vs ~8.9K tokens). The full mechanism,
numbers, upstream-vs-ours attribution, and reproduce steps are written up in
[`reports/findings-summary-threshold.md`](reports/findings-summary-threshold.md).

Use `--summary-token-threshold 0` when you want a cleaner "generated summaries over
headings" condition:

```bash
# Cloud summarizer: force a generated summary for every node
cd vendor/PageIndex
python3 run_pageindex.py --md_path ../../corpus/site-book-v1/site-book-v1.md \
  --model gpt-4o-2024-11-20 \
  --if-add-node-summary yes --if-add-doc-description yes --if-add-node-text yes \
  --summary-token-threshold 0

# Keep this separate from IDX-C unless intentionally replacing it.
mkdir -p ../../indexes/IDX-C0
cp results/site-book-v1_structure.json ../../indexes/IDX-C0/index.json
```

```bash
# Local Ollama summarizer: same idea, but expect a much slower run
cd vendor/PageIndex
python3 run_pageindex.py --md_path ../../corpus/site-book-v1/site-book-v1.md \
  --model ollama_chat/qwen2.5-7b-instruct-ctx32k \
  --if-add-node-summary yes --if-add-doc-description yes --if-add-node-text yes \
  --summary-token-threshold 0

mkdir -p ../../indexes/IDX-O0
cp results/site-book-v1_structure.json ../../indexes/IDX-O0/index.json
```

Interpretation rule of thumb: threshold `200` evaluates headings plus copied short
section text plus generated summaries for longer nodes; threshold `0` evaluates
headings plus generated summaries for every node.

## Local models (Ollama) — required setup for IDX-O / RET-OLL

The local conditions (`IDX-O` index, `RET-OLL` retriever) need a running Ollama service
**and an enlarged-context derived model**. This is not optional: Ollama's default context
window (~2–4K tokens) truncates the ~9K-token index tree, so the retriever would navigate
a blind, half-read index. Build the derived model once per machine:

```bash
ollama pull llama3.1:8b
ollama create llama3.1-8b-ctx32k -f config/ollama/llama3.1-8b-ctx32k.Modelfile
```

Then use it: retriever `ollama_chat/llama3.1-8b-ctx32k` (the `ollama_chat/` prefix is the
tool-calling path), index model `ollama/llama3.1-8b-ctx32k`. The Modelfile
(`config/ollama/llama3.1-8b-ctx32k.Modelfile`) documents the `num_ctx` rationale and is the
single source to rebuild on a new machine. Larger `num_ctx` uses more RAM — tune to your box.

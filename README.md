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

## How it works

The website is flattened into a single derived Markdown "book" (`site-book-v1.md`),
PageIndex reads that book and emits a nested tree of nodes, and we curate the raw
output into named index variants for evaluation.

```
website source  →  corpus/site-book-v1.md  →  PageIndex  →  results/  →  indexes/IDX-*
   (barbhs.com)      (derived corpus)          (tree gen)    (raw run)   (curated variants)
```

## Corpus source & authority

**This repo does not produce the corpus — it consumes a frozen snapshot of it.**

The corpus is built by a pipeline that lives in the website repo at
`dagny099.github.io/experiments/pageindex/` (build/validate scripts, selection config,
normalization tests, and the QC/normalization reports). That repo is the **authoritative
producer**; the original website source files remain authoritative over the corpus.

This repo pins the exact snapshot it consumes in
[`corpus/site-book-v1/provenance.json`](corpus/site-book-v1/provenance.json): source repo,
source path, `website_commit`, `pageindex_commit`, and SHA256s of the corpus and manifest.
**To change the corpus, fix the pipeline in the website repo, then re-sync here** — never
hand-edit `corpus/`. See [CLAUDE.md](CLAUDE.md) for the re-sync workflow.

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

Evaluated against a frozen **15-question set** across 5 categories (direct location,
cross-section synthesis, consistency, evidence gap, reflective discovery), scored on a
5-layer rubric (preprocessing / index / retrieval / answer / operational).

## Layout

| Path | What it is |
|------|------------|
| `corpus/site-book-v1/` | Frozen input corpus (Markdown book stitched from 26 website documents) + `manifest.json` + `provenance.json`. Consumed, not produced here. |
| `indexes/IDX-<letter>/index.json` | Curated, evaluated index variants. Currently: `IDX-D` (Deterministic). |
| `results/` | Raw PageIndex run output (gitignored scratch). |
| `reports/` | Experimental brief / lab notebook. (Corpus QC & normalization reports live in the website repo.) |
| `vendor/PageIndex/` | The PageIndex tool, pinned as a git submodule. |
| `config/` `evaluations/` `runs/` `scripts/` | Scaffolding for run configs, eval harnesses, reporting (currently empty). |

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

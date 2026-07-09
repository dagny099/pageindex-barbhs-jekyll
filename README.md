# PageIndex Website Experiment

An experiment workspace for running [PageIndex](https://github.com/VectifyAI/PageIndex) —
an open-source, *vectorless, reasoning-based* RAG tool that builds a hierarchical
table-of-contents-style tree over a document (no chunking, no vector DB) — against a
frozen snapshot of the [barbhs.com](https://barbhs.com) website.

The goal is to study how PageIndex builds a navigable hierarchy over website content,
and to compare index variants (different node fields, summaries, thinning settings)
against the same reproducible corpus.

## How it works

The website is flattened into a single derived Markdown "book" (`site-book-v1.md`),
PageIndex reads that book and emits a nested tree of nodes, and we curate the raw
output into named index variants for evaluation.

```
website source  →  corpus/site-book-v1.md  →  PageIndex  →  results/  →  indexes/IDX-*
   (barbhs.com)      (derived corpus)          (tree gen)    (raw run)   (curated variants)
```

## Layout

| Path | What it is |
|------|------------|
| `corpus/site-book-v1/` | The input corpus. `site-book-v1.md` is a single Markdown book stitched from 26 website source documents (4 core pages, 6 projects, 10 articles, 6 resources). Ships with a `manifest.json` (heading transformations, per-document SHA256s) and `provenance.json` (pins the exact website + PageIndex commits). |
| `indexes/IDX-D/index.json` | A curated, structure-only index variant: `title` / `text` / `node_id` / `line_num` per node, no summaries. |
| `results/site-book-v1_structure.json` | Raw PageIndex output (default location), including per-node `summary` / `prefix_summary` and a `doc_description`. |
| `vendor/PageIndex/` | The PageIndex tool, pinned as a git submodule at a fixed commit. |
| `config/` `evaluations/` `reports/` `runs/` `scripts/` | Scaffolding for run configs, eval harnesses, and reporting (currently empty). |

## Reproducibility

Every artifact is content-hashed and pinned to exact commits:

- `corpus/site-book-v1/provenance.json` records `website_commit`, `pageindex_commit`,
  `corpus_sha256`, and `synced_at`.
- `.gitmodules` pins `vendor/PageIndex` to a specific upstream commit.
- The corpus is explicitly **derived and experimental** — the original website source
  files remain authoritative.

## Running PageIndex

Prereqs: Python 3.12 (a `.venv/` is checked out locally), the PageIndex submodule,
and an LLM API key.

```bash
# 1. Fetch the pinned PageIndex submodule (first checkout only)
git submodule update --init --recursive

# 2. Activate the environment
source .venv/bin/activate

# 3. Provide an API key for PageIndex (LiteLLM-compatible; OpenAI by default)
#    Create vendor/PageIndex/.env with e.g.:
#    OPENAI_API_KEY=sk-...

# 4. Generate a tree from the corpus
cd vendor/PageIndex
python3 run_pageindex.py --md_path ../../corpus/site-book-v1/site-book-v1.md
# → writes results/site-book-v1_structure.json inside vendor/PageIndex/results/
```

Generation behavior (model, node summaries, node IDs, thinning) is controlled by
`vendor/PageIndex/pageindex/config.yaml` and overridable via CLI flags
(`--model`, `--if-add-node-summary`, `--if-add-node-text`, `--if-thinning`, …).
The default model is `gpt-4o-2024-11-20`.

## Index variants

Raw runs land in `results/`. Curated variants — the artifacts we actually evaluate —
live under `indexes/IDX-<letter>/index.json`. `IDX-D` is a structure-only variant
(headings + text, no summaries) derived from the same 369-node tree as the raw run.

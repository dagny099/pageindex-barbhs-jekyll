# CLAUDE.md

Guidance for Claude Code when working in this repo. See `README.md` for the human-facing overview.

## What this repo is

An experiment harness for running [PageIndex](https://github.com/VectifyAI/PageIndex)
(vectorless, reasoning-based RAG that builds a hierarchical tree over a document)
against a frozen Markdown snapshot of the barbhs.com website. We compare index
variants over one reproducible corpus.

## Key facts

- **Python 3.12**, local `.venv/` (not committed). Key packages: `openai`, `tiktoken`, `pydantic`, `pyyaml`.
- **PageIndex is a git submodule** at `vendor/PageIndex/`, pinned via `.gitmodules`. Do **not** edit files inside it — it's vendored upstream. If it's missing, run `git submodule update --init --recursive`.
- PageIndex needs an LLM API key in `vendor/PageIndex/.env` (LiteLLM-compatible; `OPENAI_API_KEY` by default). Never commit keys — `.env` is gitignored.
- Generation config lives in `vendor/PageIndex/pageindex/config.yaml` (default model `gpt-4o-2024-11-20`); CLI flags override it.

## The corpus is authoritative-by-hash — do not hand-edit it

`corpus/site-book-v1/site-book-v1.md` is a **derived** artifact whose SHA256 is pinned
in both `provenance.json` and `site-book-v1.manifest.json`. Do not edit it by hand — it
is regenerated upstream from the website source. If the corpus changes, its hashes and
provenance must change together. Treat `corpus/` as read-only unless the task is
explicitly about re-syncing the corpus.

## Artifacts: raw runs vs. curated indexes

- **Raw output** → `results/<doc_name>_structure.json`. This is PageIndex's default write
  location and includes `summary`, `prefix_summary`, and `doc_description`.
- **Curated variants** → `indexes/IDX-<letter>/index.json`. Named, evaluated variants
  derived from a run. `IDX-D` is structure-only: nodes carry `title` / `text` /
  `node_id` / `line_num`, no summaries or doc description. Same 369-node tree as the raw run.

When creating a new variant, follow the `indexes/IDX-<letter>/index.json` convention and
keep the node schema consistent within a variant.

## Common commands

```bash
# Generate a tree from the corpus (writes to vendor/PageIndex/results/)
cd vendor/PageIndex && python3 run_pageindex.py --md_path ../../corpus/site-book-v1/site-book-v1.md

# Validate any index JSON is well-formed
python3 -c "import json,sys; json.load(open(sys.argv[1])); print('ok')" indexes/IDX-D/index.json
```

## Conventions

- `indexes/` is tracked (committed); `results/`, `logs/`, `workspace(s)/` are gitignored — they're scratch/raw.
- Commit only what the task calls for. Don't commit `.venv/`, `.env`, `.DS_Store`, or anything under `vendor/PageIndex/results/`.
- The scaffolding dirs (`config/`, `evaluations/`, `reports/`, `runs/`, `scripts/`) are currently empty; populate them as the experiment grows rather than scattering files at the root.
- Preserve reproducibility: any new corpus or index artifact should carry or reference its provenance (source commit + hash).

# CLAUDE.md

Guidance for Claude Code when working in this repo. See `README.md` for the human-facing overview.

## What this repo is

An experiment harness for running [PageIndex](https://github.com/VectifyAI/PageIndex)
(vectorless, reasoning-based RAG that builds a hierarchical tree over a document)
against a frozen Markdown snapshot of the barbhs.com website. The full experimental
design lives in `reports/experimental-brief-lab-notebook.html`.

## Key facts

- **Python 3.12**, local `.venv/` (not committed). Key packages: `openai`, `tiktoken`, `pydantic`, `pyyaml`.
- **PageIndex is a git submodule** at `vendor/PageIndex/`, pinned via `.gitmodules`. Do **not** edit files inside it — it's vendored upstream. If missing, run `git submodule update --init --recursive`.
- Model-based conditions need an LLM API key in the **repo-root `.env`** (auto-loaded by python-dotenv's walk-up when running from `vendor/PageIndex/`; `.env.example` is the committed template). The deterministic **IDX-D** needs no key. Never commit keys — `.env` is gitignored.
- Generation config lives in `vendor/PageIndex/pageindex/config.yaml` (default model `gpt-4o-2024-11-20`); CLI flags override it.

## The corpus is produced ELSEWHERE — do not hand-edit it

`corpus/site-book-v1/` is a **frozen, consumed snapshot**, not a source. The corpus is
built by a pipeline in the website repo at `dagny099.github.io/experiments/pageindex/`
(scripts, config, tests, QC/normalization reports). That repo is the authoritative producer.

- **To change the corpus, fix the pipeline in the website repo, rebuild + revalidate there,
  then re-sync into this repo.** Never edit `corpus/site-book-v1.md` or its manifest by hand.
- The snapshot is pinned in `corpus/site-book-v1/provenance.json`: `source_repo`, `source_path`,
  `website_commit`, `pageindex_commit`, `corpus_sha256`, `normalization_manifest_sha256`, `synced_at`.

### Re-sync procedure

1. `cp` the corpus `.md` and `.manifest.json` verbatim from the website repo's
   `experiments/pageindex/corpus/` into `corpus/site-book-v1/` (preserve bytes so hashes match).
2. Recompute both SHA256s and update `provenance.json` (`corpus_sha256`,
   `normalization_manifest_sha256`, `website_commit`, `synced_at`).
3. Verify the on-disk files hash to the values in `provenance.json`.
4. **Any existing index is now stale** — the corpus changed underneath it. Regenerate
   affected `indexes/IDX-*` and mark stale ones (see the STALE.md convention).

## Index conditions and variants

Variant letters encode the **index-generation condition**, not a sequence:

- **IDX-D** = **D**eterministic (Markdown headings, no generated summaries). Node schema:
  `title` / `text` / `node_id` / `line_num`. The baseline most sensitive to heading fidelity.
- **IDX-C** = capable **C**loud model, with summaries (planned).
- **IDX-O** = local **O**llama model, with summaries (planned).

Only **IDX-D** exists so far. **It is currently STALE** — built from a pre-audit corpus;
see `indexes/IDX-D/STALE.md`. Regenerate it after the corpus is finalized, then delete
the marker. Raw runs write to `results/<doc_name>_structure.json` (includes `summary`,
`prefix_summary`, `doc_description`); curated variants live in `indexes/IDX-<letter>/index.json`.

## Common commands

```bash
# Generate the deterministic (IDX-D) tree (writes to vendor/PageIndex/results/)
# Markdown-heading tree only: no LLM call, no API key. Curate result into indexes/IDX-D/.
cd vendor/PageIndex && python3 run_pageindex.py --md_path ../../corpus/site-book-v1/site-book-v1.md \
  --if-add-node-summary no --if-add-doc-description no --if-add-node-text yes

# Verify an index/corpus JSON is well-formed
python3 -c "import json,sys; json.load(open(sys.argv[1])); print('ok')" indexes/IDX-D/index.json

# Verify corpus on disk matches pinned provenance hashes
python3 -c "import json,hashlib as h; p=json.load(open('corpus/site-book-v1/provenance.json')); \
print('corpus', p['corpus_sha256']==h.sha256(open('corpus/site-book-v1/site-book-v1.md','rb').read()).hexdigest()); \
print('manifest', p['normalization_manifest_sha256']==h.sha256(open('corpus/site-book-v1/site-book-v1.manifest.json','rb').read()).hexdigest())"
```

## Conventions

- `indexes/` is tracked (committed); `results/`, `logs/`, `workspace(s)/` are gitignored scratch.
- Don't commit `.venv/`, `.env`, `.DS_Store`, or anything under `vendor/PageIndex/results/`.
- Scaffolding dirs (`config/`, `evaluations/`, `runs/`, `scripts/`) are currently empty; populate them as the experiment grows rather than scattering files at the root.
- Any new corpus or index artifact must carry or reference its provenance (source commit + hash).

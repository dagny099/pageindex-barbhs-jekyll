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
  `title` / `text` / `node_id` / `line_num`. The baseline most sensitive to heading fidelity. **Built.**
- **IDX-C** = capable **C**loud model (gpt-4o), with summaries + doc description. **Built.**
- **IDX-O** = local **O**llama model (qwen2.5), with summaries. **Built.** Requires a running
  Ollama service and the enlarged-context derived model (`ollama create qwen2.5-7b-instruct-ctx32k
  -f config/ollama/qwen2.5-7b-instruct-ctx32k.Modelfile`) — Ollama's default context truncates the
  ~9K-token tree. qwen2.5 (not llama3.1, which fabricates tool calls) also serves as the RET-OLL
  retriever. See `config/index-conditions.yml` and `reports/findings-retriever-prompt-revision.md`.

All three index conditions (IDX-D / IDX-C / IDX-O) are built; the 14-question evaluation set is
frozen in `evaluations/questions.csv`. Retrieval runs record to `runs/<timestamp>/`.

Each built index carries `indexes/IDX-*/provenance.json` (pins `corpus_sha256`, model, flags)
so staleness against the corpus is detectable. Raw runs write to
`results/<doc_name>_structure.json`; curated variants live in `indexes/IDX-<letter>/index.json`.
Retrieval over an index uses `scripts/run_retrieval.py` (OpenAI Agents SDK; non-OpenAI
retrievers via LiteLLM, e.g. `ollama_chat/llama3.1-8b-ctx32k` or `anthropic/…`).

## Common commands

```bash
# Generate the deterministic (IDX-D) tree (writes to vendor/PageIndex/results/)
# Markdown-heading tree only: no LLM call, no API key. Curate result into indexes/IDX-D/.
cd vendor/PageIndex && python3 run_pageindex.py --md_path ../../corpus/site-book-v1/site-book-v1.md \
  --if-add-node-summary no --if-add-doc-description no --if-add-node-text yes

# Verify an index/corpus JSON is well-formed
python3 -c "import json,sys; json.load(open(sys.argv[1])); print('ok')" indexes/IDX-D/index.json

# Regenerate the Index Comparison Explorer + outlines + alignment report
# (self-contained offline HTML; no LLM calls; refuses to overwrite without the flag)
python3 scripts/render_index_comparison.py --overwrite
python3 -m pytest tests/test_render_index_comparison.py

# Verify corpus on disk matches pinned provenance hashes
python3 -c "import json,hashlib as h; p=json.load(open('corpus/site-book-v1/provenance.json')); \
print('corpus', p['corpus_sha256']==h.sha256(open('corpus/site-book-v1/site-book-v1.md','rb').read()).hexdigest()); \
print('manifest', p['normalization_manifest_sha256']==h.sha256(open('corpus/site-book-v1/site-book-v1.manifest.json','rb').read()).hexdigest())"
```

## Conventions

- `indexes/` is tracked (committed); `results/`, `logs/`, `workspace(s)/` are gitignored scratch.
- Don't commit `.venv/`, `.env`, `.DS_Store`, or anything under `vendor/PageIndex/results/`.
- Keep new tooling in `scripts/` (tests in `tests/`) rather than scattering files at the repo root.
- Any new corpus or index artifact must carry or reference its provenance (source commit + hash).
- `reports/V1_INDEX_COMPARISON.html`, `reports/index-outlines/IDX-*.md`, and
  `reports/V1_INDEX_ALIGNMENT_REPORT.md` are **derived** from the indexes + corpus by
  `scripts/render_index_comparison.py` — regenerate them (`--overwrite`), never hand-edit.
  After any index/corpus change these are stale until regenerated. See the README's
  "Index Comparison Explorer" section for usage, review workflow, and the tool's roadmap.

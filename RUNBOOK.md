# RUNBOOK — commands for the main experiment conditions

One page: what to run, and what each command *does for you*. Details live in
`README.md` / `CLAUDE.md`; findings live in `reports/`.

## 0. One-time setup

```bash
git submodule update --init --recursive   # fetch pinned PageIndex (vendor/PageIndex)
source .venv/bin/activate                 # project env (python 3.12)
cp .env.example .env                      # then add your API key(s); IDX-D needs none
```

## 1. Corpora — verify before trusting

```bash
# site-book-v1: on-disk bytes match the pinned provenance hashes
python3 -c "import json,hashlib as h; p=json.load(open('corpus/site-book-v1/provenance.json')); \
print('corpus', p['corpus_sha256']==h.sha256(open('corpus/site-book-v1/site-book-v1.md','rb').read()).hexdigest())"

# paper-book-v1: rebuild (byte-identical) + full validation
.venv/bin/python scripts/build_paper_book.py --overwrite
.venv/bin/python scripts/validate_paper_book.py
```

*Does for you:* proves the frozen inputs are exactly what the indexes and
provenance claim — the first line of "I know where my results came from."

## 2. Build an index condition

```bash
cd vendor/PageIndex

# IDX-D — deterministic headings, no LLM, no key
python3 run_pageindex.py --md_path ../../corpus/site-book-v1/site-book-v1.md \
  --if-add-node-summary no --if-add-doc-description no --if-add-node-text yes

# IDX-C0 — real gpt-4o summary for EVERY node (threshold 0 disables verbatim copies)
python3 run_pageindex.py --md_path ../../corpus/site-book-v1/site-book-v1.md \
  --if-add-node-summary yes --if-add-doc-description yes --if-add-node-text yes \
  --summary-token-threshold 0 --model gpt-4o-2024-11-20
```

**Always pass `--model` explicitly.** The CLI default (`None`) silently overrides
the `config.yaml` model in ConfigLoader's merge — you get
`litellm ... model parameter is required` storms (or worse, a wrong model).
**Always pass `--summary-token-threshold` explicitly** when summaries are on —
the default (200) copies short nodes' text verbatim instead of summarizing
(see `reports/findings-summary-threshold.md`).

*Does for you:* produces `vendor/PageIndex/results/<corpus>_structure.json` — the
raw tree for one experimental condition.

## 3. Curate the index (raw result → committed condition)

```bash
mkdir -p indexes/IDX-<ID>
cp vendor/PageIndex/results/site-book-v1_structure.json indexes/IDX-<ID>/index.json
# then write indexes/IDX-<ID>/provenance.json — pin: corpus_sha256, pageindex_commit,
# model (explicit), ALL effective flags incl. summary_token_threshold, node_count,
# summary_stats INCLUDING the verbatim-share check:
python3 - <<'PY'
import json
def walk(ns):
    for n in ns:
        yield n
        if n.get('nodes'): yield from walk(n['nodes'])
nodes=list(walk(json.load(open('indexes/IDX-C0/index.json'))['structure']))
verb=sum(1 for n in nodes if (str(n.get('summary') or n.get('prefix_summary') or '').strip())
        == str(n.get('text') or '').strip() and str(n.get('text') or '').strip())
print(f"verbatim summaries: {verb}/{len(nodes)} ({verb/len(nodes)*100:.1f}%)")
PY
```

*Does for you:* the verbatim check is the guardrail against the silent-threshold
class of surprise — every committed index carries the number that would have
exposed the IDX-C defect on day one. (Expect ~0% with threshold 0; IDX-C was 80.5%.)

## 4. Run retrieval (the experiment)

```bash
# Full grid: indexes × retrievers × all 14 questions (defaults: gpt-4o retriever, all questions)
.venv/bin/python scripts/run_retrieval.py --indexes IDX-D IDX-C IDX-C0 --cache on

# Variations
#   --retrievers gpt-4o-2024-11-20 anthropic/claude-sonnet-5 ollama_chat/qwen2.5-7b-instruct-ctx32k
#   --questions DL3 EG1              # subset for a smoke run
#   --temperature 0                  # pin sampling (used for cache parity checks)
```

*Does for you:* writes `runs/<timestamp>/run.json` + `run.md` (answers,
fetched ranges, per-call tokens) and appends per-call rows to
`runs/usage_log.jsonl`. **Caching (`--cache on`) changes cost/latency only,
never answers** — parity was proven in the V3A instrumentation work; leave it
ON to save money. Raw token counts are always logged, so uncached-equivalent
cost remains computable for any write-up.

## 5. Analyze cost

```bash
python3 scripts/cost_report.py           # per-condition input/output/cache tokens + $
python3 scripts/compare_runs.py runs/<tsA> runs/<tsB>   # merge split runs into one grid
```

*Does for you:* the re-send amplification view — input tokens climbing per agent
turn — and cost-per-question by condition; the numbers behind `reports/COST_NOTES.md`.

## 6. Score answers (currently a manual/agent step — not automated)

`evaluations/scores-master.csv` rows are
`qid,category,index,retriever,retrieval_score,answer_score,judge,note` — first
pass was scored by an agent against `evaluations/questions.csv` ground truth and
committed as a one-off. To score a new run: judge each answer in `runs/<ts>/run.md`
against the question's `ground_truth`/`expected_evidence`, append rows, and fill
`judge` honestly (who/what judged). A repeatable `scripts/score_run.py` LLM-judge
is planned once paper-corpus volume justifies it.

## 7. Inspect structure (before believing results)

```bash
python3 scripts/render_index_comparison.py --overwrite   # site-book explorer (IDX-D/C/O)
python3 -m pytest tests/                                 # tooling tests
```

*Does for you:* the eyes-on-the-tree step. For the paper corpus this becomes the
formal Prompt C gate (structure QC vs the paper-book manifest) before any
retrieval spend. Note: explorer is currently hardwired to three conditions
(D/C/O); generalizing it is part of the Prompt C tooling work.

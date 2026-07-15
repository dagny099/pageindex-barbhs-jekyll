# Runbook: representation study (Markdown vs PDF-outline) — build, retrieve, score

_Created 2026-07-15. Documents the tooling added in PR #8_
_(`scripts/build_pdf_outline_index.py`, `scripts/score_recall.py`). Commands assume you are_
_at the repo root: `/Users/bhs/PROJECTS/pageindex-website-experiment`._

---

## 0. The mental model

Everything is **three stages**. The key idea: *representation* (PDF vs Markdown) and
*structure-extraction method* (deterministic headings/outline vs LLM inference) are
**separate knobs** — don't conflate them.

```
① BUILD an index   →   ② RUN retrieval over it   →   ③ SCORE what it fetched
   (a tree of the        (an LLM agent navigates      (did it reach the gold
    document)             the tree to answer)          sections? objective, no judge)
```

An **index** is a tree of the document. Three ways to build that tree:

| Index kind | How structure is obtained | Cost | Addressing |
|---|---|---|---|
| `IDX-D` | deterministic from Markdown headings | $0, no LLM | line (`line_num`) |
| `IDX-PDF-outline` | deterministic from the PDF's embedded outline | $0, no LLM | page (`start/end_index`) |
| `IDX-C`, `IDX-PDF-vanilla` | LLM-inferred | $$$ | line / page |

The clean representation study compares the two **deterministic** arms
(`IDX-D-<doc>` vs `IDX-PDF-outline-<doc>`): same structure, differing only in addressing
and text fidelity. The LLM-inferred vanilla PDF tree is a *separate* question (it drops
section numbers and over-segments — a finding about the tool, not about PDFs).

## 0.1 Environment (one-time)

```bash
# API key lives in the repo-root .env (never committed). Model-based steps need it.
grep -q OPENAI_API_KEY .env && echo "key present"
```

**Two interpreters, on purpose — the #1 gotcha:**

- `.venv/bin/python` runs the **scripts** (has openai, fitz/PyMuPDF, litellm).
- `~/.pyenv/versions/3.12.2/bin/python` runs **pytest** (`.venv` has no pytest).

---

## 1. Build the two index arms

### 1a. PDF-outline arm (deterministic, ~$0)

```bash
.venv/bin/python scripts/build_pdf_outline_index.py \
  --pdf sources/rfc9110/rfc9110.pdf \
  --index-dir indexes/IDX-PDF-outline-rfc9110 \
  --twin IDX-D-rfc9110 \
  --overwrite
```

**Why:** reads the PDF's *embedded outline* (`fitz.get_toc()`) — the structure the PDF
already carries — instead of paying an LLM to guess it. `--index-dir` writes both
`index.json` and `provenance.json`. `--twin` records which Markdown index it should
structurally match. **Output:** `indexes/IDX-PDF-outline-rfc9110/`, page-addressed, every
node with real body text.

Offline check (no PDF, no cost): `.venv/bin/python scripts/build_pdf_outline_index.py --self-test`

### 1b. Markdown deterministic arm (`IDX-D`) — its structural twin

Already exists at `indexes/IDX-D-rfc9110/`. How an `IDX-D` is produced (headings only,
summaries OFF = no LLM):

```bash
.venv/bin/python scripts/build_index_metered.py \
  --md_path workspace/rfc9110.md \
  --if-add-node-summary no
# -> results/rfc9110_structure.json ; then curate by hand into indexes/IDX-D-<doc>/.
```

**Caveat:** the Markdown arm needs a `.md` rendering of the doc (for RFC 9110 this came from
an *ad-hoc* HTML→Markdown pass, not yet a committed script). The PDF-outline arm has no such
dependency.

### 1c. (Reference) LLM-inferred path + resumable metering

Not used for the clean study, but this is where cost metering and the **resumable cache** live:

```bash
# Pre-flight estimate + confirm, meter every call, hard-stop at a bound:
.venv/bin/python scripts/build_index_metered.py \
  --pdf_path sources/rfc9110/rfc9110.pdf --abort-over 8

# If it aborts (or to continue), RE-RUN with --resume: recorded calls replay for $0,
# only new calls hit the API. Ratchet the bound up until it finishes.
.venv/bin/python scripts/build_index_metered.py \
  --pdf_path sources/rfc9110/rfc9110.pdf --resume --abort-over 15 \
  --out results/rfc9110-pdf_structure.json
```

`--strict-resume` halts at the first uncached call (proves the cached prefix replays cleanly).
Cache lives in `runs/llm-cache/` (gitignored).

---

## 2. Run retrieval over the arms

```bash
# Smoke-test one cheap question first (RA1 ~= $0.04/arm):
.venv/bin/python scripts/run_retrieval.py \
  --indexes IDX-D-rfc9110 IDX-PDF-outline-rfc9110 \
  --retrievers gpt-4o-2024-11-20 \
  --questions-file evaluations/questions-rfc9110.csv \
  --questions RA1

# Full 25-question study (drop --questions to run them all):
.venv/bin/python scripts/run_retrieval.py \
  --indexes IDX-D-rfc9110 IDX-PDF-outline-rfc9110 \
  --retrievers gpt-4o-2024-11-20 \
  --questions-file evaluations/questions-rfc9110.csv
```

**Flags:**
- `--indexes` — the arms to compare (full cross-product with retrievers × questions).
  Addressing (line vs page) is **auto-detected per index** — no flag needed.
- `--retrievers` — hold fixed to isolate the *index* effect.
- `--questions-file` — **how you point at a gold set** (default is the site set; always pass
  this for RFC).
- `--questions` — optional subset by `id`; omit for all.

**Output:** `runs/<UTC-timestamp>/run.json` (answers + full tool trace) and `run.md`
(human-readable). Every LLM call is appended to `runs/usage_log.jsonl`.

---

## 3. Score what it fetched (objective, no LLM judge)

```bash
.venv/bin/python scripts/score_recall.py \
  --run runs/<TIMESTAMP> \
  --questions evaluations/questions-rfc9110.csv
```

**Why:** projects the *same* gold section-ids onto each index's own addressing (line-ranges
for Markdown, node-ids for PDF), then computes **recall@fetch** = did the retriever reach the
sections the answer needs. **Output:** a per-category table + `runs/<TIMESTAMP>/recall.csv`.
Watch the **`unmap_gold`** column — nonzero means that index's tree *lost* those section
labels (the signature of an LLM-inferred tree).

Offline check: `.venv/bin/python scripts/score_recall.py --self-test`

---

## 4. Check the cost

```bash
.venv/bin/python scripts/cost_report.py --run <RUN_ID>
```

Reconciles `runs/usage_log.jsonl` (logged vs recomputed cost, per index/retriever). Replayed
cache calls show `$0`; a `✓` means the ledger is exact.

---

## 5. Verify the code (before committing)

```bash
# Scripts' offline self-tests (free):
.venv/bin/python scripts/build_pdf_outline_index.py --self-test
.venv/bin/python scripts/score_recall.py --self-test

# Pytest suite (pyenv interpreter, NOT .venv):
~/.pyenv/versions/3.12.2/bin/python -m pytest \
  tests/test_build_pdf_outline_index.py tests/test_score_recall.py -q
```

---

## 6. Ship it (git workflow)

```bash
git checkout -b feat/<name>          # never commit straight to main
git add <specific files>             # stage deliberately, not `git add -A`
git commit -m "…"                    # repo appends Co-Authored-By / session lines
git push -u origin feat/<name>
gh pr create --base main --title "…" --body "…"
# Review the diff, then merge on GitHub (agent-authored merges are gate-blocked by design).
```

---

## 7. Replicate the whole thing on a NEW document

The payoff — the tooling is general. For a new bookmarked PDF `sources/<doc>/<doc>.pdf`:

```bash
# 1. Confirm the PDF actually has an outline (else this approach doesn't apply):
.venv/bin/python -c "import fitz; print(len(fitz.open('sources/<doc>/<doc>.pdf').get_toc()), 'outline entries')"

# 2. Build the deterministic PDF-outline arm (one command, ~$0):
.venv/bin/python scripts/build_pdf_outline_index.py \
  --pdf sources/<doc>/<doc>.pdf \
  --index-dir indexes/IDX-PDF-outline-<doc> --overwrite

# 3. (MD twin) get a Markdown rendering, build IDX-D, curate into indexes/IDX-D-<doc>/.

# 4. Author evaluations/questions-<doc>.csv with columns:
#      id, category, question, gold_sections
#    gold_sections = section numbers (e.g. "15.4.2; 10.2.2") that appear in node titles.

# 5. Run + score as in steps 2-3, swapping in the new index ids and questions file.
```

**The one rule that makes replication work:** gold is expressed as **section/heading
identifiers that appear in node titles**. Everything else — addressing, page vs line, which
representation — the tools handle automatically.

---

## 8. Analyzing results — notebooks (read-only)

Notebooks are the **read-only analysis layer**: they consume `runs/`, `indexes/`, and
`evaluations/` outputs and never re-implement build/score/spend logic (they import the tested
functions or shell out to the scripts). They need the analysis extras — `pandas`, `altair`,
`ipykernel` — from `requirements.txt`; charts use the brand palette via `scripts/viz_theme.py`.

```bash
.venv/bin/pip install -r requirements.txt            # once: pandas + altair + ipykernel
.venv/bin/python -m ipykernel install --user --name pageindex   # register .venv as a kernel
```

Numbered by the **experiment lifecycle** (see [`notebooks/README.md`](../notebooks/README.md)):

| # | Notebook | When / what it answers |
|---|----------|------------------------|
| 1 | `notebooks/1_validate_gold.ipynb` | **before spending:** do a corpus's gold sections resolve to nodes in an index? |
| 2 | `notebooks/2_analyze_one_run.ipynb` | after one run: recall + per-question pivot + drill-down (Steps 1–4) |
| 3 | `notebooks/3_compare_conditions.ipynb` | after several runs: recall heatmap, efficiency frontier, biggest gaps |
| 4 | `notebooks/4_cost_dashboard.ipynb` | anytime (cross-cutting): spend by phase/run/source, cache-replay, amplification |

Convention: commit notebooks with **outputs cleared** (tools, not results); if a chart becomes a
finding worth keeping, export it to `reports/` as static HTML/SVG.

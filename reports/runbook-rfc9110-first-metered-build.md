# Runbook — First Metered Index Build (RFC 9110)

**Companion to:** `reports/project-brief-2026-07-13-long-doc-corpora.md` §4.2
**Operator:** you (run every command yourself). **Date run:** ____________
**Goal of this document:** turn the §4.2 pre-flight framework into concrete
commands + artifacts, so by the end you can explain every dollar from first
principles. Fill in the blanks as you go — the filled-in runbook *is* the pilot
record that later authorizes the >$5 PHAK/AIM builds (§4.2 step 6).

Everything runs **from the repo root** (dotenv finds `.env` there; needs
`OPENAI_API_KEY` set — the deterministic steps 0–2 need no key).

---

## Step 1 — State the value (write it, don't skip it)

This run informs three decisions:
1. Calibrates the **PDF cost multiplier** (the "2–4×" guess) for born-digital
   manuals — the number that gates the PHAK/AIM builds.
2. Produces the first **tree over RFC 9110** to judge index quality on a
   short-section document (Set C of the study).
3. Proves the **metering pipeline** end-to-end on real spend.

> My one-sentence version: ________________________________________________

## Step 2 — Measure the document (free, deterministic)

The build script does this internally, but do it once by hand so you know
where its numbers come from. Token count = PyMuPDF text extraction × tiktoken:

```bash
.venv/bin/python -c "
import fitz, tiktoken
doc = fitz.open('sources/rfc9110/rfc9110.pdf')
enc = tiktoken.get_encoding('o200k_base')          # gpt-4o's tokenizer
toks = sum(len(enc.encode(p.get_text())) for p in doc)
toc = doc.get_toc()
print(f'pages={doc.page_count}  tokens={toks:,}  outline_entries={len(toc)}')
print('first 5 outline rows:', toc[:5])
"
```

Expected: **194 pages, ~111,550 tokens, 311 outline entries.**
The outline entries are your *node-count proxy* — each tree node PageIndex
keeps will get one summary LLM call, so ~300 is the ceiling on summary calls.

> pages ______  tokens ______  outline entries ______

> **Two token counts — don't conflate them.** The `tokens` above is *document tokens* (the
> whole PDF, ~111K) via tiktoken — an **estimator** of build cost only. It is a different
> quantity from the *tree-dump-per-turn* (`structure_tokens`) in
> `reports/findings-summary-threshold.md`, which is much smaller (node text stripped) and is
> the *recurring* retrieval cost, not this one-time build. And once you spend (Steps 5–7) the
> **truth is the metered provider tokens** in `usage_log.jsonl`, never a tiktoken estimate —
> tiktoken only sets the pre-flight bound; every realized dollar is computed from measured
> tokens.

## Step 3 — Understand what you're about to buy (read, no spend)

The PDF pipeline (`vendor/PageIndex/pageindex/page_index.py`) spends in three
phases; this is where the "input passes through 2–4×" rule comes from:

| Phase | What it does | Rough input cost |
|---|---|---|
| TOC detection + verification | pages sent to the model to find/check section boundaries | ~1–2× doc tokens |
| Structure fixing | re-sends slices where boundaries disagreed | ~0–1× (varies!) |
| Node summaries | each node's text sent once more (`utils.py:579`) | ~1× doc tokens |
| Doc description (off by default) | one call over the finished tree | negligible |

The *uncertain* row is structure fixing — that's why the estimate is a range
and why this pilot exists: your realized/estimated ratio pins it down for this
document class.

## Step 4 — Price and bound it (the script's pre-flight; still no spend)

Run the build and **type `n`** at the prompt — this is a free dry run that
prints the whole pre-flight:

```bash
.venv/bin/python scripts/build_index_metered.py --pdf_path sources/rfc9110/rfc9110.pdf
```

You should see (2026-07-13 values):

```
source: sources/rfc9110/rfc9110.pdf  (111,550 tokens)   <- your Step-2 number
estimate (2-4x rule of thumb): 223,100-446,200 input / 22,310-89,240 output tokens
estimated cost: $0.78 - $2.01                            <- tokens x PRICES
abort bound: $4.02                                       <- 2 x high estimate
```

Where each number comes from:
- **input range** = doc tokens × 2 … × 4 (Step-3 table).
- **output range** = 10% of low input … 20% of high input.
- **cost** = `in/1e6 × $2.50 + out/1e6 × $10.00` — rates from
  `scripts/usage_logging.py:PRICES` (single source of truth).
- **abort bound** = 2× high estimate; if metered spend crosses it mid-run the
  script kills the build (override with `--abort-over`, disable with 0).

> estimated cost range $______ – $______   abort bound $______

## Step 5 — Run it, watching the money live

Open a **second terminal** and tail the usage log — every LLM call appends one
JSON row the moment it completes:

```bash
tail -f runs/usage_log.jsonl
```

Then in the first terminal, run the same command and type `y`. Note the
`run_id` it prints (UTC timestamp) — everything is keyed by it.

> run_id: ____________________

What you'll see in the tail, and what each field means:

| Field | Meaning |
|---|---|
| `phase` | `"index_build"` — distinguishes these rows from retrieval rows |
| `call_idx` | 0-based call counter — watch it climb toward ~300+ |
| `input_tokens` | full-price input for THAT call (big during TOC parsing, small per summary) |
| `output_tokens` | generated tokens (summaries ≈ 60–100 each) |
| `cache_read/creation_tokens` | expect 0 here (no prompt caching in the build path) |
| `latency_s` | real per-call wall time (wrapper measures around the await) |
| `cost_usd` | that call, priced from PRICES |

Reading the stream is the "fully understand" moment: you can literally watch
the pipeline move through Step-3's phases — a few large-input calls first
(TOC detection over page batches), then a long burst of small parallel calls
(one summary per node).

Notes while it runs:
- `************* Retrying *************` lines are PageIndex's own retry loop
  (utils.py) — transient API errors, not your problem unless they repeat 10×.
- Expect minutes, not seconds (hundreds of sequential+parallel calls).
- If it aborts with "cost abort bound exceeded": the partial rows are still in
  the log under your run_id — investigate before re-running.

## Step 6 — Examine the artifacts

**(a) The tree** — `results/rfc9110_structure.json` (gitignored scratch until
you curate it into `indexes/`):

```bash
.venv/bin/python -c "
import json
r = json.load(open('results/rfc9110_structure.json'))
struct = r['structure'] if isinstance(r, dict) and 'structure' in r else r
def walk(nodes, d=1):
    for n in nodes:
        yield d, n
        yield from walk(n.get('nodes', []), d+1)
rows = list(walk(struct))
print('nodes:', len(rows), ' max depth:', max(d for d,_ in rows))
print('with summary:', sum(1 for _,n in rows if n.get('summary')))
d, n = rows[5]
print('sample node:', json.dumps({k: str(v)[:100] for k,v in n.items() if k != 'nodes'}, indent=2))
"
```

Sanity questions to answer by eye: does the node count roughly match the 311
outline entries? Do summaries read like summaries (LLM-written) — the PDF path
always generates them, unlike the Markdown path's <200-token verbatim copies
(`reports/findings-summary-threshold.md`)?

> nodes ______  max depth ______  nodes with summary ______

**(b) The bill** — reconciled, per call and per condition:

```bash
python3 scripts/cost_report.py --run <run_id>
```

Read three things: the per-condition total (your build under index label
`BUILD-rfc9110`), the per-call view (Step-3's phases visible as the
input-token shape over call_idx), and the **reconciliation line** — it must
end with `✓ [0 row mismatch(es)]`, meaning logged costs recompute exactly from
logged tokens.

> calls ______  input tokens ______  output tokens ______  total $______

**(c) The dashboard cross-check** (covers the known gap — calls that errored
after generating tokens are invisible to the wrapper): compare the OpenAI
usage dashboard delta for the run window against the metered total.

> dashboard delta $______  (should be ≥ metered total, gap ≈ retries)

## Step 7 — The calibration number (why you did all this)

The script prints it at the end, but compute it consciously:

```
realized / estimated-high  =  metered $ ÷ high estimate  =  ______ / ______ = ______
```

Decision rule (brief §4.2 step 5): **ratio ≤ ~1.5 → the 2–4× multiplier holds
for this document class; a PHAK single-chapter pilot is authorized next.**
Ratio above that → the estimator is wrong for this class; find out which phase
blew up (per-call view makes it obvious) before spending again.

Also record where in the 2–4× band reality landed (realized input tokens ÷ doc
tokens = ______×) — after 2–3 pilots, replace the 2–4× guess in the brief with
your measured value.

## Afterwards

- Commit the keeper: usage rows for this run_id (precedent: commit `47b31ba`)
  and the filled-in blanks in this runbook.
- If the tree is good, curate `results/rfc9110_structure.json` into an
  `indexes/IDX-*/` entry with a `provenance.json` pinning
  `sources/rfc9110/rfc9110.pdf`'s sha256 (see `config/rfc9110-book-v1.yml`).
- **Record the recurring cost too — it's the one that adds up.** This runbook meters the
  *one-time build*. The index's *per-retrieval* cost is the tree re-sent on every agent turn,
  = the harness's measured `structure_tokens` (not a tiktoken re-count). Capture it at first
  retrieval over the curated index and record it in the index's `provenance.json`, translated
  to $/turn. For a short-section document like RFC 9110 (~300 nodes), over many questions this
  per-turn cost dominates the one-time build — exactly the re-send amplification that
  `reports/findings-summary-threshold.md` measured on the site-book (a real-summary tree ran
  ~4× the headings tree, re-billed every turn).

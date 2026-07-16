# Finding: PageIndex's summary threshold makes "add summaries" mostly copy text — and that inflates the re-sent tree

*Lab note from the PageIndex website experiment. Written to be reusable in a longer
public write-up — it records what we found, the mechanism behind it, and the boundary
between upstream behavior and our own experimental setup. Measurements are read-only from
the already-built indexes and the recorded retrieval runs; nothing here required a rebuild.*

## TL;DR

- PageIndex's Markdown index path only generates a **real, model-written summary for a node
  when the node's own text exceeds `--summary-token-threshold` (default 200 tokens)**. Below
  that, it copies the node's text **verbatim** into the `summary` field — no LLM call, no
  compression.
- On our site-book corpus that means **~80% of nodes carry a "summary" that is a byte-for-byte
  copy of their own text**: **273 / 339 nodes (80.5%)** in IDX-C, **272 / 339 (80.2%)** in IDX-O.
  Only ~20% got a genuinely generated summary.
- The retriever's tree dump strips the bulky `text` field *"to save tokens"* — but for those
  80% of nodes the identical content survives in `summary`, so the saving is defeated. The tree
  the agent re-sends **on every turn** is **~43.7K tokens (IDX-C)** vs **~8.9K (IDX-D, no
  summaries)** — roughly **4.9× larger**.
- **None of this is our code.** It is stock, unmodified upstream PageIndex behavior (submodule
  pinned at `f413c66`). The `threshold = 200` is PageIndex's default, which we inherited by not
  overriding it — not a preprocessing rule we introduced.

## Why we went looking

PageIndex is "vectorless" RAG: it builds a hierarchical tree (a table of contents) over a
document, and an LLM **retriever** answers questions by navigating that tree. We built three
index conditions over the same frozen corpus:

- **IDX-D** — deterministic Markdown headings, **no summaries** (`--if-add-node-summary no`).
- **IDX-C** — the same tree **plus** gpt-4o-generated node summaries + a doc description.
- **IDX-O** — the same, with a **local** Ollama model (qwen2.5) generating the summaries.

The intent of IDX-C / IDX-O was to test *"generated summaries over headings help the
retriever navigate."* But when we inspected the built indexes, most `summary` fields were
not summaries at all — they were the node's own text, repeated. That is what this note pins
down.

## The mechanism (upstream code)

The Markdown path's per-node summary decision lives in
`vendor/PageIndex/pageindex/page_index_md.py`:

```python
async def get_node_summary(node, summary_token_threshold=200, model=None):
    node_text = node.get('text')
    num_tokens = count_tokens(node_text, model=model)
    if num_tokens < summary_token_threshold:
        return node_text                       # ← verbatim copy, no LLM
    else:
        return await generate_node_summary(node, model=model)   # ← real summary
```

So `--summary-token-threshold 200` is a **cost optimization**: don't pay to summarize a node
that's already short. Defensible in principle. Two things make it a trap in practice:

1. **The default (200) is high relative to a heading-dense document.** Most sections in our
   corpus are under 200 tokens, so most nodes take the verbatim branch — "add summaries"
   mostly *doesn't*.
2. **The verbatim semantics are undocumented.** To be precise about what is and isn't
   disclosed: the CLI `--help` does describe `--summary-token-threshold` as "(markdown
   only)", but the flag is absent from the README's "Optional parameters" list, and the
   copy-below-threshold behavior — raw node text emitted as the `summary` — is documented
   nowhere. That part was only discoverable by inspecting the emitted index.

### The two paths do NOT behave the same

Worth stating precisely, because it matters for any PDF-vs-Markdown comparison: the threshold
**only exists on the Markdown path.** The PDF path
(`generate_summaries_for_structure` in `pageindex/utils.py`) summarizes **every** node with a
real LLM call, no threshold:

| Stage | Markdown path (`--md_path`) | PDF path (`--pdf_path`) |
|---|---|---|
| Structure | Deterministically parses the `#`/`##` heading hierarchy (no LLM) | Infers it — TOC detection → LLM-generated TOC → physical-page mapping |
| Summaries | Threshold-gated: **verbatim if < 200 tok**, else generated | **Always** a real generated summary |

**Implication for the upcoming PDF study:** comparing a default Markdown index against a PDF
index would confound *representation* (how the tree was derived) with *summary regime* (verbatim
vs always-generated). To isolate representation, build the Markdown arm with
`--summary-token-threshold 0` (with threshold 0, `num_tokens < 0` is never true, so every node
gets a real summary) — this is the `IDX-C0` variant already noted in the repo backlog.

## The measurement

### How much is verbatim

Counting nodes where the emitted summary equals the node's own text (leaf nodes use `summary`,
parent nodes use `prefix_summary`), with gpt-4o token counts:

| | IDX-C | IDX-O |
|---|---|---|
| Total nodes | 339 | 339 |
| Verbatim (`summary == text`) | **273 (80.5%)** | 272 (80.2%) |
| Generated (`summary != text`) | 66 (19.5%) | 67 (19.8%) |

This matches the split already recorded in each index's `provenance.json` (`summary_stats`):
of the 258 leaf summaries, ~194 are raw-text echoes; the remaining verbatim nodes are parent
`prefix_summary` fields.

### What it costs at retrieval time

The retriever reads the tree via `get_document_structure`, which is upstream
(`pageindex/retrieve.py`) and strips `text` explicitly to save tokens:

```python
structure_no_text = remove_fields(structure, fields=['text'])   # "saves tokens"
```

But when `summary == text`, removing `text` changes nothing — the same content is still in
`summary`. So the optimization is largely undone. Tree-dump sizes below are the harness's
measured `structure_tokens` — the tokens the agent actually re-sent each turn (from
`runs/*/run.json`), and what the cost figures are computed from. This is the convention used
throughout this note; it is **not** an independent tiktoken re-count of the index files
(that depends on serialization and runs larger — kept only as an internal cross-check):

| Index | Summaries? | Tree dump re-sent each turn |
|---|---|---|
| **IDX-D** | none | **~8,934 tokens** |
| **IDX-C** | yes (80% verbatim) | **~43,730 tokens** |
| **IDX-O** | yes (80% verbatim) | **~43,245 tokens** |

(IDX-C / IDX-O dumps are constant across runs; the IDX-D figure is the single-dump size —
some runs call `get_document_structure` twice, which doubles the logged total.)

The "summary" tree is **~4.9× larger** than the heading-only tree, and that entire tree is
re-billed as input on **every** agentic turn — the re-send amplification our cost-tracking work
(V3A) was built to measure.

**Honest scoping of the 4.9×:** this compares *summaries-as-built* (IDX-C) against
*no summaries* (IDX-D) — not verbatim-vs-generated. The verbatim defect is why the summary tree
lands so close to a full-text dump rather than shrinking. The true size of a *properly*
generated-summary tree is a counterfactual we have not yet measured; it needs a
`--summary-token-threshold 0` rebuild (the `IDX-C0` experiment). That rebuild would let us
attribute the bloat precisely to the verbatim copies.

## What is ours vs. what is upstream

This distinction is the credibility backbone of the finding, so we state it explicitly.

**Upstream PageIndex, unmodified.** `vendor/PageIndex/` is a pinned git submodule at commit
`f413c66` (verified to be an unmodified commit on `origin/main`; the working tree has no edited
source files — only an untracked `results/` scratch folder). Everything in the mechanism above —
the 200-token verbatim threshold, the always-generate PDF path, the `text`-stripping serializer —
is stock upstream behavior. **We did not edit any PageIndex source.** Our discipline is: treat the
vendored submodule as read-only; to change behavior, change *flags* or *inputs*, never the
vendored code. (This is also enforced for tooling in `CLAUDE.md`.)

**Ours (this repo, entirely outside the submodule).** The corpora and their provenance
discipline, the curated `IDX-*` indexes, the frozen evaluation set, the retrieval harness
(`scripts/run_retrieval.py` — our own agent loop, not PageIndex's `retrieve.py`), the V3A
cost-logging + prompt-caching instrumentation, and the comparison reports.

**The one subtle point:** the `--summary-token-threshold 200` that produced the verbatim
summaries is PageIndex's **default** — we inherited it by not overriding it. The honest framing
is *"an undocumented upstream default we didn't override,"* not *"a rule we introduced."*

## Why it matters (beyond this project)

- **"Add summaries" can silently be a no-op.** On heading-dense documents, the default threshold
  means most nodes are never summarized — a user could reasonably believe they have a
  summary-enriched index when ~80% of it is copied text.
- **A token-saving optimization can be defeated downstream.** Stripping `text` to shrink the
  re-sent tree does nothing when the summary *is* the text. The two design choices interact in a
  way neither one's local logic reveals.
- **Defaults deserve inspection, not trust.** The behavior was undocumented and only visible by
  reading the emitted index. For any RAG pipeline where a persistent structure is re-billed every
  turn, measuring what you actually re-send is worth more than assuming the config did what its
  name implies.

## Reproduce

All read-only; no LLM calls, no rebuild.

```bash
# Verbatim-vs-generated share in the built indexes
python3 - <<'PY'
import json
def walk(ns):
    for n in ns:
        yield n
        if n.get('nodes'): yield from walk(n['nodes'])
for label in ("IDX-C","IDX-O"):
    nodes=list(walk(json.load(open(f"indexes/{label}/index.json"))["structure"]))
    verb=sum(1 for n in nodes
             if (str(n.get('summary') or n.get('prefix_summary') or '').strip())
             == str(n.get('text') or '').strip() and str(n.get('text') or '').strip())
    print(label, f"{verb}/{len(nodes)} verbatim ({verb/len(nodes)*100:.1f}%)")
PY

# Real tree-dump sizes the agent re-sends, from recorded runs.
# The index label is per-result (index_id) in multi-index sweep runs and
# top-level (run['index_id']) in single-index runs; structure_tokens is per-result.
python3 - <<'PY'
import json, glob, collections
by=collections.defaultdict(list)
for rj in glob.glob("runs/*/run.json"):
    rec=json.load(open(rj))
    top=rec.get("index_id")
    for r in rec.get("results",[]):
        idx = r.get("index_id") or top
        st  = r.get("structure_tokens")
        if idx and st: by[idx].append(st)
for k,v in sorted(by.items()):
    print(k, f"n={len(v)} mean={sum(v)/len(v):.0f} min={min(v)} max={max(v)}")
PY

# Confirm the submodule is unmodified upstream
git submodule status vendor/PageIndex
git -C vendor/PageIndex status --short   # only 'results/' (untracked) is expected
```

## Next step

Build `IDX-C0` (`--summary-token-threshold 0`) to (a) measure the true size of a properly
generated-summary tree and attribute the bloat precisely, and (b) serve as the confound-free
Markdown arm for the PDF-vs-Markdown representation comparison.

---

## Addendum (2026-07-12): IDX-C0 built, and a three-way retrieval run

`IDX-C0` is now built (`--summary-token-threshold 0`, gpt-4o) and curated at
`indexes/IDX-C0/`. Two things fell out — one that revises this note's own hypothesis,
one that was not anticipated.

### 1. The verbatim bug explains only about a quarter of the bloat

This note hypothesized that the verbatim-copy defect was why the summary tree ballooned.
The counterfactual says that was only partly right. Tree-dump sizes are the harness's
measured `structure_tokens` (the tokens re-sent each turn) — the same convention as the
table above, so these reconcile directly:

| Index | Summaries | Tree dump / turn (`structure_tokens`) |
|---|---|---|
| IDX-D | none | 8,934 |
| **IDX-C0** | **real, every node** | **35,516** |
| IDX-C | 80% verbatim | 43,730 |

Fixing the threshold (IDX-C → IDX-C0) recovers only ~8K of the ~35K excess over headings.
A *properly* summarized tree is still **~4.0× the headings-only tree** — because on a
heading-dense corpus most nodes are short, and you cannot summarize a 40-token section into
much less than 40 tokens (plus every parent carries a `prefix_summary`). **Honest revision:
the ~4× per-turn cost of "add summaries" is largely inherent to summarizing a heading-dense
document, not an artifact of the verbatim bug.** The verbatim bug added only the last ~24%
(the gap between IDX-C and IDX-C0); it was not the whole story.

> **Token convention (used throughout this note).** All tree-size figures are the harness's
> measured `structure_tokens` — what the agent actually re-sent per turn, and what the cost
> column is computed from, so tokens and dollars reconcile. An independent tiktoken re-count
> of the index files gives larger numbers (it depends on JSON serialization/indentation) and
> is retained only as an internal sanity check, never published. Rule: report one convention,
> and translate it into $/turn (≈$0.09 for the IDX-C0 tree vs ≈$0.02 for headings, at gpt-4o
> input rates) so the number means something.

### 2. Real summaries buy accuracy — verbatim ones don't, and hurt evidence-gap

A three-way retrieval run (IDX-D / IDX-C / IDX-C0, gpt-4o retriever, all 14 questions,
`--cache on`, run `runs/20260712T180445Z/`) scored as follows. **Scoring caveat: n=1 per
cell, a single agent judge (claude-fable-5), subjective 0–5; directional, not statistical.
Per-cell scores + notes in `runs/20260712T180445Z/scores.csv`.**

| Category | IDX-D | IDX-C | IDX-C0 |
|---|---|---|---|
| direct-location | 4.75 | 4.88 | 5.00 |
| evidence-gap | 4.33 | **3.67** | 4.50 |
| cross-section-synthesis | 2.33 | 3.33 | 3.83 |
| reflective-discovery | 2.75 | 4.75 | 5.00 |
| **mean (0–5)** | **3.82** | **4.11** | **4.54** |
| **cost (14 Q)** | **$0.80** | **$3.29** | **$2.69** |

- **IDX-C0 strictly dominates IDX-C**: higher quality *and* 18% cheaper. The shipped-default
  verbatim summaries were the worst value — 4× IDX-D's cost for a 0.29-point gain.
- **Summaries help where navigation is hard.** The gains concentrate in cross-section-synthesis
  and reflective-discovery (the questions requiring the agent to find the right sections across
  the corpus). On direct-location, headings alone already suffice — all three tie near 5.
- **Verbatim summaries *hurt* evidence-gap** (IDX-C 3.67, below headings-only). Verified against
  full answer text: on EG6, IDX-C wrote *"these statistics are actual numbers… not
  placeholders,"* laundering three bracketed placeholders — the exact failure that category
  exists to detect. IDX-C0 and IDX-D both caught it. The verbatim defect didn't only waste
  tokens; it degraded the most discriminating category.

**Takeaway for the public write-up:** "add summaries" carries a real, mostly-inherent ~3× tree
cost — but done properly (threshold 0) it earns that cost back in navigation accuracy, while the
shipped default earns nothing and regresses on gap-detection. The lesson generalizes: an
enrichment step's *default configuration* can invert its own value proposition.

### Still open

- A repeatable LLM-judge (`scripts/score_run.py`) to replace the single-agent scoring, and
  repetition (n>1) for a real distribution, before any strong quantitative claim is published.
- `IDX-O0` (local Ollama, threshold 0) — is the summary benefit reachable without the API bill?
  Deferred behind this result, which establishes that the benefit exists at all.

---

## Addendum (2026-07-15): verified current upstream; issue drafted

Before publishing, we checked whether this behavior still exists upstream:

- Our pinned submodule commit `f413c66` **is** upstream `main` HEAD (nothing has moved
  since 2026-07-03) — everything in this note describes the current release.
- `get_node_summary`'s verbatim branch, the always-generate PDF path (`utils.py:590`),
  and the Markdown-only flag wiring (`run_pageindex.py`) are all unchanged on `main`.
- No existing upstream issue or PR covers it (searched issues/PRs for
  summary/threshold/verbatim/get_node_summary; nearest hits #340/#341/#23/#129 are
  unrelated).

The upstream behavior report was **filed 2026-07-15**:
[VectifyAI/PageIndex#355](https://github.com/VectifyAI/PageIndex/issues/355)
(archived source: `reports/upstream-issue-draft.md`).

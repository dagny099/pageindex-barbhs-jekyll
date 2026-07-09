# Finding: local open-source models as PageIndex retrievers, and a prompt bias we found

*Lab note from the PageIndex website experiment. Written to be reusable in a longer
public write-up — it records what we tried, what broke, and why it matters.*

## The setup

PageIndex is "vectorless" RAG: instead of embedding chunks, it builds a hierarchical
tree (a table of contents) over a document, and a **retriever** — an LLM agent — answers
questions by *navigating* that tree with three tools:

- `get_document()` — metadata (line count, status)
- `get_document_structure()` — the tree of section titles + line numbers (no body text)
- `get_page_content(pages="…")` — the actual text of a line range

We wanted to know whether a **local, open-source model** (served by Ollama) can play this
agentic retriever role — one of the experiment's central questions: *can a small local
model do one PageIndex job but not the other?* (Summarizing nodes to build an index is
one job; navigating the index to answer is the other.)

## Gotcha #0: Ollama silently truncates the index

Before any model quality question, a practical trap: **Ollama defaults to a ~2K–4K token
context window regardless of what the model architecture supports.** Our index tree dump
is **~9,000 tokens**, so the retriever was being handed a *truncated* index and navigating
half-blind — with no error. The fix is a derived model that sets `num_ctx` explicitly
(see `config/ollama/*.Modelfile`, `num_ctx=32768`). After the fix, the model received the
full tree (`structure_tokens = 8934`). **Lesson: with local serving, verify the context
window before trusting any retrieval result.**

## What broke: `llama3.1:8b` fabricates tool calls

With the context window fixed, we ran `llama3.1:8b` as the retriever under our *original*
prompt. Across three questions it showed two failure modes:

| Question | Real tool calls | Fetched body text? | Outcome |
|---|---|---|---|
| DL3 (project + stack) | `get_document_structure` only | **No** | Correct — but only because the project *title* was self-describing |
| CS2 (critique across articles) | `get_document_structure` only | **No** | Correct-looking — again answered from titles |
| DL1 (definition of "knowledge legibility") | `get_document_structure` only | **No** | **Collapsed** — emitted raw `{"name": "get_document_structure", "parameters": {}}` as prose |

Two distinct failures:

1. **Fabrication.** The model made one real `get_document_structure()` call, then *narrated*
   a content fetch in prose — literally *"I will call get_page_content(pages=120-160)… Here's
   the output: {…}"* — pasting a fragment it already had, **without ever invoking the tool**
   (`content_tokens = 0`). It then answered from section **titles** alone. This looks fine
   when a title happens to contain the answer, and fails silently when it doesn't.
2. **Collapse.** On DL1, whose answer is a *definition* living in body text (not any title),
   the model had nothing to fake from and broke down, emitting a malformed tool-call-as-text.

**The shortcut is the story:** the model was answering from the cheap signal (titles in the
structure) and only *pretending* to do the expensive, correct step (reading the text).

## The prompt was part of the problem — but not all of it

Our original prompt included this line:

> *Before each tool call, output one short sentence explaining why.*

We suspected this **biased** weaker models toward *narrating* tool calls as prose instead of
emitting real ones. A controlled probe supported it: dropping that line and adding an explicit
"you must read content before answering" made `llama3.1` **actually fetch content** — but it
then **skipped the structure step and guessed a line range** (fetched lines 120–160, the wrong
end of the corpus, and cited a page that wasn't even in what it fetched).

So the prompt was a **genuine confound** — it changed the failure mode — but no prompt made
`llama3.1:8b` a *reliable* retriever. Its weakness is the multi-step *navigate-then-read* loop
itself, not just phrasing.

## Before / after prompt

**Before:**

```
You are PageIndex, a document QA assistant answering questions about a personal
professional website compiled into one Markdown "site book".
TOOL USE:
- Call get_document() first to confirm status and line count.
- Call get_document_structure() to identify relevant sections and their line_num values.
- Call get_page_content(pages="120-160") with tight line ranges from the structure;
  never fetch the whole document.
- Before each tool call, output one short sentence explaining why.
Answer based only on tool output. Cite the section titles you used. Be concise.
```

**After:**

```
You are PageIndex, a document QA assistant answering questions about a personal
professional website compiled into a single Markdown "site book", which you can only
read through tools.

Workflow - follow in order:
1. get_document() - confirm the document is available and get its line count.
2. get_document_structure() - read the tree of section titles and their line numbers;
   decide which sections are relevant and note their line_num values.
3. get_page_content(pages="...") - read the actual text of those sections, using tight
   line ranges from step 2 (e.g. "2403-2476"). Fetch content for every section you rely
   on; never fetch the whole document at once.

Ground every claim in text returned by get_page_content - the structure gives titles
only, which is not enough to answer. If multiple sections are relevant, fetch each one.
Cite the section titles you used. Be concise, and say so if the corpus does not contain
the answer.
```

**Why we changed each thing:**

- **Removed** *"output one short sentence before each tool call."* It nudged weaker models to
  *describe* tool calls instead of *making* them. We already capture the full tool-call trace
  in the harness, so we lose zero observability by dropping it.
- **Kept an explicit, ordered workflow** (document → structure → content). When we *only*
  removed the narration line, the model started skipping the structure step and guessing line
  ranges — so the ordering has to be stated.
- **Added** *"ground every claim in text returned by get_page_content — titles are not enough."*
  This directly targets the fabrication/answer-from-titles shortcut.
- **Goal:** a prompt that is *detailed but model-neutral*, so a weak model's failure reflects
  the **model**, not an instrument that nudged it into a bad pattern. Fair comparison across
  model tiers requires the prompt itself not to carry hidden bias.

## Does a stronger tool-calling model fix it? — `qwen2.5:7b-instruct`

**Yes, qualitatively — with real caveats.** Under the new prompt we compared `gpt-4o` (cloud
baseline) against `qwen2.5:7b-instruct` — same 7–8B size class as `llama3.1`, but tuned for
tool use — on three questions:

| Retriever | DL1 (definition in body text) | CS2 (synthesis) | DL3 (project + stack) | Latency |
|---|---|---|---|---|
| `gpt-4o` | Fetched lines 261–275 → **correct** (Knowledge Legibility Audit service) | Fetched the two right articles → **correct** | Fetched → **correct** | 7–12 s |
| `qwen2.5:7b-instruct` | **Fetched** content, but from the *wrong* section (line ~2403, the judgment-gap article) → plausible but **mislocated** | Fetched the right articles → **correct** | Fetched → **correct** | **174–296 s** |
| `llama3.1:8b` *(old prompt)* | Collapsed (no fetch) | Faked (titles) | Faked (titles) | 90–115 s |

The decisive difference: **`qwen2.5` actually ran the navigate-then-read loop on every
question — it called `get_page_content` and grounded in real text, with zero fabrication.**
That's the threshold `llama3.1:8b` never crossed. But two caveats:

1. **Slow.** 174–296 s per question — roughly **20–40× gpt-4o**. Local agentic retrieval is
   *viable* but operationally heavy.
2. **Clumsier navigation.** It made redundant/malformed calls (a duplicate `get_document`, an
   empty `get_page_content()`) and recovered — and on the hardest question (DL1) it navigated to
   the **wrong section**, answering the "knowledge legibility" definition from the *judgment-gap
   article* rather than the *Knowledge Legibility Audit* service where `gpt-4o` correctly found
   it. So it retrieves, but with weaker precision.

**Refined takeaway:** the dividing line isn't "local vs cloud" — it's **reliable tool-calling
vs not, and that line runs *through* the small-local tier.** Two ~7–8B models: `llama3.1:8b`
fabricates tool calls; `qwen2.5:7b-instruct` genuinely navigates. A local PageIndex retriever
is *possible* — if you pick a tool-calling-tuned model — but you pay ~20–40× latency and some
navigation precision. Model *selection within local* matters as much as local-vs-cloud.

## Why this is interesting (beyond this project)

- **Agentic RAG's bottleneck is reliable tool-calling, and that's exactly where small local
  models break.** The limiter isn't the model's knowledge or (once fixed) its context window —
  it's executing a disciplined multi-step tool loop without fabricating or shortcutting.
- **Evaluation prompts carry hidden bias.** A seemingly harmless instruction ("explain before
  each call") quietly sabotaged weaker models. Comparing models fairly means auditing the
  prompt for nudges that help or hurt one tier more than another.
- **Local serving has silent failure modes.** Ollama's default context truncated the index with
  no error — the kind of thing that produces confidently wrong results and no traceback.
- **It concretely supports the "viable for one role, not the other" thesis.** The same local
  model that can plausibly *summarize* nodes (to build IDX-O) cannot reliably *retrieve*.

## Reproduce

Prompt lives in `scripts/run_retrieval.py`; runs are recorded under `runs/`. The two local
models use enlarged-context derived models (`config/ollama/*.Modelfile`). Example:

```bash
python3 scripts/run_retrieval.py --index-id IDX-D \
  --retrievers gpt-4o-2024-11-20 ollama_chat/llama3.1-8b-ctx32k --questions DL1 CS2 DL3
```

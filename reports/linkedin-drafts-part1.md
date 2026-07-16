# LinkedIn drafts — Part 1 sequence (3 posts) + one-pager opportunities

*Drafted 2026-07-16 in Barbara's voice (calibrated to the v2 blog draft: plain
declarative sentences, concrete numbers, no hype, honest scoping, no emoji). Numbers
match the corrected fact-check (total spend ~$50; $30 captured in the per-call ledger).
Each post: hook lands in the first two lines (before the "…see more" fold), one idea,
one image, link at the bottom or in the first comment, and ends with a genuine question
to seed comments. Space posts 3–5 days apart, weekday mornings. Reply to every
substantive comment in the first few hours.*

---

## Post 1 — The discovery (pairs with the tree-tax figure)

**Image:** `results-tree-tax` as PNG. Alt text: "Bar chart comparing tokens re-sent per
agent turn: headings-only trees are 4–6× smaller than summary-bearing trees across three
corpora."

---

I turned on a RAG tool's "add summaries" feature and compared the output from GPT-4o
and a local model.

80% of the summaries were identical. Not similar — byte-for-byte copies of the source
text, from both models.

The cause wasn't either model. It was a default: below a 200-token threshold, the tool
skips the LLM call and copies the node's text into the field named "summary." Nothing in
the documentation says so. I only saw it because I diffed the emitted index against the
source.

The twist is what it cost. The tool strips the raw text from the tree it sends the
retrieval agent — to save tokens. But when summary == text, there's nothing to save. The
"summarized" index was the largest artifact of every condition I built: ~43,700 tokens,
versus ~8,900 for plain headings. And that tree gets re-sent on every agent turn, for
every question.

A feature I enabled was mostly not running, and I was paying more because of it.

I verified the behavior in the current release, confirmed nobody had reported it, and
filed it upstream before writing about it. Full write-up, with every number traceable to
a run artifact, is on my site (link below).

What's the default you're glad you diffed — or wish you had?

[link to blog post]

---

## Post 2 — The method (the client-facing one; pairs with the four-stage cheatsheet)

**Image:** the "Four-Stage Autopsy" one-pager (see below) or the quality-vs-cost figure.
Alt text: "Diagram of a retrieval pipeline decomposed into four inspectable stages:
representation, tree, navigation, synthesis."

---

A retrieval demo tells you the system ran. It doesn't tell you what did the work.

When I found a RAG tool's summaries were mostly copied text, I stopped demoing and built
a small measurement lab around it instead: frozen corpora with pinned provenance, named
index conditions, saved retrieval traces, per-call cost logging, and — for the last
comparison — predictions written down before the run.

The whole study cost about $50 in model spend. The structure is what made it useful. I
split the pipeline into four stages, each separately inspectable:

representation → tree → navigation → synthesis

Every failure I found had a home. Corrupted statistics in extracted PDF text:
representation. A tree that dropped the section numbers my questions keyed on: tree. A
local model that wrote fluent answers without ever fetching content — in 15 of 28 runs:
navigation. A model that smoothed "13 years" and "14 years" into one clean number:
synthesis.

Without the decomposition, all four of those would have looked like the same thing: "the
answer was wrong."

This is what I mean when I say knowledge legibility is measurable. Not a vibe about
whether your documents are "AI-ready" — a specific set of artifacts you can open,
diff, and price.

Which stage does your team actually inspect today?

[link to blog post]

---

## Post 3 — The reversal (pairs with the RFC recall figure)

**Image:** `results-rfc-recall` panel A as PNG. Alt text: "Dot plot showing gold-section
recall dropped in every question category when generated summaries were added to an
RFC 9110 index."

---

I built a test to give node summaries their best chance. They made retrieval worse.

The earlier result was promising: on my website corpus, real generated summaries
(after fixing the copied-text default) scored highest AND cost less than that default.
So I picked the hardest fair venue I could — RFC 9110, 311 sections, deep
cross-references — and wrote down my prediction before running: summaries should improve
recall on the hard questions by at least 0.15.

Recall went the other way. 0.92 with plain headings, 0.69 with a real summary on every
node. Down in every hard category. At 4.6× the cost.

Here's the detail I keep thinking about: the final answers were still right. Fact scores
were tied. The traces show why — with summaries in the tree, the agent answered from the
paraphrases instead of fetching the spec's actual text. Same facts, weaker grounding, in
a document where the exact normative wording is the point.

Two corpora, two opposite outcomes. That's not enough to declare a rule about when
summaries help — it's enough to say "add summaries" is not a default upgrade. It's a
trade, and you have to measure it on your documents and your questions.

Next test: a legal document. GDPR's obligations live in articles, its context lives in
recitals, and its PDF has no embedded outline to lean on. If the reversal replicates
there, I'll say so. If it doesn't, I'll say that too.

What would you rather have from a retrieval system: a slightly better answer, or a
provably grounded one?

[link to blog post]

---

---

# One-pager opportunities (infographics / cheatsheets)

Ranked by fit with the sequence. The first two are worth actually producing now; the
rest are a backlog. All can reuse the brand palette + `viz_theme.py` tokens, and all
work in LinkedIn's document/carousel format (multi-slide PDFs get strong organic reach —
each gets a title slide + one idea per slide + a closing slide with the site URL).

## 1. "The Four-Stage Autopsy" (pairs with Post 2 — make this one)

One page, four rows: **representation / tree / navigation / synthesis**. Three columns:
*what it is* · *what failure looks like here* (each with the real example from the study:
`pB.001`, dropped section numbers, zero-fetch fluent answers, the smoothed 13-vs-14) ·
*what to open and check*. This is the consulting artifact — it encodes the audit method,
it's evergreen, and it's the thing a technical leader saves and shares internally.
Carousel version: 6 slides (title, one per stage, close).

## 2. "The Tree Tax" (pairs with Post 1)

A single visual explainer: agent loop diagram showing the tree re-sent on every turn,
with the formula **tree tokens × turns × questions = recurring cost**, and the measured
bars (8.9K / 35.5K / 43.7K). Message: index-build cost is a one-time line item everyone
sees; recurring context is the cost nobody prices. Mostly assembled already from the
existing figure.

## 3. "Before you buy inferred structure" checklist (pairs with the blog post / Post 3 era)

Five checks to run on a document before paying an LLM to guess its hierarchy: embedded
PDF outline (`get_toc()` count), heading fidelity, section/article numbering, extraction
corruption sample, page-vs-line addressing needs. Punchline from the study: the free
outline matched the authored tree 311/311; the inferred one cost $6.44 and dropped the
section numbers. Practitioner cheatsheet; good repo README material too.

## 4. "RAG review checklist for production teams" (lead-magnet candidate)

Your blog post's closing section, verbatim structure, as a designed one-pager: inspect
the artifact · track recurring context · preserve authored structure · score retrieval
and synthesis separately · match the metric to the document. This is the one to gate
behind nothing (no email wall — goodwill play) but brand clearly; it will circulate
detached from the post, so the site URL goes on the page itself.

## 5. "How to read an index like an auditor" (later; Part 2 era)

A worked mini-example: node JSON with summary == text highlighted, three-line diff
recipe. Very practitioner-y; better after Part 2 when there's a second corpus to cite.

---

*Production notes: LinkedIn needs PNG (SVG unsupported); export share-card crops at
1200×627 for link previews and ~1080×1350 for feed images. The two "make now" one-pagers
can be produced the same way as the results figures (scripted SVG → PNG) so they stay
regenerable and on-palette.*

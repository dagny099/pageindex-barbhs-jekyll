# Story scaffold — Part 1 website post ("defaults deserve autopsy")

*Prepared 2026-07-15 for Barbara's writing session. Every number here is pre-verified
against the committed artifacts (sources cited per beat; deep layer =
[`reports/RESULTS.md`](RESULTS.md)). **How to use this file:** the beats are the agreed
arc; the "facts you can use" are safe to quote as-is; the "voice prompts" are questions
to answer in your own words — they are where the post's personality lives. Nothing here
is prose to copy.*

---

## The pitch (one paragraph, for orientation — not for pasting)

I asked a RAG tool to index my website, and discovered its headline feature was silently
doing nothing: an undocumented default meant "add summaries" copied text verbatim 80% of
the time. Chasing *why* turned a weekend demo into a small measurement laboratory —
frozen corpora, pinned provenance, per-call cost metering, eventually a pre-registered
test. The verdict so far: the free, boring structure (authored headings; the PDF's own
bookmarks) did the retrieval work; the tool's paid intelligence mostly bought a 4–5×
"tree tax" re-billed on every agent turn — and on the one hard document where I tested
summaries rigorously, they made navigation *worse*. Whether that's about summaries or
about that document type is exactly what the next experiment tests.

## Title / hook candidates (pick or riff)

- "The RAG Feature That Wasn't: What I Found When I Diffed the Index"
- "I Measured a RAG Tool Instead of Demoing It"
- "Add Summaries: [does nothing]" *(the config-flag joke format)*
- "The Tree Tax: the RAG Cost Nobody Shows You in the Demo"
- Hook option A (in medias res): the moment of diffing `summary` against `text` and
  seeing byte-identical fields, 273 times out of 339.
- Hook option B (the invoice): "$6.44 to have an LLM guess a table of contents the PDF
  already carried, for free, 311 entries, byte-for-byte."

## Audience layering (agreed: both, layered)

Narrative body written for technical leaders (the knowledge-legibility thesis carries
it); every quantitative claim links to [`RESULTS.md`](RESULTS.md) sections for
practitioners; figures embedded inline; the issue and repro linked for the "prove it"
reader. Suggested pattern: numbers appear in the prose *rounded* ("about 80%"), exact in
the linked tables.

---

## The beats

### Beat 1 — The curiosity (setup, short)

**Job:** establish stakes personally, not abstractly. You know your own website; that's
the point — you can catch an AI being wrong about it.

**Facts you can use:**
- PageIndex: open-source, "vectorless" reasoning-based RAG — builds an LLM-inferred
  hierarchical tree over a document; an agent navigates the tree instead of embedding
  search. Tested unmodified, pinned at commit `f413c66` (which was and still is upstream
  `main`). *(RESULTS.md §0)*
- The corpus: 26 pages of barbhs.com frozen into one ~27.7K-word Markdown "site book,"
  339 tree nodes, provenance-pinned by SHA-256. 14 evaluation questions across 5
  categories, frozen before the runs. *(RESULTS.md §1.1)*
- The one methodological move to state early, because everything depends on it:
  **the corpus was frozen outside the tool**, so document representation became an
  experimental variable instead of a hidden preprocessing step.

**Voice prompts:** Why *your* website and *your* dissertation paper, and not a demo
dataset? What did you expect PageIndex to be when you cloned it?

### Beat 2 — The discovery (the post's engine)

**Job:** the "wait, what?" moment. Concrete, visual, reproducible.

**Facts you can use:**
- "Add summaries" (`--if-add-node-summary yes`) generated a real summary only for nodes
  over an undocumented **200-token threshold**; below it, the node's text is **copied
  verbatim into the `summary` field** — no LLM call. *(findings-summary-threshold.md;
  upstream `page_index_md.py::get_node_summary`)*
- On the site book: **273 of 339 nodes (80.5%)** carried a byte-identical copy as their
  "summary" (IDX-O, local model: 80.2%). *(RESULTS.md §2.2)*
- The two ingestion paths disagree: the **PDF path always generates real summaries** and
  the threshold flag does nothing there. The `--help` text does say "markdown only" —
  what no documentation anywhere says is the verbatim-copy semantics. *(Be precise here;
  we corrected our own overclaim on this.)*
- The compounding irony: the retriever strips the bulky `text` field from the tree "to
  save tokens" — defeated when `summary == text`. The default produced the **largest**
  tree of all conditions: 43.7K tokens vs 35.5K for real-summaries-everywhere vs 8.9K
  for headings-only. *(RESULTS.md §2.2–2.3, fig results-tree-tax)*

**Figure:** `figures/results-tree-tax.svg`

**Voice prompts:** How did you actually notice — what made you open the index JSON at
all? (The honest detective story beats any generalization here.)

**Guardrail:** credit the threshold as a defensible cost optimization; the finding is
that its *semantics are invisible*, not that the developers are careless.

### Beat 3 — Demo becomes laboratory (the method beat — your professional thesis)

**Job:** show what "inspectable" means in practice; this beat *is* the portfolio.

**Facts you can use:**
- The decomposition: representation → tree → navigation → synthesis, each stage
  inspectable and separately scorable — versus the tool's single opaque pipeline.
- The apparatus, plainly listed: frozen corpora with SHA-pinned provenance; curated
  index conditions with build provenance; frozen question sets; per-call cost ledger;
  a tree-quality gate *before* retrieval (which caught the paper PDF's 39 glyph-corrupted
  statistics — `p<.001` extracted as `pB.001` — before they could be misattributed to
  retrieval). *(RESULTS.md §1, §3; qc-paper-tree-gate.md)*
- Total instrumented spend for the entire 11-run study: **$29.95**. *(RESULTS.md §5)*
- Self-referential hook, use deliberately: one of the frozen eval questions asked what
  evidence supports the claim that you build inspectable AI systems. **This project is
  that evidence.**

**Voice prompts:** What's your definition of "inspectable" in one sentence? Which piece
of discipline (freezing, provenance, pre-registration) felt like overkill at the time
and then paid off?

### Beat 4 — What the measurements said (three results, ascending surprise)

**Job:** deliver findings crisply; resist the leaderboard framing.

**Result A — the navigator, not the map.** Holding the index fixed and swapping
retriever models moved answer quality by ~0.6–2 points (0–5); holding the navigator
fixed and adding summaries moved it by ±0.1 (Sonnet: literally identical scores on all
14 questions with and without summaries). The local 7B navigator collapsed outright —
fetched nothing in 15 of 28 runs yet wrote fluent, confident answers; its verbosity was
the tell. *(RESULTS.md §2.1; scores in evaluations/scores-master.csv)*

**Result B — fixing the default helps… here.** Threshold-0 summaries (IDX-C0) beat the
shipped default on *every* summary-sensitive category **and** cost 18% less ($2.69 vs
$3.29 per 14 questions; headings-only: $0.80). Verbatim summaries actively *hurt* the
gap-detection category — on one question the default-index run laundered three bracketed
placeholder statistics as "actual numbers," the exact failure that category exists to
catch; headings-only and real summaries both caught it. *(RESULTS.md §2.3, fig
results-website-quality-cost; scoring caveat below)*

**Result C — the boring structure kept winning.** The 2009 paper and RFC 9110 PDFs:
PageIndex's native path paid **$6.44** to LLM-infer a 474-node tree for RFC 9110 —
while the PDF's own embedded outline (311 entries, extracted for ~$0) matched the
authored Markdown tree **byte-for-byte on titles** and navigated as well. With structure
held equal, Markdown-vs-PDF barely mattered (recall 0.906 vs 0.821 at cost parity, and
the gap partly a page-granularity artifact). *(RESULTS.md §3–4.2, fig results-rfc-recall
panel B)*

**Honesty box to include near Result B (short, in your voice):** website scores are one
run, one judge, 0–5 rubric — directional, not statistical. The objective metric arrives
in the next beat.

### Beat 5 — The reversal (scoped, then the cliffhanger)

**Job:** the twist that keeps Part 2 alive. State it exactly as big as it is.

**Facts you can use:**
- RFC 9110 was chosen *to give summaries their best chance* — deep, cross-referential,
  hard to navigate by headings alone — with predictions written down **before** running.
  *(design-rfc-summary-test.md)*
- The metric is objective: gold section labels, hit-tested against what the agent
  actually fetched. No judge. *(RESULTS.md §1.3)*
- Outcome: real summaries **reduced** gold-section recall **0.92 → 0.69**, dropping in
  every hard category (worst on scattered-evidence questions, −0.32), at **4.6× the
  cost** ($6.01 vs $1.30 for 24 questions). *(RESULTS.md §4.1, fig results-rfc-recall
  panel A)*
- The mechanism clue: answer fact-scores were **tied** (~0.95 both) — the agent
  increasingly answered *from the summaries in the tree* instead of fetching the primary
  text. For a normative spec, that trades verifiable grounding for trust in paraphrases.
- **The scoping you insisted on (correctly):** one document type each way. Website
  (discursive, subjectively scored): summaries helped. RFC (technical, objectively
  scored): summaries hurt. Two venues cannot establish "corpus-dependent" — that's the
  open question, not the conclusion.

**Cliffhanger:** the same pipeline is already pointed at a legal document (GDPR — the
EUR-Lex PDF has *no* embedded outline, so even the "free structure" claim gets stress-
tested). Does the reversal replicate? Part 2.

### Beat 6 — Closing the loop upstream (short, sympathetic)

**Facts you can use:**
- Before publishing: verified the behavior unchanged on current upstream `main` (== the
  pinned commit), searched for prior reports (none), then filed
  [VectifyAI/PageIndex#355](https://github.com/VectifyAI/PageIndex/issues/355) — a
  behavior report with a two-minute repro and both fix options left to the maintainers.
- Optional wry footnote (verify it's still true when you publish): the repo's own
  LLM-powered issue-dedupe bot crashed on the issue — the report about an LLM feature
  silently failing was greeted by an LLM bot… failing.

**Voice prompts:** Why file rather than just blog? (Your answer to this in our session —
"the good-citizen move, plus a timestamped record" — is worth saying publicly.)

### Beat 7 — What I'd tell a team (the takeaway beat, leaders' layer)

Candidate takeaways (pick 2–3, in your words):
- **Defaults deserve autopsy**: a feature's default configuration can invert its value
  proposition, invisibly. Diff what the pipeline *emits* against what you *believe* it
  does.
- **Measure what you re-send, not just what you send**: persistent context (the tree) is
  re-billed every turn; enrichment multiplies every future question's cost.
- **Spend on structure last**: if your documents already carry authored structure
  (headings, bookmarks), you may not need to buy inferred structure at all —
  AI-readiness is partly a representation problem you may have already solved.
- **A good navigator beats a rich map** (on well-structured corpora — keep the scope).

---

## Evidence map (claim → number → artifact → figure)

| Claim | Number | Source artifact | Figure |
|---|---|---|---|
| Default summaries are mostly verbatim | 273/339 = 80.5% (IDX-O 80.2%) | `findings-summary-threshold.md`; `indexes/IDX-C/` | — |
| Tree tax, site corpus | 8.9K / 35.5K / 43.7K tok per turn (D / C0 / C) | `runs/*/run.json` `structure_tokens` | tree-tax |
| Tree tax, RFC | 6.8K vs 39.3K | `runs/20260715T051258Z/` | tree-tax |
| C0 dominates C | mean 4.54 vs 4.11 (0–5); $2.69 vs $3.29 | `runs/20260712T180445Z/scores.csv` | quality-cost |
| Headings baseline value | mean 3.82 at $0.80/14Q | same run | quality-cost |
| Navigator > index | Sonnet ans 3.93 vs gpt-4o ~3.25; summaries Δ ±0.1 | `evaluations/scores-master.csv`; `V1_FINDINGS_HANDOFF.md` §2 | — |
| qwen collapse | 15/28 runs zero fetches; mean 0.89/5 | `V1_FINDINGS_HANDOFF.md` §5 | — |
| RFC reversal | recall 0.918→0.687; facts tied ~0.95; cost 4.6× | `runs/20260715T051258Z/{recall,answer_facts}.csv` | rfc-recall A |
| Representation ≈ nil (structure equal) | 0.906 vs 0.821, $1.27 vs $1.24 | `runs/20260715T174748Z/recall.csv` | rfc-recall B |
| Outline = authored tree | 311/311 titles identical; ~$0 vs $6.44 LLM-inferred (474 nodes) | `indexes/IDX-PDF-outline-rfc9110/`; usage ledger | — |
| Extraction corruption caught pre-retrieval | 39 × `pB.001`, 57 ligatures | `qc-paper-tree-gate.md` | — |
| Whole study cost | $29.95 total; $13.67 of it index builds | `runs/usage_log.jsonl` | — |
| Upstream behavior current + reported | main == `f413c66`; issue #355 | `upstream-issue-draft.md` | — |

## Do-not-claim list (verbatim from our guardrails)

- Not "PageIndex beats / loses to vector RAG" — **no baseline was run**.
- Not "summaries are useless" — they helped the website corpus.
- Not "Sonnet is better than gpt-4o" — scoped to navigation behavior on this corpus;
  tied on direct lookup.
- Not "summaries hurt in general" — one document type; that's Part 2's question.
- No category-level rate stated as statistically powered (2–6 questions per cell).
- Not "deterministic outlines always suffice" — GDPR's outline-less PDF is the live
  counterexample being tested.

## Links to embed

- Deep layer: `reports/RESULTS.md` (now on `main`)
- Mechanism note: `reports/findings-summary-threshold.md`
- Pre-registration: `reports/design-rfc-summary-test.md`
- Upstream issue: https://github.com/VectifyAI/PageIndex/issues/355
- PageIndex: https://github.com/VectifyAI/PageIndex
- Figures: `reports/figures/results-{tree-tax,website-quality-cost,rfc-recall}.svg`

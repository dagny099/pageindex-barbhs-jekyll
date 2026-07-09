# Candidate Questions — site-book-v1

Proposed additions to the evaluation question set. **27 candidates**, grouped by the five
categories, numbered to continue the seed set in `questions.csv` (DL4+, CS4+, …) so winners
transfer directly. Every question was verified against `corpus/site-book-v1/site-book-v1.md`
(line numbers below refer to that file); node ids refer to `indexes/IDX-D/index.json`.

**Field semantics** (matches the CSV / rubric): `expected_evidence` = WHERE a correct answer
must draw from (grades retrieval, rubric C). `ground_truth` = WHAT it must contain (grades the
answer, rubric D). For open-ended questions, ground_truth is acceptance criteria.

*Not empirically pressure-tested: the harness only loads questions from `questions.csv`
(scripts/run_retrieval.py:115), which this exercise must not modify. All grounding is by
direct corpus verification.*

---

## Direct location

### DL4 — Poolula's five scoring dimensions
- **question:** According to the Poolula platform page, what five dimensions does its evaluation harness score, and what composite target must be met before production deployment?
- **expected_evidence:** Poolula Platform § Governance & Reliability → Evaluation Harness (node 0068, L681–700; dimensions table L690–699, target L700).
- **ground_truth:** Tool Usage, Content Relevance, Semantic Similarity, Numerical Accuracy, Citation Accuracy; target ≥90% composite score before production deployment.
- **why_strategic:** "Evaluation harness" appears in ~6 documents; the answer lives under a non-obvious parent heading ("Governance & Reliability"), so keyword grabbing lands in the wrong doc while hierarchy navigation succeeds.
- **difficulty:** easy

### DL5 — Era-based smart defaults
- **question:** What is the "era-based smart defaults" fallback in the fitness dashboard's workout classification, and what date defines the era boundary?
- **expected_evidence:** Self-Hosted Workout Intelligence § How It Works → ML Classification System, the "Era-Based Smart Defaults" details block (node 0084, L972–1000; the fallback hierarchy L983–1000).
- **ground_truth:** When K-means has <5 workouts, classification falls back to era defaults at medium confidence (0.5): before June 1, 2018 (Choco's arrival) → real_run; after → pup_walk; tertiary fallback is rule-based pace thresholds.
- **why_strategic:** Content inside a collapsed `<details>` block under one of SIX identical "How It Works" headings — tests both disambiguation of a recurring title and navigation depth.
- **difficulty:** medium

### DL6 — Hybrid ranking formula and its epistemic status
- **question:** In the GraphRAG migration post, what are the four components and weights of the hybrid ranking score, and what does the author say about how those numbers were chosen?
- **expected_evidence:** Twin GraphRAG post § Three problems, three architectural moves (node 0183, L2339–2349, formula L2347) **and** § Where I'm being cautious (node 0186, L2377). Both sections needed.
- **ground_truth:** 60% vector similarity + 25% boost for sections that explicitly describe a project + 10% entity-mention richness + 5% substantial length. Explicitly "calibrated guesses" / "a working hypothesis" with no empirical optimization yet; Phase 5 will tune them.
- **why_strategic:** The formula and its caveat live in different sections of the same article; an answer citing the numbers without the "educated guess" status is incomplete — grades evidence completeness, not just branch hit.
- **difficulty:** medium

### DL7 — The saturated MENTIONS signal
- **question:** Which document explains why an entity-richness ranking signal is "effectively binary in production," and what specific numbers support that claim?
- **expected_evidence:** Twin GraphRAG post § Where I'm being cautious (node 0186, L2379).
- **ground_truth:** The MENTIONS edge bonus caps at 5 mentions per section, but the median section has 9 mentions and the mean is just under 10, so ~75% of sections sit above the cap — the signal saturates.
- **why_strategic:** Needle question: no heading contains the keywords, and "Where I'm being cautious" appears in TWO articles (nodes 0176 and 0186). Summaries (IDX-C) may or may not surface it — a clean IDX-D vs IDX-C discriminator.
- **difficulty:** hard

### DL8 — Multi-library EXIF cascade
- **question:** What is the beehive platform's multi-library EXIF extraction strategy, and what quantified improvement did it deliver?
- **expected_evidence:** Beehive Analytics Platform § How It Works, "Multi-Library EXIF Strategy" details block (node 0106, L1308–1334); corroborated in § What Shipped → Data Extraction (L1367).
- **ground_truth:** Cascade of three libraries in order of speed vs comprehensiveness: PIL → ExifRead → PyExifTool; reduced metadata extraction failures from ~30% to under 5% (95%+ success rate).
- **why_strategic:** Single-node lookup baseline with a numeric answer that can be graded exactly; again buried under a recurring "How It Works" heading.
- **difficulty:** easy

### DL9 — The instruction ceiling
- **question:** What instruction-count ceiling does the instruction-file scoring post cite from Anthropic's guidance, and how did the author's own CLAUDE.md measure against it?
- **expected_evidence:** A Scoring System for AI Instruction Files § What the research says about size (node 0210, L2703–2709).
- **ground_truth:** Frontier models follow roughly 150–200 instructions reliably; Claude Code's system prompt accounts for ~50. Her CLAUDE.md contained ~150 instructions, putting the total at ~200 — right at the ceiling.
- **why_strategic:** Clean single-source lookup with two related numbers that must be combined correctly (150–200 ceiling vs 150 + 50 = 200 at the ceiling) — catches sloppy synthesis.
- **difficulty:** easy

---

## Cross-section synthesis

### CS4 — Three homemade scoring rubrics, compared
- **question:** The corpus describes at least three evaluation rubrics the author built: Poolula's harness, the Digital Twin's planned rubric, and the instruction-file scorecard. What does each score, and with what dimensions or categories?
- **expected_evidence:** Poolula § Evaluation Harness (node 0068, L690–700); Twin model-comparison post § What I'm doing next (node 0177, L2274); Scoring System post § The framework (node 0211, L2711–2723). All three sections.
- **ground_truth:** Poolula: 5 dimensions (tool usage, content relevance, semantic similarity, numerical accuracy, citation accuracy), ≥90% composite target. Twin: 6 dimensions (accuracy, specificity, voice fidelity, strategic usefulness, grounding, follow-up quality) — scores not yet filled in. Instruction files: 6 categories / 100 points (structure, accuracy, comprehensiveness, actionability, information balance, usability for AI).
- **why_strategic:** Three near-synonymous vocabularies ("dimensions", "rubric", "categories") in three branches; vector-ish similarity would blur them together, hierarchy keeps them distinct. Also personally useful: shows her evaluation habit is portable.
- **difficulty:** hard

### CS5 — The hold-one-variable-constant method
- **question:** Both Digital Twin posts use the same experimental design. What is it, and which variable does each post isolate?
- **expected_evidence:** Twin model-comparison § The setup (node 0172, L2204–2215); Twin GraphRAG § Same questions, two retrieval systems (node 0182, L2323–2331, which explicitly contrasts the two posts).
- **ground_truth:** Run the same 58-question set while holding everything else constant. Post 1 varies the language model (GPT-4.1 vs Gemini 2.5 Flash; same retrieval, top-k, prompt, temperature 0.6). Post 2 varies the retrieval architecture (ChromaDB ~900-char chunks vs Neo4j GraphRAG with section-level units) with the same LLM.
- **why_strategic:** Requires connecting two documents through an explicit cross-reference; also the method mirrors this very PageIndex experiment's design, so the answer doubles as a coherence check on her public methodology.
- **difficulty:** medium

### CS6 — Memory-retrieval-through-context, across domains
- **question:** The idea that "retrieval works through context and association, not brute-force search" recurs across the corpus. Where does it appear, and to what different technical domain does each instance apply it?
- **expected_evidence:** Homepage § Cognitive Principles in Practice → Metadata Matters card (node 0015, L98–102); My Journey § The Big Turns → Making Metadata Human-Friendly (node 0053, L428–430); Three Readers § The deeper idea (node 0223, L2843–2852); Memory Is More Than Storage resource (node ~0263, L3689–3696). At least three of the four.
- **ground_truth:** Acceptance criteria: identify ≥3 instances and their domains — (a) homepage: web metadata as "digital equivalent of cognitive context"; (b) My Journey: SEC data-catalog design mirroring associative human recall; (c) Three Readers: structured data as the associations that let queries surface a page ("the page is the memory"); (d) Memory resource: selection/structure/retrieval/revision/forgetting for AI agents. Strong answers name the shared claim; which instances are cited may reasonably vary.
- **why_strategic:** The concept is never given one canonical name — tests whether the system can track an idea across surface vocabularies (metadata/SEO, data governance, agent memory). Directly probes the experiment's "knowledge legibility" theme.
- **difficulty:** hard

### CS7 — When do graphs beat vectors?
- **question:** Synthesizing the GraphRAG migration post, "RAG Without the Theater," and "Bees, Graphs & Governance": when does the author say graph-based or hybrid retrieval earns its keep over plain vector retrieval, and when is vector retrieval fine?
- **expected_evidence:** Twin GraphRAG § Three problems (node 0183, L2339–2349) and § Where I'm being cautious (L2381, "GraphRAG isn't automatically better…"); RAG Without the Theater § Three small patterns → Hybrid Retrieval (node 0244, L3082–3089) and § Anti-patterns ("vector monoculture", L3057–3060); Bees, Graphs & Governance § From piles of stuff to a knowledge graph (node 0253, L3160–3172).
- **ground_truth:** Graphs/hybrid win on relationship queries ("which projects use X"), joined/contextual queries, multi-signal ranking, and when lineage/governance must be queryable; vector similarity alone can't distinguish describing from mentioning. Vector retrieval is "fast and entirely adequate" for short factual questions answered in one place. Anti-pattern named: vector monoculture. Costs acknowledged: operational complexity, entity-extraction as a new failure surface.
- **why_strategic:** Three documents in two different corpus sections (Articles + the "thinking" pieces) with consistent doctrine — grades multi-branch synthesis and whether the nuance (vectors are fine sometimes) survives.
- **difficulty:** hard

### CS8 — The Streamlit habit and its acknowledged trade-off
- **question:** Which of the six portfolio projects use Streamlit, and what trade-off do the project pages repeatedly acknowledge for choosing it?
- **expected_evidence:** Technology headers of all six project pages (L550, L807, L1226, L1487, L1723, L1975); "Why Streamlit?" details blocks in Fitness (L1102–1115) and Beehive (L1394–1406); Convoscope § Why These Choices (L2129–2131).
- **ground_truth:** Five of six: Fitness, Beehive, ChronoScope, Digital Memory Chest, Convoscope. Poolula is the exception (FastAPI + CLI; no Streamlit in its stack). Trade-off, stated near-verbatim in multiple places: less UI customization (than React) and Streamlit-specific session/state patterns, accepted for much faster data-app development.
- **why_strategic:** Enumeration across ALL project branches, including two where the evidence is only in the metadata header — punishes first-match retrieval; the "which one doesn't" part tests completeness.
- **difficulty:** medium

---

## Consistency

### CN4 — 13 or 14 years of workout data?
- **question:** How many years of workout/running data does the corpus claim? Compare Start Here, the fitness project page, and the 7±2 essay — do they agree?
- **expected_evidence:** Start Here § quickest path, item 2 (node 0021 area, L185: "13 years of running data"); Self-Hosted Workout Intelligence § Summary / 30-second version (L815–817: "14 years") and The Problem (L843: "14 years"); Choco Effect table (L1060–1065: 7 yrs + 6.5 yrs ≈ 13.5); 7±2 essay § Evidence across three domains (L3252: "14 years, 2,593 workouts").
- **ground_truth:** They do not fully agree: Start Here says 13 years; the project page and the essay say 14; the project's own pre/post table sums to ~13.5. A correct answer surfaces the discrepancy (plausibly drift as time passed) rather than picking one number.
- **why_strategic:** Classic naive-retrieval trap: any single hit "answers" the question confidently. Only a system that checks multiple branches detects the inconsistency.
- **difficulty:** medium

### CN5 — Three clusters or four classifications?
- **question:** The fitness project page and the 7±2 essay both describe ML clustering of the same workout data. Do they agree on how many categories emerged, and on what those categories are?
- **expected_evidence:** Self-Hosted Workout Intelligence § ML Classification System (node 0084, L972–981: real_run / pup_walk / mixed / outlier); 7±2 essay § Fitness tracker, 14 years, 2,593 workouts (node ~0253 area, L3252–3260: "snapped to three durable groups" — fast / slow / transition).
- **ground_truth:** They diverge: the project page presents four classifications (including an "outlier" data-quality bucket); the essay says clustering snapped to three durable groups. A strong answer notes the tension and the plausible reconciliation (mixed≈transition; outlier as a QC label rather than a cluster) — but must not paper over the different counts.
- **why_strategic:** True same-entity cross-reference with a genuine surface contradiction — exactly the class of question the experiment's "consistency" category was designed for, and one the CN2 seed failed to find.
- **difficulty:** hard

### CN6 — The metadata post's own metadata
- **question:** What publication date does "Why Metadata Matters" carry in its metadata header, and what date does the post's body claim it was published? Do they agree?
- **expected_evidence:** Why Metadata Matters header block (node 0225, L2866–2875: "Publication date: 2025-11-7") and § The Meta-Meta Insight (node 0235, L2992–3001: "It was published on 2025-11-15").
- **ground_truth:** They disagree: header says Nov 7, 2025; the body's self-describing example says Nov 15, 2025. Bonus for noting the irony (a post about metadata consistency, whose author later wrote "dates are promises you'll break" in the instruction-file scoring post, L2743).
- **why_strategic:** Requires reading both the doc's metadata preamble and a deep body section — tests whether normalized front-matter is actually reachable through the index, an explicit preprocessing/rubric-A concern of the brief.
- **difficulty:** medium

### CN7 — "One click from how it was calculated"
- **question:** Work With Me claims the fitness dashboard "keeps every metric one click from how it was calculated." Does the fitness project page support that description, and via what named feature?
- **expected_evidence:** Work With Me § Verified AI System Build, "Proof this is how I actually work" (node 0035, L283); Self-Hosted Workout Intelligence § What Shipped → ML/AI Features (node 0088, L1035: "Algorithm Transparency: Full visibility into how each AI feature makes decisions"; also Performance Benchmarks L1157).
- **ground_truth:** Substantively yes — the "Algorithm Transparency" feature is the backing evidence, though the project page never uses the "one click" phrasing; the consulting page's wording is a marketing gloss on "full visibility." A precise answer maps claim → feature and notes the paraphrase.
- **why_strategic:** A clean, verified same-entity cross-reference (consulting claim ↔ project feature) — the sharpened replacement for seed CN2, whose validation run only found a thematic pairing.
- **difficulty:** medium

### CN8 — The chunking essay's incoherent identity
- **question:** For the essay "7+-2 is Everywhere: Chunking is all you need," do its source filename date, publication date, and canonical URL tell a consistent story about what and when it is?
- **expected_evidence:** Essay header block (node 0251 area, L3227–3238): source path `_thinking/2024-09-26-chunking-is-all-you-need.md`, publication date 2025-09-11, canonical URL `/thinking/why-dashboards-fail/`.
- **ground_truth:** No, three ways: filename says 2024-09-26 but publication date says 2025-09-11; the URL slug ("why-dashboards-fail") doesn't match the title or filename ("chunking"); nothing reconciles them. A good answer flags all three.
- **why_strategic:** Pure metadata-fidelity probe (rubric A/B): the facts sit in the normalized header, not the prose. Discriminates whether IDX-C summaries preserve or wash out provenance details.
- **difficulty:** medium

### CN9 — Poolula's Streamlit ghost *(stretch)*
- **question:** Poolula's Implementation Notes list "Lazy loading of ML models via `@st.cache_resource`" as a key pattern. Is Streamlit anywhere in Poolula's declared stack, and what might explain the mismatch?
- **expected_evidence:** Poolula header technologies (L550 — no Streamlit; FastAPI/SQLModel/CLI) vs § Implementation Notes → Key patterns (node 0075, L773–776).
- **ground_truth:** `st.cache_resource` is a Streamlit API, but Streamlit is absent from Poolula's technologies and its shipped interface is a CLI + FastAPI. Most plausible explanation: boilerplate carried over from the author's five Streamlit projects. Any answer that (a) confirms the mismatch and (b) doesn't invent a Streamlit UI for Poolula passes.
- **why_strategic:** The hardest kind of consistency check — a single-token internal contradiction. Likely fails for every condition; valuable as a ceiling probe. FLAG: may be too subtle to be a fair scored question; consider keeping as an exploratory item.
- **difficulty:** hard

---

## Evidence gap

### EG4 — The missing Resume Explorer
- **question:** Work With Me names "Resume Explorer" among "live, deployed systems" to browse. Is there a Resume Explorer project page in the corpus, and where — if anywhere — is that work actually described?
- **expected_evidence:** Work With Me § Browse projects card (node 0042, L329–331); the Project Portfolio section as a whole (nodes 0059–0167, L540–2174 — six projects, none of them Resume Explorer); indirect descriptions: Twin GraphRAG post (L2317, L2333–2337, "Resume Graph Explorer") and the Resume Data Schema resource (L3717 onward).
- **ground_truth:** No project page exists. The system appears only obliquely: as an anecdote in the GraphRAG article and via the resume-data-schema resource that documents its underlying JSON. A strong answer states the absence confidently and cites the two indirect traces. Personally actionable: a showcased system with no portfolio page.
- **why_strategic:** Absence detection requires exhaustively ruling out a whole branch — the capability the brief says hierarchical reasoning should enable and keyword retrieval can't ("no hits" ≠ verified absence).
- **difficulty:** hard

### EG5 — Certifications on assertion alone
- **question:** Work With Me cites two professional certifications. What are they, and does any other document in the corpus mention or evidence them?
- **expected_evidence:** Work With Me § Production AI (node 0040, L315–317). Negative evidence: My Journey (incl. § Dive Deeper, L480–530) and the rest of the corpus contain no mention; the resume PDF is referenced (L171, L299, L506) but is outside the corpus.
- **ground_truth:** CDMP (data management) and Azure AI Engineer Associate. No other corpus document mentions either — the claims rest on assertion plus a pointer to an out-of-corpus resume PDF. (They are plausible, just unevidenced *here*.)
- **why_strategic:** Small, checkable instance of the seed EG1 pattern; grades whether the system distinguishes "supported elsewhere in corpus" from "asserted once."
- **difficulty:** medium

### EG6 — Real numbers vs bracketed placeholders
- **question:** The 7±2 essay presents quantitative evidence from three domains. Which of its statistics are actual numbers, and which are unfilled placeholders?
- **expected_evidence:** 7±2 essay § Evidence across three domains (L3252–3275): real figures at L3252, L3263–3266, L3272–3274; placeholder lines L3260 ("[X%] of variance"), L3269 ("[Y%] of production queries"), L3275 ("[Z%] dwell time").
- **ground_truth:** Real: 2,593 workouts / 14 years; 3 clusters; 400+ inspections / 4 seasons; 5 weather variables; 7 edge types; the Convoscope 10-vs-3 model card anecdote. Placeholders (literal bracketed stubs labeled "optional … placeholder"): variance explained, query coverage, engagement lift. A correct answer must not launder the placeholders into claimed results.
- **why_strategic:** Tests reading precision over gist — summarization (IDX-C) plausibly erases the bracket-placeholder distinction, making this a sharp index-condition discriminator and a genuinely useful editorial finding for the owner.
- **difficulty:** medium

### EG7 — The diagnostic that isn't there
- **question:** What are the fifteen questions in the "Is Your Knowledge Ready for AI?" diagnostic? If the corpus can't answer that, what does it actually contain about the diagnostic?
- **expected_evidence:** Resources & Guides index: featured card (L3398–3400) and collection entry (L3517–3523); Work With Me § Knowledge Legibility Audit footer link (L271). The diagnostic page itself is NOT among the corpus's 25 documents.
- **ground_truth:** Unanswerable as asked: the corpus never lists the fifteen questions. It only says there are fifteen, across five dimensions — findability, structure, provenance (traceable), ownership, verification (checkable). The correct behavior is to say so; inventing fifteen questions is the failure mode this probes.
- **why_strategic:** Hallucination bait with a partial-credit answer available — separates honest-fallback behavior (a stated goal in her own "RAG Without the Theater," L3107) from confident fabrication.
- **difficulty:** medium

### EG8 — Targets and promises vs measured results
- **question:** Which evaluation numbers in the corpus are targets or in-progress plans rather than completed measurements? Cover Poolula, the GraphRAG migration, and the Twin model comparison.
- **expected_evidence:** Poolula: ≥90% target (L700), 31/37 tests passing (L739–740), eval set expansion 15→40 "in progress" (L747, L754); GraphRAG § Where I'm being cautious (L2375: five-battery plan "none … run end-to-end") and § What I'm doing next (L2387: old system "passes at roughly 85%"); Twin comparison § Where I'm being cautious (L2260: human-scoring columns "left blank").
- **ground_truth:** Targets/plans: Poolula's 90% composite (a gate, not a result); GraphRAG's five evaluation batteries and weight tuning (not yet run); Twin's manual rubric scores (blank). Actually measured: the Twin's 58-question behavioral metrics (lengths, follow-ups, costs), the old pipeline's ~85% pass rate, Poolula's 31/37 test suite. Distinguishing the two lists correctly is the answer.
- **why_strategic:** High personal value — an honest audit of "verification-first" positioning — and a hard synthesis task where every source deliberately mixes achieved and aspirational numbers in adjacent sentences.
- **difficulty:** hard

---

## Reflective discovery

### RD4 — The exhausted human
- **question:** A recurring character in this corpus is the exhausted human — someone making decisions while tired, stressed, or distracted. Where does this figure appear, and what design principle does it encode?
- **expected_evidence:** My Journey § Lenses I Bring to Every Problem (node 0047, L378–380: "a tired human at 3pm on Friday") and § Healthcare Through a Cognitive Lens (node 0051, L414–416: "Nurses making decisions at 3am"); reinforced by the 7±2 essay's cognitive-load design rules (L3286–3311).
- **ground_truth:** Acceptance criteria: find both My Journey instances; articulate the principle — systems must work under real cognitive load, not ideal conditions ("If it doesn't work when you're distracted, it doesn't work"). Strong answers connect it to chunking/progressive-disclosure rules; which connections are drawn may vary.
- **why_strategic:** The motif is verbal, not headed — no section is titled anything like it. Tests thematic retrieval across a single doc's branches plus optional cross-doc linkage.
- **difficulty:** medium

### RD5 — What is she afraid of shipping?
- **question:** Based only on the six project pages, what failure does this builder seem most determined to prevent — and what does each project include to guard against it? Which project's guard is thinnest?
- **expected_evidence:** Poolula § Governance & Reliability (L679–727); ChronoScope quality validation/confidence scoring (L1508, L1564–1566); Fitness Algorithm Transparency (L1035); Memory Chest moderation + AI fallbacks (L1799–1805, L1867–1891); Convoscope blind scoring (L2049–2059, L2085–2092); Beehive confidence thresholds (L1373, L1453) — the whole Project Portfolio branch.
- **ground_truth:** Acceptance criteria: identify the fear as unverified/untrustworthy AI output (trusting fluent answers without provenance). Guards: Poolula eval harness + provenance/audit; ChronoScope confidence scoring + validation; Fitness algorithm transparency; Memory Chest moderation + graceful fallbacks; Convoscope blind comparison scoring. Thinnest: Beehive (only CV confidence thresholds; no evaluation layer). Reasonable answers may frame the fear as "hallucination" or "unaccountable automation" — same substance.
- **why_strategic:** Reflective synthesis requiring coverage of all six branches plus a comparative judgment (thinnest guard) that punishes partial retrieval; output is directly useful positioning feedback.
- **difficulty:** hard

### RD6 — Does she use "harness" the way she decodes it?
- **question:** The harness resource decodes five meanings of "harness" in AI. Judged across the whole corpus, which meaning dominates the author's own usage, and does the resource itself acknowledge that origin?
- **expected_evidence:** What Does 'Harness' Mean in AI? (node ~0261, L3653–3668, esp. L3659 and § See one in practice); usage sites: Poolula evaluation harness (L560, L681+), Twin posts (L2387, L2426, "evaluation harness"), Work With Me Offer 2 (L279).
- **ground_truth:** Meaning #1 — the evaluation harness — dominates every corpus usage; the resource explicitly says she built the decoder while building the Twin's evaluation setup, and its "See one in practice" links point to the two Twin posts. Consistent usage; the other four meanings appear only inside the decoder.
- **why_strategic:** Terminology-consistency probe (sharpens seed CN3) that requires aggregating scattered usages against a definitional page — a task where IDX-C's summaries might genuinely help, making it a good index-condition contrast.
- **difficulty:** medium

### RD7 — Evidence of outcomes, or evidence of process?
- **question:** What evidence of external outcomes — client results, testimonials, adoption or usage numbers from other people — exists anywhere in the corpus? What does the answer imply about how the consulting positioning is evidenced?
- **expected_evidence:** Work With Me in full (L234–347); the "Proof this is how I actually work" list (L283); project pages' shipped/benchmarks sections (e.g., L1017–1050, L1151–1158); the two Twin posts. The point is what's *absent* after checking these.
- **ground_truth:** Acceptance criteria: conclude there are none — no client case studies, testimonials, or third-party adoption metrics anywhere. All evidence is self-built systems, self-run evaluations, and public write-ups ("watch me work in public"). Strong answers note this is a deliberate-looking but risky positioning: process transparency substitutes for client proof, and the closest thing to external validation is citation count (430+) from a prior career. Judgments about severity may vary.
- **why_strategic:** The highest-value owner question in the set: it grades whether the system can characterize a corpus-wide absence and reason about positioning, not just fetch. Companion to EG4/EG5 at a strategic altitude.
- **difficulty:** hard

### RD8 — From patterns to governance: the 2025→2026 shift
- **question:** Compare the two September-2025 "thinking" essays (RAG Without the Theater; Bees, Graphs & Governance) with the mid-2026 articles (Judgment Gap; Missing Layer). How has the author's framing of trustworthy AI shifted, and what stayed constant?
- **expected_evidence:** RAG Without the Theater (nodes 0238–0250, L3031–3127); Bees, Graphs & Governance (nodes 0251–0260, L3133–3223); Judgment Gap (nodes 0188–0194, L2403–2484); Missing Layer (nodes 0195–0206, L2490–2664). Publication dates in each header.
- **ground_truth:** Acceptance criteria: shift = from tactical implementation patterns and checklists (claims→evidence maps, provenance fields, router rules) to organizational/judgment framing (literacy stack, governance, the "missing layer" of accountability, cost visibility, work design). Constants = evidence-linked answers, provenance, honest fallback / defining "good" before trusting output. Framing of the shift (audience change vs intellectual evolution) may legitimately vary.
- **why_strategic:** Tests whether the index makes chronology usable (dates live in headers) and whether retrieval can sustain a four-document compare — the hardest legitimate synthesis in the set.
- **difficulty:** hard

---

## Corpus observations

**Structural quirks that make good question fodder**
- Recurring headings are pervasive: **"How It Works"** ×6, **"Architecture"** ×6-7, **"What's Next"** ×7, **"Summary"** ×25, **"Implementation Notes"** ×5, **"Where I'm being cautious" / "What I'm doing next"** ×2 each. Any question whose answer sits under one of these is automatically a hierarchy-disambiguation test (DL4, DL5, DL7, DL8 exploit this).
- Much load-bearing detail lives inside `<details>` blocks (era defaults L983, EXIF cascade L1308, Streamlit trade-offs L1102/L1394) — a preprocessing/boundary-accuracy sensitivity worth watching in rubric A/B.
- Normalized metadata headers are first-class content here (dates, URLs, technologies). CN6 and CN8 only work if the index preserves them; a summary-based index might paraphrase them away.

**Where contradiction lurks (verified)**
- 13 vs 14 years of workout data (Start Here L185 vs project L817 vs essay L3252); 3 clusters vs 4 classifications for the same ML system (L3255 vs L976); the metadata post's header date vs its body date (L2871 vs L2998); the chunking essay's filename/date/URL triple mismatch (L3231–3238); Poolula's `@st.cache_resource` with no Streamlit in its stack (L550 vs L775).

**Where evidence is thin**
- Consulting claims resting on assertion: certifications (L317), the workshop offer (no case evidence anywhere), "Resume Explorer" as a named showcase with no portfolio page (L331).
- Aspirational numbers adjacent to measured ones: Poolula's ≥90% is a gate not a result (L700); GraphRAG's evaluation plan is unrun (L2375); the Twin's human-scored rubric is blank (L2260); the 7±2 essay ships literal `[X%]`/`[Y%]`/`[Z%]` placeholders (L3260, L3269, L3275).
- No external/client outcomes anywhere in the corpus — all proof is self-evaluation in public (see RD7).

**Duplication worth knowing about**
- The Choco story is told at least four times (project summary, 2-minute version, Choco Effect section, 7±2 essay) with slightly drifting numbers — retrievers may stop at the first telling.
- The "same questions, one variable" methodology is described in both Twin posts, and Work With Me's proof list re-describes Poolula/Twin/Fitness — useful for cross-reference questions, but it also means shallow retrieval can look right by hitting the paraphrase instead of the source (CN7 grades exactly this).

**Notes on the seed set**
- CN2's validation flag is addressed by CN7 (a verified same-entity cross-reference) and CN5 (a verified same-entity contradiction).
- DL1's premise is worth re-checking: the corpus never formally *defines* "knowledge legibility"; the closest things are Work With Me's gloss (L251, "made legible — to the machines processing it, or to the humans acting on it") and the diagnostic card's five dimensions (L3399, L3523). Either sharpen DL1's expected_evidence to those, or treat it as a soft evidence-gap question.

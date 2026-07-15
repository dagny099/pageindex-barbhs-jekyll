# Grading worksheet — the 5 pivotal questions (IDX-D vs IDX-C vs IDX-C0)

Run `20260712T180445Z` · retriever `gpt-4o-2024-11-20` · 0–4 scale.
Fill the **YOUR score** columns; my draft (claude-opus first pass) is shown for reference.
These 5 questions drive the whole IDX-C0 result — if your grades soften them, the C0 edge shrinks.

## Scoreboard (fill in)

| qid | D retr/ans | C retr/ans | C0 retr/ans |
|---|---|---|---|
| CS6 (draft: D 1/2, C 3/3, C0 4/4) | __/__ | __/__ | __/__ |
| RD4 (draft: D 1/2, C 4/4, C0 4/4) | __/__ | __/__ | __/__ |
| RD6 (draft: D 2/2, C 3/4, C0 4/4) | __/__ | __/__ | __/__ |
| EG6 (draft: D 4/4, C 3/1, C0 4/4) | __/__ | __/__ | __/__ |
| CN4 (draft: D 4/4, C 4/3, C0 4/4) | __/__ | __/__ | __/__ |

---

## CS6 — cross-section-synthesis

**Q.** The idea that "retrieval works through context and association, not brute-force search" recurs across the corpus. Where does it appear, and to what different technical domain does each instance apply it?

**Expected evidence.** Homepage § Cognitive Principles in Practice → Metadata Matters card (node 0015, L98–102); My Journey § The Big Turns → Making Metadata Human-Friendly (node 0053, L428–430); Three Readers § The deeper idea (node 0223, L2843–2852); Memory Is More Than Storage resource (node ~0263, L3689–3696). At least three of the four.

**Ground truth.** Acceptance criteria: identify ≥3 instances and their domains — (a) homepage: web metadata as "digital equivalent of cognitive context"; (b) My Journey: SEC data-catalog design mirroring associative human recall; (c) Three Readers: structured data as the associations that let queries surface a page ("the page is the memory"); (d) Memory resource: selection/structure/retrieval/revision/forgetting for AI agents. Strong answers name the shared claim; which instances are cited may reasonably vary.

### IDX-D  (fetched: `3062-3091`, `2323-2339`, `3160-3187`)

The idea that "retrieval works through context and association, not brute-force search" appears in the corpus across three technical domains:

1. **Retrieval System Architecture**: In the section *"Same questions, two retrieval systems"* and *"Three problems, three architectural moves"*, the concept is applied to a retrieval system that transitions from a flat vector-based approach to a graph-based architecture. This enables richer contextual queries, such as identifying relationships between projects or methods, by explicitly modeling entities and their connections. [Source: "What Happened When I Asked the Same Questions of Two Retrieval Systems"]

2. **Hybrid Retrieval Patterns**: In *"Hybrid Retrieval with 'Must-Include' Filters"*, the principle is applied to blend sparse (e.g., BM25) and dense (e.g., embeddings) retrieval methods. This approach enforces contextual filters like date or document type, ensuring results are both relevant and fresh. [Source: "RAG Without the Theater — Evidence‑Linked Retrieval Patterns You Can Defend"]

3. **Knowledge Graphs for Analytics**: In *"From 'piles of stuff' to a knowledge graph"*, the idea is used to transform unstructured data into a queryable knowledge graph. By naming entities and relationships explicitly, the system supports complex, context-aware queries, such as analyzing environmental factors affecting outcomes. [Source: "Bees, Graphs, and Governance — Turning Unruly Observations into Evidence‑Ready Decisions"]

These instances demonstrate the application of context and association in retrieval across system design, hybrid search strategies, and knowledge graph modeling.

### IDX-C  (fetched: `98-106`, `2442-2476`, `3031-3103`, `3133-3202`)

The idea that "retrieval works through context and association, not brute-force search" appears in the following sections, each applying it to a distinct technical domain:

1. **Metadata Matters** (Cognitive Principles in Practice):
   - **Domain**: Web metadata and search systems.
   - **Application**: Metadata is likened to cognitive context, enabling the web to surface meaning through associations rather than brute-force indexing. This parallels how human memory relies on associations for retrieval.

2. **The Missing Layer** (What Looks Like an AI Skills Gap Is Often a Judgment Gap):
   - **Domain**: AI literacy and governance.
   - **Application**: Emphasizes judgment and governance in AI workflows, advocating for framing problems and evaluating outputs based on context and association rather than relying solely on tool capabilities.

3. **RAG Without the Theater**:
   - **Domain**: Retrieval-Augmented Generation (RAG) systems.
   - **Application**: Proposes retrieval pipelines that prioritize context and association, such as hybrid retrieval methods and attribution-first composition, to ensure evidence-linked and defensible outputs.

4. **Bees, Graphs, and Governance**:
   - **Domain**: Knowledge graphs and data governance.
   - **Application**: Models relationships explicitly (e.g., photos ↔ weather ↔ events) to make patterns queryable, turning messy data into structured, evidence-ready decisions.

These instances collectively highlight the importance of structured relationships and contextual understanding across domains like web systems, AI workflows, RAG pipelines, and knowledge graphs.

### IDX-C0  (fetched: `98-106`, `428-432`, `2842-2856`)

The idea that "retrieval works through context and association, not brute-force search" appears in the following sections, each applying it to a distinct technical domain:

1. **Metadata Matters** (Cognitive Principles in Practice):
   - **Domain**: Web metadata and search engines.
   - **Application**: Metadata is likened to cognitive context, enabling search engines to surface meaning by association rather than brute force. This parallels how human memory retrieves information through contextual cues.

2. **Making Metadata Human-Friendly** (My Journey):
   - **Domain**: Data discovery systems.
   - **Application**: Interfaces were designed to mirror human memory patterns, emphasizing association and context over rigid taxonomies. This approach improved findability by aligning with natural human retrieval methods.

3. **The Deeper Idea: Metadata as a Knowledge Graph** (Articles):
   - **Domain**: Knowledge representation and structured data.
   - **Application**: Metadata tags (e.g., Open Graph, Schema.org) are described as graph statements that enable entity reconciliation. This structured approach mirrors cognitive processes, where context and associations guide memory retrieval.

These instances collectively highlight the principle's relevance across web systems, data discovery, and knowledge representation.

---

## RD4 — reflective-discovery

**Q.** A recurring character in this corpus is the exhausted human — someone making decisions while tired, stressed, or distracted. Where does this figure appear, and what design principle does it encode?

**Expected evidence.** My Journey § Lenses I Bring to Every Problem (node 0047, L378–380: "a tired human at 3pm on Friday") and § Healthcare Through a Cognitive Lens (node 0051, L414–416: "Nurses making decisions at 3am"); reinforced by the 7±2 essay's cognitive-load design rules (L3286–3311).

**Ground truth.** Acceptance criteria: find both My Journey instances; articulate the principle — systems must work under real cognitive load, not ideal conditions ("If it doesn't work when you're distracted, it doesn't work"). Strong answers connect it to chunking/progressive-disclosure rules; which connections are drawn may vary.

### IDX-D  (fetched: `106-114`, `3296-3313`)

The figure of the "exhausted human" appears in the context of cognitive offloading and decision-making under constraints. Two relevant sections highlight this:

1. **Cognitive Offloading**: This section emphasizes designing dashboards that respect the brain's processing limits by leveraging preattentive attributes like position and luminance. This approach acknowledges that users often make decisions while tired, stressed, or distracted, and aims to reduce cognitive load by aligning design with human perceptual strengths. (Source: *Cognitive Offloading*)

2. **Three Design Rules That Actually Matter**: The principle of "Respect the edges" directly addresses the needs of decision-makers under stress. It suggests front-loading critical constraints and ending with actionable steps, recognizing that first and last positions in a sequence receive disproportionate attention. This design principle encodes the reality of selective attention and cognitive fatigue. (Source: *Three Design Rules That Actually Matter*)

These principles collectively encode the design philosophy of reducing cognitive strain and enabling effective decision-making for users operating under less-than-ideal conditions.

### IDX-C  (fetched: `414-420`, `376-394`)

The recurring figure of the "exhausted human" appears in several contexts within the corpus:

1. **Cognitive Scientist's Lens**: The question, "How will a tired human at 3pm on Friday actually use this?" highlights the importance of designing systems that function effectively under cognitive load, such as when users are tired, stressed, or distracted. This principle emphasizes testing interfaces under real-world conditions to ensure usability when attention is limited. ([Source: Lenses I Bring to Every Problem](#))

2. **Healthcare Technology**: While running BALEX Healthcare Services, the author observed that healthcare technology often fails because it is designed for ideal scenarios rather than the cognitive realities of users, such as nurses making decisions at 3am. Interfaces were designed to reduce cognitive load, ensuring usability under stress and multitasking. ([Source: Healthcare Through a Cognitive Lens](#))

3. **Consulting Work**: Across industries, the author identified that technical solutions often fail when they ignore human cognition. Interfaces were designed to guide attention to critical information and reduce complexity, enabling quick and accurate decision-making. ([Source: The Pattern Recognition Years](#))

### Design Principle Encoded
The overarching design principle is **cognitive scalability**—creating systems that reduce cognitive load and adapt to the user's mental state, ensuring usability even under challenging conditions. This principle prioritizes clarity, attention guidance, and simplicity to support decision-making when users are tired or distracted.

### IDX-C0  (fetched: `376-394`, `414-420`)

The figure of the "exhausted human" appears in multiple sections of the corpus, encoding a design principle focused on reducing cognitive load for users under stress or distraction:

1. **Healthcare Through a Cognitive Lens**: This section highlights the challenges of designing healthcare technology for nurses working late at night. It emphasizes that successful systems must present information in ways that reduce cognitive load, especially when users are exhausted, stressed, and multitasking. ([Healthcare Through a Cognitive Lens](#))

2. **Lenses I Bring to Every Problem**: The cognitive scientist's perspective explicitly asks, "How will a tired human at 3pm on Friday actually use this?" This lens tests interfaces under cognitive load, ensuring they work even when users are distracted. ([Lenses I Bring to Every Problem](#))

These examples underscore the principle that technology must align with human cognitive realities, particularly in high-stakes or demanding scenarios.

---

## RD6 — reflective-discovery

**Q.** The harness resource decodes five meanings of "harness" in AI. Judged across the whole corpus, which meaning dominates the author's own usage, and does the resource itself acknowledge that origin?

**Expected evidence.** What Does 'Harness' Mean in AI? (node ~0261, L3653–3668, esp. L3659 and § See one in practice); usage sites: Poolula evaluation harness (L560, L681+), Twin posts (L2387, L2426, "evaluation harness"), Work With Me Offer 2 (L279).

**Ground truth.** Meaning #1 — the evaluation harness — dominates every corpus usage; the resource explicitly says she built the decoder while building the Twin's evaluation setup, and its "See one in practice" links point to the two Twin posts. Consistent usage; the other four meanings appear only inside the decoder.

### IDX-D  (fetched: `3493-3500`, `3424-3429`)

The resource "What Does 'Harness' Mean in AI?" identifies five meanings of "harness" in AI: evaluation harness, agent harness, readiness harness, judge harness, and test/fuzzing harness. It describes the harness as making the model's power usable, reflecting its role across various technical traditions.

The dominant usage by the author appears to align with "evaluation harness," as this term is explicitly mentioned in the context of governance and reliability in the "Poolula Platform" project (line 681). However, the resource itself does not explicitly acknowledge this origin or emphasize one meaning over the others. It presents all five meanings as equally significant, offering a broad overview rather than focusing on the author's specific usage.

Cited sections:
- "What does 'harness' mean in AI?" (lines 3424–3429)
- "What Does 'Harness' Mean in AI?" (lines 3493–3500)

### IDX-C  (fetched: `3649-3663`, `3424-3663`)

The term "harness" in AI is used across five distinct contexts: evaluation harness, agent harness, readiness harness, judge harness, and fuzzing harness. Each represents a surrounding structure that enables the use, control, testing, or measurement of a capability. The resource emphasizes that "the model gives the power; the harness makes that power usable." These meanings originate from various technical traditions, including software testing, agent runtimes, release engineering, LLM evaluation, and security fuzzing.

The resource itself acknowledges its origin in the author's work on building a systematic evaluation setup for their Digital Twin. This setup includes repeatable questions and checks to assess whether changes improve the system's functionality or merely its appearance of competence. The resource also provides practical examples of harnesses in action, such as behavioral comparisons of LLMs and retrieval-layer migrations.

The dominant usage in the author's work appears to be the "evaluation harness," as it is central to their Digital Twin and consulting projects. This focus is explicitly acknowledged in the resource. 

**Cited Sections:**
- ["What Does 'Harness' Mean in AI?"](https://resources/what-is-a-harness-in-ai/)

### IDX-C0  (fetched: `3424-3429`, `3649-3662`)

The author's usage of "harness" in AI predominantly aligns with the concept of an **evaluation harness**, as evidenced by their focus on systematic evaluation setups for their Digital Twin. This involves repeatable tasks, questions, and checks to assess whether system changes improve functionality or merely enhance superficial performance. The resource itself acknowledges this origin, explicitly stating that the decoder was created during the development of such an evaluation setup.

### Sources:
- **"What does 'harness' mean in AI?"** (Infographic and explanation of five meanings of "harness" in AI)
- **"Summary"** (Discussion of the author's systematic evaluation setup for their Digital Twin)

---

## EG6 — evidence-gap

**Q.** The 7±2 essay presents quantitative evidence from three domains. Which of its statistics are actual numbers, and which are unfilled placeholders?

**Expected evidence.** 7±2 essay § Evidence across three domains (L3252–3275): real figures at L3252, L3263–3266, L3272–3274; placeholder lines L3260 ("[X%] of variance"), L3269 ("[Y%] of production queries"), L3275 ("[Z%] dwell time").

**Ground truth.** Real: 2,593 workouts / 14 years; 3 clusters; 400+ inspections / 4 seasons; 5 weather variables; 7 edge types; the Convoscope 10-vs-3 model card anecdote. Placeholders (literal bracketed stubs labeled "optional … placeholder"): variance explained, query coverage, engagement lift. A correct answer must not launder the placeholders into claimed results.

### IDX-D  (fetched: `3250-3284`)

The "7±2" essay presents quantitative evidence from three domains, with a mix of actual numbers and placeholders:

1. **Fitness tracker**:
   - Actual numbers: 14 years, 2,593 workouts, three clusters (Fast, Slow, Transition).
   - Placeholder: **[X%]** of variance explained by the clusters.

2. **Beehive monitoring**:
   - Actual numbers: Four seasons, 400+ photo-inspections, seven edge types in the knowledge graph.
   - Placeholder: **[Y%]** of production queries covered by the seven edge types.

3. **Convoscope interface**:
   - Actual numbers: Ten models compared, three model cards with five topic chips.
   - Placeholder: **[Z%]** increase in dwell time or click-through for the 3-way comparison.

These placeholders (**[X%]**, **[Y%]**, **[Z%]**) indicate areas where specific percentages could be added but are not yet provided. 

Cited section: "Evidence across three domains."

### IDX-C  (fetched: `3229-3354`)

The essay "7±2 is Everywhere: Chunking is all you need" presents quantitative evidence from three domains, each supported by actual numbers:

1. **Fitness Tracker Data**:
   - 14 years of data encompassing 2,593 workouts.
   - Clustering analysis revealed three durable groups: fast (runs), slow (walks), and transition (brisk-walk-or-jog blur).

2. **Beehive Monitoring**:
   - Four seasons of data with over 400 photo-inspections.
   - Seven edge types in the knowledge graph were identified as critical for practical queries, such as "Inspections before swarms."

3. **Convoscope Interface**:
   - A comparison of ten side-by-side models showed that users engaged more effectively with three model cards and five topic chips, leading to clearer comparisons and faster decisions.

These statistics are actual numbers derived from the analysis, not placeholders. The essay emphasizes the importance of chunking (3–7 meaningful units) for effective decision-making across these domains. [Source: "7±2 is Everywhere: Chunking is all you need"]

### IDX-C0  (fetched: `3229-3363`)

The essay "7±2 is Everywhere: Chunking is all you need" presents quantitative evidence from three domains, with some statistics being placeholders and others actual numbers:

1. **Fitness Tracker Data**:
   - **Actual Numbers**: 14 years of data, 2,593 workouts.
   - **Placeholder**: The percentage of variance explained by the three clusters is left as **[X%]**.

2. **Beehive Monitoring**:
   - **Actual Numbers**: Four seasons, 400+ photo-inspections, five key weather variables, and seven edge types in the knowledge graph.
   - **Placeholder**: The percentage of production queries covered by the seven edge types is left as **[Y%]**.

3. **Convoscope Interface**:
   - **Actual Numbers**: Three model cards with five topic chips were more effective than ten side-by-side models.
   - **Placeholder**: The increase in dwell time or click-through rate for the three-way comparison is left as **[Z%]**.

These placeholders indicate areas where specific quantitative results are yet to be finalized or reported. (Source: "7±2 is Everywhere: Chunking is all you need")

---

## CN4 — consistency

**Q.** How many years of workout/running data does the corpus claim? Compare Start Here, the fitness project page, and the 7±2 essay — do they agree?

**Expected evidence.** Start Here § quickest path, item 2 (node 0021 area, L185: "13 years of running data"); Self-Hosted Workout Intelligence § Summary / 30-second version (L815–817: "14 years") and The Problem (L843: "14 years"); Choco Effect table (L1060–1065: 7 yrs + 6.5 yrs ≈ 13.5); 7±2 essay § Evidence across three domains (L3252: "14 years, 2,593 workouts").

**Ground truth.** They do not fully agree: Start Here says 13 years; the project page and the essay say 14; the project's own pre/post table sums to ~13.5. A correct answer surfaces the discrepancy (plausibly drift as time passed) rather than picking one number.

### IDX-D  (fetched: `134-236`, `3229-3369`, `801-1220`)

The corpus provides three references to the duration of workout/running data:

1. **Start Here**: Mentions "13 years of running data" in the context of a data story about analyzing exercise KPIs.
2. **Self-Hosted Workout Intelligence (Fitness Project)**: States "14 years of workout data" and provides a timeline of pre-Choco (7 years) and post-Choco (6.5 years), totaling 13.5 years.
3. **7±2 Essay**: Refers to "14 years, 2,593 workouts" in the fitness tracker example.

### Comparison:
- The **Start Here** page slightly underestimates the duration at 13 years.
- The **Fitness Project** and **7±2 Essay** agree on 14 years, with the project providing a detailed breakdown.

### Conclusion:
The **Fitness Project** and **7±2 Essay** align, while the **Start Here** page is slightly inconsistent, likely due to rounding or simplification.

### IDX-C  (fetched: `134-236`, `3229-3363`, `801-1211`)

The corpus provides three perspectives on the years of workout/running data:

1. **Start Here Page**: Mentions "13 years of running data" analyzed with machine learning and visualization tools. This aligns with the timeline of 2011–2018 for pre-Choco data, as described in the fitness project.

2. **Self-Hosted Workout Intelligence Project**: States "14 years of workout data" were transformed into actionable intelligence. This includes both pre-Choco (2011–2018) and post-Choco (2018–present) data, totaling approximately 14 years.

3. **7±2 Essay**: Refers to "2,593 workouts" over "14 years," consistent with the fitness project timeline.

### Agreement:
All three sources agree on the 14-year span of workout data, with the Start Here page slightly underestimating it as 13 years. This discrepancy likely arises from rounding or focusing on pre-Choco data.

### Sources:
- **Start Here**: Overview of key projects.
- **Self-Hosted Workout Intelligence**: Detailed project description.
- **7±2 Essay**: Broader context of data analysis.

### IDX-C0  (fetched: `134-223`, `3229-3363`, `801-1211`)

The corpus provides three perspectives on the years of workout/running data:

1. **Start Here**: Mentions a data story analyzing "13 years of running data" using machine learning and visualization ([Start Here](#)).
2. **Self-Hosted Workout Intelligence**: Describes a fitness analytics project covering "14 years of workout data," with a focus on the impact of a rescue puppy in 2018 ([Self-Hosted Workout Intelligence](#)).
3. **7±2 Essay**: Refers to "14 years of fitness tracker data encompassing 2,593 workouts," analyzed using clustering methods ([7±2 is Everywhere](#)).

### Comparison:
- **Agreement**: Both the fitness project and the 7±2 essay consistently state 14 years of data.
- **Discrepancy**: The "Start Here" section mentions 13 years, which may reflect an earlier snapshot or a rounding difference.

### Conclusion:
The fitness project and 7±2 essay align on 14 years, suggesting this is the most accurate figure. The "Start Here" section likely needs updating for consistency.

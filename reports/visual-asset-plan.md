# Visual Asset Plan — PageIndex Website Experiment

*A handoff document: where visuals would strengthen this project, what each one should
show, and copy-paste-ready prompts for producing them — whether by an image-generation
agent (Tier 3), a code/diagram agent (Tiers 1–2), or by hand.*

**Surfaces served:** the GitHub README + repo docs, the lab notebook
(`reports/experimental-brief-lab-notebook.html`), and an eventual public write-up on
barbhs.com. One visual system spans all three; only the export format changes.

---

## 1. Style guide (derived, canonical for this project)

**Register call (veto if wrong):** This experiment is barbhs.com-surface work —
practitioner register, "cognitive scientist who builds things." It borrows the
Sensemaking parent *palette and warmth* but **not the swirl mark** (product branding
stays on product surfaces, per `brand-stack.md` routing). Happily, the palettes already
converge: barbhs.com's `#c34528` terracotta ≈ the brand kit's `#C04818` burnt orange.

### 1.1 Color tokens

| Token | Hex | Role |
|---|---|---|
| `ground` | `#F4F0E8` | Warm cream background. **Never pure white.** |
| `ink` | `#1C3A55` | Deep navy — linework, diagram strokes, labels. (From barbhs.com.) |
| `primary` | `#C04818` | Burnt orange — the warm lead. Emphasis, key nodes, "the answer." |
| `amber` | `#F0A818` | Spark accent — highlights, one emphasis element per image, warnings-with-warmth. |
| `cobalt` | `#186090` | Cool counterweight — secondary elements, links, "the machine's view." |
| `text` | `#2B2B2B` | Charcoal body text / captions. |
| `muted` | `#6B6B66` | Metadata, de-emphasized elements, "what got ignored." |
| `ground-dark` | `#0E0E12` | Dark-mode ground (dark variants only). |

**Rule:** one warm lead (orange/amber), one cool balance (cobalt/navy), generous cream
ground. In diagrams, use `primary` to mark *the thing the figure is about* and `cobalt`
for supporting structure — a consistent semantic: **warm = the point, cool = the system.**

A useful second semantic for this project: **warm = human/curated, cool = machine/generated**
(e.g., corpus vs. index, ground truth vs. model output). Pick one semantic per figure;
don't mix both in the same image.

### 1.2 Typography

- Headlines / figure titles: transitional serif (Fraunces or close match), 600 weight.
- Labels / annotations: humanist sans (Hanken Grotesk / Public Sans), 400–500.
- "Serif for ideas, sans for instructions."

### 1.3 Mood

Field notes from a working scientist. Hand-drawn-adjacent editorial illustration: confident
ink linework, flat warm color fills, visible texture, generous negative space. Sophisticated
warmth — think science-magazine explainer, not corporate clip-art, not edtech kitsch, never
childish. Wit is welcome (several of these figures are about failure stories); condescension
is not.

### 1.4 The reusable style preamble (paste at the top of every image-gen prompt)

```
STYLE: Editorial illustration in a warm scientific-field-notebook style. Confident
dark-navy ink linework (#1C3A55) with flat color fills on a warm cream ground (#F4F0E8,
never white). Palette: burnt orange (#C04818) as the single warm lead, golden amber
(#F0A818) as one small spark accent, cobalt blue (#186090) as the cool counterweight,
charcoal (#2B2B2B) details. Generous negative space; the composition breathes. Subtle
paper grain or stipple texture. Sophisticated, warm, a little witty — drawn by a
cognitive scientist who likes people.

RECURRING CHARACTER: a small honeybee naturalist — navy ink linework with amber-and-
charcoal striping, round spectacles, drawn as an earnest working field scientist. She
is capable and busy, never a mascot sticker: no giant eyes, no smiley face, no
anthropomorphic gloves. Think scientific-illustration bee granted one professional prop.

TEXT: the image includes ONLY the exact quoted strings specified in the scene, and no
other words, letters, or scribbles anywhere. Hand-lettered serif for title strings;
small-caps sans for labels; typewriter monospace for code/transcript strings. Every
string must be spelled exactly as given.

No photorealism, no 3D render, no corporate flat-design clip art, no childish cartoon,
no neon, no pure white background.
```

**On-image text rules** (the policy behind that TEXT paragraph):
- Specify every string **in quotes** in the scene prompt; end with "no other words."
  Models render short text faithfully but improvise when underspecified.
- Budget ≈3 strings per image, each ≤8 words (transcript strings may run longer —
  they're the ones worth a retry).
- Three type voices, semantically assigned: **serif = the idea** (titles), **sans
  small-caps = labels**, **monospace = what the machine actually said**. That last one
  is this project's signature move — real transcript lines rendered as evidence.
- Proofread every generation letter-by-letter; text is the highest-retry element.

### 1.5 Diagram (Mermaid/SVG) theme

For Mermaid figures, prepend this init block so code-drawn diagrams match the drawn ones:

```
%%{init: {"theme": "base", "themeVariables": {
  "background": "#F4F0E8", "primaryColor": "#F4F0E8",
  "primaryBorderColor": "#1C3A55", "primaryTextColor": "#2B2B2B",
  "lineColor": "#186090", "fontFamily": "Hanken Grotesk, sans-serif"
}}}%%
```

Highlight the figure's "point" nodes with `style <id> fill:#C04818,color:#F4F0E8`.

### 1.6 Format ladder (one source, three surfaces)

| Surface | Format |
|---|---|
| GitHub README / repo `.md` | Mermaid blocks (native render) or committed SVG in `reports/figures/` |
| Lab notebook HTML | Inline SVG (self-contained, no external requests) |
| barbhs.com write-up | PNG/WebP export at 2× (1600px+ wide); OG/hero at 1200×630 |

Suggested home for assets: `reports/figures/` (committed; they're publication artifacts,
not scratch).

---

## 2. The visual inventory

Three tiers by production method. Priority column says where the leverage is.

| ID | Figure | Tier | Priority |
|---|---|---|---|
| V1 | Corpus pipeline flow | 1 diagram | ★★★ |
| V2 | Two-repo provenance architecture | 1 diagram | ★★ |
| V3 | Experiment condition matrix (IDX × RET) | 1 diagram | ★★★ |
| V4 | Five-layer evaluation rubric stack | 1 diagram | ★★ |
| V5 | Retriever navigate-then-read tool loop | 1 diagram | ★★★ |
| V6 | Question-set anatomy (14 q × 5 categories) | 2 data | ★★ |
| V7 | The index tree itself, rendered | 2 data | ★★★ |
| V8 | IDX-D vs IDX-C node anatomy | 2 data | ★★ |
| V9 | Results heatmap (question × condition) | 2 data | later (needs scored runs) |
| V10 | Hero: the map vs. the navigator | 3 image-gen | ★★★ |
| V11 | The truncated map (Ollama gotcha) | 3 image-gen | ★★★ |
| V12 | The waggle dance (fabricated fetch) | 3 image-gen | ★★★ |
| V13 | Vectorless vs. vector retrieval | 3 image-gen | ★★ |
| V14 | The evidence auditor | 3 image-gen | ★ (optional) |

---

## 3. Tier 1 — Deterministic diagrams (Mermaid/SVG; a code agent or I can build these)

### V1 · Corpus pipeline flow
- **Placement:** README "How it works" (replaces the ASCII art); write-up intro.
- **Story:** website → frozen corpus → PageIndex → raw results → curated IDX-* variants —
  and that the corpus is *consumed, not produced* here.
- **Prompt (to a diagram agent):**
  > Build a left-to-right Mermaid flowchart with the project theme block (§1.5). Nodes:
  > "barbhs.com website source" → "corpus/site-book-v1.md (frozen snapshot, SHA-pinned)"
  > → "PageIndex tree generation" → "results/ (raw run output)" → "indexes/IDX-D / IDX-C /
  > IDX-O (curated variants)". Draw a dashed boundary box around the first node labeled
  > "website repo (authoritative producer)" and another around the rest labeled "this repo
  > (consumer)". Style the corpus node with the burnt-orange highlight — it is the frozen
  > contract between the two. Add a small annotation on the corpus edge: "provenance.json
  > pins commit + SHA256".

### V2 · Two-repo provenance architecture
- **Placement:** README "Corpus source & authority"; CLAUDE.md could link to it.
- **Story:** who owns what; the re-sync loop; why hand-editing the corpus is forbidden.
- **Prompt:**
  > Two-column Mermaid diagram, project theme. Left box: "dagny099.github.io —
  > experiments/pageindex/ (build scripts, QC, normalization)". Right box: "pageindex-
  > website-experiment (harness, indexes, evaluations, runs)". One arrow left→right
  > labeled "re-sync: copy verbatim → recompute SHA256 → update provenance.json".
  > A return dashed arrow labeled "corpus fixes go back to the pipeline — never edited
  > here". Under the right box, a warning note node in amber: "corpus change ⇒ existing
  > indexes stale (STALE.md)". Cool cobalt for structure; orange only on provenance.json.

### V3 · Experiment condition matrix
- **Placement:** README "Experimental design"; lab notebook conditions section.
- **Story:** two axes (3 index conditions × 3 retrievers), deliberately varied
  one-at-a-time, not full-factorial; which cells are run vs. planned.
- **Prompt:**
  > Draw a 3×3 grid as SVG (or a Mermaid quadrant-style table), project theme. Rows =
  > IDX-D (deterministic), IDX-C (cloud + summaries), IDX-O (local + summaries); columns =
  > RET-OAI, RET-ANT, RET-OLL. Shade completed cells cream-with-orange-border, planned
  > cells muted. Draw two accent paths: a vertical arrow down column RET-OAI labeled
  > "vary the map, hold the navigator" and a horizontal arrow across row IDX-D labeled
  > "vary the navigator, hold the map". Those two phrases are the experiment's thesis —
  > give them the serif treatment in the exported figure.

### V4 · Five-layer rubric stack
- **Placement:** lab notebook rubric section; write-up methods.
- **Story:** scoring separates failure layers — A preprocessing, B index quality,
  C retrieval quality, D answer quality, E operational behavior — so a wrong answer can
  be blamed on the right layer.
- **Prompt:**
  > Vertical stacked-layer SVG diagram, project theme: five horizontal slabs from bottom
  > (A · Preprocessing — "did the corpus preserve the content?") to top (E · Operational —
  > "cost, latency, reliability"). Left margin: one thin arrow rising through all layers
  > labeled "where did the failure enter?". Each slab: letter + name + one-line question,
  > navy ink on cream; slab C (retrieval) gets the orange highlight in figures about
  > retrieval, slab B in figures about indexes — parameterize the highlight. Caption
  > carries the detail; keep in-figure text to ≤8 words per slab.

### V5 · Retriever navigate-then-read tool loop
- **Placement:** README or findings report; essential for the write-up.
- **Story:** the agentic loop PageIndex retrieval depends on — and the two places weak
  models break it (skip the read; fake the call).
- **Prompt:**
  > Mermaid sequence diagram, project theme. Participants: "Retriever LLM", "PageIndex
  > tools", "Corpus". Flow: get_document() → line count/status; get_document_structure()
  > → tree of titles + line numbers (annotate: "titles only — no body text"); retriever
  > reasons over tree; get_page_content(pages=…) → body text; retriever answers WITH
  > page citations. Then two failure annotations in amber: ✗ at the third step, "shortcut:
  > answers from titles, never reads" and ✗ at the fourth, "fabrication: narrates a tool
  > call in prose instead of making it". Orange highlight on the get_page_content step —
  > the step that separates real retrieval from theater.

---

## 4. Tier 2 — Data-driven graphics (generated from this repo's JSON)

### V6 · Question-set anatomy
- **Source:** `evaluations/questions.csv` (frozen, 14 questions).
- **Placement:** lab notebook question-set section; write-up methods.
- **Story:** 5 categories with distinct jobs (locate / synthesize / check consistency /
  detect gaps / reflect), difficulty mix, and that 2 questions are pre-validated.
- **Prompt (to a code agent):**
  > From evaluations/questions.csv, generate an SVG figure: five labeled category columns
  > (direct-location ×4, cross-section-synthesis ×3, consistency ×2, evidence-gap ×3,
  > reflective-discovery ×2), one card per question showing id + difficulty as a small
  > chip (easy=cream/navy outline, medium=cobalt, hard=orange). Validated questions get
  > an amber corner mark. Under each column, a ≤6-word caption of what the category
  > probes: "find it" / "connect it" / "does it agree?" / "what's missing?" / "what does
  > it mean?". Project palette per reports/visual-asset-plan.md §1.

### V7 · The index tree itself, rendered ★ the signature figure
- **Source:** `indexes/IDX-D/index.json`.
- **Placement:** README hero-adjacent; lab notebook; write-up. This is the experiment's
  central artifact made visible — "the map of knowledge" literally.
- **Story:** one document, ~270 nodes, real hierarchy; recurring headings ("How It
  Works" ×6, "Summary" ×25) visible as a genuine navigation hazard.
- **Prompt (to a code agent):**
  > Load indexes/IDX-D/index.json and render the node tree as an icicle (preferred) or
  > radial tier diagram, SVG, project palette: depth-0 root in navy, major sections in
  > cobalt, leaves in muted gray. Then color every node whose title recurs elsewhere in
  > the tree (exact title match, e.g. "How It Works", "Summary", "Architecture") in
  > burnt orange — the figure's point is that identical titles pepper the map, so naive
  > title-matching is ambiguous by construction. Legend: "orange = this title appears
  > 2+ times". Height-scale nodes by line span. Export at 1600px wide.
- **Option:** render nodes as honeycomb hexagons to rhyme with the Tier-3 world. Try
  rectangles first — if the hexagons cost legibility at ~270 nodes, the rhyme isn't
  worth it.

### V8 · IDX-D vs IDX-C node anatomy
- **Source:** same node from `indexes/IDX-D/index.json` and `indexes/IDX-C/index.json`.
- **Placement:** lab notebook index-conditions section; write-up.
- **Story:** the conditions share one hierarchy; what changes is what a node *carries*
  (bare title+lines vs. added summary + doc description) — i.e., what the navigator can
  see before paying to read.
- **Prompt (to a code agent):**
  > Pick one mid-depth node present in both IDX-D and IDX-C (e.g. the Poolula "Evaluation
  > Harness" node). Draw two side-by-side "index card" SVGs, project palette: left card
  > (IDX-D) shows title / node_id / line_num fields only, with the summary slot drawn as
  > an empty dashed outline; right card (IDX-C) shows the same fields plus the actual
  > generated summary text (truncate ~40 words) in cobalt. One amber annotation between
  > them: "same map — different signage". Field labels in sans, values in mono.

### V9 · Results heatmap *(build once runs are scored)*
- **Source:** `runs/*/run.json` + rubric scores.
- **Placement:** write-up results; lab notebook run log.
- **Prompt (to a code agent):**
  > Matrix heatmap SVG: rows = 14 question ids grouped by category, columns = conditions
  > (IDX×RET cells actually run). Cell color = rubric layer-D answer score (cream→cobalt
  > scale); overlay a small orange dot where layer-C retrieval failed but layer-D looked
  > right — the "right answer, wrong evidence" cells the experiment exists to expose.
  > Project palette; category separators as thin navy rules.

---

## 5. Tier 3 — Image-generation prompts (the non-mathy ones)

Assembly: **paste the style preamble (§1.4), a blank line, then the scene prompt.**
Aspect ratios given per image.

**The world (shared across all five):** one recurring character — the honeybee
naturalist — in one visual universe. The corpus is a hand-drawn field map; the index is
honeycomb; content/answers are flowers; retrieval is her flight path; the waggle dance
is how findings get reported. The metaphor is earned in-corpus: the Beehive Analytics
Platform is one of the six portfolio projects and "Bees, Graphs & Governance" is one of
the indexed essays. Flowers are supporting cast (content), never a second character.

### V10 · Hero — the map and the navigator ★
- **Placement:** README top / OG image / write-up hero. 1200×630 (OG) and 1600×900.
- **Concept:** the experiment's thesis — *building a map of knowledge* and *reasoning
  over that map* are different jobs.
- **Scene prompt:**
  > A wide naturalist's desk viewed slightly from above. Spread across it, a large
  > hand-drawn hierarchical map — a tree of nested territories drawn like a vintage
  > cartographic survey in navy ink on cream, its margins decorated with small
  > honeycomb-hexagon legend cells, one small region glowing warm burnt orange. Above
  > the map hovers the honeybee naturalist, trailing a dotted cobalt flight line that
  > descends the tree's branches with two thoughtful zigzag detours before arriving at
  > the glowing region. A warm amber desk lamp lights the scene from the corner.
  > Composition: map dominates the left two-thirds; the bee and her flight line enter
  > from the right; generous cream margins. On-image text, exactly: title across the
  > top margin in hand-lettered serif: "THE MAP AND THE NAVIGATOR"; small-caps sans
  > label pinned to the map legend: "index"; small-caps sans label along the flight
  > line: "retrieval". No other words.
- **Caption:** *Two jobs, deliberately separated: building the map (indexing) and
  navigating it (retrieval).*

### V11 · The map that arrived (the Ollama context gotcha) ★
- **Placement:** findings report §"Gotcha #0"; write-up. 1600×900.
- **Concept:** the local model silently received half the index and navigated blind —
  no error, just a map that ends.
- **Scene prompt:**
  > The honeybee naturalist flies confidently over a paper landscape — a meadow drawn
  > as a hand-drawn map extending beneath her like terrain, navy trails and cobalt
  > landmarks on cream. Midway across the scene the map is torn cleanly off; beyond the
  > tear there is only blank cream paper, no lines at all. She consults a small copy of
  > the map and points ahead into the blankness, oblivious. In the missing half, one
  > flower rendered ghost-faint in burnt orange — the destination she cannot see. A
  > small amber flag planted exactly at the tear line is the only honest object in the
  > scene. Flat editorial style, big negative space above the horizon. On-image text,
  > exactly: on the amber flag in small-caps sans: "CONTEXT ENDS HERE"; faint charcoal
  > note floating in the blank region in typewriter monospace: "~5,000 tokens missing";
  > title along the bottom margin in hand-lettered serif: "THE MAP THAT ARRIVED".
  > No other words.
- **Caption:** *Ollama's default context window truncated the ~9K-token index mid-tree —
  no error raised. The retriever navigated the half that arrived.*

### V12 · The waggle dance (retrieval theater) ★
- **Placement:** findings report (the llama3.1 fabrication story); write-up. 1600×900.
- **Concept:** the model *narrated* a content fetch it never performed and reported
  findings from a source it never visited. In bee terms: dancing directions to a flower
  you never foraged. The on-image transcript strings are the model's real output.
- **Scene prompt:**
  > Interior of a hive drawn as a warm study: a wall of hexagonal honeycomb cells in
  > navy ink on cream, a few cells filled with amber honey. Center stage, the honeybee
  > naturalist performs an extravagant waggle dance on the comb — wings flared,
  > theatrical, eyes closed in confident recitation — while a semicircle of three
  > smaller bees takes earnest notes in tiny field notebooks. Her pollen baskets are
  > visibly, conspicuously EMPTY. Through the hive entrance behind her, far away and
  > untouched, the flower she claims to describe glows burnt orange with an unbroken
  > cobweb between its petals — never visited. Gentle wit, no cruelty; she believes
  > herself. On-image text, exactly: a speech ribbon above her in typewriter monospace:
  > "I will call get_page_content(pages=120-160)... Here's the output:"; a small
  > charcoal ledger tag at the base of the comb in typewriter monospace:
  > "content_tokens = 0"; title along the top margin in hand-lettered serif:
  > "THE WAGGLE DANCE". No other words.
- **Fallback:** if the long transcript string garbles after two retries, shorten the
  speech ribbon to exactly: "Here's the output: { ... }" — keep the ledger tag; it
  carries the punchline.
- **Caption:** *llama3.1:8b made one real structure call, then narrated a content fetch
  it never performed — reporting on a flower it never visited. The ledger doesn't lie:
  `content_tokens = 0`.*

### V13 · Vectorless vs. vector retrieval
- **Placement:** write-up background section (explaining PageIndex to newcomers). 1600×800, two-panel.
- **Concept:** navigating a table of contents vs. matching against shredded fragments.
  The bee appears only in the left panel — the navigate world is hers; the right panel
  is a machine with no navigator at all.
- **Scene prompt:**
  > A two-panel editorial diptych on one warm desk, divided by a thin navy rule. LEFT
  > PANEL: an intact book stands open to its table of contents, drawn as an elegant
  > indented tree in navy ink; the honeybee naturalist descends the entries along a
  > dotted cobalt flight line and dives into the page block at one spot marked burnt
  > orange — deliberate, sequential, legible. RIGHT PANEL: the same book has been passed
  > through a paper shredder that sits proudly on the desk; hundreds of small cream
  > paper strips float in a loose cloud, and a claw-machine-style magnet hovers above,
  > pulling toward it the handful of strips that happen to shimmer cobalt — nearby
  > strips of nearly identical shade drift ignored; one caught strip glows faintly
  > orange. No bee anywhere in the right panel. Neither panel is mocked; both are honest
  > machines. On-image text, exactly: left panel header in hand-lettered serif:
  > "NAVIGATE"; right panel header in hand-lettered serif: "MATCH"; small-caps sans
  > label under the left book: "table of contents"; small-caps sans label under the
  > strip cloud: "embedded chunks". No other words.
- **Caption:** *Two retrieval philosophies: navigate the document's own structure
  (PageIndex), or embed shredded chunks and fish by similarity (vector RAG).*

### V14 · The evidence audit *(optional)*
- **Placement:** write-up section on the consistency / evidence-gap question categories. 1200×1200.
- **Concept:** the question set doesn't just ask "find it" — it asks "do these two pages
  agree?" and "is this claim backed anywhere?"
- **Scene prompt:**
  > The honeybee naturalist as inspector, wearing a small inspector's sash and holding
  > a clipboard, walking along a wall of hexagonal honeycomb cells drawn in navy ink on
  > cream. Some cells are capped and full of amber honey; several are conspicuously
  > empty. Beside the comb, claim-notes on small paper scraps are pinned like a
  > detective's cork board, and burnt orange threads run from each note to a cell —
  > some threads end at full amber cells, others dangle at empty ones. She examines one
  > dangling thread through her spectacles, patient rather than accusatory. Amber desk-
  > lamp warmth, evening mood. On-image text, exactly: clipboard header in small-caps
  > sans: "EVIDENCE AUDIT"; label beside a full cell in small-caps sans: "supported";
  > label beside an empty cell in small-caps sans: "asserted". No other words.
- **Caption:** *Beyond lookup: consistency questions ask whether pages agree; evidence-gap
  questions ask which claims have honey behind them.*

---

## 6. Placement map (which figure goes where)

| Surface | Figures |
|---|---|
| **README** | V10 (hero), V1, V3, V7 |
| **Lab notebook HTML** | V3, V4, V6, V7, V8, V9 (when scored) |
| **Findings report** (`findings-retriever-prompt-revision.md`) | V5, V11, V12 |
| **barbhs.com write-up** | V10 hero, V13 (background), V5, V11, V12 (the story), V7 + V9 (the evidence), V14 (optional) |

## 7. Suggested production order

1. **V7** (index tree render) — signature figure, pure data, no taste risk.
2. **V1 + V3 + V5** (core diagrams) — biggest README/notebook payoff per effort.
3. **V10 → V12 → V11** (image-gen set) — V10 first: it calibrates the two risky
   elements (character design + text rendering) on the simplest composition. Lock the
   bee's look there, fold any preamble fixes back into §1.4, then batch the rest —
   reusing V10's accepted output as a style/character reference image if your agent
   supports it.
4. **V6, V8, V4, V2** — fill in.
5. **V9** — the moment scored runs exist.

## 8. Decisions made / ideas parked

- **Character: DECIDED (2026-07-10) — the honeybee naturalist.** One character, one
  world (map = corpus, comb = index, flowers = content, flight = retrieval, waggle
  dance = reporting). Earned in-corpus via the Beehive Analytics project and "Bees,
  Graphs & Governance." Guardrail: she is a field scientist, not a mascot sticker —
  if a generation drifts cute (giant eyes, waving gloves), reject on style.
- **On-image text: DECIDED — allowed and semantic.** Serif = idea, sans small-caps =
  label, monospace = machine transcript. Every string specified exactly; "no other
  words" closes every prompt. Real transcript lines as in-image evidence is the
  signature move.
- **Dark-mode variants:** the lab notebook and barbhs.com may want `ground-dark`
  (`#0E0E12`) versions. Cheap for Tier 1/2 (swap tokens); a re-roll for Tier 3.
- **Figure numbering:** if the write-up is real, adopt `Fig. N` numbering + a
  `reports/figures/captions.md` so captions stay in one place.
- **Style preamble is v1:** expect one calibration round on your image agent (V10);
  the *negative* clauses (no white ground, no clip-art, no mascot-cute) and exact
  text strings are the parts most models need repeated.

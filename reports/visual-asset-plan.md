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
cognitive scientist who likes people. No photorealism, no 3D render, no corporate
flat-design clip art, no childish cartoon, no neon, no pure white background.
Contains NO text, NO words, NO letters, NO labels — all labeling happens in the caption.
```

(The no-text instruction matters: image models garble text, and your captions will do
that job better anyway. For diagrams that *need* labels, use Tier 1/2 — code, not pixels.)

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
| V12 | The librarian who never opens the book | 3 image-gen | ★★★ |
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
Aspect ratios given per image. All are text-free by design — pair each with the caption
provided.

### V10 · Hero — the map and the navigator ★
- **Placement:** README top / OG image / write-up hero. 1200×630 (OG) and 1600×900.
- **Concept:** the experiment's thesis — *building a map of knowledge* and *reasoning
  over that map* are different jobs.
- **Scene prompt:**
  > A wide desk scene viewed slightly from above. On the left, a large hand-drawn
  > hierarchical map spread across the desk — a tree of nested territories drawn like a
  > vintage cartographic survey in navy ink on cream, with one small region glowing warm
  > burnt orange. On the right, a small owl wearing round spectacles peers at the map
  > through a magnifying lens, one wing tracing a dotted cobalt route that descends the
  > tree's branches toward the glowing region. The route makes two thoughtful zigzag
  > detours before arriving. A warm amber desk lamp lights the scene from the corner.
  > Composition: map dominates left two-thirds; navigator and lens on the right third;
  > generous cream margins.
- **Caption:** *Two jobs, deliberately separated: building the map (indexing) and
  navigating it (retrieval).*
- **Note:** if the owl reads too whimsical for the README, swap "a small owl wearing
  round spectacles" for "a pair of human hands holding a brass magnifying lens" — same
  composition otherwise.

### V11 · The truncated map (the Ollama context gotcha) ★
- **Placement:** findings report §"Gotcha #0"; write-up. 1600×900.
- **Concept:** the local model silently received half the index and navigated blind —
  no error, just a map that ends.
- **Scene prompt:**
  > A lone hiker with a walking stick stands mid-stride on a hand-drawn trail map that
  > extends under their feet like a paper landscape, navy ink paths on cream. Ahead of
  > them, the map is torn cleanly off — beyond the tear is only blank cream paper, no
  > lines at all. The hiker, oblivious, consults a small map copy and points confidently
  > into the blankness. Behind them, the intact half of the map is dense with lovely
  > branching trails and small landmarks in cobalt, with one destination marked in burnt
  > orange — located in the torn-off missing half, faintly visible like a ghost. A tiny
  > amber warning flag planted exactly at the tear line is the only honest object in the
  > scene. Flat editorial style, big negative space above the horizon.
- **Caption:** *Ollama's default context window truncated the ~9K-token index mid-tree —
  no error raised. The retriever navigated the half that arrived.*

### V12 · The librarian who never opens the book ★
- **Placement:** findings report (the llama3.1 fabrication story); write-up. 1600×900.
- **Concept:** the model answered from section titles and *narrated* a content fetch it
  never performed — retrieval theater.
- **Scene prompt:**
  > Interior of a small warm library, cream walls, navy-ink shelving. A theatrical cat
  > librarian in a bow tie stands on a stool before a wall of books, gesturing grandly
  > with one paw pressed to its chest, eyes closed in confident recitation, mouth open
  > mid-proclamation. Every book on the shelf is firmly CLOSED; their spines are
  > beautifully decorated in cobalt and navy. One book — the relevant one — has a burnt
  > orange spine and sits within easy reach, with a fine layer of dust and a tiny cobweb
  > connecting it to the shelf, clearly never touched. On the floor, a single amber
  > reading lamp beside an empty, unused reading chair. Flat editorial illustration,
  > gentle wit, no cruelty — the cat believes itself.
- **Caption:** *llama3.1:8b made one real structure call, then narrated a content fetch
  it never performed — answering from spines, not pages.*

### V13 · Vectorless vs. vector retrieval
- **Placement:** write-up background section (explaining PageIndex to newcomers). 1600×800, two-panel.
- **Concept:** navigating a table of contents vs. matching against shredded fragments.
- **Scene prompt:**
  > A two-panel editorial diptych, same warm library-desk world in both panels, divided
  > by a thin navy rule. LEFT PANEL: an intact book stands open to its table of contents,
  > drawn as an elegant indented tree in navy ink; a dotted cobalt path descends the
  > entries and dives into the page block at one spot marked burnt orange — deliberate,
  > sequential, legible. RIGHT PANEL: the same book has been passed through a paper
  > shredder that sits proudly on the desk; hundreds of small cream paper strips float
  > in a loose cloud, and a claw-machine-style magnet hovers above, pulling toward it
  > the handful of strips that happen to shimmer cobalt — nearby strips of nearly
  > identical shade drift ignored. One strip caught by the magnet glows faintly orange.
  > Neither panel is mocked; both are honest machines. Flat editorial style.
- **Caption:** *Two retrieval philosophies: navigate the document's own structure
  (PageIndex), or embed shredded chunks and fish by similarity (vector RAG).*

### V14 · The evidence auditor *(optional)*
- **Placement:** write-up section on the consistency / evidence-gap question categories. 1200×1200.
- **Concept:** the question set doesn't just ask "find it" — it asks "do these two pages
  agree?" and "is this claim backed anywhere?"
- **Scene prompt:**
  > A meticulous badger in a cardigan sits at a cream desk with two open documents, one
  > under each paw, drawn in navy ink. Red thread — rendered burnt orange — connects a
  > passage in the left document to a contradicting passage in the right, pinned like a
  > detective's cork board. Around the desk, a few more orange threads run from claims
  > on the pages to small empty picture frames on the wall labeled by their emptiness —
  > where the supporting evidence should hang, there is nothing. One frame does hold a
  > small cobalt certificate. Amber desk lamp, evening warmth, patient rather than
  > accusatory mood.
- **Caption:** *Beyond lookup: consistency questions ask whether pages agree; evidence-gap
  questions ask which claims have nothing behind them.*

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
3. **V10 → V11 → V12** (image-gen set) — generate V10 first to calibrate the style
   preamble against your image agent; iterate the preamble once, then batch the rest.
4. **V6, V8, V4, V2** — fill in.
5. **V9** — the moment scored runs exist.

## 8. Open questions / ideas parked for Barbara

- **Mascot consistency:** V10 (owl), V12 (cat), V14 (badger) each carry their own animal.
  Charming as a menagerie, stronger as a recurring single character ("the navigator")
  if these ever live in one article. Decide before batch-generating.
- **Dark-mode variants:** the lab notebook and barbhs.com may want `ground-dark`
  (`#0E0E12`) versions. Cheap for Tier 1/2 (swap tokens); a re-roll for Tier 3.
- **Figure numbering:** if the write-up is real, adopt `Fig. N` numbering + a
  `reports/figures/captions.md` so captions stay in one place.
- **Style preamble is v1:** expect one calibration round on your image agent; the
  preamble's *negative* clauses (no white ground, no corporate clip-art, no text) are
  the part most models need repeated.

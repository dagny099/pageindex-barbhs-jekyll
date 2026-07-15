# Candidate Questions — paper-book-v1 (representation comparison)

Draft evaluation questions for the PDF-vs-Markdown representation study on
Ehinger, Hidalgo-Sotelo, Torralba & Oliva (2009). **16 candidates** in
[`candidate_questions.csv`](candidate_questions.csv), schema-compatible with
`questions.csv` plus two Prompt-D columns: `representation_sensitivity`
(none/low/high) and `confidence` (high/medium). Line numbers cite
`corpus/paper-book-v1/paper-book-v1.md`; every candidate was verified against
that file.

**These are candidates for Barbara to cut to 6–8 — over-produced on purpose.**
`ground_truth` is a DRAFT. As the paper's co-author, Barbara is the oracle; the
items below flagged *medium* confidence are where I am least certain and where a
fabricated ground truth would do the most damage.

## Field semantics

- `expected_evidence` = WHERE a correct answer must draw from (grades retrieval).
- `ground_truth` = WHAT it must contain (grades the answer); a DRAFT here.
- `representation_sensitivity` = whether the item is expected to expose PDF-vs-Markdown
  extraction differences (see the gate report, `reports/qc-paper-tree-gate.md`).
- `confidence` = my confidence the DRAFT ground truth is correct as written.

## Coverage (16 candidates)

| Category | Count | IDs |
|---|---|---|
| direct-location | 2 | PDL1, PDL2 |
| methods-procedural | 2 | PMP1, PMP2 |
| figure-or-table-evidence | 3 | PFT1, PFT2, PFT3 |
| consistency | 2 | PCN1, PCN2 |
| **evidence-gap** | **4** | PEG1, PEG2, PEG3, PEG4 |
| cross-section-synthesis | 2 | PCS1, PCS2 |
| reflective-discovery | 1 | PRD1 |

Evidence-gap is weighted up (4) — it was the most discriminating category in V1.

## Representation-sensitive items (6, all tagged `high`)

These are designed to expose where the three arms diverge — grounded in the
Prompt C gate's findings (vanilla PDF arm: 39 `pB.001` stat corruptions, no
table node, no figure nodes, page-level addressing):

- **PMP1** — the `32×64` window prints as `3264` in the raw PDF extraction (missing `×`).
- **PFT1** — reads specific **Table 1** cells; the vanilla arm has no table node (values spill as raw lines).
- **PFT2** — Greek-symbol **equation** weights (γ→`g` in raw extraction).
- **PFT3** — **figure caption** content; the vanilla arm has zero figure nodes.
- **PCN2** — reconciles a **Table 1 cell with prose**; only faithfully answerable where the table survives.
- **PEG4** — retrieval over **all 12 figure captions**; the "colour online only" note.

Prediction (to be tested, not assumed): the Markdown arms should answer these
correctly; the vanilla arm should degrade on PMP1/PFT1/PFT2/PCN2 because the
underlying text/table is corrupted — which is the study's whole point.

## Ground truths ranked by verification need (highest-risk first)

1. **PEG1** (medium) — *weights-vs-importance tension.* My draft says the paper
   reconciles the small γ3 (scene-context weight) with context's dominance via
   **ablation** (removing context causes the largest drop, t(405)=17.381), not via
   the weights. This is an interpretive reading — confirm it's the intended one, and
   that I haven't overstated "the paper reconciles this."
2. **PFT2** (medium) — *γ→source mapping.* The numbers (0.1, 0.85, 0.05) are
   verbatim, but "**target features** gets the largest weight (0.85)" is
   counterintuitive vs the paper's headline. The mapping rests on Equation 1's
   ordering (MS^γ1 · MT^γ2 · MC^γ3). Please confirm γ2 pairs with target features.
3. **PEG4** (medium) — *11-of-12 count.* I derived that 11 captions carry the
   "colour online only" note (all but Figure 2); `grep` finds 11. Confirm Figure 2
   is the sole exception.
4. **PCS2** (medium) — *"model matches the oracle."* Rests on the non-significant
   target-absent difference (t(405)=−1.233, p=.218). Confirm "matches" is a fair
   reading in context (p=.019 target-present is arguably significant at .05).

The other 12 (PDL1/2, PMP1/2, PFT1/3, PCN1, PEG2/3, PCS1, PRD1) are `high`
confidence — directly quoted or read from Table 1 with no interpretation.

## Notes / caveats

- Two candidates deliberately span a **false premise** the correct answer must
  refute (PEG2 "…or only AUCs?", PEG3 "…or defer it?") — these reward honesty over
  fluent hallucination.
- `expected_evidence` prefers evidence locatable in **both** representations where
  possible; the representation-sensitive items intentionally pick evidence that
  survives cleanly in Markdown but not in the vanilla PDF extraction.
- The harness only loads from `questions.csv`; this candidate file is not wired in.
  After Barbara selects the winners, promote them into a questions CSV
  (set `status=validated`) before the paper retrieval runs.

## Promoted winners (2026-07-14)

Barbara selected **8** of the 16. They are promoted verbatim (full 11-column schema,
`status=validated`) into **`evaluations/questions-paper-book-v1.csv`** — a paper-specific
file kept separate from the site-book `questions.csv`. The harness now loads it via
`run_retrieval.py --questions-file evaluations/questions-paper-book-v1.csv`.

| ID | Category | representation_sensitivity |
|---|---|---|
| PDL1 | direct-location | low |
| PMP1 | methods-procedural | **high** |
| PFT1 | figure-or-table-evidence | **high** |
| PFT3 | figure-or-table-evidence | **high** |
| PEG2 | evidence-gap | low |
| PCS1 | cross-section-synthesis | low |
| PCS2 | cross-section-synthesis | low |
| PRD1 | reflective-discovery | low |

Three high-sensitivity items (PMP1, PFT1, PFT3) drive the vanilla-vs-Markdown contrast;
the rest are low-sensitivity controls. `PCS2` is the only `confidence=medium` ground
truth in the set — confirm the "computational model matches the oracle" reading before
scoring.

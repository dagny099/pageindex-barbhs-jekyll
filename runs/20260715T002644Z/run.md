# Retrieval run 20260715T002644Z

- Indexes: `IDX-PDF-vanilla-paper`
- Retrievers: `gpt-4o-2024-11-20`
- Corpus: `unknown` (`unknown…`)
- Repo commit: `1cffdcafd2`  ·  questions: 1

## Comparison — means across questions

| Index | Retriever | n | tools | struct_tok | content_tok | total_tok | $ | s |
|---|---|---|---|---|---|---|---|---|
| `IDX-PDF-vanilla-paper` | `gpt-4o-2024-11-20` | 1 | 4.0 | 4515.0 | 1120.0 | 12725 | 0.033 | 13.0 |

## Per-question detail (question, expected evidence, ground truth, answer)
*Everything needed to score each answer is inline below — no cross-referencing.*

### [IDX-PDF-vanilla-paper | gpt-4o-2024-11-20] PDL1 — direct-location

**Q:** How many observers and how many scenes were used in the main eye-tracking search experiment, and what was the search target?

**Expected evidence:** Abstract L46; Introduction L77; Participants L83 ('Fourteen observers'); Stimuli L93 ('912 colour pictures').

**Ground truth:** 14 observers searched 912 outdoor urban scenes (half target-present, half target-absent) for a person/pedestrian.

metrics: tools=4 · struct_tok=4515 · content_tok=1120 · total_tok=12725 · $0.033 · 13.02s
fetched line ranges: `0007`, `0005`

**Answer:**

The main eye-tracking search experiment involved **14 observers** searching through **912 urban scenes**. Half of these scenes (456) contained the search target—a **person (pedestrian)**—while the other half were target-absent. The targets in the target-present images were generally positioned in the periphery of the scenes. 

Sources:
- "Participants" section.
- "Stimuli" section.

---

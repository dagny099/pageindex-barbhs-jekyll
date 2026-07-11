# Retrieval run 20260711T201610Z

- Indexes: `IDX-D`
- Retrievers: `ollama_chat/qwen2.5-7b-instruct-ctx32k`
- Corpus: `site-book-v1` (`7379cad3da7b…`)
- Repo commit: `12bab4185c`  ·  questions: 1

## Comparison — means across questions

| Index | Retriever | n | tools | struct_tok | content_tok | total_tok | $ | s |
|---|---|---|---|---|---|---|---|---|
| `IDX-D` | `ollama_chat/qwen2.5-7b-instruct-ctx32k` | 1 | 3.0 | 8934.0 | 250.0 | 23772 | 0 | 141.2 |

## Per-question detail (question, expected evidence, ground truth, answer)
*Everything needed to score each answer is inline below — no cross-referencing.*

### [IDX-D | ollama_chat/qwen2.5-7b-instruct-ctx32k] DL4 — direct-location

**Q:** According to the Poolula platform page, what five dimensions does its evaluation harness score, and what composite target must be met before production deployment?

**Expected evidence:** Poolula Platform § Governance & Reliability → Evaluation Harness (node 0068, L681–700; dimensions table L690–699, target L700).

**Ground truth:** Tool Usage, Content Relevance, Semantic Similarity, Numerical Accuracy, Citation Accuracy; target ≥90% composite score before production deployment.

metrics: tools=3 · struct_tok=8934 · content_tok=250 · total_tok=23772 · $0.0 · 141.22s
fetched line ranges: `681-702`

**Answer:**

Based on the content fetched from the document:

### Evaluation Harness

The Poolula platform includes a rigorous testing system with a golden question set. This system uses five scoring dimensions to evaluate AI responses before they can be deployed in production.

#### Scoring Dimensions:
1. **Tool Usage**: Did the AI invoke the correct tools?
2. **Content Relevance**: Does the answer address the actual question?
3. **Semantic Similarity**: Does the answer match expected content (embedding comparison)?
4. **Numerical Accuracy**: Do financial figures match expected values?
5. **Citation Accuracy**: Are sources correct and relevant?

The target for these dimensions before production deployment is a composite score of at least 90%.

### Summary
- **Five Scoring Dimensions**:
  - Tool Usage
  - Content Relevance
  - Semantic Similarity
  - Numerical Accuracy
  - Citation Accuracy

- **Composite Target**: ≥90% before production deployment.

This information is directly derived from the document's content.

---

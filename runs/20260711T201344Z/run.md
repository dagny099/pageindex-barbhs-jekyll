# Retrieval run 20260711T201344Z

- Indexes: `IDX-D`
- Retrievers: `anthropic/claude-sonnet-4-5`
- Corpus: `site-book-v1` (`7379cad3da7b…`)
- Repo commit: `12bab4185c`  ·  questions: 2

## Comparison — means across questions

| Index | Retriever | n | tools | struct_tok | content_tok | total_tok | $ | s |
|---|---|---|---|---|---|---|---|---|
| `IDX-D` | `anthropic/claude-sonnet-4-5` | 0 | — | — | — | — | — | — |

## Per-question detail (question, expected evidence, ground truth, answer)
*Everything needed to score each answer is inline below — no cross-referencing.*

### [IDX-D | anthropic/claude-sonnet-4-5] DL3 — direct-location

**Q:** Which project is a self-hosted ML pipeline for workout/fitness data, and what stack does it describe?

**Expected evidence:** Project: Self-Hosted Workout Intelligence (fitness-dashboard). Stack: Python, Streamlit, MySQL, scikit-learn, Plotly, AWS Lambda/RDS, K-means.

**Ground truth:** Self-Hosted Workout Intelligence; full-stack ETL + K-means classification + Streamlit dashboard.

**ERROR:** BadRequestError: litellm.BadRequestError: AnthropicException - {"type":"error","error":{"type":"invalid_request_error","message":"Your credit balance is too low to access the Anthropic API. Please go to Plans & Billing to upgrade or purchase credits."},"request_id":"req_011Ccvt7HjLqiW1fxUtbd9Fv"}

---

### [IDX-D | anthropic/claude-sonnet-4-5] DL4 — direct-location

**Q:** According to the Poolula platform page, what five dimensions does its evaluation harness score, and what composite target must be met before production deployment?

**Expected evidence:** Poolula Platform § Governance & Reliability → Evaluation Harness (node 0068, L681–700; dimensions table L690–699, target L700).

**Ground truth:** Tool Usage, Content Relevance, Semantic Similarity, Numerical Accuracy, Citation Accuracy; target ≥90% composite score before production deployment.

**ERROR:** BadRequestError: litellm.BadRequestError: AnthropicException - {"type":"error","error":{"type":"invalid_request_error","message":"Your credit balance is too low to access the Anthropic API. Please go to Plans & Billing to upgrade or purchase credits."},"request_id":"req_011Ccvt7L8TLVcsRk8U27x9o"}

---

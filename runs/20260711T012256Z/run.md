# Retrieval run 20260711T012256Z

- Indexes: `IDX-D`
- Retrievers: `gpt-4o-2024-11-20`
- Corpus: `site-book-v1` (`7379cad3da7b…`)
- Repo commit: `42e950f745`  ·  questions: 2

## Comparison — means across questions

| Index | Retriever | n | tools | struct_tok | content_tok | total_tok | $ | s |
|---|---|---|---|---|---|---|---|---|
| `IDX-D` | `gpt-4o-2024-11-20` | 2 | 3.0 | 8934.0 | 2410.0 | 22122 | 0.1135 | 11.6 |

## Per-question detail (question, expected evidence, ground truth, answer)
*Everything needed to score each answer is inline below — no cross-referencing.*

### [IDX-D | gpt-4o-2024-11-20] DL3 — direct-location

**Q:** Which project is a self-hosted ML pipeline for workout/fitness data, and what stack does it describe?

**Expected evidence:** Project: Self-Hosted Workout Intelligence (fitness-dashboard). Stack: Python, Streamlit, MySQL, scikit-learn, Plotly, AWS Lambda/RDS, K-means.

**Ground truth:** Self-Hosted Workout Intelligence; full-stack ETL + K-means classification + Streamlit dashboard.

metrics: tools=3 · struct_tok=8934 · content_tok=4632 · total_tok=24355 · $0.0625 · 16.96s
fetched line ranges: `801-1211`

**Answer:**

The self-hosted project for fitness and workout data is called **Self-Hosted Workout Intelligence**. It is a full-stack fitness analytics platform that ingests, classifies, and visualizes workout data. The ML pipeline leverages **AWS-cloud ETL, K-means clustering for ML classification, and a multi-page Streamlit dashboard** for analytics and visualization. 

### Technology Stack:
- **Languages/Frameworks**: Python, Streamlit
- **Machine Learning**: scikit-learn
- **Data Storage**: MySQL (AWS RDS)
- **ETL and Cloud Services**: AWS Lambda, S3, SNS
- **Visualization**: Plotly

For more information, refer to ["Self-Hosted Workout Intelligence"](https://workouts.barbhs.com/). (Section: **Self-Hosted Workout Intelligence**)

---

### [IDX-D | gpt-4o-2024-11-20] DL4 — direct-location

**Q:** According to the Poolula platform page, what five dimensions does its evaluation harness score, and what composite target must be met before production deployment?

**Expected evidence:** Poolula Platform § Governance & Reliability → Evaluation Harness (node 0068, L681–700; dimensions table L690–699, target L700).

**Ground truth:** Tool Usage, Content Relevance, Semantic Similarity, Numerical Accuracy, Citation Accuracy; target ≥90% composite score before production deployment.

metrics: tools=3 · struct_tok=8934 · content_tok=188 · total_tok=19889 · $0.051 · 6.28s
fetched line ranges: `681-701`

**Answer:**

The Poolula platform's evaluation harness measures performance across five dimensions:

1. **Tool Usage** - Correctness in invoking the appropriate tools.
2. **Content Relevance** - Whether the answer addresses the actual question.
3. **Semantic Similarity** - Match between the answer and expected content via embedding comparison.
4. **Numerical Accuracy** - Accuracy of financial figures compared to expected values.
5. **Citation Accuracy** - Relevance and correctness of sources.

The platform requires achieving a composite score of at least **90%** across these dimensions before production deployment.  
(*Source: Evaluation Harness section of the Poolula Platform page*)

---

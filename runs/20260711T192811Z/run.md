# Retrieval run 20260711T192811Z

- Indexes: `IDX-D`
- Retrievers: `anthropic/claude-sonnet-4-5`
- Corpus: `site-book-v1` (`7379cad3da7b…`)
- Repo commit: `12bab4185c`  ·  questions: 2

## Comparison — means across questions

| Index | Retriever | n | tools | struct_tok | content_tok | total_tok | $ | s |
|---|---|---|---|---|---|---|---|---|
| `IDX-D` | `anthropic/claude-sonnet-4-5` | 2 | 3.0 | 8934.0 | 2410.0 | 27240 | 0.1737 | 17.7 |

## Per-question detail (question, expected evidence, ground truth, answer)
*Everything needed to score each answer is inline below — no cross-referencing.*

### [IDX-D | anthropic/claude-sonnet-4-5] DL3 — direct-location

**Q:** Which project is a self-hosted ML pipeline for workout/fitness data, and what stack does it describe?

**Expected evidence:** Project: Self-Hosted Workout Intelligence (fitness-dashboard). Stack: Python, Streamlit, MySQL, scikit-learn, Plotly, AWS Lambda/RDS, K-means.

**Ground truth:** Self-Hosted Workout Intelligence; full-stack ETL + K-means classification + Streamlit dashboard.

metrics: tools=3 · struct_tok=8934 · content_tok=4632 · total_tok=29369 · $0.094 · 15.04s
fetched line ranges: `801-1219`

**Answer:**

Perfect! I found the information. The project is **"Self-Hosted Workout Intelligence"** (also referred to as the Fitness Dashboard ML Pipeline).

## Answer

The project is **"Self-Hosted Workout Intelligence"** (Fitness Dashboard ML Pipeline).

### Stack Description:

**Technologies:** Python, Streamlit, MySQL, scikit-learn, Plotly, AWS Lambda, AWS RDS

The full stack breakdown by layer:

| Layer | Components | Technology |
|-------|------------|------------|
| **Data Ingestion** | ETL pipeline, validation | AWS Lambda, S3, SNS |
| **Storage** | Workout database | AWS RDS (MySQL) |
| **Intelligence** | Classification, analytics | scikit-learn, scipy |
| **Visualization** | Interactive charts | Plotly, Streamlit |
| **UI** | Multi-page dashboard | Streamlit 1.44+ |
| **Infrastructure** | Deployment, config | Docker, systemd, TOML |

This is a full-stack fitness analytics platform that transforms 14 years of workout data into actionable intelligence. The AWS-based ETL pipeline ingests MapMyRun exports, ML models (K-means clustering) automatically classify workouts as runs vs. dog walks, and a multi-page Streamlit dashboard surfaces trends, anomalies, and personalized insights—all self-hosted for complete data ownership.

---

### [IDX-D | anthropic/claude-sonnet-4-5] DL4 — direct-location

**Q:** According to the Poolula platform page, what five dimensions does its evaluation harness score, and what composite target must be met before production deployment?

**Expected evidence:** Poolula Platform § Governance & Reliability → Evaluation Harness (node 0068, L681–700; dimensions table L690–699, target L700).

**Ground truth:** Tool Usage, Content Relevance, Semantic Similarity, Numerical Accuracy, Citation Accuracy; target ≥90% composite score before production deployment.

metrics: tools=3 · struct_tok=8934 · content_tok=188 · total_tok=25112 · $0.0797 · 20.45s
fetched line ranges: `681-701`

**Answer:**

Perfect! I found the information. According to the Poolula Platform page, specifically in the "Evaluation Harness" section:

## Five Scoring Dimensions:

1. **Tool Usage** - Did the AI invoke the correct tools?
2. **Content Relevance** - Does the answer address the actual question?
3. **Semantic Similarity** - Does the answer match expected content (embedding comparison)?
4. **Numerical Accuracy** - Do financial figures match expected values?
5. **Citation Accuracy** - Are sources correct and relevant?

## Composite Target:

**≥90% composite score** must be met before production deployment.

The platform uses a rigorous testing system with a golden question set, and the evaluation harness outputs detailed reports to track performance across these five dimensions.

---

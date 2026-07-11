# Retrieval run 20260711T192855Z

- Indexes: `IDX-D`
- Retrievers: `anthropic/claude-sonnet-4-5`
- Corpus: `site-book-v1` (`7379cad3da7b…`)
- Repo commit: `12bab4185c`  ·  questions: 2

## Comparison — means across questions

| Index | Retriever | n | tools | struct_tok | content_tok | total_tok | $ | s |
|---|---|---|---|---|---|---|---|---|
| `IDX-D` | `anthropic/claude-sonnet-4-5` | 2 | 3.0 | 8934.0 | 2410.0 | 27242 | 0.1738 | 11.7 |

## Per-question detail (question, expected evidence, ground truth, answer)
*Everything needed to score each answer is inline below — no cross-referencing.*

### [IDX-D | anthropic/claude-sonnet-4-5] DL3 — direct-location

**Q:** Which project is a self-hosted ML pipeline for workout/fitness data, and what stack does it describe?

**Expected evidence:** Project: Self-Hosted Workout Intelligence (fitness-dashboard). Stack: Python, Streamlit, MySQL, scikit-learn, Plotly, AWS Lambda/RDS, K-means.

**Ground truth:** Self-Hosted Workout Intelligence; full-stack ETL + K-means classification + Streamlit dashboard.

metrics: tools=3 · struct_tok=8934 · content_tok=4632 · total_tok=29372 · $0.0941 · 14.58s
fetched line ranges: `801-1219`

**Answer:**

Perfect! I found the information. The project is **"Self-Hosted Workout Intelligence"** (also referred to as the Fitness Dashboard ML Pipeline).

## Answer

The project is **Self-Hosted Workout Intelligence** (Fitness Dashboard ML Pipeline), and it describes the following stack:

**Technologies:** 
- **Python** - Core language
- **Streamlit** - Multi-page dashboard UI
- **MySQL** - Database (AWS RDS in production, local MySQL in dev)
- **scikit-learn** - ML classification (K-means clustering)
- **Plotly** - Interactive visualizations
- **AWS Lambda** - ETL processing
- **AWS RDS** - Cloud database storage
- **AWS S3** - File storage and upload triggers
- **AWS SNS** - Notifications

**Architecture Layers:**
- **Data Ingestion:** AWS Lambda, S3, SNS for ETL pipeline
- **Storage:** AWS RDS (MySQL)
- **Intelligence:** scikit-learn, scipy for ML classification and analytics
- **Visualization:** Plotly, Streamlit
- **Infrastructure:** Docker, systemd, TOML for deployment

The project is a full-stack fitness analytics platform that transforms 14 years of workout data into actionable intelligence, featuring ML-powered workout classification (distinguishing runs from dog walks), cloud ETL pipeline, and interactive dashboards—all self-hosted for complete data ownership.

---

### [IDX-D | anthropic/claude-sonnet-4-5] DL4 — direct-location

**Q:** According to the Poolula platform page, what five dimensions does its evaluation harness score, and what composite target must be met before production deployment?

**Expected evidence:** Poolula Platform § Governance & Reliability → Evaluation Harness (node 0068, L681–700; dimensions table L690–699, target L700).

**Ground truth:** Tool Usage, Content Relevance, Semantic Similarity, Numerical Accuracy, Citation Accuracy; target ≥90% composite score before production deployment.

metrics: tools=3 · struct_tok=8934 · content_tok=188 · total_tok=25112 · $0.0797 · 8.9s
fetched line ranges: `681-701`

**Answer:**

Perfect! I found the information. According to the Poolula platform page, specifically in the "Evaluation Harness" section:

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

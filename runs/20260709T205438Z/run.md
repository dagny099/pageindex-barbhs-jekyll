# Retrieval run 20260709T205438Z

- Index: **IDX-D** (site-book-v1, corpus `7379cad3da7b…`)
- Retrievers: `gpt-4o-mini`, `anthropic/claude-sonnet-4-5`
- Repo commit: `069424db59`

## Comparison (means across questions)

| Retriever | n | tools | struct_tok | content_tok | total_tok | $ | s |
|---|---|---|---|---|---|---|---|
| `gpt-4o-mini` | 1 | 3.0 | 8934.0 | 739.0 | 20037 | 0.0031 | 10.0 |
| `anthropic/claude-sonnet-4-5` | 1 | 3.0 | 8934.0 | 4795.0 | 29234 | 0.093 | 14.6 |

## [gpt-4o-mini] DL3 — direct-location

**Q:** Which project is a self-hosted ML pipeline for workout/fitness data, and what stack does it describe?

tools=3 · struct_tok=8934 · content_tok=739 · total_tok=20037 · $0.0031 · 10.01s

- `get_document()` → 45 tok
- `get_document_structure()` → 8934 tok
- `get_page_content(801-830)` → 739 tok

**Answer:**

The project you're looking for is titled **"Self-Hosted Workout Intelligence."** It describes a full-stack ML pipeline for analyzing workout and fitness data, transforming 14 years of data into actionable insights. 

### Technology Stack:
- **Python**
- **Streamlit**
- **MySQL**
- **scikit-learn**
- **Plotly**
- **AWS Lambda**
- **AWS RDS** 

This project features a cloud ETL pipeline, ML classification for distinguishing runs from walks, and an interactive dashboard for analytics (Source: *Self-Hosted Workout Intelligence* section).

---

## [anthropic/claude-sonnet-4-5] DL3 — direct-location

**Q:** Which project is a self-hosted ML pipeline for workout/fitness data, and what stack does it describe?

tools=3 · struct_tok=8934 · content_tok=4795 · total_tok=29234 · $0.093 · 14.63s

- `get_document()` → 45 tok
- `get_document_structure()` → 8934 tok
- `get_page_content(801-1220)` → 4795 tok

**Answer:**

Perfect! I found the information. The project is **"Self-Hosted Workout Intelligence"** (also referred to as the Fitness Dashboard ML Pipeline).

Based on the "Self-Hosted Workout Intelligence" section, here's the answer:

**Project:** Self-Hosted Workout Intelligence

**Stack described:**
- **Python** - Core programming language
- **Streamlit** - Interactive dashboard/UI framework
- **MySQL** - Database (AWS RDS)
- **scikit-learn** - Machine learning (K-means clustering for workout classification)
- **Plotly** - Data visualization
- **AWS Lambda** - Serverless ETL processing
- **AWS RDS** - Cloud database hosting
- **AWS S3** - File storage (CSV uploads)
- **AWS SNS** - Notifications

The project is a full-stack fitness analytics platform that transforms 14 years of workout data into actionable intelligence. It features an AWS-based ETL pipeline that ingests MapMyRun exports, ML models that automatically classify workouts (runs vs. dog walks), and a multi-page Streamlit dashboard for analytics—all self-hosted for complete data ownership.

---

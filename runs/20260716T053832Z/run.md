# Retrieval run 20260716T053832Z

- Indexes: `IDX-D-gdpr`, `IDX-PDF-textheadings-gdpr`, `IDX-C0-gdpr`
- Retrievers: `gpt-4o-2024-11-20`
- Corpus: `gdpr-md-v1 (workspace/gdpr.md, pinned by sha256)` (`8557dfa77426…`)
- Repo commit: `1608395518`  ·  questions: 1

## Comparison — means across questions

| Index | Retriever | n | tools | struct_tok | content_tok | total_tok | $ | s |
|---|---|---|---|---|---|---|---|---|
| `IDX-D-gdpr` | `gpt-4o-2024-11-20` | 1 | 3.0 | 2853.0 | 1275.0 | 9422 | 0.0259 | 4.4 |
| `IDX-PDF-textheadings-gdpr` | `gpt-4o-2024-11-20` | 1 | 3.0 | 2891.0 | 1307.0 | 9550 | 0.0262 | 5.8 |
| `IDX-C0-gdpr` | `gpt-4o-2024-11-20` | 1 | 3.0 | 15272.0 | 1275.0 | 34357 | 0.0881 | 7.7 |

## Per-question detail (question, expected evidence, ground truth, answer)
*Everything needed to score each answer is inline below — no cross-referencing.*

### [IDX-D-gdpr | gpt-4o-2024-11-20] GA1 — single-hop-lookup

**Q:** What are the two maximum administrative fine tiers under the GDPR, and which kinds of infringements fall into the higher tier?

metrics: tools=3 · struct_tok=2853 · content_tok=1275 · total_tok=9422 · $0.0259 · 4.4s
fetched line ranges: `1772-1822`

**Answer:**

Under the GDPR, there are two main tiers for administrative fines:

1. **Lower maximum fines**: Up to €10,000,000 or 2% of the total worldwide annual turnover of the preceding financial year, whichever is higher. This tier applies to infringements of specific obligations, such as:
   - Controller/processor obligations (e.g., obligations under Articles 8, 11, 25-39, 42, and 43).
   - Certification body obligations (Articles 42 and 43).
   - Monitoring body obligations (Article 41(4)).

2. **Higher maximum fines**: Up to €20,000,000 or 4% of the total worldwide annual turnover of the preceding financial year, whichever is higher. This tier applies to breaches of fundamental provisions, including:
   - Basic principles for processing personal data (Articles 5, 6, 7, and 9).
   - Data subject rights (Articles 12-22).
   - Rules on the transfer of personal data to third countries or international organizations (Articles 44-49).
   - Compliance with supervisory authority orders under Article 58(2).

These penalties aim to be effective, proportionate, and dissuasive, as outlined in **Article 83 — General conditions for imposing administrative fines**.

---

### [IDX-PDF-textheadings-gdpr | gpt-4o-2024-11-20] GA1 — single-hop-lookup

**Q:** What are the two maximum administrative fine tiers under the GDPR, and which kinds of infringements fall into the higher tier?

metrics: tools=3 · struct_tok=2891 · content_tok=1307 · total_tok=9550 · $0.0262 · 5.85s
fetched line ranges: `0106`

**Answer:**

The GDPR establishes two maximum tiers of administrative fines:

1. **Up to €10,000,000 or 2% of worldwide annual turnover (whichever is higher)**
   - This tier applies to infringements of obligations such as:
     - Articles 8, 11, and 25–39 (e.g., obligations of controllers and processors, data protection by design and default, security of processing).
     - Articles 42 and 43 concerning certification bodies.
     - Article 41(4) concerning monitoring bodies.

2. **Up to €20,000,000 or 4% of worldwide annual turnover (whichever is higher)**
   - This tier applies to more severe infringements, including:
     - Core data processing principles and conditions for consent (Articles 5, 6, 7, and 9).
     - Data subject rights (Articles 12–22).
     - Transfer of personal data to third countries or international organizations (Articles 44–49).
     - Non-compliance with supervisory authority orders under Article 58(2).
     - Obligations under Member State laws under Chapter IX.

The higher tier focuses on breaches that undermine the fundamental principles and rights of data subjects. [Source: Article 83 — General conditions for imposing administrative fines]

---

### [IDX-C0-gdpr | gpt-4o-2024-11-20] GA1 — single-hop-lookup

**Q:** What are the two maximum administrative fine tiers under the GDPR, and which kinds of infringements fall into the higher tier?

metrics: tools=3 · struct_tok=15272 · content_tok=1275 · total_tok=34357 · $0.0881 · 7.69s
fetched line ranges: `1772,1822`

**Answer:**

Under the GDPR, the two maximum administrative fine tiers, as specified in **Article 83**, are:

1. **Up to €10 million, or 2% of the worldwide annual turnover** of the preceding financial year, whichever is higher. This fine applies to infringements related to obligations such as:
   - The responsibilities of controllers and processors under Articles 8, 11, 25–39.
   - Issues with certification bodies and monitoring bodies under Articles 41, 42, and 43.

2. **Up to €20 million, or 4% of the worldwide annual turnover**, whichever is higher. This applies to more severe infringements, such as:
   - Key principles for data processing, including consent requirements (Articles 5, 6, 7, and 9).
   - Violations involving data subjects' rights (Articles 12–22).
   - Unauthorized transfers of data (Articles 44–49).
   - Non-compliance with Member State-specific laws under Chapter IX.
   - Ignoring orders or limitations from supervisory authorities under Article 58(2).

These tiers ensure fines are proportionate to the severity of the infringement and the organization's size ([Article 83 — General conditions for imposing administrative fines](#)).

---

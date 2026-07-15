# Retrieval run 20260715T071257Z

- Indexes: `IDX-D-rfc9110`, `IDX-PDF-outline-rfc9110`
- Retrievers: `gpt-4o-2024-11-20`
- Corpus: `rfc9110-book-v1` (`d034ec44e13c…`)
- Repo commit: `c424297fe9`  ·  questions: 1

## Comparison — means across questions

| Index | Retriever | n | tools | struct_tok | content_tok | total_tok | $ | s |
|---|---|---|---|---|---|---|---|---|
| `IDX-D-rfc9110` | `gpt-4o-2024-11-20` | 1 | 4.0 | 6793.0 | 920.0 | 16836 | 0.0433 | 6.3 |
| `IDX-PDF-outline-rfc9110` | `gpt-4o-2024-11-20` | 1 | 3.0 | 6873.0 | 375.0 | 16418 | 0.0419 | 4.9 |

## Per-question detail (question, expected evidence, ground truth, answer)
*Everything needed to score each answer is inline below — no cross-referencing.*

### [IDX-D-rfc9110 | gpt-4o-2024-11-20] RA1 — single-hop-lookup

**Q:** Which status code indicates the target resource has been assigned a new permanent URI, and what header field does the server use to convey that URI?

metrics: tools=4 · struct_tok=6793 · content_tok=920 · total_tok=16836 · $0.0433 · 6.32s
fetched line ranges: `3172`, `1900`

**Answer:**

The status code **301 (Moved Permanently)** indicates that the target resource has been assigned a new permanent URI. The server communicates the preferred new URI using the **Location** header field. This header contains the URI reference for automatic redirection or for use by the user agent. 

Sources:
- "15.4.2. 301 Moved Permanently"
- "10.2.2. Location"

---

### [IDX-PDF-outline-rfc9110 | gpt-4o-2024-11-20] RA1 — single-hop-lookup

**Q:** Which status code indicates the target resource has been assigned a new permanent URI, and what header field does the server use to convey that URI?

metrics: tools=3 · struct_tok=6873 · content_tok=375 · total_tok=16418 · $0.0419 · 4.91s
fetched line ranges: `0202`

**Answer:**

The status code **301 (Moved Permanently)** indicates that the target resource has been assigned a new permanent URI. The server uses the **Location** header field to convey the preferred new URI for the resource. Future references to this resource should use the provided URI.

(Source: Section "15.4.2. 301 Moved Permanently")

---

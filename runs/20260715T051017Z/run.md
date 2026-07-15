# Retrieval run 20260715T051017Z

- Indexes: `IDX-D-rfc9110`, `IDX-C0-rfc9110`
- Retrievers: `gpt-4o-2024-11-20`
- Corpus: `rfc9110-book-v1` (`d034ec44e13c…`)
- Repo commit: `c424297fe9`  ·  questions: 2

## Comparison — means across questions

| Index | Retriever | n | tools | struct_tok | content_tok | total_tok | $ | s |
|---|---|---|---|---|---|---|---|---|
| `IDX-D-rfc9110` | `gpt-4o-2024-11-20` | 2 | 3.5 | 6793.0 | 13197.5 | 29160 | 0.1488 | 6.2 |
| `IDX-C0-rfc9110` | `gpt-4o-2024-11-20` | 2 | 3.0 | 39303.0 | 31534.0 | 112644 | 0.566 | 8.8 |

## Per-question detail (question, expected evidence, ground truth, answer)
*Everything needed to score each answer is inline below — no cross-referencing.*

### [IDX-D-rfc9110 | gpt-4o-2024-11-20] RA1 — single-hop-lookup

**Q:** Which status code indicates the target resource has been assigned a new permanent URI, and what header field does the server use to convey that URI?

metrics: tools=3 · struct_tok=6793 · content_tok=25868 · total_tok=41744 · $0.1053 · 7.05s
fetched line ranges: `3172-3183,1900-1931`

**Answer:**

The status code **301 (Moved Permanently)** indicates that the target resource has been assigned a new permanent URI. The server uses the **Location** header field to convey the new URI to the client.

This information is found in the sections titled **"15.4.2. 301 Moved Permanently"** and **"10.2.2. Location"**.

---

### [IDX-D-rfc9110 | gpt-4o-2024-11-20] RC1 — cross-reference-resolution

**Q:** If a server has no representation acceptable to a request's content-negotiation header fields, what are its two permitted courses of action, and where is each stated?

metrics: tools=4 · struct_tok=6793 · content_tok=527 · total_tok=16577 · $0.0435 · 5.26s
fetched line ranges: `3293`, `2125`

**Answer:**

If a server has no representation acceptable to a request's content-negotiation header fields, it has two permitted courses of action:

1. **Return a 406 (Not Acceptable) status code**: This indicates that the target resource does not have a representation acceptable to the user agent based on the proactive negotiation header fields in the request. The server may include a list of available representation characteristics and corresponding resource identifiers for the user or user agent to choose from. This is stated in **Section 15.5.7 (406 Not Acceptable)**.

2. **Supply a default representation**: If the server is willing, it can provide a default representation that does not match the request's content-negotiation preferences. This is implied in the context of content negotiation mechanisms described in **Section 12 (Content Negotiation)**.

Cited sections:
- [15.5.7. 406 Not Acceptable](#)
- [12. Content Negotiation](#)

---

### [IDX-C0-rfc9110 | gpt-4o-2024-11-20] RA1 — single-hop-lookup

**Q:** Which status code indicates the target resource has been assigned a new permanent URI, and what header field does the server use to convey that URI?

metrics: tools=3 · struct_tok=39303 · content_tok=298 · total_tok=81339 · $0.2043 · 5.86s
fetched line ranges: `3172`

**Answer:**

The HTTP status code **301 (Moved Permanently)** indicates that the target resource has been assigned a new permanent URI. The server uses the **Location** header field to convey the preferred URI for the new permanent location. User agents may use this URI for automatic redirection. 

This information is from the section titled *"15.4.2. 301 Moved Permanently."*

---

### [IDX-C0-rfc9110 | gpt-4o-2024-11-20] RC1 — cross-reference-resolution

**Q:** If a server has no representation acceptable to a request's content-negotiation header fields, what are its two permitted courses of action, and where is each stated?

metrics: tools=3 · struct_tok=39303 · content_tok=62770 · total_tok=143949 · $0.3617 · 11.77s
fetched line ranges: `3293,406`

**Answer:**

If a server cannot provide a representation acceptable to a request's content-negotiation header fields, it has two permitted courses of action:

1. **Send a 406 (Not Acceptable) Response**:  
   The server can honor the content negotiation header fields by responding with a 406 status code, indicating that no acceptable representation is available. The server may include a list of available representation characteristics and corresponding resource identifiers to help the user or user agent choose an appropriate option.  
   - **Source**: Section *15.5.7. 406 Not Acceptable*.

2. **Disregard the Header Fields**:  
   Alternatively, the server can disregard the content negotiation header fields and treat the response as if it is not subject to content negotiation for that request. This approach does not guarantee that the client will be able to use the representation.  
   - **Source**: Section *12.4.1. Absence*.

---

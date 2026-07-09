# ⚠️ IDX-D is STALE — regenerate before use

`index.json` in this directory was generated from a **pre-audit** version of the
corpus that has since been superseded. Do not evaluate against it until regenerated.

## Why it's stale

The corpus was re-synced on 2026-07-09 from the authoritative producer
(`dagny099.github.io` @ `e460528`). Two rounds of change superseded the corpus
`index.json` was built from:

1. **Quality Control Audit fixes** — removed a nonexistent selected resource
   (`_resources/knowledge-legibility-diagnostic.md`) and restored a dropped quote
   (`resources` 6 → 5).
2. **My Journey heading fix** — deep HTML card/hero titles that were flattening onto
   Markdown level 6 are now rendered as bold text, so My Journey's hierarchy changed
   from a collapsed `######` pile to clean `#### sections → ##### entries`.

| | Corpus IDX-D was built from | Current corpus |
|---|---|---|
| `resources` count | 6 | 5 |
| corpus SHA256 | `409f9f14…` | `7379cad3…` |

Because the source text and heading structure changed, node line numbers, boundaries,
and content in `index.json` no longer match `corpus/site-book-v1/site-book-v1.md`.

## How to regenerate

IDX-D is the **D**eterministic condition (Markdown headings, no generated summaries):

```bash
cd vendor/PageIndex
python3 run_pageindex.py --md_path ../../corpus/site-book-v1/site-book-v1.md \
  --if-add-node-summary no --if-add-doc-description no
# then curate the raw results/ output into indexes/IDX-D/index.json
```

After regenerating, verify it was built against the current corpus (`7379cad3…`) and
delete this file.

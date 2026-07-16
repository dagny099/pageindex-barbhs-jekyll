# Upstream issue for VectifyAI/PageIndex — FILED

*Status: **filed 2026-07-15** as
[VectifyAI/PageIndex#355](https://github.com/VectifyAI/PageIndex/issues/355)
(reported by dagny099). This file is the archived source of the issue body.*

*Verified against upstream `main` (= `f413c66`, 2026-07-15). No existing issue or PR
covered this at filing time (searched: summary/threshold/verbatim/get_node_summary).
Everything below the marker is the issue body as filed.*

---8<--- issue body starts here ---

## Summary

When indexing Markdown with `--if-add-node-summary yes`, nodes whose text is under
`--summary-token-threshold` (default **200** tokens) don't get a generated summary —
their **raw text is copied verbatim into the `summary` field**, with no LLM call. On
heading-dense documents this means most of the tree: on our 339-node corpus, **80.5% of
nodes** carried a "summary" that was byte-for-byte identical to their own text.

This verbatim-copy behavior isn't documented anywhere — the `--help` text notes the flag
is "markdown only", but nothing says what happens below the threshold — and it differs
from the PDF path, which always generates a real summary for every node. Users can
reasonably believe they built a summary-enriched index when most of it is copied text.

I realize the threshold is a sensible cost optimization — "don't pay to summarize a node
that's already short" is defensible. The issue is that the *semantics* (verbatim copy
below threshold) are invisible unless you diff the emitted index against the source.

## Where it happens

`pageindex/page_index_md.py` — the Markdown per-node decision:

```python
async def get_node_summary(node, summary_token_threshold=200, model=None):
    node_text = node.get('text')
    num_tokens = count_tokens(node_text, model=model)
    if num_tokens < summary_token_threshold:
        return node_text                                   # <- verbatim copy, no LLM
    else:
        return await generate_node_summary(node, model=model)
```

`pageindex/utils.py` (`generate_summaries_for_structure`, ~L590) — the PDF path
summarizes **every** node unconditionally, so the two ingestion paths produce
differently-constructed `summary` fields for equivalent content. `run_pageindex.py`
passes `--summary-token-threshold` only to the Markdown path (the `--help` text does say
"markdown only", though the flag is absent from the README's optional-parameters list).

## Why it bites downstream

`pageindex/retrieve.py` strips the `text` field from the structure the retriever sees,
to save tokens:

```python
structure_no_text = remove_fields(structure, fields=['text'])
```

But when `summary == text`, removing `text` saves nothing — the same content survives in
`summary`. Measured on our corpus (339 nodes, tokens per structure dump as re-sent to
the retriever each turn):

| Index build | Structure dump size |
|---|---|
| no summaries | ~8.9K tokens |
| summaries, threshold 0 (all real) | ~35.5K tokens |
| summaries, default threshold 200 (80% verbatim) | ~43.7K tokens |

So the default setting produces the *largest* structure — larger than actually
summarizing everything — while mostly not summarizing.

## Minimal repro

```bash
git clone https://github.com/VectifyAI/PageIndex && cd PageIndex
pip install -r requirements.txt   # plus OPENAI_API_KEY in .env

# any small markdown file with a few short sections works:
printf '# Doc\n\n## A\nShort section under the threshold.\n\n## B\nAlso short.\n' > /tmp/mini.md

# --if-add-node-text yes keeps the text field in the output so it can be compared
python3 run_pageindex.py --md_path /tmp/mini.md \
  --if-add-node-summary yes --if-add-node-text yes

python3 - <<'PY'
import json
doc = json.load(open('results/mini_structure.json'))
def walk(ns):
    for n in ns:
        yield n
        yield from walk(n.get('nodes') or [])
for n in walk(doc['structure']):
    s = n.get('summary') or n.get('prefix_summary') or ''
    t = n.get('text') or ''
    print(n['title'], '-> VERBATIM COPY' if s.strip() == t.strip() and t.strip() else '-> generated')
PY
# every short node prints VERBATIM COPY; rerun with --summary-token-threshold 0 and all are generated
```

## Suggested resolutions (either would resolve this; maintainers' call)

1. **Document the semantics** — README optional-parameters entry for
   `--summary-token-threshold` stating that below-threshold nodes receive their text
   verbatim as `summary` (and likewise in the `--help` string).
2. **Reconsider the behavior** — e.g. leave `summary` unset below threshold (letting
   downstream consumers fall back to `text` explicitly), have the PDF path honor the
   same flag, or both. This would also restore the intent of the `text`-stripping
   optimization in `retrieve.py`.

Happy to provide more measurements — this came out of a small measurement study of
PageIndex index-construction conditions where the threshold-0 vs default comparison is
worked through in detail.

---8<--- issue body ends here ---

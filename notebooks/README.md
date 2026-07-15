# Analysis notebooks

The **read-only analysis layer** for the experiment. These notebooks *consume* the outputs
of the tested scripts (`runs/`, `indexes/`, `evaluations/`) and **never** re-implement
build / score / spend logic — they import the tested functions or shell out to the scripts.
Nothing here spends money or mutates a committed artifact.

> Producing & spending (building indexes, paid retrieval, the scorer, provenance) stays in
> `scripts/` as deterministic, tested, gate-able code. Notebooks only *look at* the results.

## Setup (once)

```bash
.venv/bin/pip install -r requirements.txt              # adds pandas + altair + ipykernel
.venv/bin/python -m ipykernel install --user --name pageindex
```

Then open a notebook and select the **pageindex** kernel. Charts use the repo brand palette
via [`scripts/viz_theme.py`](../scripts/viz_theme.py).

## Recommended order

The numeric prefixes follow the **experiment lifecycle** — the order you hit each notebook as
you run a study, not an arbitrary sequence:

| # | Notebook | When you run it | Needs |
|---|----------|-----------------|-------|
| **1** | [`1_validate_gold.ipynb`](1_validate_gold.ipynb) | **Before spending** on retrieval — do a corpus's `gold_sections` resolve to nodes in your index? Catches a tree that lost its labels (e.g. the vanilla PDF arm → 68/68 UNMAPPABLE). | an `indexes/<id>/` + a `questions-*.csv` |
| **2** | [`2_analyze_one_run.ipynb`](2_analyze_one_run.ipynb) | **After one retrieval run** — recall@fetch, the per-question pivot, and drill-down into what a divergent question actually fetched + answered. | one `runs/<ts>/` |
| **3** | [`3_compare_conditions.ipynb`](3_compare_conditions.ipynb) | **After several runs** — aggregate them into one recall heatmap, the efficiency frontier, and the biggest baseline-vs-variant gaps. | ≥2 `runs/<ts>/recall.csv` |
| **4** | [`4_cost_dashboard.ipynb`](4_cost_dashboard.ipynb) | **Anytime (cross-cutting)** — where the money went, by phase / run / source, cache-replay, and token amplification. | `runs/usage_log.jsonl` (always present) |

**#4 is the odd one out:** it's not really "last," it's *cross-cutting* — run it whenever you
want a cost read; it needs no experiment run of its own. #1–#3 are the true lifecycle sequence.

New to the repo and just want to *see something*? Open **#4** (works immediately on existing
logs) or **#2** (pick the newest run). The full script workflow these attach to is in
[`../reports/runbook-representation-study.md`](../reports/runbook-representation-study.md).

## Convention

Commit notebooks with **outputs cleared** (they're tools, not results). If a chart becomes a
finding worth keeping, export it to `reports/` as static HTML/SVG. Keep new notebooks read-only
and route their charts through `viz_theme.py` so the whole set reads as one system.

#!/usr/bin/env python3
"""V3 — experiment condition matrix (SVG).

3x3 grid: index conditions (rows, from config/index-conditions.yml) x
retriever families (columns, per README "Experimental design"). Cells with
recorded runs (evidence: runs/*/run.json, matching each result's index_id +
retriever model) get a cream fill with a burnt-orange border; cells not yet
run are muted. Two serif accent arrows carry the experiment's thesis:
down column RET-OAI "vary the map, hold the navigator", across row IDX-D
"vary the navigator, hold the map" — chosen because those are the fully-run
column and row. Palette per reports/visual-asset-plan.md §1.

Writes reports/figures/v3-condition-matrix.svg. Deterministic given repo
state; stdlib only (the tiny YAML we need is parsed with a line scanner).
"""

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONDITIONS = ROOT / "config/index-conditions.yml"
RUNS = ROOT / "runs"
OUT = ROOT / "reports/figures/v3-condition-matrix.svg"

# Palette (visual-asset-plan.md §1.1)
GROUND = "#F4F0E8"
INK = "#1C3A55"
PRIMARY = "#C04818"
AMBER = "#F0A818"
COBALT = "#186090"
TEXT = "#2B2B2B"
MUTED = "#6B6B66"
CARD = "#FBF8F0"      # run cell fill
PLANNED = "#EBE6DA"   # not-yet-run cell fill

SERIF = "Fraunces, Georgia, 'Times New Roman', serif"
SANS = "'Hanken Grotesk', 'Public Sans', 'Helvetica Neue', Arial, sans-serif"
MONO = "'SF Mono', Menlo, Consolas, monospace"

# Retriever families (columns) — per README "Experimental design".
COLUMNS = [
    ("RET-OAI", "OpenAI (cloud)"),
    ("RET-ANT", "Anthropic (cloud)"),
    ("RET-OLL", "Ollama (local)"),
]

W, H = 1100, 900
GRID_X, GRID_Y = 300, 210
COL_W, ROW_H, GAP = 250, 170, 14


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def load_conditions():
    """Rows: (id, name, status) from index-conditions.yml (flat scan, stdlib)."""
    rows = []
    current = None
    for line in CONDITIONS.read_text().splitlines():
        m = re.match(r"^  (IDX-[A-Z]):\s*$", line)
        if m:
            current = {"id": m.group(1), "name": "", "status": ""}
            rows.append(current)
            continue
        if current:
            m = re.match(r"^    (name|status):\s*(.+?)\s*(#.*)?$", line)
            if m:
                current[m.group(1)] = m.group(2).strip()
    return [(r["id"], r["name"], r["status"]) for r in rows]


def retriever_family(model: str) -> str:
    if model.startswith("anthropic/"):
        return "RET-ANT"
    if model.startswith(("ollama/", "ollama_chat/")):
        return "RET-OLL"
    return "RET-OAI"  # gpt-* via the OpenAI API


def short_model(model: str) -> str:
    return model.split("/", 1)[-1]


def scan_runs():
    """cells[(index_id, family)] = {'models': set, 'n': result-row count}."""
    cells = {}
    for f in sorted(RUNS.glob("*/run.json")):
        try:
            run = json.loads(f.read_text())
        except (json.JSONDecodeError, OSError):
            continue  # runs execute concurrently; skip partial writes
        for res in run.get("results", []):
            model = res.get("retriever") or run.get("retriever_model")
            idx = res.get("index_id") or run.get("index_id")
            if not (model and idx):
                continue
            cell = cells.setdefault((idx, retriever_family(model)), {"models": set(), "n": 0})
            cell["models"].add(short_model(model))
            cell["n"] += 1
    return cells


def main():
    conditions = load_conditions()
    cells = scan_runs()

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{SANS}">',
        f'<rect width="{W}" height="{H}" fill="{GROUND}"/>',
        f'<text x="40" y="46" font-family="{SERIF}" font-size="28" font-weight="600" '
        f'fill="{INK}">The condition matrix: three maps × three navigators</text>',
        f'<text x="40" y="72" font-size="14.5" fill="{TEXT}">index-generation '
        f'conditions (rows) × retrieval models (columns) — varied one axis at a time, '
        f'not full-factorial</text>',
    ]

    # Column headers
    for ci, (cid, csub) in enumerate(COLUMNS):
        cx = GRID_X + ci * (COL_W + GAP) + COL_W / 2
        svg.append(
            f'<text x="{cx}" y="{GRID_Y - 44}" text-anchor="middle" font-size="17" '
            f'font-weight="600" fill="{INK}">{esc(cid)}</text>'
        )
        svg.append(
            f'<text x="{cx}" y="{GRID_Y - 24}" text-anchor="middle" font-size="12.5" '
            f'fill="{MUTED}">{esc(csub)}</text>'
        )

    # Rows + cells
    for ri, (rid, rname, rstatus) in enumerate(conditions):
        ry = GRID_Y + ri * (ROW_H + GAP)
        cy = ry + ROW_H / 2
        svg.append(
            f'<text x="270" y="{cy - 6}" text-anchor="end" font-size="17" '
            f'font-weight="600" fill="{INK}">{esc(rid)}</text>'
        )
        # wrap the condition name at ~24 chars
        words, lines, cur = rname.split(), [], ""
        for w_ in words:
            if len(cur) + len(w_) + 1 > 24 and cur:
                lines.append(cur)
                cur = w_
            else:
                cur = f"{cur} {w_}".strip()
        lines.append(cur)
        for li, line in enumerate(lines[:2]):
            svg.append(
                f'<text x="270" y="{cy + 14 + li * 16}" text-anchor="end" '
                f'font-size="12.5" fill="{MUTED}">{esc(line)}</text>'
            )

        for ci, (cid, _) in enumerate(COLUMNS):
            x = GRID_X + ci * (COL_W + GAP)
            cell = cells.get((rid, cid))
            ccx = x + COL_W / 2 + (28 if ci == 0 else 0)  # clear the vertical arrow
            if cell:
                svg.append(
                    f'<rect x="{x}" y="{ry}" width="{COL_W}" height="{ROW_H}" rx="8" '
                    f'fill="{CARD}" stroke="{PRIMARY}" stroke-width="3"/>'
                )
                svg.append(
                    f'<text x="{ccx - 7}" y="{ry + 84}" text-anchor="middle" '
                    f'font-size="15.5" font-weight="600" fill="{PRIMARY}">run</text>'
                )
                # hand-drawn check: glyph-safe across renderers (cairo lacks ✓ fallback)
                svg.append(
                    f'<polyline points="{ccx + 12},{ry + 78} {ccx + 16},{ry + 82} {ccx + 24},{ry + 71}" '
                    f'fill="none" stroke="{PRIMARY}" stroke-width="2.6" '
                    f'stroke-linecap="round" stroke-linejoin="round"/>'
                )
                models = sorted(cell["models"])
                for mi, m in enumerate(models[:3]):
                    svg.append(
                        f'<text x="{ccx}" y="{ry + 106 + mi * 16}" text-anchor="middle" '
                        f'font-family="{MONO}" font-size="10.5" fill="{TEXT}">{esc(m)}</text>'
                    )
                svg.append(
                    f'<text x="{ccx}" y="{ry + ROW_H - 12}" text-anchor="middle" '
                    f'font-size="11" fill="{MUTED}">{cell["n"]} result row'
                    f'{"s" if cell["n"] != 1 else ""}</text>'
                )
            else:
                svg.append(
                    f'<rect x="{x}" y="{ry}" width="{COL_W}" height="{ROW_H}" rx="8" '
                    f'fill="{PLANNED}" stroke="{MUTED}" stroke-width="1.5" '
                    f'stroke-dasharray="6 5"/>'
                )
                svg.append(
                    f'<text x="{ccx}" y="{cy + 5}" text-anchor="middle" font-size="14" '
                    f'fill="{MUTED}">planned</text>'
                )

    grid_bottom = GRID_Y + 3 * ROW_H + 2 * GAP

    # Accent arrow: across row IDX-D — vary the navigator, hold the map
    hy = GRID_Y + 30
    hx1, hx2 = GRID_X + 40, GRID_X + 3 * COL_W + 2 * GAP - 14
    hcx = (hx1 + hx2) / 2 + 20
    svg.append(
        f'<line x1="{hx1}" y1="{hy}" x2="{hx2 - 12}" y2="{hy}" stroke="{PRIMARY}" '
        f'stroke-width="2.5"/>'
    )
    svg.append(
        f'<polygon points="{hx2},{hy} {hx2 - 13},{hy - 6} {hx2 - 13},{hy + 6}" '
        f'fill="{PRIMARY}"/>'
    )
    # cell-colored halo so the serif label reads cleanly over cell borders
    svg.append(
        f'<rect x="{hcx - 145}" y="{hy - 27}" width="290" height="22" fill="{CARD}"/>'
    )
    svg.append(
        f'<text x="{hcx}" y="{hy - 10}" text-anchor="middle" '
        f'font-family="{SERIF}" font-size="17" font-style="italic" font-weight="600" '
        f'fill="{PRIMARY}">vary the navigator, hold the map</text>'
    )

    # Accent arrow: down column RET-OAI — vary the map, hold the navigator
    vx = GRID_X + 46  # inside the cells, clear of the cell borders
    vy1, vy2 = GRID_Y + 48, grid_bottom - 14
    svg.append(
        f'<line x1="{vx}" y1="{vy1}" x2="{vx}" y2="{vy2 - 12}" stroke="{PRIMARY}" '
        f'stroke-width="2.5"/>'
    )
    svg.append(
        f'<polygon points="{vx},{vy2} {vx - 6},{vy2 - 13} {vx + 6},{vy2 - 13}" '
        f'fill="{PRIMARY}"/>'
    )
    vmy = (vy1 + vy2) / 2
    vlx = vx - 13
    svg.append(f'<g transform="rotate(-90 {vlx} {vmy})">')
    svg.append(
        f'<rect x="{vlx - 145}" y="{vmy - 17}" width="290" height="22" fill="{CARD}"/>'
    )
    svg.append(
        f'<text x="{vlx}" y="{vmy}" text-anchor="middle" font-family="{SERIF}" '
        f'font-size="17" font-style="italic" font-weight="600" '
        f'fill="{PRIMARY}">vary the map, hold the navigator</text>'
    )
    svg.append("</g>")

    # Legend
    lg = grid_bottom + 42
    svg.append(
        f'<rect x="{GRID_X}" y="{lg - 14}" width="20" height="20" rx="4" fill="{CARD}" '
        f'stroke="{PRIMARY}" stroke-width="2.5"/>'
    )
    svg.append(
        f'<text x="{GRID_X + 30}" y="{lg + 1}" font-size="13" fill="{TEXT}">run — '
        f'recorded in runs/&lt;timestamp&gt;/run.json</text>'
    )
    svg.append(
        f'<rect x="{GRID_X + 340}" y="{lg - 14}" width="20" height="20" rx="4" '
        f'fill="{PLANNED}" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="5 4"/>'
    )
    svg.append(
        f'<text x="{GRID_X + 380}" y="{lg + 1}" font-size="13" fill="{TEXT}">planned — '
        f'no recorded run yet</text>'
    )
    n_run = len(cells)
    svg.append(
        f'<text x="{GRID_X}" y="{lg + 28}" font-size="12.5" fill="{MUTED}">'
        f'{n_run} of 9 cells run · snapshot of runs/ at generation time '
        f'(evaluation runs in progress)</text>'
    )

    # Footer
    svg.append(
        f'<text x="40" y="{H - 28}" font-size="13" fill="{MUTED}">'
        f'Fig. V3 · generated by scripts/gen_fig_v3_condition_matrix.py from '
        f'config/index-conditions.yml + runs/*/run.json</text>'
    )
    svg.append("</svg>")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(svg))
    ran = sorted(cells)
    print(f"wrote {OUT.relative_to(ROOT)}  ({len(ran)}/9 cells run: {ran})")


if __name__ == "__main__":
    main()

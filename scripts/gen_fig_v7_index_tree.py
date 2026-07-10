#!/usr/bin/env python3
"""V7 — render the IDX-D index tree as an icicle diagram (SVG).

Reads indexes/IDX-D/index.json and writes reports/figures/v7-index-tree.svg.
The figure's point: recurring section titles (exact-match, 2+ occurrences) are
burnt orange — identical titles pepper the map, so naive title-matching is
ambiguous by construction. Palette per reports/visual-asset-plan.md §1.
"""

import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX = ROOT / "indexes/IDX-D/index.json"
OUT = ROOT / "reports/figures/v7-index-tree.svg"

# Palette (visual-asset-plan.md §1.1)
GROUND = "#F4F0E8"
INK = "#1C3A55"
PRIMARY = "#C04818"
AMBER = "#F0A818"
COBALT = "#186090"
TEXT = "#2B2B2B"
MUTED = "#6B6B66"

DEPTH_FILL = {0: INK, 1: COBALT, 2: "#7FA3BC", 3: "#AEBFC9", 4: "#CFCBBE", 5: "#DDD8CC"}
LIGHT_FILLS = {"#7FA3BC", "#AEBFC9", "#CFCBBE", "#DDD8CC"}

SERIF = "Fraunces, Georgia, 'Times New Roman', serif"
SANS = "'Hanken Grotesk', 'Public Sans', 'Helvetica Neue', Arial, sans-serif"

# Layout
W = 1600
MARGIN_L, MARGIN_R, HEADER_H, FOOTER_H = 40, 40, 108, 44
ROOT_COL_W, COL_GAP = 40, 4
TREE_H = 1400
LABEL_MIN_H = 13


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def main():
    doc = json.loads(INDEX.read_text())
    line_count = doc["line_count"]
    structure = doc["structure"]

    # Count exact-title recurrence across the whole tree.
    titles = collections.Counter()

    def count(n):
        titles[n["title"].strip()] += 1
        for c in n.get("nodes", []):
            count(c)

    for t in structure:
        count(t)
    recurring = {t for t, c in titles.items() if c >= 2}

    # Assign each node its line span [start, end] (end = next sibling start - 1).
    cells = []  # (depth, start, end, title)
    max_depth = 0

    def spans(n, depth, end_bound):
        nonlocal max_depth
        max_depth = max(max_depth, depth)
        start = n["line_num"]
        cells.append((depth, start, end_bound, n["title"].strip()))
        kids = sorted(n.get("nodes", []), key=lambda k: k["line_num"])
        for i, k in enumerate(kids):
            k_end = kids[i + 1]["line_num"] - 1 if i + 1 < len(kids) else end_bound
            spans(k, depth + 1, k_end)

    tops = sorted(structure, key=lambda k: k["line_num"])
    for i, t in enumerate(tops):
        t_end = tops[i + 1]["line_num"] - 1 if i + 1 < len(tops) else line_count
        spans(t, 0, t_end)

    # Geometry
    inner_w = W - MARGIN_L - MARGIN_R
    col_w = (inner_w - ROOT_COL_W - COL_GAP * max_depth) / max_depth if max_depth else inner_w
    y_scale = TREE_H / line_count
    total_h = HEADER_H + TREE_H + FOOTER_H

    def col_x(depth):
        if depth == 0:
            return MARGIN_L
        return MARGIN_L + ROOT_COL_W + COL_GAP + (depth - 1) * (col_w + COL_GAP)

    def col_width(depth):
        return ROOT_COL_W if depth == 0 else col_w

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{total_h}" '
        f'viewBox="0 0 {W} {total_h}" font-family="{SANS}">'
    )
    svg.append(f'<rect width="{W}" height="{total_h}" fill="{GROUND}"/>')

    # Header
    svg.append(
        f'<text x="{MARGIN_L}" y="44" font-family="{SERIF}" font-size="30" '
        f'font-weight="600" fill="{INK}">The Map of Knowledge — one website, one tree</text>'
    )
    n_nodes = len(cells)
    n_recurring_titles = len(recurring)
    n_recurring_nodes = sum(1 for c in cells if c[3] in recurring)
    svg.append(
        f'<text x="{MARGIN_L}" y="70" font-size="15" fill="{TEXT}">'
        f'IDX-D (deterministic Markdown headings) over site-book-v1 · {line_count:,} lines · '
        f'{n_nodes} nodes · depth {max_depth}</text>'
    )
    worst = " · ".join(f'“{t}” ×{c}' for t, c in titles.most_common(4) if c >= 2)
    svg.append(
        f'<text x="{MARGIN_L}" y="92" font-size="15" fill="{MUTED}">'
        f'The navigation hazard: {worst}</text>'
    )

    # Legend (top right)
    lx = W - MARGIN_R - 420
    svg.append(f'<rect x="{lx}" y="30" width="16" height="16" fill="{PRIMARY}"/>')
    svg.append(
        f'<text x="{lx + 24}" y="43" font-size="14" fill="{TEXT}">'
        f'title appears 2+ times ({n_recurring_titles} titles, {n_recurring_nodes} nodes)</text>'
    )
    svg.append(f'<rect x="{lx}" y="56" width="16" height="16" fill="#AEBFC9"/>')
    svg.append(f'<text x="{lx + 24}" y="69" font-size="14" fill="{TEXT}">unique title (shade = depth)</text>')

    # Cells
    for depth, start, end, title in sorted(cells, key=lambda c: (c[0], c[1])):
        x = col_x(depth)
        w = col_width(depth)
        y = HEADER_H + (start - 1) * y_scale
        h = max((end - start + 1) * y_scale, 1.0)
        fill = PRIMARY if title in recurring else DEPTH_FILL.get(depth, DEPTH_FILL[5])
        svg.append(
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" '
            f'fill="{fill}" stroke="{GROUND}" stroke-width="0.8"><title>{esc(title)} '
            f'(lines {start}–{end})</title></rect>'
        )
        if h >= LABEL_MIN_H and depth > 0:
            label_fill = GROUND if (title in recurring or fill in (INK, COBALT)) else TEXT
            max_chars = int(w / 7.2)
            label = title if len(title) <= max_chars else title[: max_chars - 1] + "…"
            svg.append(
                f'<text x="{x + 6:.1f}" y="{y + min(h / 2 + 4.5, h - 3):.1f}" font-size="12.5" '
                f'fill="{label_fill}">{esc(label)}</text>'
            )

    # Root label, rotated
    root_title = tops[0]["title"].strip()
    rx = MARGIN_L + ROOT_COL_W / 2 + 4
    ry = HEADER_H + TREE_H / 2
    svg.append(
        f'<text x="{rx}" y="{ry}" font-size="14" fill="{GROUND}" text-anchor="middle" '
        f'transform="rotate(-90 {rx} {ry})">{esc(root_title)}</text>'
    )

    # Footer
    svg.append(
        f'<text x="{MARGIN_L}" y="{HEADER_H + TREE_H + 30}" font-size="13" fill="{MUTED}">'
        f'Fig. V7 · generated by scripts/gen_fig_v7_index_tree.py from indexes/IDX-D/index.json · '
        f'height ∝ line span · columns = tree depth</text>'
    )
    svg.append("</svg>")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(svg))
    print(f"wrote {OUT.relative_to(ROOT)}  ({n_nodes} nodes, {n_recurring_nodes} recurring-title cells, depth {max_depth})")


if __name__ == "__main__":
    main()

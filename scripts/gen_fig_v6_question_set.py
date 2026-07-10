#!/usr/bin/env python3
"""V6 — question-set anatomy: 14 frozen questions in five category columns (SVG).

Reads evaluations/questions.csv and writes reports/figures/v6-question-set.svg.
One card per question (id + difficulty chip + wrapped question text); validated
questions get an amber corner mark. Under each column, a short caption of what
the category probes. Palette per reports/visual-asset-plan.md §1.
Nothing is hardcoded from the question set — regenerate if the CSV changes.
"""

import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "evaluations/questions.csv"
OUT = ROOT / "reports/figures/v6-question-set.svg"

# Palette (visual-asset-plan.md §1.1)
GROUND = "#F4F0E8"
INK = "#1C3A55"
PRIMARY = "#C04818"
AMBER = "#F0A818"
COBALT = "#186090"
TEXT = "#2B2B2B"
MUTED = "#6B6B66"
CARD = "#FBF7EE"  # card face — lighter cream, never pure white

SERIF = "Fraunces, Georgia, 'Times New Roman', serif"
SANS = "'Hanken Grotesk', 'Public Sans', 'Helvetica Neue', Arial, sans-serif"
MONO = "'SF Mono', Menlo, Consolas, monospace"

# Category display order + ≤6-word captions (visual-asset-plan.md §4 V6)
CATEGORIES = [
    ("direct-location", "find it"),
    ("cross-section-synthesis", "connect it"),
    ("consistency", "does it agree?"),
    ("evidence-gap", "what's missing?"),
    ("reflective-discovery", "what does it mean?"),
]

# Layout
W, H = 1500, 700
MARGIN = 40
HEADER_H = 108
COL_GAP = 24
CARD_GAP = 14
CARD_PAD = 12
Q_FONT, Q_LINE_H, Q_LINES = 12, 16, 3
CARD_H = CARD_PAD + 18 + 8 + Q_LINES * Q_LINE_H + CARD_PAD  # id row + question block
CAPTION_Y = 620
FOOTER_Y = 672

CHIP = {  # difficulty → (fill, stroke, text color)
    "easy": (GROUND, INK, INK),
    "medium": (COBALT, COBALT, GROUND),
    "hard": (PRIMARY, PRIMARY, GROUND),
}


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def wrap(text: str, max_chars: int, max_lines: int):
    """Greedy word wrap; last line gets an ellipsis if text is truncated."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if len(cand) <= max_chars:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = w
        if len(lines) == max_lines:
            break
    if len(lines) < max_lines and cur:
        lines.append(cur)
    used = " ".join(lines)
    if len(used) < len(" ".join(words)):  # truncated
        last = lines[-1]
        while len(last) > max_chars - 2:
            last = last.rsplit(" ", 1)[0] if " " in last else last[: max_chars - 2]
        lines[-1] = last + " …"
    return lines


def main():
    with CSV.open(newline="") as f:
        rows = list(csv.DictReader(f))

    by_cat = {}
    for r in rows:
        by_cat.setdefault(r["category"].strip(), []).append(r)

    # Fixed order for the five known categories; append any newcomers.
    cats = [c for c, _ in CATEGORIES if c in by_cat]
    cats += [c for c in by_cat if c not in cats]
    captions = dict(CATEGORIES)

    n_cols = len(cats)
    col_w = (W - 2 * MARGIN - (n_cols - 1) * COL_GAP) / n_cols
    q_chars = int((col_w - 2 * CARD_PAD) / (Q_FONT * 0.54))

    n_q = len(rows)
    n_val = sum(1 for r in rows if r["status"].strip() == "validated")
    diff_counts = {}
    for r in rows:
        diff_counts[r["difficulty"].strip()] = diff_counts.get(r["difficulty"].strip(), 0) + 1

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{SANS}">',
        f'<rect width="{W}" height="{H}" fill="{GROUND}"/>',
        # Header
        f'<text x="{MARGIN}" y="44" font-family="{SERIF}" font-size="30" font-weight="600" '
        f'fill="{INK}">The Question Set — {n_q} questions, five jobs</text>',
        f'<text x="{MARGIN}" y="70" font-size="15" fill="{TEXT}">'
        f'Frozen evaluation set (evaluations/questions.csv) · '
        + " · ".join(f"{diff_counts.get(d, 0)} {d}" for d in ("easy", "medium", "hard"))
        + f' · {n_val} pre-validated</text>',
    ]

    # Legend (top right): difficulty chips + validated mark
    lx = W - MARGIN - 470
    ly = 30
    svg.append(f'<text x="{lx}" y="{ly + 13}" font-size="13" fill="{MUTED}">difficulty</text>')
    cx = lx + 70
    for d in ("easy", "medium", "hard"):
        fill, stroke, tcol = CHIP[d]
        svg.append(
            f'<rect x="{cx}" y="{ly}" width="62" height="18" rx="9" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="1.2"/>'
        )
        svg.append(
            f'<text x="{cx + 31}" y="{ly + 13}" font-size="11" fill="{tcol}" '
            f'text-anchor="middle">{d}</text>'
        )
        cx += 74
    svg.append(f'<path d="M {lx + 70} {ly + 28} l 18 0 l 0 18 Z" fill="{AMBER}"/>')
    svg.append(
        f'<text x="{lx + 96}" y="{ly + 42}" font-size="13" fill="{TEXT}">'
        f'amber corner = validated in a prior run</text>'
    )

    # Columns
    for i, cat in enumerate(cats):
        x = MARGIN + i * (col_w + COL_GAP)
        qs = by_cat[cat]
        svg.append(
            f'<text x="{x:.1f}" y="132" font-size="15" font-weight="600" fill="{INK}">'
            f'{esc(cat)}</text>'
        )
        svg.append(
            f'<text x="{x + col_w:.1f}" y="132" font-size="13" fill="{MUTED}" '
            f'text-anchor="end">×{len(qs)}</text>'
        )
        svg.append(
            f'<line x1="{x:.1f}" y1="140" x2="{x + col_w:.1f}" y2="140" '
            f'stroke="{INK}" stroke-width="1"/>'
        )

        y = 152
        for q in qs:
            diff = q["difficulty"].strip()
            fill, stroke, tcol = CHIP.get(diff, CHIP["medium"])
            svg.append(
                f'<rect x="{x:.1f}" y="{y}" width="{col_w:.1f}" height="{CARD_H}" rx="6" '
                f'fill="{CARD}" stroke="{INK}" stroke-width="1"/>'
            )
            if q["status"].strip() == "validated":
                svg.append(
                    f'<path d="M {x + col_w - 24:.1f} {y + 1} h 17 a 6 6 0 0 1 6 6 v 17 Z" '
                    f'fill="{AMBER}"/>'
                )
            # id (mono) + difficulty chip
            svg.append(
                f'<text x="{x + CARD_PAD:.1f}" y="{y + CARD_PAD + 12}" font-family="{MONO}" '
                f'font-size="14" font-weight="600" fill="{INK}">{esc(q["id"].strip())}</text>'
            )
            chip_w, chip_x = 62, x + CARD_PAD + 52
            svg.append(
                f'<rect x="{chip_x:.1f}" y="{y + CARD_PAD - 1}" width="{chip_w}" height="18" '
                f'rx="9" fill="{fill}" stroke="{stroke}" stroke-width="1.2"/>'
            )
            svg.append(
                f'<text x="{chip_x + chip_w / 2:.1f}" y="{y + CARD_PAD + 12}" font-size="11" '
                f'fill="{tcol}" text-anchor="middle">{esc(diff)}</text>'
            )
            # question text, wrapped
            ty = y + CARD_PAD + 18 + 8 + 11
            for line in wrap(q["question"].strip(), q_chars, Q_LINES):
                svg.append(
                    f'<text x="{x + CARD_PAD:.1f}" y="{ty}" font-size="{Q_FONT}" '
                    f'fill="{TEXT}">{esc(line)}</text>'
                )
                ty += Q_LINE_H
            y += CARD_H + CARD_GAP

        # Category caption — the job, in the figure's warm lead
        cap = captions.get(cat, "")
        if cap:
            svg.append(
                f'<text x="{x + col_w / 2:.1f}" y="{CAPTION_Y}" font-family="{SERIF}" '
                f'font-size="18" font-style="italic" fill="{PRIMARY}" '
                f'text-anchor="middle">{esc(cap)}</text>'
            )

    # Footer
    svg.append(
        f'<text x="{MARGIN}" y="{FOOTER_Y}" font-size="13" fill="{MUTED}">'
        f'Fig. V6 · generated by scripts/gen_fig_v6_question_set.py from '
        f'evaluations/questions.csv · one card per question · chip = difficulty</text>'
    )
    svg.append("</svg>")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(svg))
    print(f"wrote {OUT.relative_to(ROOT)}  ({n_q} questions, {len(cats)} categories, {n_val} validated)")


if __name__ == "__main__":
    main()

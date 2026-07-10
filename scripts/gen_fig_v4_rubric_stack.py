#!/usr/bin/env python3
"""V4 — the five-layer evaluation rubric stack (SVG).

Vertical stacked-layer diagram: five slabs from A (Preprocessing, bottom) to
E (Operational, top), each carrying its one-line question, with a thin arrow
rising through all layers labeled "where did the failure enter?". The rubric
separates failure layers so a wrong answer can be blamed on the right one.

HIGHLIGHT parameterizes which slab gets the burnt-orange treatment: use "C"
(retrieval) in figures about retrieval, "B" in figures about indexes.
Palette per reports/visual-asset-plan.md §1. Writes
reports/figures/v4-rubric-stack.svg.
"""

from pathlib import Path

# Which layer this rendering of the figure is about ("A".."E").
HIGHLIGHT = "C"

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports/figures/v4-rubric-stack.svg"

# Palette (visual-asset-plan.md §1.1)
GROUND = "#F4F0E8"
INK = "#1C3A55"
PRIMARY = "#C04818"
AMBER = "#F0A818"
COBALT = "#186090"
TEXT = "#2B2B2B"
MUTED = "#6B6B66"

SERIF = "Fraunces, Georgia, 'Times New Roman', serif"
SANS = "'Hanken Grotesk', 'Public Sans', 'Helvetica Neue', Arial, sans-serif"

# Bottom-to-top order; question text kept to ≤8 words per slab.
LAYERS = [  # (letter, name, question, aside)
    ("A", "Preprocessing", "did the corpus preserve the content?", "the frozen site-book snapshot"),
    ("B", "Index quality", "does the tree match the document?", "IDX-D / IDX-C / IDX-O"),
    ("C", "Retrieval", "did it read the right sections?", "the navigate-then-read loop"),
    ("D", "Answer", "is the answer right — and cited?", "grounded, correct, attributed"),
    ("E", "Operational", "cost, latency, reliability", "what it took to get there"),
]
LAYER_NAMES = {"A": "preprocessing", "B": "index quality", "C": "retrieval",
               "D": "answer", "E": "operational"}

# Layout
W, H = 1100, 900
SLAB_X, SLAB_W = 260, 760
SLAB_H, SLAB_GAP = 112, 16
STACK_TOP = 168
ARROW_X = 185

svg = []


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def text(x, y, s, size=15, fill=TEXT, family=SANS, weight=None, anchor=None,
         style=None, transform=None, spacing=None):
    attrs = f'x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-family="{family}"'
    if weight:
        attrs += f' font-weight="{weight}"'
    if anchor:
        attrs += f' text-anchor="{anchor}"'
    if style:
        attrs += f' font-style="{style}"'
    if transform:
        attrs += f' transform="{transform}"'
    if spacing:
        attrs += f' letter-spacing="{spacing}"'
    svg.append(f"<text {attrs}>{esc(s)}</text>")


def main():
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{SANS}">'
    )
    svg.append("<defs>")
    svg.append(
        f'<marker id="arr-up" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="9" markerHeight="9" orient="auto-start-reverse">'
        f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{COBALT}"/></marker>'
    )
    svg.append("</defs>")
    svg.append(f'<rect width="{W}" height="{H}" fill="{GROUND}"/>')

    # Header
    text(64, 62, "Five layers of blame", size=32, fill=INK, family=SERIF, weight="600")
    text(64, 92,
         "The rubric scores each layer separately, so a wrong answer gets blamed on the right one.",
         size=15, fill=TEXT)

    stack_bot = STACK_TOP + 5 * SLAB_H + 4 * SLAB_GAP

    # Rising arrow through all layers (failures propagate upward)
    svg.append(
        f'<line x1="{ARROW_X}" y1="{stack_bot + 6}" x2="{ARROW_X}" y2="{STACK_TOP - 14}" '
        f'stroke="{COBALT}" stroke-width="2.5" marker-end="url(#arr-up)"/>'
    )
    mid_y = (STACK_TOP + stack_bot) / 2
    text(ARROW_X - 16, mid_y, "where did the failure enter?", size=16, fill=COBALT,
         style="italic", anchor="middle", transform=f"rotate(-90 {ARROW_X - 16} {mid_y})")

    # Slabs, bottom (A) to top (E)
    for i, (letter, name, question, aside) in enumerate(LAYERS):
        y = stack_bot - (i + 1) * SLAB_H - i * SLAB_GAP
        hot = letter == HIGHLIGHT
        fill = PRIMARY if hot else GROUND
        stroke = PRIMARY if hot else INK
        main_col = GROUND if hot else INK
        sub_col = GROUND if hot else TEXT
        aside_col = "#EAD9CE" if hot else MUTED
        svg.append(
            f'<rect x="{SLAB_X}" y="{y}" width="{SLAB_W}" height="{SLAB_H}" rx="8" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="2.5"/>'
        )
        # Tick connecting the slab to the rising arrow
        svg.append(
            f'<line x1="{ARROW_X + 8}" y1="{y + SLAB_H/2}" x2="{SLAB_X}" y2="{y + SLAB_H/2}" '
            f'stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="2 5"/>'
        )
        # Letter (serif, large) + name + question
        text(SLAB_X + 52, y + SLAB_H / 2 + 17, letter, size=48, fill=main_col,
             family=SERIF, weight="600", anchor="middle")
        svg.append(
            f'<line x1="{SLAB_X + 96}" y1="{y + 22}" x2="{SLAB_X + 96}" y2="{y + SLAB_H - 22}" '
            f'stroke="{main_col}" stroke-width="1" opacity="0.5"/>'
        )
        text(SLAB_X + 122, y + 44, name.upper(), size=18, fill=main_col,
             weight="700", spacing="2.5")
        text(SLAB_X + 122, y + 76, f"“{question}”", size=19, fill=sub_col,
             family=SERIF, style="italic")
        text(SLAB_X + 122, y + 97, aside, size=13, fill=aside_col)

    # Upstream/downstream cues above and below the stack
    text(SLAB_X + SLAB_W, STACK_TOP - 14, "symptoms surface here", size=13.5,
         fill=MUTED, style="italic", anchor="end")
    text(SLAB_X + SLAB_W, stack_bot + 26, "root causes start here", size=13.5,
         fill=MUTED, style="italic", anchor="end")

    # Footer
    text(64, H - 36,
         f"Fig. V4 · generated by scripts/gen_fig_v4_rubric_stack.py · highlighted layer = "
         f"{HIGHLIGHT} ({LAYER_NAMES[HIGHLIGHT]}); set HIGHLIGHT to re-aim the figure",
         size=13, fill=MUTED)

    svg.append("</svg>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(svg))
    print(f"wrote {OUT.relative_to(ROOT)} (highlight={HIGHLIGHT})")


if __name__ == "__main__":
    main()

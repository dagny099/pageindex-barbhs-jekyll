#!/usr/bin/env python3
"""V1 — corpus pipeline flow (SVG).

Left-to-right: website source -> frozen corpus (SHA-pinned) -> PageIndex tree
generation -> raw results/ -> curated IDX-* variants. Dashed boundary boxes
mark the website repo (authoritative producer) vs this repo (consumer); the
corpus node is burnt orange because the frozen snapshot is the contract
between the two. Palette per reports/visual-asset-plan.md §1.

Writes reports/figures/v1-pipeline.svg. Deterministic; stdlib only.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports/figures/v1-pipeline.svg"

# Palette (visual-asset-plan.md §1.1)
GROUND = "#F4F0E8"
INK = "#1C3A55"
PRIMARY = "#C04818"
AMBER = "#F0A818"
COBALT = "#186090"
TEXT = "#2B2B2B"
MUTED = "#6B6B66"
CARD = "#FBF8F0"  # node fill: a hair lighter than ground, never white

SERIF = "Fraunces, Georgia, 'Times New Roman', serif"
SANS = "'Hanken Grotesk', 'Public Sans', 'Helvetica Neue', Arial, sans-serif"
MONO = "'SF Mono', Menlo, Consolas, monospace"

W, H = 1600, 600
BOX_Y, BOX_H = 260, 110
BOUND_Y, BOUND_H = 120, 320
MID_Y = BOX_Y + BOX_H / 2


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def node(svg, x, w, title, subs, fill=CARD, stroke=INK, tcolor=INK, scolor=MUTED,
         title_font=SANS, title_size=15.5):
    cx = x + w / 2
    svg.append(
        f'<rect x="{x}" y="{BOX_Y}" width="{w}" height="{BOX_H}" rx="10" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>'
    )
    ty = BOX_Y + 34 if len(subs) >= 2 else BOX_Y + 44
    svg.append(
        f'<text x="{cx}" y="{ty}" text-anchor="middle" font-family="{title_font}" '
        f'font-size="{title_size}" font-weight="600" fill="{tcolor}">{esc(title)}</text>'
    )
    for i, sub in enumerate(subs):
        svg.append(
            f'<text x="{cx}" y="{ty + 24 + i * 18}" text-anchor="middle" '
            f'font-size="12.5" fill="{scolor}">{esc(sub)}</text>'
        )


def arrow(svg, x1, x2, y, color=COBALT, width=2.5):
    svg.append(
        f'<line x1="{x1}" y1="{y}" x2="{x2 - 11}" y2="{y}" stroke="{color}" '
        f'stroke-width="{width}"/>'
    )
    svg.append(
        f'<polygon points="{x2},{y} {x2 - 12},{y - 6} {x2 - 12},{y + 6}" fill="{color}"/>'
    )


def main():
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{SANS}">',
        f'<rect width="{W}" height="{H}" fill="{GROUND}"/>',
        # Header
        f'<text x="40" y="46" font-family="{SERIF}" font-size="28" font-weight="600" '
        f'fill="{INK}">One-way pipeline: the corpus is consumed here, not produced</text>',
        f'<text x="40" y="72" font-size="14.5" fill="{TEXT}">website source → frozen '
        f'snapshot → PageIndex tree generation → raw results → curated index variants</text>',
    ]

    # Boundary: website repo (authoritative producer)
    svg.append(
        f'<rect x="40" y="{BOUND_Y}" width="290" height="{BOUND_H}" rx="12" fill="none" '
        f'stroke="{INK}" stroke-width="1.5" stroke-dasharray="8 6"/>'
    )
    svg.append(
        f'<text x="60" y="150" font-size="13" font-weight="600" letter-spacing="1" '
        f'fill="{INK}">WEBSITE REPO</text>'
    )
    svg.append(
        f'<text x="60" y="169" font-size="12" fill="{MUTED}">authoritative producer</text>'
    )
    svg.append(
        f'<text x="60" y="188" font-size="12" font-family="{MONO}" '
        f'fill="{MUTED}">dagny099.github.io</text>'
    )

    # Boundary: this repo (consumer)
    svg.append(
        f'<rect x="470" y="{BOUND_Y}" width="1090" height="{BOUND_H}" rx="12" fill="none" '
        f'stroke="{INK}" stroke-width="1.5" stroke-dasharray="8 6"/>'
    )
    svg.append(
        f'<text x="490" y="150" font-size="13" font-weight="600" letter-spacing="1" '
        f'fill="{INK}">THIS REPO</text>'
    )
    svg.append(f'<text x="490" y="169" font-size="12" fill="{MUTED}">consumer</text>')
    svg.append(
        f'<text x="490" y="188" font-size="12" font-family="{MONO}" '
        f'fill="{MUTED}">pageindex-website-experiment</text>'
    )

    # Nodes
    node(svg, 65, 240, "barbhs.com website source",
         ["26 documents", "build scripts · QC · normalization"])
    node(svg, 500, 250, "corpus/site-book-v1.md",
         ["frozen snapshot — SHA-pinned", "the contract between repos"],
         fill=PRIMARY, stroke=PRIMARY, tcolor=GROUND, scolor="#F6DFD2")
    node(svg, 800, 230, "PageIndex tree generation",
         ["vendor/PageIndex (submodule)", "IDX-D needs no LLM"],
         stroke=COBALT, tcolor=COBALT)
    node(svg, 1080, 190, "results/",
         ["raw run output", "(gitignored scratch)"], stroke=MUTED, tcolor=TEXT)
    node(svg, 1320, 210, "indexes/IDX-*",
         ["IDX-D · IDX-C · IDX-O", "curated + provenance.json"])

    # Arrows between nodes
    arrow(svg, 305, 500, MID_Y)   # crosses the repo boundary
    arrow(svg, 750, 800, MID_Y)
    arrow(svg, 1030, 1080, MID_Y)
    arrow(svg, 1270, 1320, MID_Y)

    # Edge annotation on the boundary-crossing arrow
    svg.append(
        f'<text x="402" y="{MID_Y + 34}" text-anchor="middle" font-family="{MONO}" '
        f'font-size="12.5" font-weight="600" fill="{PRIMARY}">provenance.json</text>'
    )
    svg.append(
        f'<text x="402" y="{MID_Y + 52}" text-anchor="middle" font-size="12" '
        f'fill="{PRIMARY}">pins commit + SHA256</text>'
    )
    svg.append(
        f'<text x="402" y="{MID_Y - 16}" text-anchor="middle" font-size="12" '
        f'fill="{MUTED}">re-sync (verbatim copy)</text>'
    )

    # Footer
    svg.append(
        f'<text x="40" y="{H - 30}" font-size="13" fill="{MUTED}">'
        f'Fig. V1 · generated by scripts/gen_fig_v1_pipeline.py · to change the corpus, '
        f'fix the pipeline in the website repo and re-sync — never edit corpus/ here '
        f'(see CLAUDE.md)</text>'
    )
    svg.append("</svg>")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(svg))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""V5 — the retriever's navigate-then-read tool loop, as a sequence diagram (SVG).

Hand-built SVG (no mermaid dependency). Three lifelines — Retriever LLM,
PageIndex tools, Corpus — showing the agentic loop PageIndex retrieval depends
on, with the two amber failure annotations from
reports/findings-retriever-prompt-revision.md (the title shortcut and the
fabricated tool call). The get_page_content step gets the burnt-orange
highlight: it is the step that separates real retrieval from theater.
Palette per reports/visual-asset-plan.md §1. Writes
reports/figures/v5-retrieval-loop.svg.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports/figures/v5-retrieval-loop.svg"

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
MONO = "'IBM Plex Mono', 'SF Mono', Menlo, Consolas, monospace"

# Layout
W, H = 1600, 880
MARGIN_L = 48
LX_RET, LX_TOOLS, LX_CORPUS = 560, 940, 1260  # lifeline x positions
LIFE_TOP, LIFE_BOT = 158, 782
NOTE_L, NOTE_R = MARGIN_L, 380  # left gutter for failure notes

svg = []


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def text(x, y, s, size=15, fill=TEXT, family=SANS, weight=None, anchor=None, style=None):
    attrs = f'x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-family="{family}"'
    if weight:
        attrs += f' font-weight="{weight}"'
    if anchor:
        attrs += f' text-anchor="{anchor}"'
    if style:
        attrs += f' font-style="{style}"'
    svg.append(f"<text {attrs}>{esc(s)}</text>")


def cross(cx, cy, r=6):
    """Amber ✗ drawn as two strokes (glyph-safe across SVG renderers)."""
    for dx1, dy1, dx2, dy2 in ((-r, -r, r, r), (-r, r, r, -r)):
        svg.append(
            f'<line x1="{cx+dx1}" y1="{cy+dy1}" x2="{cx+dx2}" y2="{cy+dy2}" '
            f'stroke="{AMBER}" stroke-width="3.5" stroke-linecap="round"/>'
        )


def arrow(x1, x2, y, label, color=INK, dashed=False, mono=False, width=2, label_size=15):
    """Horizontal message arrow with its label centered above."""
    dash = ' stroke-dasharray="7 5"' if dashed else ""
    svg.append(
        f'<line x1="{x1}" y1="{y}" x2="{x2}" y2="{y}" stroke="{color}" '
        f'stroke-width="{width}"{dash} marker-end="url(#arr-{color.lstrip("#")})"/>'
    )
    text((x1 + x2) / 2, y - 9, label, size=label_size, fill=color,
         family=MONO if mono else SANS, anchor="middle",
         weight="600" if color == PRIMARY else None)


def main():
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{SANS}">'
    )
    # Arrowhead markers, one per color used
    svg.append("<defs>")
    for c in (INK, COBALT, PRIMARY, MUTED, AMBER):
        svg.append(
            f'<marker id="arr-{c.lstrip("#")}" viewBox="0 0 10 10" refX="9" refY="5" '
            f'markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
            f'<path d="M 0 0 L 10 5 L 0 10 z" fill="{c}"/></marker>'
        )
    svg.append("</defs>")
    svg.append(f'<rect width="{W}" height="{H}" fill="{GROUND}"/>')

    # Header
    text(MARGIN_L, 54, "Navigate, then read — the retriever's tool loop",
         size=30, fill=INK, family=SERIF, weight="600")
    text(MARGIN_L, 84,
         "PageIndex retrieval is agentic: the LLM must walk the tree, then pay to read. "
         "Weak models break the loop in two places.",
         size=15, fill=TEXT)

    # Participant boxes + lifelines
    participants = [
        (LX_RET, "Retriever LLM", INK, GROUND),
        (LX_TOOLS, "PageIndex tools", COBALT, GROUND),
        (LX_CORPUS, "Corpus", GROUND, INK),
    ]
    for x, name, fill, tcol in participants:
        bw = 200
        stroke = f' stroke="{INK}" stroke-width="2"' if fill == GROUND else ""
        svg.append(f'<rect x="{x - bw/2}" y="112" width="{bw}" height="46" rx="6" fill="{fill}"{stroke}/>')
        text(x, 141, name, size=17, fill=tcol, weight="600", anchor="middle")
        svg.append(
            f'<line x1="{x}" y1="{LIFE_TOP}" x2="{x}" y2="{LIFE_BOT}" '
            f'stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="3 5"/>'
        )
        svg.append(f'<line x1="{x-9}" y1="{LIFE_BOT}" x2="{x+9}" y2="{LIFE_BOT}" stroke="{MUTED}" stroke-width="1.5"/>')

    # Activation bars (tools active during each call; corpus during the read)
    for y1, y2 in ((202, 254), (302, 354), (518, 642)):
        svg.append(f'<rect x="{LX_TOOLS-6}" y="{y1}" width="12" height="{y2-y1}" fill="{COBALT}" opacity="0.25"/>')
    svg.append(f'<rect x="{LX_CORPUS-6}" y="548" width="12" height="60" fill="{INK}" opacity="0.25"/>')

    # -- Step 1: get_document() --------------------------------------------
    arrow(LX_RET, LX_TOOLS, 212, "get_document()", color=INK, mono=True)
    arrow(LX_TOOLS, LX_RET, 248, "line count · status: ok", color=MUTED, dashed=True, label_size=14)

    # -- Step 2: get_document_structure() ----------------------------------
    arrow(LX_RET, LX_TOOLS, 312, "get_document_structure()", color=INK, mono=True)
    arrow(LX_TOOLS, LX_RET, 348, "tree of section titles + line numbers", color=MUTED, dashed=True, label_size=14)
    text((LX_RET + LX_TOOLS) / 2, 368, "titles only — no body text",
         size=13.5, fill=COBALT, anchor="middle", style="italic")

    # -- Step 3: reasoning over the tree (self box) -------------------------
    rb_w, rb_y, rb_h = 330, 402, 56
    svg.append(
        f'<rect x="{LX_RET - rb_w/2}" y="{rb_y}" width="{rb_w}" height="{rb_h}" rx="6" '
        f'fill="{GROUND}" stroke="{COBALT}" stroke-width="2"/>'
    )
    text(LX_RET, rb_y + 24, "reasons over the tree", size=15, fill=TEXT, weight="600", anchor="middle")
    text(LX_RET, rb_y + 44, "picks sections + tight line ranges", size=13.5, fill=MUTED, anchor="middle")

    # -- Step 4: get_page_content — THE step (burnt-orange highlight) -------
    arrow(LX_RET, LX_TOOLS, 528, 'get_page_content(pages="2403-2476")',
          color=PRIMARY, mono=True, width=3)
    arrow(LX_TOOLS, LX_CORPUS, 564, "read lines 2403–2476", color=COBALT, label_size=14)
    arrow(LX_CORPUS, LX_TOOLS, 600, "raw text", color=MUTED, dashed=True, label_size=14)
    arrow(LX_TOOLS, LX_RET, 636, "body text of the chosen sections",
          color=PRIMARY, dashed=True, label_size=14)

    # Right-gutter emphasis note for the orange step
    for i, line in enumerate(("the step that separates", "real retrieval", "from theater")):
        text(1310, 560 + i * 20, line, size=14.5, fill=PRIMARY, style="italic")

    # -- Step 5: the answer (self box) ---------------------------------------
    ab_w, ab_y, ab_h = 330, 684, 56
    svg.append(
        f'<rect x="{LX_RET - ab_w/2}" y="{ab_y}" width="{ab_w}" height="{ab_h}" rx="6" '
        f'fill="{INK}"/>'
    )
    text(LX_RET, ab_y + 24, "answers the question", size=15, fill=GROUND, weight="600", anchor="middle")
    text(LX_RET, ab_y + 44, "grounded in fetched text · cites pages", size=13.5, fill=GROUND, anchor="middle")

    # -- Failure annotation 1: the title shortcut (amber) --------------------
    f1_y, f1_h = 388, 84
    svg.append(
        f'<rect x="{NOTE_L}" y="{f1_y}" width="{NOTE_R - NOTE_L}" height="{f1_h}" rx="6" '
        f'fill="{GROUND}" stroke="{AMBER}" stroke-width="2.5"/>'
    )
    cross(NOTE_L + 22, f1_y + 20)
    text(NOTE_L + 40, f1_y + 26, "the title shortcut", size=15, fill=TEXT, weight="700")
    text(NOTE_L + 14, f1_y + 48, "answers from the titles alone —", size=13.5, fill=TEXT)
    text(NOTE_L + 14, f1_y + 66, "never reads the body text", size=13.5, fill=TEXT)
    svg.append(
        f'<line x1="{NOTE_R}" y1="{f1_y + f1_h/2}" x2="{LX_RET - rb_w/2 - 4}" y2="{rb_y + rb_h/2}" '
        f'stroke="{AMBER}" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#arr-{AMBER.lstrip("#")})"/>'
    )

    # -- Failure annotation 2: the fabricated call (amber) -------------------
    f2_y, f2_h = 500, 142
    svg.append(
        f'<rect x="{NOTE_L}" y="{f2_y}" width="{NOTE_R - NOTE_L}" height="{f2_h}" rx="6" '
        f'fill="{GROUND}" stroke="{AMBER}" stroke-width="2.5"/>'
    )
    cross(NOTE_L + 22, f2_y + 20)
    text(NOTE_L + 40, f2_y + 26, "the fabricated call", size=15, fill=TEXT, weight="700")
    text(NOTE_L + 14, f2_y + 48, "narrates the call in prose — never makes it:", size=13.5, fill=TEXT)
    text(NOTE_L + 14, f2_y + 72, '"I will call get_page_content(', size=12.5, fill=MUTED, family=MONO)
    text(NOTE_L + 14, f2_y + 90, ' pages=120-160)… Here\'s the output:"', size=12.5, fill=MUTED, family=MONO)
    text(NOTE_L + 14, f2_y + 118, "content_tokens = 0", size=13, fill=PRIMARY, family=MONO, weight="600")
    svg.append(
        f'<line x1="{NOTE_R}" y1="{f2_y + 42}" x2="{LX_RET - 8}" y2="528" '
        f'stroke="{AMBER}" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#arr-{AMBER.lstrip("#")})"/>'
    )

    # Footer
    text(MARGIN_L, H - 34,
         "Fig. V5 · generated by scripts/gen_fig_v5_retrieval_loop.py · loop and failure modes per "
         "reports/findings-retriever-prompt-revision.md (llama3.1:8b, original prompt)",
         size=13, fill=MUTED)

    svg.append("</svg>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(svg))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

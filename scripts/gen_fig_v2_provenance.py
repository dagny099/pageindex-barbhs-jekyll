#!/usr/bin/env python3
"""V2 — two-repo provenance architecture (SVG).

Two columns: the producer repo (dagny099.github.io — build scripts, QC,
normalization) and this repo (harness, indexes, evaluations, runs). The
re-sync arrow carries the three-step procedure; a dashed return arrow says
corpus fixes go back to the pipeline; an amber note warns that a corpus
change strands existing indexes (STALE.md). Orange only on provenance.json.
Palette per reports/visual-asset-plan.md §1.

Writes reports/figures/v2-provenance.svg. Deterministic; stdlib only.
"""

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "reports/figures/v2-provenance.svg"

# Palette (visual-asset-plan.md §1.1)
GROUND = "#F4F0E8"
INK = "#1C3A55"
PRIMARY = "#C04818"
AMBER = "#F0A818"
COBALT = "#186090"
TEXT = "#2B2B2B"
MUTED = "#6B6B66"
CARD = "#FBF8F0"

SERIF = "Fraunces, Georgia, 'Times New Roman', serif"
SANS = "'Hanken Grotesk', 'Public Sans', 'Helvetica Neue', Arial, sans-serif"
MONO = "'SF Mono', Menlo, Consolas, monospace"

W, H = 1400, 800

LBOX = (60, 140, 560, 480)    # x, y, w, h — producer
RBOX = (780, 140, 560, 480)   # consumer
ITEM_H = 60


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def item(svg, bx, y, title, sub, stroke=COBALT, title_font=MONO):
    x, w = bx + 40, 480
    svg.append(
        f'<rect x="{x}" y="{y}" width="{w}" height="{ITEM_H}" rx="8" '
        f'fill="{CARD}" stroke="{stroke}" stroke-width="1.8"/>'
    )
    svg.append(
        f'<text x="{x + 18}" y="{y + 26}" font-family="{title_font}" font-size="14" '
        f'font-weight="600" fill="{INK}">{esc(title)}</text>'
    )
    svg.append(
        f'<text x="{x + 18}" y="{y + 46}" font-size="12.5" fill="{MUTED}">{esc(sub)}</text>'
    )


def main():
    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{SANS}">',
        f'<rect width="{W}" height="{H}" fill="{GROUND}"/>',
        # Header
        f'<text x="40" y="46" font-family="{SERIF}" font-size="28" font-weight="600" '
        f'fill="{INK}">Two repos, one contract: who owns the corpus</text>',
        f'<text x="40" y="72" font-size="14.5" fill="{TEXT}">the website repo builds '
        f'and validates the corpus; this repo consumes a frozen, SHA-pinned snapshot '
        f'of it</text>',
    ]

    # ---- Left column: producer -------------------------------------------
    lx, ly, lw, lh = LBOX
    svg.append(
        f'<rect x="{lx}" y="{ly}" width="{lw}" height="{lh}" rx="12" fill="none" '
        f'stroke="{INK}" stroke-width="2"/>'
    )
    svg.append(
        f'<text x="{lx + 40}" y="{ly + 42}" font-family="{MONO}" font-size="18" '
        f'font-weight="600" fill="{INK}">dagny099.github.io</text>'
    )
    svg.append(
        f'<text x="{lx + 40}" y="{ly + 66}" font-size="13" letter-spacing="1" '
        f'font-weight="600" fill="{COBALT}">AUTHORITATIVE PRODUCER</text>'
    )
    svg.append(
        f'<text x="{lx + 40}" y="{ly + 86}" font-size="12.5" font-family="{MONO}" '
        f'fill="{MUTED}">experiments/pageindex/</text>'
    )
    item(svg, lx, ly + 110, "build + validate scripts", "selection config · corpus stitching")
    item(svg, lx, ly + 190, "normalization tests", "heading fidelity, structure checks")
    item(svg, lx, ly + 270, "QC + normalization reports", "the corpus paper trail lives here")
    svg.append(
        f'<text x="{lx + 40}" y="{ly + 420}" font-size="12.5" fill="{MUTED}" '
        f'font-style="italic">the original website source stays authoritative</text>'
    )
    svg.append(
        f'<text x="{lx + 40}" y="{ly + 438}" font-size="12.5" fill="{MUTED}" '
        f'font-style="italic">over the corpus — always</text>'
    )

    # ---- Right column: consumer ------------------------------------------
    rx, ry, rw, rh = RBOX
    svg.append(
        f'<rect x="{rx}" y="{ry}" width="{rw}" height="{rh}" rx="12" fill="none" '
        f'stroke="{INK}" stroke-width="2"/>'
    )
    svg.append(
        f'<text x="{rx + 40}" y="{ry + 42}" font-family="{MONO}" font-size="18" '
        f'font-weight="600" fill="{INK}">pageindex-website-experiment</text>'
    )
    svg.append(
        f'<text x="{rx + 40}" y="{ry + 66}" font-size="13" letter-spacing="1" '
        f'font-weight="600" fill="{COBALT}">CONSUMER (THIS REPO)</text>'
    )
    svg.append(
        f'<text x="{rx + 40}" y="{ry + 86}" font-size="12.5" fill="{MUTED}">'
        f'experiment harness · never edits the corpus</text>'
    )
    item(svg, rx, ry + 110, "corpus/site-book-v1/", "frozen snapshot — consumed, not produced")
    # provenance.json badge — the only orange in the figure
    bx, by, bw, bh = rx + 60, ry + 178, 440, 36
    svg.append(
        f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="8" '
        f'fill="{PRIMARY}"/>'
    )
    svg.append(
        f'<text x="{bx + bw / 2}" y="{by + 23}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="13.5" font-weight="600" fill="{GROUND}">'
        f'provenance.json — pins website_commit + SHA256</text>'
    )
    item(svg, rx, ry + 240, "indexes/IDX-D · IDX-C · IDX-O",
         "each carries its own provenance vs the corpus")
    item(svg, rx, ry + 320, "evaluations/ · runs/ · scripts/",
         "14-question set · retrieval harness · run log")

    # ---- Re-sync arrow (left -> right) ------------------------------------
    ay = 320
    gx1, gx2 = lx + lw, rx  # 620 .. 780
    mid = (gx1 + gx2) / 2
    svg.append(
        f'<text x="{mid}" y="{ay - 88}" text-anchor="middle" font-size="14" '
        f'font-weight="600" letter-spacing="1" fill="{INK}">RE-SYNC</text>'
    )
    for i, step in enumerate(["1 · copy verbatim", "2 · recompute SHA256", "3 · update provenance.json"]):
        svg.append(
            f'<text x="{mid}" y="{ay - 64 + i * 18}" text-anchor="middle" '
            f'font-size="12" fill="{TEXT}">{esc(step)}</text>'
        )
    svg.append(
        f'<line x1="{gx1}" y1="{ay}" x2="{gx2 - 12}" y2="{ay}" stroke="{COBALT}" '
        f'stroke-width="3"/>'
    )
    svg.append(
        f'<polygon points="{gx2},{ay} {gx2 - 14},{ay - 7} {gx2 - 14},{ay + 7}" '
        f'fill="{COBALT}"/>'
    )

    # ---- Return arrow (right -> left, dashed) ------------------------------
    ry2 = 520
    svg.append(
        f'<line x1="{gx2}" y1="{ry2}" x2="{gx1 + 12}" y2="{ry2}" stroke="{MUTED}" '
        f'stroke-width="2" stroke-dasharray="7 6"/>'
    )
    svg.append(
        f'<polygon points="{gx1},{ry2} {gx1 + 14},{ry2 - 7} {gx1 + 14},{ry2 + 7}" '
        f'fill="{MUTED}"/>'
    )
    for i, line in enumerate(["corpus fixes go back", "to the pipeline —", "never edited here"]):
        svg.append(
            f'<text x="{mid}" y="{ry2 + 24 + i * 17}" text-anchor="middle" '
            f'font-size="12.5" font-style="italic" fill="{MUTED}">{esc(line)}</text>'
        )

    # ---- Amber staleness warning under the consumer box --------------------
    wy = ry + rh + 34
    svg.append(
        f'<rect x="{rx}" y="{wy}" width="{rw}" height="{ITEM_H}" rx="8" '
        f'fill="{AMBER}" stroke="{INK}" stroke-width="1.5"/>'
    )
    svg.append(
        f'<text x="{rx + rw / 2}" y="{wy + 26}" text-anchor="middle" font-size="14.5" '
        f'font-weight="600" fill="{TEXT}">corpus change ⇒ existing indexes stale</text>'
    )
    svg.append(
        f'<text x="{rx + rw / 2}" y="{wy + 46}" text-anchor="middle" font-size="12.5" '
        f'fill="{TEXT}">regenerate affected IDX-* and mark stale ones (STALE.md)</text>'
    )

    # Footer
    svg.append(
        f'<text x="40" y="{H - 28}" font-size="13" fill="{MUTED}">'
        f'Fig. V2 · generated by scripts/gen_fig_v2_provenance.py · re-sync procedure '
        f'in CLAUDE.md · snapshot pins in corpus/site-book-v1/provenance.json</text>'
    )
    svg.append("</svg>")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(svg))
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

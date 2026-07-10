#!/usr/bin/env python3
"""V8 — IDX-D vs IDX-C node anatomy: the same node, two signages (SVG).

Locates the same node (by exact title, default "Evaluation Harness" — the
Poolula evaluation-harness section) in indexes/IDX-D/index.json and
indexes/IDX-C/index.json and draws two side-by-side index cards: IDX-D carries
title / node_id / line_num with an empty dashed summary slot; IDX-C carries the
same fields plus its actual generated summary (truncated to ~40 words).
All values are pulled from the JSON — nothing invented.
Writes reports/figures/v8-node-anatomy.svg. Palette per
reports/visual-asset-plan.md §1.
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IDX_D = ROOT / "indexes/IDX-D/index.json"
IDX_C = ROOT / "indexes/IDX-C/index.json"
OUT = ROOT / "reports/figures/v8-node-anatomy.svg"

NODE_TITLE = "Evaluation Harness"
SUMMARY_WORDS = 40

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

# Layout
W, H = 1400, 700
CARD_W, CARD_H, CARD_Y = 540, 460, 122
LEFT_X, RIGHT_X = 70, W - 70 - CARD_W
PAD = 24


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def find_node(doc, title):
    """Return (node, path-of-parent-titles) for the first exact-title match."""
    def walk(n, path):
        if n.get("title", "").strip() == title:
            return n, path
        for c in n.get("nodes", []):
            hit = walk(c, path + [n["title"].strip()])
            if hit:
                return hit
    for top in doc["structure"]:
        hit = walk(top, [])
        if hit:
            return hit
    raise SystemExit(f"node titled {title!r} not found")


def wrap_mono(text: str, max_chars: int):
    lines, cur = [], ""
    for w in text.split():
        cand = f"{cur} {w}".strip()
        if len(cand) <= max_chars:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            while len(w) > max_chars:
                lines.append(w[:max_chars])
                w = w[max_chars:]
            cur = w
    if cur:
        lines.append(cur)
    return lines


def field(svg, x, y, label, value):
    svg.append(
        f'<text x="{x}" y="{y}" font-size="11" letter-spacing="1.5" '
        f'fill="{MUTED}">{esc(label.upper())}</text>'
    )
    svg.append(
        f'<text x="{x}" y="{y + 21}" font-family="{MONO}" font-size="15" '
        f'font-weight="600" fill="{TEXT}">{esc(value)}</text>'
    )


def card_shell(svg, x, band_fill, band_label, band_sub):
    svg.append(
        f'<rect x="{x}" y="{CARD_Y}" width="{CARD_W}" height="{CARD_H}" rx="10" '
        f'fill="{CARD}" stroke="{INK}" stroke-width="1.5"/>'
    )
    svg.append(
        f'<path d="M {x + 10} {CARD_Y} h {CARD_W - 20} a 10 10 0 0 1 10 10 v 34 '
        f'h -{CARD_W} v -34 a 10 10 0 0 1 10 -10 Z" fill="{band_fill}"/>'
    )
    svg.append(
        f'<text x="{x + PAD}" y="{CARD_Y + 29}" font-size="17" font-weight="600" '
        f'fill="{GROUND}">{esc(band_label)}</text>'
    )
    svg.append(
        f'<text x="{x + CARD_W - PAD}" y="{CARD_Y + 29}" font-size="13" '
        f'fill="{GROUND}" text-anchor="end" opacity="0.85">{esc(band_sub)}</text>'
    )


def main():
    doc_d = json.loads(IDX_D.read_text())
    doc_c = json.loads(IDX_C.read_text())
    node_d, path_d = find_node(doc_d, NODE_TITLE)
    node_c, _ = find_node(doc_c, NODE_TITLE)
    assert node_d["node_id"] == node_c["node_id"] and node_d["line_num"] == node_c["line_num"], (
        "IDX-D and IDX-C disagree on the node — pick another"
    )

    summary_full = " ".join(node_c["summary"].split())
    words = summary_full.split()
    shown = " ".join(words[:SUMMARY_WORDS]) + (" …" if len(words) > SUMMARY_WORDS else "")
    verbatim = node_c["summary"].strip() == node_c.get("text", "").strip()
    breadcrumb = " › ".join(path_d[1:])  # drop the document root

    svg = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
        f'viewBox="0 0 {W} {H}" font-family="{SANS}">',
        f'<rect width="{W}" height="{H}" fill="{GROUND}"/>',
        # Header
        f'<text x="{LEFT_X}" y="46" font-family="{SERIF}" font-size="30" font-weight="600" '
        f'fill="{INK}">Anatomy of a Node — IDX-D vs IDX-C</text>',
        f'<text x="{LEFT_X}" y="73" font-size="15" fill="{TEXT}">One node, both indexes: '
        f'“{esc(node_d["title"])}” · node {esc(node_d["node_id"])} · '
        f'line {node_d["line_num"]} · {esc(breadcrumb)}</text>',
        f'<text x="{LEFT_X}" y="95" font-size="15" fill="{MUTED}">The hierarchy is identical. '
        f'What differs is what the node carries — what a navigator can read before paying '
        f'to fetch the text.</text>',
    ]

    # ---- Left card: IDX-D
    card_shell(svg, LEFT_X, INK, "IDX-D", "deterministic · Markdown headings, no LLM")
    fx, fy = LEFT_X + PAD, CARD_Y + 82
    field(svg, fx, fy, "title", node_d["title"])
    field(svg, fx, fy + 56, "node_id", node_d["node_id"])
    field(svg, fx + 200, fy + 56, "line_num", str(node_d["line_num"]))
    # empty summary slot
    sy = fy + 118
    slot_h = CARD_Y + CARD_H - PAD - sy - 18
    svg.append(
        f'<text x="{fx}" y="{sy}" font-size="11" letter-spacing="1.5" '
        f'fill="{MUTED}">SUMMARY</text>'
    )
    svg.append(
        f'<rect x="{fx}" y="{sy + 10}" width="{CARD_W - 2 * PAD}" height="{slot_h}" rx="6" '
        f'fill="none" stroke="{MUTED}" stroke-width="1.5" stroke-dasharray="7 5"/>'
    )
    cx = LEFT_X + CARD_W / 2
    cy = sy + 10 + slot_h / 2
    svg.append(
        f'<text x="{cx}" y="{cy - 4}" font-size="14" font-style="italic" fill="{MUTED}" '
        f'text-anchor="middle">no summary field —</text>'
    )
    svg.append(
        f'<text x="{cx}" y="{cy + 16}" font-size="14" font-style="italic" fill="{MUTED}" '
        f'text-anchor="middle">the title is all the signage there is</text>'
    )

    # ---- Right card: IDX-C
    card_shell(svg, RIGHT_X, COBALT, "IDX-C", "gpt-4o · adds generated summaries")
    fx = RIGHT_X + PAD
    field(svg, fx, fy, "title", node_c["title"])
    field(svg, fx, fy + 56, "node_id", node_c["node_id"])
    field(svg, fx + 200, fy + 56, "line_num", str(node_c["line_num"]))
    svg.append(
        f'<text x="{fx}" y="{sy}" font-size="11" letter-spacing="1.5" '
        f'fill="{MUTED}">SUMMARY</text>'
    )
    svg.append(
        f'<rect x="{fx}" y="{sy + 10}" width="{CARD_W - 2 * PAD}" height="{slot_h}" rx="6" '
        f'fill="none" stroke="{COBALT}" stroke-width="1.5"/>'
    )
    tx, ty = fx + 14, sy + 10 + 22
    max_chars = int((CARD_W - 2 * PAD - 28) / (12 * 0.602))
    for line in wrap_mono(shown, max_chars):
        svg.append(
            f'<text x="{tx}" y="{ty}" font-family="{MONO}" font-size="12" '
            f'fill="{COBALT}">{esc(line)}</text>'
        )
        ty += 17
    note = f"first {min(SUMMARY_WORDS, len(words))} of {len(words)} words"
    if verbatim:
        note += " — for this leaf, the generated summary reproduces the node text verbatim"
    svg.append(
        f'<text x="{fx}" y="{sy + 10 + slot_h + 16}" font-size="11" font-style="italic" '
        f'fill="{MUTED}">{esc(note)}</text>'
    )
    if doc_c.get("doc_description"):
        svg.append(
            f'<text x="{fx}" y="{CARD_Y + CARD_H + 26}" font-size="12" fill="{MUTED}">'
            f'+ IDX-C also carries a document-level doc_description; IDX-D has none.</text>'
        )

    # ---- Amber annotation between the cards
    mid = W / 2
    svg.append(
        f'<text x="{mid}" y="330" font-family="{SERIF}" font-size="21" font-style="italic" '
        f'fill="{AMBER}" text-anchor="middle">same map —</text>'
    )
    svg.append(
        f'<text x="{mid}" y="357" font-family="{SERIF}" font-size="21" font-style="italic" '
        f'fill="{AMBER}" text-anchor="middle">different signage</text>'
    )
    ay = 384
    x1, x2 = LEFT_X + CARD_W + 14, RIGHT_X - 14
    svg.append(
        f'<line x1="{x1 + 10}" y1="{ay}" x2="{x2 - 10}" y2="{ay}" stroke="{AMBER}" '
        f'stroke-width="2"/>'
    )
    svg.append(f'<path d="M {x1} {ay} l 11 -6 v 12 Z" fill="{AMBER}"/>')
    svg.append(f'<path d="M {x2} {ay} l -11 -6 v 12 Z" fill="{AMBER}"/>')

    # Footer
    svg.append(
        f'<text x="{LEFT_X}" y="{H - 30}" font-size="13" fill="{MUTED}">'
        f'Fig. V8 · generated by scripts/gen_fig_v8_node_anatomy.py from '
        f'indexes/IDX-D/index.json + indexes/IDX-C/index.json · all field values verbatim '
        f'from the JSON</text>'
    )
    svg.append("</svg>")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(svg))
    print(
        f"wrote {OUT.relative_to(ROOT)}  (node {node_d['node_id']} “{node_d['title']}”, "
        f"line {node_d['line_num']}, summary {len(words)} words, verbatim={verbatim})"
    )


if __name__ == "__main__":
    main()

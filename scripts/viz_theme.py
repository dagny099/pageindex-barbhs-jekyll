#!/usr/bin/env python3
"""
viz_theme.py — the repo's brand palette + an Altair theme, in one place.

Notebooks do `from viz_theme import PALETTE, register; register()` so every chart
matches the figures in reports/ (burnt-orange lead on a warm cream ground). The
palette tokens are the ones defined in reports/visual-asset-plan.md and used across
reports/figures/*.svg — this module is the single programmatic source of them.

COLOR DISCIPLINE (validated with the dataviz skill's validate_palette.js)
-------------------------------------------------------------------------
- CATEGORICAL = [primary(burnt-orange), cobalt] ONLY. That pair PASSES every check
  on the cream surface (lightness band, chroma, CVD ΔE 17.7, normal ΔE 27.6,
  contrast). The other brand tokens (amber, ink/navy) FAIL categorical use (too
  light / reads gray), so they are for accents and linework, never series fills.
  Need >2 categories? Facet (small multiples) or use magnitude-on-axis with a
  single hue — never invent unvalidated hues.
- SEQUENTIAL (heatmaps/ramps) = one hue, light→dark orange.
- Charts commit to the single cream LIGHT surface on purpose (matches reports/
  figures), so they render on the validated surface regardless of the viewer's
  light/dark mode.
"""

from __future__ import annotations

# --- Brand tokens (reports/visual-asset-plan.md §1.1) --------------------------
PALETTE = {
    "ground": "#F4F0E8",       # warm cream background (never pure white)
    "ink": "#1C3A55",          # deep navy — linework / titles
    "primary": "#C04818",      # burnt orange — the warm lead / "the answer"
    "amber": "#F0A818",        # spark accent (NOT a categorical series color)
    "cobalt": "#186090",       # cool counterweight / links
    "text": "#2B2B2B",         # charcoal body text
    "muted": "#6B6B66",        # metadata / de-emphasized
    "grid": "#E4DDCC",         # recessive warm gridline
    "ground_dark": "#0E0E12",  # dark-mode ground (reference only)
}

# Validated categorical order: warm lead first, cool balance second.
CATEGORICAL = [PALETTE["primary"], PALETTE["cobalt"]]

# Sequential ramp for heatmaps (cream-tint -> burnt orange -> deep), light→dark.
SEQUENTIAL = ["#F6EBDE", "#E8A874", "#C04818", "#7A2D0F"]

FONT = "Hanken Grotesk, Inter, -apple-system, Segoe UI, Helvetica, Arial, sans-serif"

THEME_NAME = "pageindex-brand"


def theme_config() -> dict:
    """The Vega-Lite config dict (Altair ThemeConfig-shaped)."""
    p = PALETTE
    return {
        "config": {
            "background": p["ground"],
            "view": {"stroke": "transparent", "continuousWidth": 480, "continuousHeight": 300},
            "font": FONT,
            "title": {"color": p["ink"], "fontSize": 15, "fontWeight": 600,
                      "anchor": "start", "subtitleColor": p["muted"]},
            "axis": {"labelColor": p["text"], "titleColor": p["ink"],
                     "gridColor": p["grid"], "gridOpacity": 0.9,
                     "domainColor": p["muted"], "tickColor": p["muted"],
                     "labelFontSize": 11, "titleFontSize": 12, "labelFont": FONT,
                     "titleFont": FONT, "titleFontWeight": 600},
            "legend": {"labelColor": p["text"], "titleColor": p["ink"],
                       "labelFont": FONT, "titleFont": FONT, "titleFontWeight": 600},
            "header": {"labelColor": p["ink"], "labelFont": FONT, "labelFontWeight": 600,
                       "titleColor": p["ink"]},
            "range": {"category": CATEGORICAL, "heatmap": SEQUENTIAL, "ramp": SEQUENTIAL,
                      "ordinal": SEQUENTIAL},
            # single-series defaults: burnt-orange, 4px rounded data-end
            "bar": {"fill": p["primary"], "cornerRadiusEnd": 4},
            "mark": {"color": p["primary"]},
            "line": {"color": p["primary"], "strokeWidth": 2},
            "point": {"filled": True, "size": 80, "fill": p["primary"]},
            "rule": {"color": p["muted"]},
            "text": {"color": p["text"], "font": FONT},
        }
    }


def register(enable: bool = True) -> str:
    """Register (and by default enable) the brand Altair theme. Returns its name.
    Idempotent — safe to call in every notebook's setup cell."""
    import altair as alt

    @alt.theme.register(THEME_NAME, enable=enable)
    def _brand():
        return theme_config()

    if enable:
        alt.theme.enable(THEME_NAME)
    return THEME_NAME


def _self_test() -> None:
    expected = {"ground", "ink", "primary", "amber", "cobalt", "text", "muted", "grid"}
    missing = expected - PALETTE.keys()
    assert not missing, f"PALETTE missing keys: {missing}"
    assert all(v.startswith("#") and len(v) == 7 for v in PALETTE.values()), "hex tokens malformed"
    assert CATEGORICAL == ["#C04818", "#186090"], CATEGORICAL
    cfg = theme_config()["config"]
    assert cfg["background"] == PALETTE["ground"]
    assert cfg["range"]["category"] == CATEGORICAL
    try:
        import altair as alt  # noqa
        name = register()
        assert name == THEME_NAME
        assert alt.theme.active == THEME_NAME, alt.theme.active
        print("viz_theme self-test OK (altair theme registered & enabled)")
    except ImportError:
        print("viz_theme self-test OK (palette only; altair not installed)")


if __name__ == "__main__":
    _self_test()

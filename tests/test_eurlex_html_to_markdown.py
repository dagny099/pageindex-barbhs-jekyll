"""Tests for eurlex_html_to_markdown.py — EUR-Lex ELI XHTML -> Markdown twin.

The pure conversion test runs anywhere. The GDPR test needs the source HTML and
skips cleanly if it is missing.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import eurlex_html_to_markdown as E  # noqa: E402

GDPR_HTML = ROOT / "sources" / "gdpr-2016-679" / "gdpr.html"


def test_self_test_passes():
    E.self_test()  # raises SystemExit on failure


def test_conversion_is_deterministic_and_nests_by_structure():
    html = """
    <p class="oj-normal">preamble.</p>
    <p class="oj-ti-section-1"><span>CHAPTER I</span></p>
    <div class="eli-title"><p class="oj-ti-section-2">General</p></div>
    <p class="oj-ti-art">Article 1</p>
    <div class="eli-title"><p class="oj-sti-art">Scope</p></div>
    <p class="oj-ti-section-1"><span>Section 1</span></p>
    <div class="eli-title"><p class="oj-ti-section-2">Sub</p></div>
    <p class="oj-ti-art">Article 2</p>
    <div class="eli-title"><p class="oj-sti-art">More</p></div>
    """
    md = E.html_to_markdown(html)
    assert md == E.html_to_markdown(html)  # deterministic
    heads = [l for l in md.splitlines() if l.startswith("#")]
    # article directly under chapter is ##, article under a section is ###
    assert "## Article 1 — Scope" in heads
    assert "### Article 2 — More" in heads
    assert heads[0] == "# " + E.PREAMBLE_TITLE


def test_gdpr_structure_mirrors_the_act(tmp_path):
    if not GDPR_HTML.is_file():
        import pytest
        pytest.skip("gdpr.html not available")
    md = E.html_to_markdown(GDPR_HTML.read_text(encoding="utf-8"))
    heads = [l for l in md.splitlines() if re.match(r"#{1,6} ", l)]
    arts = sorted(int(re.search(r"Article (\d+)", h).group(1)) for h in heads if "Article" in h)
    assert arts == list(range(1, 100)), "99 articles, contiguous"
    assert sum("Chapter" in h for h in heads) == 11
    assert sum(h.startswith("## Section") for h in heads) == 15
    assert sum(E.PREAMBLE_TITLE in h for h in heads) == 1
    assert len(heads) == 126  # parity with IDX-PDF-textheadings-gdpr

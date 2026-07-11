"""Tests for the paper-book-v1 producer and validator.

Builds the corpus into a temp directory from the frozen PDF, so these tests
require sources/paper-2009/ and the pinned PyMuPDF version but never touch the
committed corpus.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / "scripts" / "build_paper_book.py"
VALIDATE = ROOT / "scripts" / "validate_paper_book.py"
PDF = ROOT / "sources" / "paper-2009" / "EhingerHidalgoTorralbaOliva_VisCog2009.pdf"

# The producer needs PyMuPDF, which lives in the project venv; pytest itself
# may run under a different interpreter.
VENV_PY = ROOT / ".venv" / "bin" / "python"
PY = str(VENV_PY) if VENV_PY.exists() else sys.executable

pytestmark = pytest.mark.skipif(not PDF.exists(), reason="source PDF not present")


def build(out_root: Path):
    subprocess.run([PY, str(BUILD), "--out-root", str(out_root),
                    "--overwrite"], check=True, capture_output=True, text=True)
    return out_root / "corpus" / "paper-book-v1"


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    return build(tmp_path_factory.mktemp("book"))


def test_reproducible_byte_identical(built, tmp_path_factory):
    again = build(tmp_path_factory.mktemp("book-again"))
    assert (built / "paper-book-v1.md").read_bytes() == \
           (again / "paper-book-v1.md").read_bytes()
    assert (built / "paper-book-v1.manifest.json").read_bytes() == \
           (again / "paper-book-v1.manifest.json").read_bytes()


def test_validator_passes(built):
    res = subprocess.run([PY, str(VALIDATE), "--corpus-root",
                          str(built.parents[1])], capture_output=True, text=True)
    assert res.returncode == 0, res.stdout + res.stderr


def test_expected_content(built):
    md = (built / "paper-book-v1.md").read_text()
    # symbol-font glyphs decoded
    assert "p<.001" in md and "1024×768" in md and "945–978" in md
    assert "© 2009 Psychology Press" in md
    assert "γ1=0.1, γ2=0.85, γ3=0.05" in md
    # compound hyphens survived de-hyphenation
    assert "targetpresent" not in md and "target-present" in md
    # furniture stripped
    assert "Downloaded By" not in md
    # placeholders
    assert "[FIGURE 12:" in md and "[TABLE 1:" in md and "[EQUATION 1:" in md
    # ligatures normalized
    assert "ﬁ" not in md


def test_manifest_counts(built):
    m = json.loads((built / "paper-book-v1.manifest.json").read_text())
    assert m["counts"]["figures"] == 12
    assert m["counts"]["footnotes"] == 7
    assert m["counts"]["equations"] == 1
    assert m["counts"]["pdf_pages"] == 34
    assert m["expectation_mismatches"] == []
    # every PDF page contributes at least one line
    assert all(entry["ranges"] for entry in m["page_map"])


def test_overwrite_guard(built):
    res = subprocess.run([PY, str(BUILD), "--out-root",
                          str(built.parents[1])], capture_output=True, text=True)
    assert res.returncode != 0
    assert "--overwrite" in res.stderr + res.stdout


def test_committed_corpus_valid_if_present():
    if not (ROOT / "corpus" / "paper-book-v1" / "paper-book-v1.md").exists():
        pytest.skip("committed corpus not built yet")
    res = subprocess.run([PY, str(VALIDATE)], capture_output=True,
                         text=True)
    assert res.returncode == 0, res.stdout + res.stderr

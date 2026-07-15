"""Tests for build_pdf_outline_index.py — deterministic PDF-outline extractor.

Pure-helper tests run anywhere. The RFC-PDF tests need the pinned PyMuPDF and
the source PDF; they skip cleanly if either is missing.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import build_pdf_outline_index as B  # noqa: E402

VENV_PY = ROOT / ".venv" / "bin" / "python"
PY = str(VENV_PY) if VENV_PY.exists() else sys.executable
PDF = ROOT / "sources" / "rfc9110" / "rfc9110.pdf"
TWIN = ROOT / "indexes" / "IDX-D-rfc9110" / "index.json"


def _titles(structure):
    out = []
    stack = list(structure)
    while stack:
        n = stack.pop()
        out.append(re.sub(r"\s+", " ", n["title"]).strip().lower())
        stack.extend(n.get("nodes", []))
    return out


def test_self_test_passes():
    r = subprocess.run([PY, str(ROOT / "scripts" / "build_pdf_outline_index.py"), "--self-test"],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "self-test OK" in r.stdout


def test_nest_and_ids_are_pure_and_preorder():
    flat = [{"level": 1, "title": "A", "node_id": "0000"},
            {"level": 2, "title": "A.1", "node_id": "0001"},
            {"level": 1, "title": "B", "node_id": "0002"}]
    tree = B.nest_by_level([dict(e) for e in flat])
    assert [n["title"] for n in tree] == ["A", "B"]
    assert tree[0]["nodes"][0]["title"] == "A.1"
    assert B.count_nodes(tree) == 3
    assert B.assign_node_ids(3) == ["0000", "0001", "0002"]


SCRIPT = ROOT / "scripts" / "build_pdf_outline_index.py"


def _build_rfc_via_venv(out: Path):
    """Build through the venv interpreter (PyMuPDF lives there, not necessarily
    under the pytest interpreter). Returns the parsed index, or None to skip."""
    if not PDF.is_file() or not TWIN.is_file() or not VENV_PY.exists():
        return None
    r = subprocess.run([PY, str(SCRIPT), "--pdf", str(PDF), "--out", str(out), "--overwrite"],
                       capture_output=True, text=True)
    if r.returncode != 0:
        # pinned-version mismatch or missing dep -> skip, not fail
        if "PyMuPDF" in (r.stdout + r.stderr) or "No module" in (r.stdout + r.stderr):
            return None
        raise AssertionError(r.stdout + r.stderr)
    return json.loads(out.read_text())


def test_rfc_index_matches_markdown_twin_and_is_complete(tmp_path):
    idx = _build_rfc_via_venv(tmp_path / "idx.json")
    if idx is None:
        import pytest
        pytest.skip("rfc9110.pdf / twin / pinned PyMuPDF not available")
    nodes = list(_preorder(idx["structure"]))
    # 311 nodes, page-addressed, every node has real body text
    assert B.count_nodes(idx["structure"]) == 311
    assert all("start_index" in n and "end_index" in n for n in nodes)
    assert all(n.get("text", "").strip() for n in nodes), "every node must carry non-empty text"
    # structurally identical to the Markdown IDX-D twin (isolates representation)
    twin = json.load(open(TWIN))["structure"]
    assert set(_titles(idx["structure"])) == set(_titles(twin))
    # pre-order start pages are non-decreasing
    order = [n["start_index"] for n in nodes]
    assert all(order[i] <= order[i + 1] for i in range(len(order) - 1))


def test_rfc_index_is_byte_deterministic(tmp_path):
    a = _build_rfc_via_venv(tmp_path / "a.json")
    if a is None:
        import pytest
        pytest.skip("rfc9110.pdf / pinned PyMuPDF not available")
    b = _build_rfc_via_venv(tmp_path / "b.json")
    assert (tmp_path / "a.json").read_bytes() == (tmp_path / "b.json").read_bytes()


def _preorder(structure):
    for n in structure:
        yield n
        yield from _preorder(n.get("nodes", []))

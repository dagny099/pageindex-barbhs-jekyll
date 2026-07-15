"""Tests for the retrieval harness's addressing modes.

Offline — no API keys, no network, no spend. run_retrieval.py imports the OpenAI
Agents SDK / litellm / pageindex at module load, which live in the project venv, so
(like test_build_index_metered.py) we drive the script's --self-test through that
interpreter rather than importing it here.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "run_retrieval.py"

VENV_PY = ROOT / ".venv" / "bin" / "python"
PY = str(VENV_PY) if VENV_PY.exists() else sys.executable


def test_self_test_passes():
    """Covers addressing detection (line vs node), the node-mode tools
    (get_document / get_document_structure / get_page_content), and that
    build_documents selects the right mode + type for each index shape."""
    r = subprocess.run([PY, str(SCRIPT), "--self-test"],
                       capture_output=True, text=True, cwd=ROOT)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "self-test OK" in r.stdout, r.stdout + r.stderr

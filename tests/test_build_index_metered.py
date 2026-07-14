"""Tests for the metered index builder.

Everything here is offline — no API keys, no network, no spend. The paid path
is gated behind an interactive confirmation, so the closest end-to-end test
drives the real pre-flight (estimate + prompt) and declines it.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build_index_metered.py"

# tiktoken / litellm / pageindex live in the project venv; pytest itself may
# run under a different interpreter.
VENV_PY = ROOT / ".venv" / "bin" / "python"
PY = str(VENV_PY) if VENV_PY.exists() else sys.executable


def run(args, **kw):
    return subprocess.run([PY, str(SCRIPT), *args],
                          capture_output=True, text=True, cwd=ROOT, **kw)


def test_self_test_passes():
    r = run(["--self-test"])
    assert r.returncode == 0, r.stdout + r.stderr
    assert "self-test OK" in r.stdout


def test_requires_exactly_one_source():
    assert run([]).returncode != 0
    assert run(["--pdf_path", "a.pdf", "--md_path", "b.md"]).returncode != 0


def test_preflight_estimates_and_declines_without_spend(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text("# Big\n" + ("word " * 400) + "\n## Small\ntiny\n", encoding="utf-8")
    log = tmp_path / "usage.jsonl"
    r = run(["--md_path", str(md), "--if-add-node-summary", "yes",
             "--log", str(log)], input="n\n")
    assert r.returncode != 0
    assert "aborted before any spend" in (r.stdout + r.stderr)
    # near-exact markdown estimate: only the over-threshold section costs a call
    assert "1 summary calls" in r.stdout
    assert not log.exists(), "declined pre-flight must write no usage rows"


def test_summaries_off_is_estimated_free(tmp_path):
    md = tmp_path / "doc.md"
    md.write_text("# Big\n" + ("word " * 400) + "\n", encoding="utf-8")
    r = run(["--md_path", str(md), "--if-add-node-summary", "no",
             "--log", str(tmp_path / "usage.jsonl")], input="n\n")
    assert "0 summary calls" in r.stdout

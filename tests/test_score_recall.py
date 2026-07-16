"""Tests for score_recall.py — representation-neutral gold-section recall.

Pure stdlib scorer, so it imports directly under any interpreter.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import score_recall as S  # noqa: E402

SCRIPT = ROOT / "scripts" / "score_recall.py"


def test_self_test_passes():
    r = subprocess.run([sys.executable, str(SCRIPT), "--self-test"], capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "self-test OK" in r.stdout


def test_line_and_node_indexes_score_from_same_gold(tmp_path):
    """One gold key (section ids) scores both a line-addressed and a node-addressed
    index of the same two sections — the representation-neutral property."""
    line_struct = [{"title": "15.4.2. 301", "node_id": "0", "line_num": 100},
                   {"title": "10.2.2. Location", "node_id": "1", "line_num": 200}]
    node_struct = [{"title": "15.4.2. 301", "node_id": "0202", "start_index": 134, "end_index": 134},
                   {"title": "10.2.2. Location", "node_id": "0090", "start_index": 90, "end_index": 90}]
    idxdir = tmp_path / "indexes"
    for name, struct in [("IDX-LINE", line_struct), ("IDX-NODE", node_struct)]:
        d = idxdir / name
        d.mkdir(parents=True)
        (d / "index.json").write_text(json.dumps({"doc_name": name, "structure": struct}))

    # line index fetched a range covering 15.4.2's line (100) but not 10.2.2's (200)
    # node index fetched node_id 0202 (15.4.2) but not 0090 (10.2.2)
    run = {"run_id": "T", "results": [
        {"index_id": "IDX-LINE", "retriever": "m", "qid": "RA1", "category": "lookup",
         "tool_calls": [{"tool": "get_page_content", "args": {"pages": "95-150"}}]},
        {"index_id": "IDX-NODE", "retriever": "m", "qid": "RA1", "category": "lookup",
         "tool_calls": [{"tool": "get_page_content", "args": {"pages": "0202"}}]},
    ]}
    run_dir = tmp_path / "run"; run_dir.mkdir()
    (run_dir / "run.json").write_text(json.dumps(run))
    qcsv = tmp_path / "q.csv"
    qcsv.write_text("id,category,question,gold_sections\nRA1,lookup,Q,15.4.2; 10.2.2\n")

    r = subprocess.run([sys.executable, str(SCRIPT), "--run", str(run_dir),
                        "--questions", str(qcsv), "--indexes-dir", str(idxdir)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr
    rows = {row["index"]: row for row in _read_csv(run_dir / "recall.csv")}
    assert rows["IDX-LINE"]["recall"] == "0.5"   # hit 15.4.2, missed 10.2.2
    assert rows["IDX-NODE"]["recall"] == "0.5"   # hit 15.4.2, missed 10.2.2


def test_unmappable_section_is_flagged_not_zero(tmp_path):
    """A gold section absent from an index's titles is UNMAPPABLE (excluded from the
    recall denominator), modelling the LLM-inferred tree that dropped section numbers."""
    struct = [{"title": "301 Moved Permanently", "node_id": "0202",  # no section number
               "start_index": 134, "end_index": 134}]
    d = tmp_path / "indexes" / "IDX-INFER"; d.mkdir(parents=True)
    (d / "index.json").write_text(json.dumps({"structure": struct}))
    addr, sec_map = S.section_map(struct)
    res = {"tool_calls": [{"tool": "get_page_content", "args": {"pages": "0202"}}]}
    hits, total, unmappable = S.score_result(res, ["15.4.2"], addr, sec_map)
    assert (hits, total, unmappable) == (0, 0, 1)


def test_article_and_recitals_keys_map_for_legal_docs():
    """GDPR-style trees have 'Article N — rubric' headings and a single Recitals node;
    gold is expressed as 'Article 17' / 'Recitals' and must project onto both
    addressings, without disturbing the dotted-section (RFC) behavior."""
    line_struct = [{"title": "Recitals (Preamble)", "node_id": "0000", "line_num": 3},
                   {"title": "Article 17 — Right to erasure", "node_id": "0021", "line_num": 700}]
    node_struct = [{"title": "Recitals (Preamble)", "node_id": "0000",
                    "start_index": 1, "end_index": 30},
                   {"title": "Article 17 — Right to erasure", "node_id": "0021",
                    "start_index": 40, "end_index": 42}]
    la, lm = S.section_map(line_struct)
    na, nm = S.section_map(node_struct)
    assert (la, lm["Article 17"], lm["Recitals"]) == ("line", 700, 3)
    assert (na, nm["Article 17"]) == ("node", "0021")
    res = {"tool_calls": [{"tool": "get_page_content", "args": {"pages": "690-720"}}]}
    assert S.score_result(res, ["Article 17", "Recitals"], la, lm) == (1, 2, 0)


def _read_csv(path):
    import csv
    return list(csv.DictReader(path.open()))

#!/usr/bin/env python3
"""Harness-validation run: query an index with the OpenAI Agents SDK retriever.

Loads a curated index (default IDX-D), exposes PageIndex's three retrieval tools
(get_document / get_document_structure / get_page_content) over it, and runs an
agent ("retriever") over a set of questions. Captures each answer, the full
tool-call trace, timings, and token usage to runs/<timestamp>/ so the harness
can be inspected before scaling (per the experiment protocol).

Usage:
  python3 scripts/run_retrieval.py --retriever gpt-4o-2024-11-20 --questions Q3 Q5 Q8
"""
from __future__ import annotations

import argparse
import asyncio
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENDOR = REPO / "vendor" / "PageIndex"
sys.path.insert(0, str(VENDOR))

from dotenv import load_dotenv

load_dotenv(REPO / ".env")  # OPENAI_API_KEY etc.

from agents import Agent, Runner, function_tool, set_tracing_disabled
import pageindex.retrieve as R

# ── Frozen candidate question bank (see reports/experimental-brief-lab-notebook.html) ──
QUESTIONS = {
    "Q3": ("direct-location",
           "Which project is a self-hosted ML pipeline for workout/fitness data, "
           "and what stack does it describe?"),
    "Q5": ("cross-section-synthesis",
           "Across the articles, what recurring critique is made about how "
           "organizations adopt AI (adoption-vs-value, skills-vs-judgment)?"),
    "Q8": ("consistency",
           "Where is a single project or service described in more than one place "
           "(project page vs. an article that references it), and do the descriptions "
           "agree on scope and outcome?"),
}

AGENT_SYSTEM_PROMPT = """
You are PageIndex, a document QA assistant answering questions about a personal
professional website that has been compiled into one Markdown "site book".
TOOL USE:
- Call get_document() first to confirm status and line count.
- Call get_document_structure() to identify relevant sections and their line_num values.
- Call get_page_content(pages="120-160") with tight line ranges from the structure;
  never fetch the whole document.
- Before each tool call, output one short sentence explaining why.
Answer based only on tool output. Cite the section titles you used. Be concise.
""".strip()


def git_head(repo: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(repo), "rev-parse", "HEAD"], text=True
        ).strip()
    except Exception:
        return "unknown"


def build_documents(index_path: Path) -> tuple[dict, str]:
    idx = json.loads(index_path.read_text())
    doc_id = idx["doc_name"]
    documents = {
        doc_id: {
            "id": doc_id,
            "type": "md",
            "doc_name": idx["doc_name"],
            "doc_description": idx.get("doc_description", ""),
            "line_count": idx.get("line_count", 0),
            "structure": idx["structure"],
        }
    }
    return documents, doc_id


def run_one(documents: dict, doc_id: str, model: str, question: str) -> dict:
    """Run the retriever agent for one question; return answer + trace + timing + usage."""
    trace: list[dict] = []

    @function_tool
    def get_document() -> str:
        """Get document metadata: doc_name, line_count, status."""
        out = R.get_document(documents, doc_id)
        trace.append({"tool": "get_document", "args": {}, "output_chars": len(out)})
        return out

    @function_tool
    def get_document_structure() -> str:
        """Get the document's tree structure (titles + line numbers, no body text)."""
        out = R.get_document_structure(documents, doc_id)
        trace.append({"tool": "get_document_structure", "args": {}, "output_chars": len(out)})
        return out

    @function_tool
    def get_page_content(pages: str) -> str:
        """Get text by Markdown line numbers. Use tight ranges, e.g. '120-160' or '540,2176'."""
        out = R.get_page_content(documents, doc_id, pages)
        trace.append({"tool": "get_page_content", "args": {"pages": pages}, "output_chars": len(out)})
        return out

    agent = Agent(
        name="PageIndex-Retriever",
        instructions=AGENT_SYSTEM_PROMPT,
        tools=[get_document, get_document_structure, get_page_content],
        model=model,
    )

    t0 = time.perf_counter()
    result = asyncio.run(Runner.run(agent, question, max_turns=20))
    elapsed = round(time.perf_counter() - t0, 2)

    usage = {}
    try:
        u = result.context_wrapper.usage
        usage = {"requests": u.requests, "input_tokens": u.input_tokens,
                 "output_tokens": u.output_tokens, "total_tokens": u.total_tokens}
    except Exception:
        pass

    return {
        "answer": str(result.final_output),
        "tool_calls": trace,
        "n_tool_calls": len(trace),
        "latency_seconds": elapsed,
        "usage": usage,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--index", default=str(REPO / "indexes" / "IDX-D" / "index.json"))
    ap.add_argument("--index-id", default="IDX-D")
    ap.add_argument("--retriever", default="gpt-4o-2024-11-20")
    ap.add_argument("--questions", nargs="+", default=["Q3", "Q5", "Q8"])
    args = ap.parse_args()

    set_tracing_disabled(True)
    index_path = Path(args.index)
    documents, doc_id = build_documents(index_path)
    provenance = json.loads((REPO / "corpus" / "site-book-v1" / "provenance.json").read_text())

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = REPO / "runs" / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    record = {
        "run_id": ts,
        "purpose": "harness-validation",
        "index_id": args.index_id,
        "retriever_model": args.retriever,
        "retriever_provider": "openai",
        "corpus_version": provenance["corpus_version"],
        "corpus_sha256": provenance["corpus_sha256"],
        "pageindex_commit": provenance["pageindex_commit"],
        "repo_commit": git_head(REPO),
        "results": [],
    }

    for qid in args.questions:
        category, question = QUESTIONS[qid]
        print(f"\n{'='*70}\n{qid} [{category}]  {question}\n{'='*70}")
        res = run_one(documents, doc_id, args.retriever, question)
        res.update({"qid": qid, "category": category, "question": question})
        record["results"].append(res)
        print(f"tools={res['n_tool_calls']}  {res['latency_seconds']}s  "
              f"tokens={res['usage'].get('total_tokens','?')}")
        print(f"ANSWER:\n{res['answer']}")

    (run_dir / "run.json").write_text(json.dumps(record, indent=2, ensure_ascii=False))

    # Human-readable summary
    lines = [f"# Retrieval run {ts} — harness validation", "",
             f"- Index: **{args.index_id}** ({provenance['corpus_version']}, corpus `{provenance['corpus_sha256'][:12]}…`)",
             f"- Retriever: **{args.retriever}** (openai)",
             f"- Repo commit: `{record['repo_commit'][:10]}`", ""]
    for r in record["results"]:
        lines += [f"## {r['qid']} — {r['category']}", "",
                  f"**Q:** {r['question']}", "",
                  f"**Tool calls ({r['n_tool_calls']})**, {r['latency_seconds']}s, "
                  f"{r['usage'].get('total_tokens','?')} tokens:", ""]
        for tc in r["tool_calls"]:
            arg = tc["args"].get("pages", "")
            lines.append(f"- `{tc['tool']}({arg})` → {tc['output_chars']} chars")
        lines += ["", "**Answer:**", "", r["answer"], "", "---", ""]
    (run_dir / "run.md").write_text("\n".join(lines))

    print(f"\nSaved: {run_dir}/run.json  and  run.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

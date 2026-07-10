#!/usr/bin/env python3
"""Retrieval harness: query an index with one or more retriever models.

Loads a curated index (default IDX-D), exposes PageIndex's three retrieval tools
over it (no re-indexing), and runs the OpenAI Agents SDK retriever over questions
drawn from evaluations/questions.csv. Captures answers, full tool-call traces, and
the operational metrics that are actually decision-useful — not noise:

  - n_tool_calls        navigation effort
  - structure_tokens    size of the tree dump the agent pulls (the IDX-D vs IDX-C
                        headline: how much the index costs to *navigate*)
  - content_tokens      text actually fetched via get_page_content (retrieval tightness)
  - input/output/total  tokens the model consumed (from the SDK)
  - est_cost_usd        approximate $ per question (see PRICING)
  - latency_seconds

Payload sizes (structure/content tokens) use one fixed reference encoding so they
are comparable across retrievers regardless of each model's own tokenizer.

Usage:
  # Index comparison ("does a summarized index help?") — hold retriever fixed:
  python3 scripts/run_retrieval.py --indexes IDX-D IDX-C IDX-O --retrievers gpt-4o-2024-11-20
  # Retriever comparison ("open-source vs commercial") — hold index fixed:
  python3 scripts/run_retrieval.py --indexes IDX-C \
      --retrievers gpt-4o-2024-11-20 anthropic/claude-sonnet-4-5 ollama_chat/qwen2.5-7b-instruct-ctx32k
  # Subset of questions, one index/retriever:
  python3 scripts/run_retrieval.py --indexes IDX-D --retrievers gpt-4o-2024-11-20 --questions DL3 CS2 CN4
  python3 scripts/run_retrieval.py                      # IDX-D, gpt-4o, all questions
"""
from __future__ import annotations

import argparse
import asyncio
import csv
import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VENDOR = REPO / "vendor" / "PageIndex"
sys.path.insert(0, str(VENDOR))

from dotenv import load_dotenv

load_dotenv(REPO / ".env")  # OPENAI_API_KEY / ANTHROPIC_API_KEY

import tiktoken
from agents import Agent, Runner, function_tool, set_tracing_disabled
import pageindex.retrieve as R

_ENC = tiktoken.get_encoding("o200k_base")  # reference tokenizer for payload accounting


def ntok(s: str) -> int:
    return len(_ENC.encode(s or ""))


# Approximate USD per 1M tokens (input, output). Edit as prices change; unknown -> no cost.
PRICING = {
    "gpt-4o-2024-11-20": (2.50, 10.00),
    "gpt-4o": (2.50, 10.00),
    "gpt-4o-mini": (0.15, 0.60),
    "gpt-4.1": (2.00, 8.00),
    "gpt-4.1-mini": (0.40, 1.60),
    "anthropic/claude-sonnet-4-5": (3.00, 15.00),
    "anthropic/claude-3-5-sonnet-latest": (3.00, 15.00),
}


def est_cost(model: str, inp, out):
    if inp is None:
        return None
    if model.startswith("ollama/"):
        return 0.0
    p = PRICING.get(model)
    if not p:
        return None
    return round(inp / 1e6 * p[0] + out / 1e6 * p[1], 4)


# NOTE: this canonical prompt was revised after the RET-OLL (local model) probe — the
# prior version asked the model to "output one short sentence before each tool call",
# which biased weaker open-source models toward *narrating* tool calls in prose instead
# of actually invoking them. See reports/findings-retriever-prompt-revision.md for the
# before/after and rationale. Keep this prompt constant across all retrievers.
AGENT_SYSTEM_PROMPT = """
You are PageIndex, a document QA assistant answering questions about a personal
professional website compiled into a single Markdown "site book", which you can only
read through tools.

Workflow - follow in order:
1. get_document() - confirm the document is available and get its line count.
2. get_document_structure() - read the tree of section titles and their line numbers;
   decide which sections are relevant and note their line_num values.
3. get_page_content(pages="...") - read the actual text of those sections, using tight
   line ranges from step 2 (e.g. "2403-2476"). Fetch content for every section you rely
   on; never fetch the whole document at once.

Ground every claim in text returned by get_page_content - the structure gives titles
only, which is not enough to answer. If multiple sections are relevant, fetch each one.
Cite the section titles you used. Be concise, and say so if the corpus does not contain
the answer.
""".strip()


def resolve_model(name: str):
    """Bare OpenAI names pass through natively; other providers use LiteLLM."""
    if "/" not in name and name.startswith(("gpt-", "o1", "o3", "o4", "chatgpt")):
        return name
    from agents.extensions.models.litellm_model import LitellmModel

    key = None
    if name.startswith("anthropic/") or "claude" in name:
        key = os.getenv("ANTHROPIC_API_KEY")
    elif name.startswith("openai/"):
        key = os.getenv("OPENAI_API_KEY")
    return LitellmModel(model=name, api_key=key)


def git_head(repo: Path) -> str:
    try:
        return subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def load_questions(ids: list[str]) -> list[dict]:
    rows = {r["id"]: r for r in csv.DictReader((REPO / "evaluations" / "questions.csv").open())}
    ids = ids or list(rows)
    unknown = [q for q in ids if q not in rows]
    if unknown:
        raise SystemExit(f"Unknown question id(s): {unknown}. Valid ids: {sorted(rows)}")
    return [rows[qid] for qid in ids]


def build_documents(index_path: Path) -> tuple[dict, str]:
    idx = json.loads(index_path.read_text())
    doc_id = idx["doc_name"]
    return {doc_id: {"id": doc_id, "type": "md", "doc_name": idx["doc_name"],
                     "doc_description": idx.get("doc_description", ""),
                     "line_count": idx.get("line_count", 0), "structure": idx["structure"]}}, doc_id


def run_one(documents: dict, doc_id: str, model_name: str, model_obj, question: str) -> dict:
    trace: list[dict] = []

    def _log(tool, out, **args):
        trace.append({"tool": tool, "args": args, "output_chars": len(out), "output_tokens": ntok(out)})
        return out

    @function_tool
    def get_document() -> str:
        """Get document metadata: doc_name, line_count, status."""
        return _log("get_document", R.get_document(documents, doc_id))

    @function_tool
    def get_document_structure() -> str:
        """Get the tree structure (titles + summaries + line numbers, no body text)."""
        return _log("get_document_structure", R.get_document_structure(documents, doc_id))

    @function_tool
    def get_page_content(pages: str) -> str:
        """Get text by Markdown line numbers. Tight ranges, e.g. '120-160' or '540,2176'."""
        return _log("get_page_content", R.get_page_content(documents, doc_id, pages), pages=pages)

    agent = Agent(name="PageIndex-Retriever", instructions=AGENT_SYSTEM_PROMPT,
                  tools=[get_document, get_document_structure, get_page_content], model=model_obj)

    t0 = time.perf_counter()
    error = None
    answer = ""
    usage = {}
    try:
        result = asyncio.run(Runner.run(agent, question, max_turns=20))
        answer = str(result.final_output)
        try:
            u = result.context_wrapper.usage
            usage = {"input_tokens": u.input_tokens, "output_tokens": u.output_tokens,
                     "total_tokens": u.total_tokens}
        except Exception:
            pass
    except Exception as e:
        error = f"{type(e).__name__}: {e}"
    elapsed = round(time.perf_counter() - t0, 2)

    return {
        "retriever": model_name,
        "answer": answer,
        "error": error,
        "tool_calls": trace,
        "n_tool_calls": len(trace),
        "structure_tokens": sum(t["output_tokens"] for t in trace if t["tool"] == "get_document_structure"),
        "content_tokens": sum(t["output_tokens"] for t in trace if t["tool"] == "get_page_content"),
        "usage": usage,
        "est_cost_usd": est_cost(model_name, usage.get("input_tokens"), usage.get("output_tokens")),
        "latency_seconds": elapsed,
    }


def write_markdown(run_dir: Path, record: dict, provenance: dict, indexes: list[str], retrievers: list[str]) -> None:
    lines = [f"# Retrieval run {record['run_id']}", "",
             f"- Indexes: {', '.join('`'+i+'`' for i in indexes)}",
             f"- Retrievers: {', '.join('`'+m+'`' for m in retrievers)}",
             f"- Corpus: `{provenance['corpus_version']}` (`{provenance['corpus_sha256'][:12]}…`)",
             f"- Repo commit: `{record['repo_commit'][:10]}`  ·  questions: {len(record['questions'])}", "",
             "## Comparison — means across questions", "",
             "| Index | Retriever | n | tools | struct_tok | content_tok | total_tok | $ | s |",
             "|---|---|---|---|---|---|---|---|---|"]
    for index_id in indexes:
        for m in retrievers:
            rs = [r for r in record["results"] if r["index_id"] == index_id and r["retriever"] == m and not r["error"]]
            if not rs:
                lines.append(f"| `{index_id}` | `{m}` | 0 | — | — | — | — | — | — |"); continue
            n = len(rs)
            avg = lambda k: round(sum(r[k] for r in rs) / n, 1)
            tt = round(sum(r["usage"].get("total_tokens", 0) for r in rs) / n)
            cost = round(sum(r["est_cost_usd"] or 0 for r in rs), 4)
            lines.append(f"| `{index_id}` | `{m}` | {n} | {avg('n_tool_calls')} | {avg('structure_tokens')} | "
                         f"{avg('content_tokens')} | {tt} | {cost} | {avg('latency_seconds')} |")

    lines += ["", "## Per-question detail (question, expected evidence, ground truth, answer)",
              "*Everything needed to score each answer is inline below — no cross-referencing.*", ""]
    for r in record["results"]:
        lines += [f"### [{r['index_id']} | {r['retriever']}] {r['qid']} — {r['category']}", "",
                  f"**Q:** {r['question']}", ""]
        if r.get("expected_evidence"):
            lines += [f"**Expected evidence:** {r['expected_evidence']}", ""]
        if r.get("ground_truth"):
            lines += [f"**Ground truth:** {r['ground_truth']}", ""]
        if r["error"]:
            lines += [f"**ERROR:** {r['error']}", "", "---", ""]; continue
        fetched = ", ".join(f"`{tc['args'].get('pages','')}`" for tc in r["tool_calls"]
                            if tc["tool"] == "get_page_content") or "— (no content fetched)"
        lines += [f"metrics: tools={r['n_tool_calls']} · struct_tok={r['structure_tokens']} · "
                  f"content_tok={r['content_tokens']} · total_tok={r['usage'].get('total_tokens','?')} · "
                  f"${r['est_cost_usd']} · {r['latency_seconds']}s",
                  f"fetched line ranges: {fetched}", "",
                  "**Answer:**", "", r["answer"], "", "---", ""]
    (run_dir / "run.md").write_text("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--indexes", nargs="+", default=["IDX-D"],
                    help="index ids to run/compare, e.g. IDX-D IDX-C IDX-O")
    ap.add_argument("--retrievers", nargs="+", default=["gpt-4o-2024-11-20"])
    ap.add_argument("--questions", nargs="*", default=[], help="question ids (default: all in the CSV)")
    args = ap.parse_args()

    set_tracing_disabled(True)
    provenance = json.loads((REPO / "corpus" / "site-book-v1" / "provenance.json").read_text())
    questions = load_questions(args.questions)

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_dir = REPO / "runs" / ts
    run_dir.mkdir(parents=True, exist_ok=True)

    record = {"run_id": ts, "purpose": "retrieval", "indexes": args.indexes,
              "retrievers": args.retrievers, "questions": [q["id"] for q in questions],
              "corpus_version": provenance["corpus_version"], "corpus_sha256": provenance["corpus_sha256"],
              "repo_commit": git_head(REPO), "results": []}

    for index_id in args.indexes:
        documents, doc_id = build_documents(REPO / "indexes" / index_id / "index.json")
        for model_name in args.retrievers:
            model_obj = resolve_model(model_name)
            for q in questions:
                print(f"\n{'='*70}\n[{index_id} | {model_name}] {q['id']} [{q['category']}]\n{q['question']}\n{'='*70}")
                res = run_one(documents, doc_id, model_name, model_obj, q["question"])
                res.update({"index_id": index_id, "qid": q["id"], "category": q["category"],
                            "question": q["question"], "expected_evidence": q.get("expected_evidence", ""),
                            "ground_truth": q.get("ground_truth", "")})
                record["results"].append(res)
                if res["error"]:
                    print(f"ERROR: {res['error']}")
                else:
                    print(f"tools={res['n_tool_calls']} struct_tok={res['structure_tokens']} "
                          f"content_tok={res['content_tokens']} total_tok={res['usage'].get('total_tokens','?')} "
                          f"${res['est_cost_usd']} {res['latency_seconds']}s")

    (run_dir / "run.json").write_text(json.dumps(record, indent=2, ensure_ascii=False))
    write_markdown(run_dir, record, provenance, args.indexes, args.retrievers)
    print(f"\nSaved: {run_dir}/run.json and run.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

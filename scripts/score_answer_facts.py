#!/usr/bin/env python3
"""Objective answer-correctness metric for the RFC summary test.

Recall@fetch (score_recall.py) measures navigation, but it is confounded: a retriever
can answer correctly from a tight fetch (or from a node summary) and score LOW recall
(see RA1). So the OUTCOME metric is: did the answer actually contain the facts the
question requires? Each question's required facts are concrete, checkable atoms — status
codes, header-field names, RFC numbers, method names — encoded below as regex alternates.
The score is the fraction present. This is objective and reproducible (no LLM judge).

Limits (stated, not hidden): only CONCRETE atoms are auto-checked. A few questions also
need a *relational* fact (e.g. RB1's evaluation ORDER, RA2's definition) that substring
matching can't verify; those are listed in `FUZZY` and flagged for a quick manual/blind
check — they are never silently counted as correct.

Usage: scripts/score_answer_facts.py --run runs/<ts>
"""
from __future__ import annotations
import argparse, csv, json, re, statistics
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

def code(n): return rf"\b{n}\b"

# per-question concrete atoms: label -> list of alternative regexes (any match = present)
FACTS: dict[str, dict[str, list[str]]] = {
 "RA1": {"301": [code(301), "moved permanently"], "Location": ["location"]},
 "RA2": {"PUT": [r"\bput\b"], "DELETE": [r"\bdelete\b"], "safe": [r"\bsafe\b"]},
 "RA3": {"201": [code(201), "created"], "Location": ["location"], "target URI": ["target uri", "target-uri"]},
 "RA4": {"OPTIONS": [r"\boptions\b"], "communication options": ["communication option", "options available", "available.*options"]},
 "RB1": {"If-Match": ["if-match"], "If-Unmodified-Since": ["if-unmodified-since"], "If-None-Match": ["if-none-match"],
         "If-Modified-Since": ["if-modified-since"], "If-Range": ["if-range"]},
 "RB2": {"GET": [r"\bget\b"], "HEAD": [r"\bhead\b"], "cacheable": ["cacheable", "caching"]},
 "RB3": {"206": [code(206), "partial content"], "200/full": [code(200), "full representation", "entire representation"],
         "416": [code(416), "not satisfiable"], "If-Range": ["if-range"]},
 "RC1": {"406": [code(406), "not acceptable"], "disregard": ["disregard", "not subject to.*negotiation", "ignore the header"]},
 "RB4": {"PUT": [r"\bput\b"], "POST": [r"\bpost\b"], "idempotent": ["idempotent"]},
 "RB5": {"Vary": [r"\bvary\b"], "cache": ["cache", "caching"], "negotiation": ["negotiat", "accept"]},
 "RB6": {"307": [code(307)], "308": [code(308)], "302": [code(302)], "method preserved": ["method.*not.*chang", "preserv.*method", "must not change.*method", "same.*method"]},
 "RC2": {"Location": ["location"], "201": [code(201)], "301": [code(301)], "method+status": ["method and status", "depends on.*method", "combination of.*method"]},
 "RC3": {"Content-Range": ["content-range"], "206": [code(206)], "416": [code(416)]},
 "RC4": {"ETag": ["etag"], "If-None-Match": ["if-none-match"], "If-Match": ["if-match"], "304": [code(304), "not modified"]},
 "RC5": {"Allow": [r"\ballow\b"], "405": [code(405), "method not allowed"], "OPTIONS": [r"\boptions\b"]},
 "RD2": {"Accept": [r"\baccept\b"], "Accept-Charset": ["accept-charset"], "Accept-Encoding": ["accept-encoding"],
         "Accept-Language": ["accept-language"], "Vary": [r"\bvary\b"]},
 "RD3": {"Range": [r"\brange\b"], "Accept-Ranges": ["accept-ranges"], "Content-Range": ["content-range"]},
 "RD4": {"200": [code(200)], "201": [code(201)], "202": [code(202)], "203": [code(203)], "204": [code(204)], "205": [code(205)], "206": [code(206)]},
 "RD5": {"Content-Type": ["content-type"], "Content-Encoding": ["content-encoding"], "Content-Language": ["content-language"],
         "Content-Length": ["content-length"], "Content-Location": ["content-location"]},
 "RE1": {"absent from 9110": ["does not define", "not define", "not specified in", "outside", "does not specify"],
         "9111/CACHING": [code(9111), r"\bcaching\b.*specification", r"\[caching\]"], "freshness": ["freshness"]},
 "RE2": {"absent from 9110": ["does not", "not define", "not specify", "outside"], "9112/HTTP-1.1-syntax": [code(9112), "messaging syntax", "http/1.1.*syntax"]},
 "RE3": {"not defined here": ["does not define", "not define", "referenced", "not.*defined"], "6265/COOKIE": [code(6265), r"\[cookie\]", "cookie.*specification"]},
 "RE4": {"absent": ["does not define", "not define", "no.*429", "not.*specify"], "429 elsewhere": [code(429), code(6585)]},
}
# relational facts substring-matching can't verify -> flagged, never auto-counted
FUZZY = {
 "RB1": "correct evaluation ORDER of the 5 fields", "RA2": "the definition of idempotent",
 "RB2": "that the intersection (both) is exactly GET+HEAD", "RB3": "if-range match->206 vs no-match->200 logic",
 "RB6": "302/303 method-change contrast", "RD4": "exactly these 7 (no over/under-enumeration)",
}

def present(ans: str, alts: list[str]) -> bool:
    return any(re.search(p, ans, re.IGNORECASE) for p in alts)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    args = ap.parse_args()
    rp = Path(args.run); rj = rp if rp.suffix == ".json" else rp / "run.json"
    run = json.loads(rj.read_text())

    rows = []
    for res in run["results"]:
        qid, idx = res["qid"], res["index_id"]
        facts = FACTS.get(qid, {})
        ans = res.get("answer", "") or ""
        if res.get("error") or not facts:
            rows.append(dict(qid=qid, index=idx, fact_score=None, hits=0, total=len(facts),
                             missing="ERROR" if res.get("error") else "no-facts-encoded",
                             fuzzy=FUZZY.get(qid, "")))
            continue
        got = {lbl: present(ans, alts) for lbl, alts in facts.items()}
        hits = sum(got.values())
        rows.append(dict(qid=qid, index=idx, fact_score=round(hits/len(facts), 3), hits=hits,
                         total=len(facts), missing=";".join(l for l, v in got.items() if not v),
                         fuzzy=FUZZY.get(qid, "")))

    idxs = list(dict.fromkeys(r["index"] for r in rows))
    print(f"RUN {run.get('run_id','?')}  |  ANSWER-FACT coverage (concrete atoms only)\n")
    print(f"  {'index':22s} {'fact_score':>11s} {'n':>4s}")
    for idx in idxs:
        rr = [r["fact_score"] for r in rows if r["index"] == idx and r["fact_score"] is not None]
        print(f"  {idx:22s} {round(statistics.mean(rr),3) if rr else '—':>11} {len(rr):>4d}")

    # by category
    q = {r["id"]: r for r in csv.DictReader(open(REPO/"evaluations"/"questions-rfc9110.csv"))}
    cats = list(dict.fromkeys(q[r["qid"]]["category"] for r in rows if r["qid"] in q))
    print("\n  by category:")
    print("  {:26s}".format("") + "".join(f"{i.replace('IDX-','').replace('-rfc9110',''):>12s}" for i in idxs))
    for c in cats:
        line = f"  {c:26s}"
        for idx in idxs:
            rr = [r["fact_score"] for r in rows if r["index"] == idx and r["qid"] in q
                  and q[r["qid"]]["category"] == c and r["fact_score"] is not None]
            line += f"{round(statistics.mean(rr),3) if rr else '—':>12}"
        print(line)

    fuzzy_qs = sorted(set(r["qid"] for r in rows if r["fuzzy"]))
    print(f"\n  ⚠ FUZZY (needs manual/blind confirm, not auto-scored): {', '.join(fuzzy_qs)}")
    out = rj.parent / "answer_facts.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["qid","index","fact_score","hits","total","missing","fuzzy"])
        w.writeheader(); w.writerows(rows)
    print(f"  wrote {out}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

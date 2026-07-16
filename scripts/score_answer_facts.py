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
# GDPR set (evaluations/questions-gdpr.csv). Same discipline: concrete atoms only;
# money/percent regexes tolerate €10,000,000 / 10 000 000 EUR / "10 million" variants.
def eur(n): return [rf"{n}\s?[,. ]?000\s?[,. ]?000", rf"{n} ?million", rf"€\s?{n}\b"]
FACTS.update({
 "GA1": {"10M tier": eur(10), "20M tier": eur(20), "2%": [r"2\s?%"], "4%": [r"4\s?%"],
         "higher-tier scope": ["basic principle", "data subject", "consent", "transfer"]},
 "GA2": {"72 hours": ["72 hours", "72-hour"], "undue delay": ["without undue delay"],
         "reasons for delay": ["reasons? for the delay", "accompanied by (the )?reasons", "justif"]},
 "GA3": {"identified/identifiable": ["identified or identifiable"], "natural person": ["natural person"],
         "identifier examples": [r"\bname\b", "identification number", "location data", "online identifier"]},
 "GA4": {"16": [r"\b16\b"], "13": [r"\b13\b"], "member-state latitude": ["member state", "lower age"]},
 "GB1": {"high risk": ["high risk"], "consult authority": ["consult the supervisory authority", "prior consultation"],
         "before processing": ["prior to (the )?processing", "before (the )?processing"],
         "trigger": ["large scale", "systematic"]},
 "GB2": {"prohibition": ["prohibit"], "explicit consent": ["explicit consent"],
         "second ground": ["occupational medicine", "preventive medicine", "public health", "employment", "vital interests", "substantial public interest"],
         "Art6 lawfulness": ["lawful", "legal bas"]},
 "GB3": {"72 hours": ["72 hours", "72-hour"], "high risk threshold": ["high risk"],
         "encryption exception": ["encrypt", "unintelligible"],
         "disproportionate effort": ["disproportionate effort", "public communication"]},
 "GB4": {"core activities": ["core activities"], "large scale": ["large scale"],
         "dismissal protection": ["dismissed", "penalis", "penaliz"],
         "highest management": ["highest management"]},
 "GB5": {"BCRs": ["binding corporate rules"], "SCCs": ["standard data protection clauses", "standard contractual clauses"],
         "derogations": ["derogation"], "consent derogation": ["explicit(ly)? consent"]},
 "GB6": {"any time": ["at any time"], "not retroactive": ["not affect the lawfulness", "before its withdrawal", "prior processing"],
         "as easy": ["as easy to withdraw"], "erasure": ["erasure", "right to be forgotten"]},
 "GC1": {"particular situation": ["particular situation"], "compelling grounds": ["compelling legitimate grounds"],
         "legal claims": ["legal claims"], "right to object": [r"\bobject"]},
 "GC2": {"explicit consent": ["explicit consent"], "substantial public interest": ["substantial public interest"],
         "suitable measures": ["suitable measures", "safeguard"]},
 "GC3": {"legally binding": ["legally binding"], "every member": ["every member", "all members"],
         "enforceable rights": ["enforceable rights"],
         "specified content": ["structure", "contact details", "complaint"]},
 "GC4": {"(h) care": ["occupational medicine", "preventive medicine", "medical diagnosis", "health or social care"],
         "(i) public health": ["public health"], "cross-border": ["cross-border threats"]},
 "GC5": {"20M/4% tier": eur(20) + [r"4\s?%"], "warnings": ["warning"], "reprimands": ["reprimand"],
         "ban/limitation": ["ban on processing", "limitation", "suspension"]},
 "GD1": {"access": [r"\baccess\b"], "rectification": ["rectif"], "erasure": ["erasure", "forgotten"],
         "restriction": ["restriction"], "portability": ["portability"], "object": [r"\bobject"],
         "automated decisions": ["automated"]},
 "GD2": {"records of processing": ["records? of (its )?processing"], "breach documentation": [r"document\w*\s.{0,40}breach", r"breach\w*\s.{0,40}document"],
         "accountability": ["accountab", "demonstrate compliance"]},
 "GD3": {"complaint (77)": ["lodge a complaint", code(77)], "vs authority (78)": ["against a supervisory authority", code(78)],
         "vs controller (79)": ["against a controller", code(79)], "compensation (82)": ["compensation", code(82)]},
 "GD4": {"codes of conduct": ["codes? of conduct"], "monitoring body": ["monitoring bod"],
         "certification": ["certification"], "certification body": ["certification bod"]},
 "GD5": {"from the subject (13)": ["obtained from the data subject", code(13)],
         "not from the subject (14)": ["not been obtained", "other sources", code(14)],
         "one month": ["one month"]},
 "GE1": {"exempt": ["does not apply", "not apply", "outside", "exempt"], "household": ["household"],
         "purely personal": ["purely personal"]},
 "GE2": {"not covered": ["does not apply", "not apply", "no(t)? protect"], "deceased": ["deceased"],
         "recital location": ["recital"], "member-state latitude": ["member state"]},
 "GE3": {"no fixed period": ["no (specific|fixed|maximum)", "does not (set|specify|prescribe|impose)", "not.{0,20}(specific|fixed|maximum)"],
         "storage limitation": ["storage limitation"],
         "necessity standard": ["no longer than is necessary", "as long as necessary", "necessary for the purposes"]},
 "GE4": {"not governed": ["does not", "not concern", "not apply"], "anonymous": ["anonymous"],
         "recital location": ["recital"]},
})

# relational facts substring-matching can't verify -> flagged, never auto-counted
FUZZY = {
 "RB1": "correct evaluation ORDER of the 5 fields", "RA2": "the definition of idempotent",
 "RB2": "that the intersection (both) is exactly GET+HEAD", "RB3": "if-range match->206 vs no-match->200 logic",
 "RB6": "302/303 method-change contrast", "RD4": "exactly these 7 (no over/under-enumeration)",
 "GB2": "the prohibition-vs-permission structural contrast", "GD1": "exactly the seven rights (over/under-enumeration)",
 "GC5": "that the powers come from 58(2) specifically", "GE3": "recognizing the ABSENCE (no number exists)",
}

def present(ans: str, alts: list[str]) -> bool:
    return any(re.search(p, ans, re.IGNORECASE) for p in alts)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run", required=True)
    ap.add_argument("--questions", default=str(REPO / "evaluations" / "questions-rfc9110.csv"),
                    help="question CSV (for the category breakdown)")
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
    q = {r["id"]: r for r in csv.DictReader(open(args.questions))}
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

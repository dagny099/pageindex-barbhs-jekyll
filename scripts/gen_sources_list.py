#!/usr/bin/env python3
"""Generate a human-readable list of the source documents in the corpus.

Derived view of corpus/site-book-v1/site-book-v1.manifest.json (the authoritative,
machine-readable record). Regenerate after every corpus re-sync:

    python3 scripts/gen_sources_list.py

Writes corpus/site-book-v1/SOURCES.md. The output is stamped with the corpus
SHA256 from provenance.json so drift (list vs. corpus) is detectable at a glance.
"""
from __future__ import annotations

import json
from pathlib import Path

CORPUS_DIR = Path(__file__).resolve().parents[1] / "corpus" / "site-book-v1"
GROUP_ORDER = ["core_pages", "projects", "articles", "resources"]
GROUP_TITLES = {
    "core_pages": "Core Positioning Pages",
    "projects": "Project Portfolio",
    "articles": "Articles",
    "resources": "Resources",
}


def main() -> None:
    manifest = json.loads((CORPUS_DIR / "site-book-v1.manifest.json").read_text())
    provenance = json.loads((CORPUS_DIR / "provenance.json").read_text())
    docs = manifest["documents"]

    by_group: dict[str, list[dict]] = {g: [] for g in GROUP_ORDER}
    for d in docs:
        by_group.setdefault(d.get("group", "other"), []).append(d)

    lines = [
        "# Corpus Source Documents — site-book-v1",
        "",
        "> **Generated** from `site-book-v1.manifest.json` by `scripts/gen_sources_list.py`.",
        "> Do not edit by hand; regenerate after each corpus re-sync. The manifest is",
        "> authoritative. The corpus is produced in the website repo — see `provenance.json`.",
        "",
        f"- Corpus version: `{provenance['corpus_version']}`",
        f"- Corpus SHA256: `{provenance['corpus_sha256'][:16]}…`",
        f"- Source commit: `{provenance['website_commit'][:10]}` "
        f"({provenance['source_repo']})",
        f"- Total documents: **{len(docs)}** "
        f"({', '.join(f'{GROUP_TITLES.get(g, g)} {len(by_group.get(g, []))}' for g in GROUP_ORDER)})",
        "",
    ]

    for group in GROUP_ORDER:
        entries = by_group.get(group, [])
        if not entries:
            continue
        lines.append(f"## {GROUP_TITLES.get(group, group)} ({len(entries)})")
        lines.append("")
        lines.append("| # | Title | Type | Canonical URL | Source path |")
        lines.append("|---|-------|------|---------------|-------------|")
        for i, d in enumerate(entries, 1):
            title = (d.get("source_title") or "—").replace("|", "\\|")
            url = d.get("canonical_url") or "—"
            lines.append(
                f"| {i} | {title} | {d.get('source_type', '—')} | `{url}` | `{d.get('source_path', '—')}` |"
            )
        lines.append("")

    out = CORPUS_DIR / "SOURCES.md"
    out.write_text("\n".join(lines).rstrip() + "\n")
    print(f"Wrote {out} ({len(docs)} documents)")


if __name__ == "__main__":
    main()

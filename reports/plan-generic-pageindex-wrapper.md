# Plan (stub): "Try it yourself" — a generic, publishable PageIndex wrapper

> **Status: growing skeleton, NOT for approval.** No timeline pressure. Timed to land
> *after* Posts 1–3 are drafted, as a companion to publicizing the experiment's results.
> Split out of the recoverable-builds plan (`~/.claude/plans/…giggly-starfish.md`) so it can
> grow across turns. Edit freely; nothing here is committed to yet.

## Intent

Extract the reusable, **non-PageIndex-overlapping** capabilities built in this experiment
harness into a clean, low-friction layer that others can adopt on top of upstream
[PageIndex](https://github.com/VectifyAI/PageIndex). The pitch: *"PageIndex is great at
building reasoning trees over documents; here's a wrapper that makes it safe and observable to
run — you'll appreciate having cost metering, resumable builds, and easy result comparison."*

The value proposition is honesty + operability around an existing tool, not a fork or a
competitor. It should make upstream PageIndex nicer to live with, and defer to it for the
actual indexing/retrieval.

## Candidate extractable features (triage later)

Ranked rough guess at "genuinely generic & valuable" vs "entangled with this experiment":

| Feature | Where it lives now | Generic? | Notes |
|---|---|---|---|
| Cost metering + pre-flight estimate + abort bound | `scripts/build_index_metered.py` | **High** | litellm-patch design is low-coupling; no vendor edits |
| Recoverable/resumable builds (response cache) | `scripts/build_index_metered.py` (this feature) | **High** | strong headline once it lands; content-addressed, vendor-agnostic |
| Honest per-call cost ledger | `scripts/usage_logging.py`, `scripts/cost_report.py` | **High** | provider token-semantics handling is broadly useful, not project-specific |
| Result comparison (explorer / outlines / alignment) | `scripts/render_index_comparison.py` | **Medium** | useful, but tied to this repo's index-condition taxonomy (IDX-D/C/O) |
| Easy retriever/indexer swapping | `scripts/run_retrieval.py`, `config/index-conditions.yml` | **Medium** | the *idea* is generic; the specific conditions are ours |
| Frozen-corpus + provenance-hash discipline | `corpus/*/provenance.json`, build scripts | **Low** | probably too experiment-specific to generalize cleanly |

## Open questions (work through over coming turns)

- **Distribution shape.** Standalone pip package that depends on PageIndex? A template/example
  repo? Upstream PRs adding hooks? (The metering-by-litellm-patch approach is deliberately
  low-coupling — favors a *thin add-on package* that never touches PageIndex source.)
- **Generic vs. entangled.** Which parts survive being lifted out of this experiment's
  corpus/provenance machinery? (See the "Low" rows above — candidates to leave behind.)
- **Minimal viable first release.** Likely: metering + resumable builds + cost report. Comparison
  tooling can follow.
- **Respecting upstream.** Naming, license compatibility, and how docs credit/reference PageIndex.
  Avoid implying endorsement; make the dependency relationship explicit.
- **Config surface.** How much of `config.yaml` / index-conditions to expose vs. hide behind
  sensible defaults for a first-time user.

## Design implications for work happening NOW

Keep the seams clean so extraction stays cheap later:
- Patch litellm only; never edit `vendor/PageIndex/` (already the discipline).
- Content-addressed cache keys; honest `$0` replay accounting (`source:"cache-replay"`).
- Keep metering/estimation/costing free of this repo's corpus-specific assumptions where
  practical, so they lift out without a rewrite.

## Not doing yet

Packaging, naming, README/quickstart, license audit, upstream outreach — all deferred until
after Posts 1–3 and until the recoverable-builds feature has proven itself on the real RFC build.

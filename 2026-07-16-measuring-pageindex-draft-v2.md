---
layout: post
classes: wide
title: "I Measured a RAG Tool Instead of Demoing It"
subtitle: "I gave PageIndex my own documents, inspected what its defaults were actually doing, and ended up with a small study of structure, navigation, grounding, and recurring context cost."
date: 2026-07-16
last_modified_at: 2026-07-16
permalink: /blog/measuring-pageindex/
excerpt: "I started by comparing PageIndex summaries from GPT-4o and a local Ollama model. About 80% were copied source text. That finding changed the experiment."
excerpt_display: true

tags: [AI, RAG, PageIndex, evaluation, retrieval, LLM, knowledge-legibility, information-architecture]
stack: [PageIndex, Python, OpenAI, Anthropic, Ollama, PyMuPDF]
categories: [data-science]

---

<!--
PUBLISHING NOTES
- Recommended hero concept: a document tree with “summary” cards that reveal repeated source text, alongside the path taken by the navigator.
- The three figures currently load from the experiment repository. For long-term site ownership, copy them into /assets/images/pageindex/ and replace the raw GitHub URLs.
- Confirm the publication date and add header.overlay_image when the hero asset is ready.
-->

## Contents

1. [I started with one comparison](#i-started-with-one-comparison)
2. [Most of the summaries were copied text](#most-of-the-summaries-were-copied-text)
3. [I separated the pipeline into four stages](#i-separated-the-pipeline-into-four-stages)
4. [Model choice moved the results more than the summary setting](#model-choice-moved-the-results-more-than-the-summary-setting)
5. [Real summaries helped on the website](#real-summaries-helped-on-the-website)
6. [Authored structure was hard to beat](#authored-structure-was-hard-to-beat)
7. [RFC 9110 reversed the result](#rfc-9110-reversed-the-result)
8. [The limits of this experiment](#the-limits-of-this-experiment)
9. [Why I filed the upstream issue](#why-i-filed-the-upstream-issue)
10. [What I would measure on a production team](#what-i-would-measure-on-a-production-team)
11. [Next: GDPR](#next-gdpr)

## I started with one comparison

I started with a small question: if I built the same PageIndex tree with GPT-4o and a local model running through Ollama, how different would the node summaries be?

[PageIndex](https://github.com/VectifyAI/PageIndex) takes a document, builds a hierarchical tree over it, and gives that tree to an LLM agent. The agent navigates the hierarchy and fetches the sections it thinks it needs. The approach avoids embedding search and preserves more of the document’s visible structure.

I wanted enough hands-on experience to understand how that worked. My own website was a useful first corpus because I know where the evidence lives. I know which projects actually use knowledge graphs, which pages describe the same work differently, and which numbers remain placeholders. A plausible answer would be easier to challenge because I already knew the source material.

I froze 26 pages of [barbhs.com](https://barbhs.com) into one Markdown “site book,” about 27,700 words arranged into 339 tree nodes. I also froze 14 questions covering direct lookup, cross-section synthesis, consistency, evidence gaps, and reflective discovery.

Then I built two summary-bearing indexes. One used GPT-4o. The other used a local Qwen 2.5 7B model through Ollama.

I opened the comparison view expecting ordinary model differences: more compression from one, more detail from the other, perhaps some awkward local-model phrasing.

Most of the summaries matched the source text exactly.

## Most of the summaries were copied text

In the GPT-built index, 273 of 339 node summaries were byte-for-byte copies of the node text. The Ollama-built index produced 272 copied summaries.

About **80% of the “summaries” were copied source text** in both conditions.

The behavior comes from PageIndex’s Markdown summary threshold. By default, a node must exceed 200 tokens before the model summarizes it. Shorter nodes skip the model call and place the original text in the `summary` field.

Avoiding a model call for a short section is a reasonable optimization. The output artifact still matters. A user who enables node summaries receives an index where most nodes carry a field named `summary`, even though that field often contains the full text. The command-line help identifies the threshold as Markdown-only, but it does not explain the copy behavior below the threshold. The PDF path follows different rules and generates summaries for every node.

The copied text also changed the cost of navigation. PageIndex removes each node’s `text` field before giving the tree to the navigator, explicitly to reduce tokens. When the same text remains in `summary`, that saving disappears.

The resulting tree sizes were:

- headings only: about **8,900 tokens**
- real summaries on every node: about **35,500 tokens**
- default summaries, mostly copied text: about **43,700 tokens**

PageIndex sends the tree to the navigator again on every agent turn. A larger tree therefore creates a recurring input cost for each question and each navigation step.

<figure>
  <img src="https://raw.githubusercontent.com/dagny099/pageindex-barbhs-jekyll/main/reports/figures/results-tree-tax.svg" alt="Comparison of recurring tree-context tokens for headings-only, real-summary, and default-summary PageIndex conditions across the website and RFC corpora.">
  <figcaption><strong>Recurring tree context.</strong> The navigator receives the tree on each agent turn. The default summary condition was larger than the condition containing a real generated summary for every node. Source: <a href="https://github.com/dagny099/pageindex-barbhs-jekyll/blob/main/reports/RESULTS.md">consolidated experimental results</a>.</figcaption>
</figure>

At that point, a simple demo would have hidden the most useful part of the exercise. The system ran. It answered questions. Its intermediate artifact showed that my named experimental condition did not mean what I thought it meant.

I expanded the experiment around that discrepancy.

## I separated the pipeline into four stages

I organized the system as four inspectable stages:

> **representation → tree → navigation → synthesis**

**Representation** is the material the tool receives. File format is only one part of it. Extraction quality, page boundaries, headings, bookmarks, and character corruption all shape the document available to the rest of the pipeline.

**Tree** is the navigational artifact built over that representation. It can come from authored headings, embedded PDF bookmarks, an LLM-inferred hierarchy, generated summaries, or some combination.

**Navigation** is the agent’s retrieval behavior. It includes which branches the model follows, which sections it fetches, how many attempts it makes, and whether it retrieves primary text at all.

**Synthesis** is the final answer produced from the tree and the fetched evidence.

This decomposition gave each failure somewhere to land. A broken statistic in extracted PDF text belongs to representation. A missing section number belongs to the tree. A fluent answer produced without a content fetch belongs to navigation. A contradiction smoothed over after both versions were retrieved belongs to synthesis.

The experiment grew around those distinctions. I froze the corpora and question sets, saved named index conditions, recorded retrieval traces, and captured token use, latency, fetched content, and estimated cost. For the RFC comparison, I wrote down the predictions before running it.

The representation check paid off on my 2009 *Visual Cognition* paper. PDF extraction converted 39 instances of `p<.001` into `pB.001` and introduced 57 ligature artifacts. Those errors were visible before retrieval evaluation began. Without a separate representation check, a later answer failure could easily have been blamed on the retriever.

The final study included three corpora, 46 frozen questions, and 11 instrumented runs. The measured model spend was **$29.95**. The sample remains small, but the traces were detailed enough to update several decisions about how I would build and evaluate a hierarchical retrieval system.

## Model choice moved the results more than the summary setting

On the website corpus, the navigator model changed answer quality much more than the default summary setting.

Holding the navigator fixed and switching between headings-only and default-summary indexes changed mean answer scores by about a tenth of a point or less on a five-point scale. Holding the index fixed and changing the navigator moved scores by roughly **0.6 to 2 points**.

Claude Sonnet produced effectively identical scores across the headings-only and default-summary indexes for all 14 questions. GPT-4o scored slightly lower with the default summaries.

The retrieval traces explained part of the difference. Sonnet searched more deeply on questions with evidence scattered across the site. It also preserved a source inconsistency that GPT-4o resolved into a cleaner answer. One page said 13 years; another said 14. Sonnet reported the discrepancy.

The local Qwen navigator showed a more serious failure mode. In 15 of 28 runs, it read the tree and never called the content-fetch tool. It produced a general answer from the tree alone and averaged 0.89 out of 5.

Fluency did not reveal the failure. The tool trace did.

For this corpus, the model deciding where to look had more influence than the extra material attached to each node. The site already had strong authored headings, and several questions could be located from those headings alone. A richer tree had limited room to improve direct retrieval.

That result also narrowed the next test. I still had not measured the value of actual summaries because the shipped default had mostly copied text.

## Real summaries helped on the website

I rebuilt the same 339-node tree with the summary threshold set to zero. Every node received a generated GPT-4o summary. I called this condition `IDX-C0`.

I compared three indexes using the same GPT-4o navigator:

1. authored headings with no summaries;
2. the default summary behavior, with about 80% copied text;
3. generated summaries on every node.

The real-summary condition produced the highest website score: **4.54 out of 5**, compared with **4.11** for the default summary condition and **3.82** for headings alone.

It also cost less than the default. The 14-question run cost **$2.69** with real summaries and **$3.29** with the copied-text default. Actual compression reduced the recurring tree context enough to save 18%.

The gains concentrated in cross-section synthesis and reflective discovery. Direct-location questions were near ceiling across all three indexes.

The evidence-gap questions exposed a different effect. One source section contained three bracketed placeholder statistics. The default-summary run presented them as actual values. The headings-only and real-summary runs both recognized that the evidence was incomplete.

<figure>
  <img src="https://raw.githubusercontent.com/dagny099/pageindex-barbhs-jekyll/main/reports/figures/results-website-quality-cost.svg" alt="Website corpus comparison of answer quality and retrieval cost for headings-only, default-summary, and real-summary PageIndex indexes.">
  <figcaption><strong>Website comparison.</strong> The real-summary condition scored highest and cost less than the copied-text default. Headings remained the lowest-cost condition.</figcaption>
</figure>

These scores come from one comparative run with one model judge and a zero-to-five rubric. I treat them as directional. They still corrected the first-pass conclusion. Generated summaries helped on this corpus once the index actually contained generated summaries.

The experiment then needed a document where headings alone had less chance of carrying the retrieval task.

## Authored structure was hard to beat

The document formats introduced another variable: the source may already contain a useful hierarchy.

The website’s Markdown headings produced a deterministic tree with no model calls. RFC 9110 also carried an authored hierarchy. Its PDF included an embedded outline with 311 entries, and those titles matched the Markdown section tree 311 out of 311.

PageIndex’s native PDF path did not use that outline. It spent **$6.44** to infer a 474-node tree and generate summaries over it. The inferred tree dropped the numbered section labels used by the evaluation set and introduced more structural noise than the embedded outline.

This changed how I framed the representation comparison. “PDF versus Markdown” bundled together several differences. The useful variable was how the hierarchy entered the system.

I built a page-addressed PDF index directly from the embedded outline and compared it with the line-addressed Markdown index. Both used the same 311 section titles.

The Markdown condition reached 0.906 recall. The PDF-outline condition reached 0.821 at nearly identical cost. Some of the remaining gap came from retrieval granularity: a PDF page can span more than one section, while the Markdown index addresses exact line ranges.

The larger result came before retrieval. The specification already contained a high-quality map. Extracting it cost essentially nothing. Inferring a replacement cost $6.44 and produced a less useful artifact for this evaluation.

Headings, bookmarks, section IDs, and article numbers carry decisions made by the document’s author or publisher. I would inspect those signals before asking a model to reconstruct the hierarchy.

## RFC 9110 reversed the result

I selected RFC 9110 for the summary test because it is harder to navigate than the website. The 194-page specification has a deep hierarchy, precise normative language, scattered evidence, and many cross-references.

The evaluation set contained 24 questions with gold section labels. Four were single-hop controls. The remaining questions tested multi-hop synthesis, cross-reference resolution, scattered enumeration, and boundary or absence claims.

The comparison held the 311-node tree and GPT-4o navigator fixed. One index had headings only. The other added a generated summary to every node.

I preregistered the expectation that summaries would improve recall on the hard questions by at least 0.15.

Recall moved in the other direction.

The headings-only index reached **0.918 recall** across the scorable questions. The summary-bearing index reached **0.687**. Recall fell in every hard category, with the largest drop on scattered-enumeration questions.

The 24-question run cost **$1.30** with headings and **$6.01** with summaries.

<figure>
  <img src="https://raw.githubusercontent.com/dagny099/pageindex-barbhs-jekyll/main/reports/figures/results-rfc-recall.svg" alt="RFC 9110 retrieval results showing lower recall and higher cost with generated node summaries, plus a representation comparison with structure held constant.">
  <figcaption><strong>RFC 9110 comparison.</strong> Generated summaries reduced gold-section recall and increased retrieval cost by 4.6 times.</figcaption>
</figure>

Final answer fact scores were almost unchanged: 0.946 for headings and 0.948 for summaries.

The retrieval traces explain how those results can coexist. With summaries in the tree, the agent could answer many questions from generated paraphrases without fetching the specification sections that contained the authoritative text. The final answer retained most required facts while its primary-text grounding weakened.

That tradeoff matters for a normative document. A paraphrase can omit a condition, soften a requirement, or collapse distinctions that the source treats carefully. The summary-bearing system cost 4.6 times as much and relied less on the language I wanted it to retrieve.

Across the two main corpora, generated summaries produced different outcomes:

- Website: higher judged answer quality, especially for synthesis and discovery questions.
- RFC 9110: lower primary-section recall with nearly unchanged fact scores.

The experiment supports a narrower conclusion than “summaries help” or “summaries hurt.” Their value depended on the corpus, question type, evaluation target, and tolerance for generated paraphrase in place of primary text.

## The limits of this experiment

Several claims remain outside the evidence.

I did not run a conventional vector-RAG baseline, so this study does not compare PageIndex with embedding retrieval.

The navigator comparison covers a small question set and fixed prompts. It does not establish a general ranking among GPT-4o, Claude Sonnet, and Qwen.

The website quality scores rely on one judge pass and no statistical replication. They identify useful patterns for follow-up testing.

The RFC recall metric measures whether the navigator fetched the gold sections. It does not capture every way a summary could improve answer wording or user experience.

The deterministic outline result also depends on documents that expose authored structure. Many PDFs have no bookmarks, weak headings, or poor extraction. Those documents may benefit more from inferred structure.

Most important, two main corpora cannot establish a stable rule by document genre. The website and RFC results identify a variable worth testing. They do not settle it.

## Why I filed the upstream issue

I confirmed the threshold behavior in the current upstream code and searched for an existing report. Then I filed [PageIndex issue #355](https://github.com/VectifyAI/PageIndex/issues/355) with the reproduction, corpus counts, and downstream token effect.

The threshold is a sensible place to reduce build cost. The issue is that the emitted `summary` field does not distinguish copied text from generated summary, and the help text does not describe that behavior. Possible remedies include documenting the semantics, leaving short-node summaries empty, or changing how the navigator’s tree is serialized.

A public issue gives the maintainers a reproducible case and gives readers a source outside this article. It also keeps the boundary clear between PageIndex behavior and the code I added around it.

## What I would measure on a production team

This experiment changed the review checklist I would use for a retrieval system.

### Inspect the generated artifact

Open the index. Compare generated fields with source text. Count copied, empty, duplicated, and unusually long values. A successful build only confirms that the pipeline completed.

### Track recurring context

Record the tokens sent on every navigation turn. Index-build cost is easy to see because it happens as a discrete job. A large tree included in every prompt can dominate the cost after deployment.

### Preserve authored structure

Extract headings, bookmarks, article numbers, section IDs, and other document metadata before introducing model-inferred structure. These signals are cheap, inspectable, and often more faithful to the source.

### Score retrieval and synthesis separately

Save the tool trace and record which source sections were fetched. Then score the final answer. A strong synthesis model can hide weak navigation, especially when generated summaries already contain enough information to compose a plausible response.

### Match the metric to the document

For a personal website, judged completeness and usefulness may be appropriate. For a technical standard or legal text, primary-source retrieval deserves its own metric. The evaluation target should reflect the cost of a missing condition or softened requirement.

## Next: GDPR

The next corpus is the General Data Protection Regulation.

GDPR gives the experiment a different kind of structure. Its obligations sit in articles; its interpretive context often sits in recitals. Definitions and exceptions create long cross-reference chains. The official HTML exposes that hierarchy clearly, while the PDF I acquired does not provide the same embedded outline that made RFC 9110 inexpensive to structure.

The next evaluation will ask whether inferred structure earns its cost when the PDF does not carry a ready-made map. It will also test whether generated summaries reduce primary-text retrieval in legal prose, and how retrieval should be scored when a complete answer requires both an operative article and its relevant recitals.

I understand PageIndex better after this experiment than I would have after producing a polished demo. I know which representation entered the pipeline, how the tree was built, what the navigator fetched, and how much context the system resent along the way.

That level of inspection is what lets me decide whether a retrieval design is useful for the document in front of me.

---

The [experiment repository](https://github.com/dagny099/pageindex-barbhs-jekyll) includes the frozen corpora, index conditions, retrieval harness, question sets, run artifacts, and figures. The detailed evidence layer is in the [consolidated results](https://github.com/dagny099/pageindex-barbhs-jekyll/blob/main/reports/RESULTS.md). The summary-threshold mechanism is documented in a separate [finding note](https://github.com/dagny099/pageindex-barbhs-jekyll/blob/main/reports/findings-summary-threshold.md). The RFC comparison was specified in advance in the [summary-test design](https://github.com/dagny099/pageindex-barbhs-jekyll/blob/main/reports/design-rfc-summary-test.md).

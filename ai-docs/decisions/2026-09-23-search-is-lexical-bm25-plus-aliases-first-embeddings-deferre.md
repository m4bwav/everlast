---
title: Search is lexical (BM25 plus aliases) first; embeddings deferred
kind: decision
status: active
date: 2026-09-23
verified: 2026-09-23
stale_after: 2027-03-22
tags: [search, retrieval, benchmark]
aliases: [semantic search, vector search, embeddings, meaning-based search]
summary: read before adding embeddings or a vector index to everlast search, or when a reworded query finds nothing
agent: claude-code
---

# Search is lexical (BM25 plus aliases) first; embeddings deferred

## Context
The index lists titles, tags and one-line summaries, so an agent finds an entry only when it thinks of the words the entry's author chose; the owner named this gap on 2026-09-23 ("no meaning-based search"). The options were plain grep, BM25 over the entry fields, embeddings (a local model or an API), or a hybrid of lexical and embedding search with a reranker. Everlast runs as one stdlib Python file on Windows, macOS and Linux, inside hooks with a 10 s budget.

## Decision
`everlast.py search` is BM25 over each entry's fields (title and `aliases` x3, tags and summary x2, body x1) with light suffix stemming and identifiers kept whole, stdlib only; entries gain an optional `aliases` frontmatter field for their other names. Embeddings are deferred.

## Reasons
- The 2026 evidence favours lexical search at this scale: a PwC study (2026-05-14) found grep beat vector search in 8 of 8 harness and model pairs when results came back inline (93.1 against 75.9 for Codex with GPT-5.4) and lost only when results came back as files; Cursor measured +12.5% from adding semantic search on top of grep, not instead of it; Anthropic's contextual retrieval cut failed retrievals 49% with hybrid BM25 plus embeddings and 67% with a reranker, gains shown on corpora far larger than a doc set (plugin RESEARCH.md R-20260923-3).
- Portability: an embedding model or API adds a dependency, a download or a network call, and often a key, to every install and every hook.
- Aliases put the other names a future agent will search for (the exact error text, the tool's own words) next to the title, which is where a doc set of tens to hundreds of entries misses.
- It is measured: on the benchmark in `bench/` (T-20260923-1) search reached Recall@3 0.93 against 0.61 for an index scan, and 0.70 on paraphrases.

## Rejected alternatives
- Embeddings now: a dependency and a model download or network call on every install, for a gain the evidence shows mainly as an addition to lexical search on larger corpora.
- Grep only: no ranking, no field weights, no stemming, and the agent already has grep.
- Hybrid search with a reranker: the right end state for a large vault, premature for this one.

## Consequences
A paraphrase that shares no word with an entry's title, aliases, tags, summary or body is missed (3 of 10 on `bench/`). Revisit when either trigger fires: paraphrase Recall@3 on `bench/` or on the planned external score (LongMemEval-V2 or a STALE-style probe; RESEARCH.md Open questions) falls below 0.6, or a real doc set's index has split by folder more than twice. The revisit adds embeddings as an optional layer on top of BM25 (hybrid), keeps the stdlib path working without it, and records a new decision that supersedes this one.

Related: see also [the benchmark](../../bench/README.md)

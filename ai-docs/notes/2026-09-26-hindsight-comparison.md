---
title: Hindsight (vectorize-io) compared with Everlast and Evergreen
kind: note
summary: read before adding embeddings, entities, a database, or other memory-system features
status: active
date: 2026-09-26
stale_after: 2027-03-26
tags: [research, retrieval, memory, competitor]
---

# Hindsight compared with Everlast and Evergreen

Source: https://github.com/vectorize-io/hindsight (MIT, about 32.7k stars on 2026-09-26), paper arXiv:2512.12818. Only the README and abstract were read; the paper PDF and source code were not.

## Summary
Hindsight is a popular memory server; its cheap ideas landed in 0.5.0, a database is not worth it at our scale.

## What Hindsight is
A memory service for agents running on Postgres with pgvector. It has three verbs: retain (an LLM extracts facts, entities and absolute dates), recall (vector, BM25, entity-graph and time-range search in parallel, merged with RRF and reranked by a cross-encoder) and reflect (synthesis). It keeps evidence (world facts, experiences) apart from inference (observations, opinions). Consolidated observations carry their supporting evidence and a proof count. It has banks per agent, an MCP endpoint per bank, Python/TS/Go SDKs, and claims 91.4% on LongMemEval and 89.6% on LoCoMo.

## What Everlast and Evergreen lack
1. Semantic retrieval. We use BM25 only, and paraphrase Recall@3 is 0.70. Embeddings were deferred by an earlier decision.
2. An entity layer: no canonical entities, per-entity summaries or entity links.
3. Time-range recall: we have staleness dates but no "what did we learn in August" query.
4. An explicit evidence/inference split with proof counts on consolidated beliefs.
5. An external benchmark: LongMemEval and LoCoMo are planned but not built.
6. MCP/API access: we have only files and a CLI.

## What we have that Hindsight lacks
Proof commands re-run through verify, staleness and recheck on cited-file drift, typed supersede and contradiction links, privacy routing to the sidecar, plain portable markdown that needs no server, and Evergreen's research refresh and skill testing.

## Candidate adoptions
- Done in 0.5.0 (C-20260926-4), low cost, keeps stdlib: `search --since/--until`; an `entities:` frontmatter field plus `search --entity`; `evidence:`/`proof_count` on consolidated notes; merge-suggestions in maintain.
- Medium: optional embeddings behind a flag with RRF fusion (revisits the deferral decision); a LongMemEval-style bench adapter.
- Out of scope (conflicts with no-server design): Postgres, hosted banks, LLM wrapper.

## Would a database beat a graph of markdown files for an LLM?
Not at this scale. The agent reads text through the same tools either way. A database pays off when the store gets too big to scan, when many writers hit it at once, or when vector search is needed. Hindsight is built for thousands of memories across many users; a project doc set holds tens to hundreds. Markdown keeps diffs, git history, Obsidian and every agent product without a server. If one is ever needed, the path is a derived, rebuildable cache (SQLite with FTS5 plus optional vectors, gitignored and regenerated from the files), never the source of truth. Triggers to revisit: a doc set past about 1,000 entries, search taking over a second, or paraphrase Recall@3 staying below 0.8 once the external benchmark exists.

# bench: a retrieval and staleness benchmark for an Everlast doc set

`python scripts/bench_everlast.py [--json] [--misses] [--today 2026-09-23]` (stdlib only, about half a second) asks 41 questions of a synthetic doc set and scores two ways of finding the answer. `scripts/test_everlast.py` runs it on every self-test and fails when `search` drops below the floor set from the first run. Results and their history: [../TESTS.md](../TESTS.md); the summary is in [../README.md](../README.md) (Benchmark).

## What it measures

- index scan (the baseline): the distinct query words found on each generated `INDEX.md` line (title, flags, tags, summary), ties broken in index order. This is what an agent can match by reading the index word for word; a real agent also matches synonyms, so the baseline understates it.
- `everlast.py search`: BM25 over title and aliases (weight 3), tags and summary (2) and body (1), light stemming, status-aware (a superseded entry ranks below its successor).
- Both use the same tokenizer and stemmer, so the difference is what each can see and how it ranks.
- Recall@1, Recall@3 and MRR (the first gold entry within the top 10), overall and by query type.
- Staleness: the share of out-of-date entries (superseded, due for a recheck, or holding a per-fact stamp older than the window) in each method's top 3 that carry a flag; and the share of stale probes where the current entry ranks above the out-of-date one.

## How the fixture was built

`fixture/ai-docs/` is 44 entries (21 solutions, 9 decisions, 7 notes, 7 plans) about a fictional game project with a Unity client, a .NET backend, Python tooling and CI, written in the everlast format with frontmatter, in one sitting on 2026-09-23, with `queries.json` written right after it and before the first run. It holds on purpose: entries with and without `stale_after` (the fallback rule), 10 active entries due for a recheck as of 2026-09-23, 4 superseded entries each with its successor, a `contradicts` pair that is still open, aliases on 13 entries, two multi-fact notes with old `(verified ...)` stamps, done and abandoned plans, and a timeless note (`stale_after: never`). Code paths in backticks do not exist (the project is fictional), so `lint` reports dead paths there by design. `fixture/ai-docs/INDEX.md` is the index as generated on 2026-09-23; the script regenerates it in memory, so a changed index format cannot skew the score.

Query types, and the rule `bench_everlast.py` checks before scoring (it exits 1 when one is broken):

| type | n | rule |
|---|---|---|
| title | 8 | words taken from the gold entry's title |
| paraphrase | 10 | no stem shared with the gold entry's title or tags (checked) |
| error | 7 | an exact error string, as a user would paste it |
| alias | 5 | every word appears only in the gold entry's aliases (checked) |
| tag | 5 | the words are tags of the gold entry and not in its title (checked) |
| stale | 6 | a current entry and an out-of-date one on the same subject; the current one must rank first and the other must be flagged |

Two mistakes were caught before any score existed: `everlast.py lint` found a supersede link with the wrong file name in the fixture (fixed), and the query check found that "SteamAPI_Init failed" was first labelled alias, but its camel-case part "Steam" is in the title, so it became an error query and "earbuds popping" took the alias slot (41 queries instead of 40). No entry or query was changed after the first scores were seen.

## Read this before quoting a number

The fixture, the queries and the method were written by the same team, in the same session, with knowledge of how `search` works. The numbers are a regression floor that catches a change for the worse; they are not evidence that lexical search matches RAG, embeddings or a person, and they say nothing about a doc set of thousands of entries. The paraphrase misses are the honest signal: lexical search finds a reworded question only when the body happens to use the user's words. An external score, an adapter that runs LongMemEval-V2 or a STALE-style probe against an Everlast doc set, is planned in [../RESEARCH.md](../RESEARCH.md) (Open questions).

## Adding to it

Add entries and queries together, run once, and record the run in `TESTS.md` before looking for ways to improve the score; never edit an entry or a query to make a method pass. Keep the date fixed (`queries.json` `today`) so staleness stays reproducible. Raise `BENCH_FLOOR_R3` in `scripts/test_everlast.py` only with a `T-` entry that shows the new level.

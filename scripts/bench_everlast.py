#!/usr/bin/env python3
"""Benchmark: does an agent find the right entry, and is knowledge that went out of date flagged?

python scripts/bench_everlast.py [--json] [--today 2026-09-23] [--fixture DIR] [--queries FILE] [--misses]

Compares two ways of finding an entry in a synthetic doc set (bench/fixture/ai-docs, 44 entries, 40 queries):
  index   an index-only baseline: the distinct query words found on each INDEX.md line (title, flags, tags, summary),
          ties in index order; what an agent scanning the index can match word for word
  search  `everlast.py search`: BM25 over title, aliases, tags, summary and body, status-aware
Both use the same tokenizer and light stemming, so the difference is what each can see and how it ranks.

Reports Recall@1, Recall@3 and MRR (first gold entry within the top 10), overall and by query type, and two staleness
measures: the share of stale or superseded entries in the top 3 that carry a flag, and the share of stale probes
where the current entry ranks above the out-of-date one. The fixture and the date are fixed, so the numbers are
reproducible. The fixture was written by the same team as the method: a regression floor, not evidence against RAG
or embeddings (bench/README.md). Stdlib only; exits 1 when a query breaks its type's rule (checked below).
"""
import argparse
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.dirname(HERE)


def load_everlast():
    spec = importlib.util.spec_from_file_location("everlast_bench_module", os.path.join(HERE, "everlast.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def out_of_date(ev, meta, body, on):
    """The flags an entry deserves on this date: superseded, recheck due, stale facts."""
    flags = set()
    if (meta.get("status") or "active") == "superseded":
        flags.add("superseded")
    if ev.is_stale(meta, on):
        flags.add("recheck due")
    if ev.stale_stamps(meta, body, on):
        flags.add("stale facts")
    return flags


def rank_index(ev, index_lines, query):
    """(relpath, shown flags) best first: distinct query tokens found on the line, ties in index order."""
    q = set(ev.tokenize(query))
    scored = []
    for order, (rel, visible, shown) in enumerate(index_lines):
        s = len(q & visible)
        if s:
            scored.append((-s, order, rel, shown))
    scored.sort()
    return [(rel, shown) for _, _, rel, shown in scored]


def rank_search(ev, root, query, on):
    hits, _ = ev.search_entries([(root, lambda p: os.path.relpath(p, root).replace("\\", "/"))], query, on)
    return [(h["path"], set(h["flags"])) for h in hits]


def index_lines(ev, root, on):
    """(relpath, tokens an agent sees on the line, flags shown) for each entry line of INDEX.md as generated on `on`."""
    text, _ = ev.index_text(root, on)
    out = []
    for line in text.splitlines():
        m = re.match(r"- (\S+) \[(.*)\]\(([^)]+)\)(.*)$", line)
        if m:
            rest = m.group(4)
            shown = {f for f in ("recheck due", "superseded") if f"({f})" in rest}
            out.append((m.group(3), set(ev.tokenize(m.group(2) + " " + rest)), shown))
    return out


def check_queries(ev, entries_by_rel, queries):
    """Each query obeys its type: paraphrase shares no stem with the gold title or tags; alias words appear only in
    the gold aliases; tag words appear in the tags and not the title."""
    problems = []
    for q in queries:
        words = set(ev.tokenize(q["query"]))
        for g in q["gold"] + q.get("stale", []):
            if g not in entries_by_rel:
                problems.append(f"{q['id']}: {g} is not in the fixture")
        if problems:
            continue
        meta, body = entries_by_rel[q["gold"][0]]
        f = ev.search_fields(meta, body)
        title, tags, aliases = set(ev.tokenize(f["title"])), set(ev.tokenize(f["tags"])), set(ev.tokenize(f["aliases"]))
        rest = set(ev.tokenize(f["summary"] + " " + f["body"]))
        if q["type"] == "paraphrase" and words & (title | tags):
            problems.append(f"{q['id']}: paraphrase shares {sorted(words & (title | tags))} with the gold title or tags")
        if q["type"] == "alias" and (not words <= aliases or words & (title | tags | rest)):
            problems.append(f"{q['id']}: alias words must appear only in the gold aliases")
        if q["type"] == "tag" and (not words <= tags or words & title):
            problems.append(f"{q['id']}: tag words must be in the tags and not the title")
    return problems


def evaluate(ranked, queries):
    n = len(queries)
    r1 = r3 = mrr = 0.0
    misses = []
    for q in queries:
        ids = [rel for rel, _ in ranked[q["id"]]]
        pos = next((i for i, rel in enumerate(ids[:10]) if rel in q["gold"]), None)
        if pos is None:
            misses.append(q["id"])
            continue
        mrr += 1.0 / (pos + 1)
        r1 += pos == 0
        r3 += pos < 3
        if pos >= 3:
            misses.append(q["id"])
    return {"recall_at_1": round(r1 / n, 3), "recall_at_3": round(r3 / n, 3), "mrr": round(mrr / n, 3), "n": n, "misses_at_3": misses}


def staleness(ranked, queries, truth):
    flagged = total = 0
    for q in queries:
        for rel, shown in ranked[q["id"]][:3]:
            due = truth.get(rel) or set()
            if due:
                total += 1
                flagged += bool(due & shown)
    probes = [q for q in queries if q["type"] == "stale"]
    ahead = 0
    for q in probes:
        ids = [rel for rel, _ in ranked[q["id"]]]
        g = next((ids.index(r) for r in q["gold"] if r in ids), None)
        s = next((ids.index(r) for r in q["stale"] if r in ids), None)
        ahead += g is not None and (s is None or g < s)
    return {"flagged": flagged, "out_of_date_in_top3": total, "flagged_share": round(flagged / total, 3) if total else None,
            "current_first": ahead, "stale_probes": len(probes), "current_first_share": round(ahead / len(probes), 3) if probes else None}


def pct(x):
    return "n/a" if x is None else f"{x * 100:.0f}%"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--today", default=None, help="the benchmark date (default: the queries file's, 2026-09-23)")
    ap.add_argument("--fixture", default=os.path.join(PLUGIN, "bench", "fixture", "ai-docs"))
    ap.add_argument("--queries", default=os.path.join(PLUGIN, "bench", "queries.json"))
    ap.add_argument("--misses", action="store_true", help="also list each method's misses with the ranks")
    a = ap.parse_args()
    ev = load_everlast()
    spec = json.loads(ev.read(a.queries))
    queries = spec["queries"]
    on = ev.parse_date(a.today or spec.get("today") or "2026-09-23")
    root = os.path.abspath(a.fixture)
    entries_by_rel = {rel: (meta, body) for rel, meta, body in ev.entries(root)}
    problems = check_queries(ev, entries_by_rel, queries)
    if problems:
        print("bench: the queries break their own rules:\n  " + "\n  ".join(problems))
        sys.exit(1)
    truth = {rel: out_of_date(ev, meta, body, on) for rel, (meta, body) in entries_by_rel.items()}
    lines = index_lines(ev, root, on)
    ranked = {"index": {q["id"]: rank_index(ev, lines, q["query"]) for q in queries},
              "search": {q["id"]: rank_search(ev, root, q["query"], on) for q in queries}}
    types = list(dict.fromkeys(q["type"] for q in queries))
    result = {"fixture": os.path.relpath(root, PLUGIN).replace("\\", "/"), "today": on.isoformat(), "entries": len(entries_by_rel),
              "queries": len(queries), "methods": {}, "by_type": {}, "staleness": {}}
    for m in ("index", "search"):
        result["methods"][m] = evaluate(ranked[m], queries)
        result["staleness"][m] = staleness(ranked[m], queries, truth)
        result["by_type"][m] = {t: evaluate(ranked[m], [q for q in queries if q["type"] == t]) for t in types}
    if a.json:
        print(json.dumps(result, indent=2))
        return
    names = {"index": "index scan (baseline)", "search": "everlast.py search"}
    print(f"Everlast benchmark: {result['entries']} entries, {result['queries']} queries, as of {result['today']} ({result['fixture']}, synthetic)\n")
    print("| method | Recall@1 | Recall@3 | MRR |")
    print("|---|---|---|---|")
    for m in ("index", "search"):
        r = result["methods"][m]
        print(f"| {names[m]} | {r['recall_at_1']:.2f} | {r['recall_at_3']:.2f} | {r['mrr']:.2f} |")
    print("\n| query type | n | index R@3 | search R@3 | index MRR | search MRR |")
    print("|---|---|---|---|---|---|")
    for t in types:
        i, s = result["by_type"]["index"][t], result["by_type"]["search"][t]
        print(f"| {t} | {i['n']} | {i['recall_at_3']:.2f} | {s['recall_at_3']:.2f} | {i['mrr']:.2f} | {s['mrr']:.2f} |")
    si, ss = result["staleness"]["index"], result["staleness"]["search"]
    print("\n| staleness | index | search |")
    print("|---|---|---|")
    print(f"| out-of-date entries in the top 3 that carry a flag | {si['flagged']}/{si['out_of_date_in_top3']} ({pct(si['flagged_share'])}) | {ss['flagged']}/{ss['out_of_date_in_top3']} ({pct(ss['flagged_share'])}) |")
    print(f"| stale probes with the current entry above the out-of-date one | {si['current_first']}/{si['stale_probes']} ({pct(si['current_first_share'])}) | {ss['current_first']}/{ss['stale_probes']} ({pct(ss['current_first_share'])}) |")
    if a.misses:
        for m in ("index", "search"):
            print(f"\n{names[m]} misses at 3:")
            for qid in result["methods"][m]["misses_at_3"]:
                q = next(x for x in queries if x["id"] == qid)
                top = [rel.split("/")[-1][:48] for rel, _ in ranked[m][qid][:3]]
                print(f"  {qid} ({q['type']}) \"{q['query']}\": top 3 {top or 'none'}")


if __name__ == "__main__":
    main()

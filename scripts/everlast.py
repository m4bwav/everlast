#!/usr/bin/env python3
"""everlast.py - deterministic helper for the Everlast Protocol (knowledge that outlives sessions, models and tools).

Pure standard library. Every command fails soft (prints a note, exits 0) unless --strict is given,
so it is safe inside hooks. Descended from aidocs.py (the ai-docs-* skills, absorbed 2026-09-13).

Two tiers, one layout ("a docs root"):
  INDEX.md      generated; one line per entry; the only file an always-on pointer names
  HANDOFF.md    continuity: state, decisions, dead ends, next single action (<= 50 lines)
  log.md        append-only: ## [date] op | title
  decisions/    YYYY-MM-DD-slug.md  (why we chose X)
  solutions/    YYYY-MM-DD-slug.md  (problem, dead ends, fix, verified by)
  plans/        YYYY-MM-DD-slug.md  (living plans)
  notes/        YYYY-MM-DD-slug.md  (anything else worth a page)

  project tier   <repo>/ai-docs/            (mode "repo": committed with the project)
                 <vault>/projects/<slug>/ai-docs/ junctioned to <repo>/ai-docs/ and excluded from git (mode "excluded")
                 <vault>/projects/<slug>/private/ the private sidecar every project has (never in the project repo)
  user tier      <vault>/user/              (about the person, their machines, cross-project lessons; PROFILE.md, ENVIRONMENTS.md)

The vault is a private git repository (EVERLAST_VAULT, everlast.config.json, or ~/everlast-vault).

Commands
  init     <repo> [--root DIR]                 scaffold a docs root (idempotent); adopts existing .md files
  pull     [--dry-run]                 update this clone from the official repository; SessionStart says when it is behind
  contribute [yes|no|status]          asked once at install: may this install open pull requests with its learnings?
  publish  [--if-changed] [--dry-run]  consent-gated draft pull request on the official repository (four log kinds only)
  note     <repo> --kind K --title T [--tags a,b] [--aliases a,b] [--summary "when to read it"] [--stale-after DATE|never]
                  [--body-file F | --stdin] [--supersedes PATH] [--private | --user]
  handoff  <repo> (--body-file F | --stdin) [--private | --user]   replace HANDOFF.md
  index    <repo> [--private | --user]         rebuild INDEX.md (an entry past its stale_after shows "(recheck due)")
  lint     <repo> [--stale-days N] [--all]     budgets, headings, dead paths and links, stale, typed Related, stamps, privacy
  search   "<query>" [<repo>] [--private] [--user] [--all] [-n 5] [--json]   BM25 over title, aliases, tags, summary, body
  recheck  <entry> [<repo>] [--private | --user]   read-only: stale?, cited files changed in git since verified, Verified by
  verify   <entry> [<repo>] [--failed "what broke"] [--note N] [--private | --user]   record a recheck (verified, stale_after, log)
  maintain [<repo>] [--private | --user] [--apply]   report recheck-due, archive, duplicate, contradiction, lint items;
                                               --apply only archives done/abandoned/superseded entries and rewrites links
  log      <repo> --op OP --title T [--private | --user]
  scan     <repo|path> [--json]                privacy scan of a repo-safe root (people, credentials, redact list)
  resolve  <repo> [--private | --user]         print the docs root a write would go to
  project  register <repo> --mode repo|excluded [--sync push|pr|off] [--slug S] [--no-link] [--root DIR]
  project  status <repo> | list
  project  sync <repo> [--if-changed] [--detach] [--pr] [--dry-run]   mode repo: commit the doc root, push when sure, pull request when not
  vault    init [--path P] | status | sync [--if-changed] [--detach] [--message M] | where
  vault    remote [<url> | --create [name]] [--dry-run]   back the vault up: a private repository you name, or one gh creates (--private)
  export   <target> [--copy]                   put the skills under <target>/.agents/skills (junction or copy)
  pack     [--out DIR]                         everlast-protocol-<ver>.zip and everlast-protocol.plugin (Cowork)
  hook     run | install | uninstall | print   Claude Code hooks (plugin hooks.json normally does this)
  promote-scan <repo> [--min-dates 3] [--json] skill candidates from evidence (unchanged from aidocs)
  skill-budget [--context N] [--roots R ...]

EVERLAST_TODAY=YYYY-MM-DD pins "today" (tests and the benchmark; never set it in normal use).
"""
import argparse
import datetime as dt
import difflib
import hashlib
import json
import math
import os
import re
import shutil
import platform
import subprocess
import sys
import tempfile
import zipfile
from urllib.parse import unquote

KINDS = ("decision", "solution", "plan", "note")
DIRS = {"decision": "decisions", "solution": "solutions", "plan": "plans", "note": "notes"}
STRICT = False
PLUGIN_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VERSION = json.load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".claude-plugin", "plugin.json"), encoding="utf-8")).get("version", "0.0.0")  # one source of truth: plugin.json

TEMPLATES = {
    "solution": """## Problem
<What was wrong, with the exact error or symptom.>

## Dead ends
<What looked like the cause and was not, and how each was ruled out. This is the part that saves the next session.>

## Fix
<What actually worked.>

## Verified by
<The command that proves it, and what it printed. Copy-pasteable.>

## Applies when
<Scope: which files, versions, environments. When this stops applying, mark status: superseded.>
""",
    "decision": """## Context
<The forces: what was needed, what constrained the choice.>

## Decision
<One or two sentences.>

## Reasons
<Why this over the alternatives.>

## Rejected alternatives
<Each with the one reason it lost. Prevents relitigating.>

## Consequences
<What becomes easier, what becomes harder, what to revisit and when.>
""",
    "plan": """## Goal
<One sentence.>

## Status
<Where it stands as of the date above.>

## Steps
- [ ] <step>

## Open questions
- <question>

## Next single action
<The one thing to do first when this plan is picked up.>
""",
    "note": """## Summary
<What this page holds and why a future session would want it.>

## Details
<...>
""",
}

REQUIRED_HEADINGS = {
    "solution": ["## Problem", "## Fix", "## Verified by"],
    "decision": ["## Context", "## Decision", "## Reasons"],
    "plan": ["## Goal", "## Status", "## Next single action"],
    "note": ["## Summary"],
}

# Check before use: days from `verified` to `stale_after`, per kind (everlast.config.json "stale_after_days" overrides).
DEFAULT_STALE_DAYS = {"solution": 90, "decision": 180, "note": 120, "plan": 30}
ARCHIVE_DAYS = 90   # done, abandoned and superseded entries older than this move to archive/ (maintain --apply)
RELATED_LABELS = ("supersedes", "superseded by", "contradicts", "builds on", "see also")   # shared with the Evergreen Protocol

INDEX_HEADER = """# Index

Generated by `everlast.py index`; do not hand-edit (edit the entries' frontmatter instead). One line per entry: kind, status, date, title, tags. Load an entry only when its title or tags match the task; when no line matches, `everlast.py search "<terms>"` also reads aliases and bodies. `(recheck due)`: past its `stale_after` date; run `everlast.py recheck <entry>` before acting on it. Continuity for the current work is in [HANDOFF.md](HANDOFF.md); the append-only history is [log.md](log.md).

"""

HANDOFF_TEMPLATE = """# Handoff

<!-- Keep under 50 lines. Replace, never append. Written at the end of a work session so the next one starts without re-deriving state. -->

## Current state
<What is done and verified. Cite files, not line numbers.>

## In progress
<What was being worked on and how far it got.>

## Decisions made this session
<Each with its reason, or a link to decisions/.>

## Dead ends hit
<What was tried and failed, so nobody retries it. Promote to solutions/ if it will recur.>

## Next single action
<One thing. The next session starts here.>
"""

LOG_HEADER = """# Log

Append-only. One line per operation: `## [YYYY-MM-DD] op | title` where op is one of add, update, supersede, verify, verify-failed, prune, handoff, index. Newest at the bottom. Never edited, only appended; this is the history the entries themselves do not carry.

"""

README_TEMPLATE = """# ai-docs

Documentation written for and by AI coding agents, kept modular so a session loads only what its task needs. Entry point: [INDEX.md](INDEX.md) (generated). Continuity: [HANDOFF.md](HANDOFF.md). History: [log.md](log.md). Layers: `decisions/` (why we chose X), `solutions/` (problem, dead ends, fix, verified command), `plans/` (living plans), `notes/` (anything else worth a page). Rules and tooling: the Everlast Protocol (`everlast-setup`, `everlast-capture`, `everlast-resume`, `everlast-vault` skills; `everlast.py`).

What does not go here: rules every session must follow (AGENTS.md), where systems live (CODEMAP.md), anything about the user or their machines (the user tier of the everlast vault), anything naming coworkers or internal politics or credentials (the project's private sidecar in the vault), and anything a grep of the code answers in ten seconds.
"""

VAULT_README = """# Everlast vault

The private, cross-tool record of what AI agents have learned for and about {owner}. Managed by the Everlast Protocol (`everlast.py`); read by any agent that can read markdown. Never shared, never public.

- `user/` the user tier: [user/INDEX.md](user/INDEX.md), `user/PROFILE.md` (how work should be done), `user/ENVIRONMENTS.md` (machines, tools, paths, what works where), plus decisions, solutions, plans, notes that span projects.
- `projects/<slug>/private/` the private sidecar of each project: entries that must not sit in the project's repository (people, politics, credentials, internal names).
- `projects/<slug>/ai-docs/` the whole doc set of a project whose repository cannot hold it (mode `excluded`; junctioned into the project as `ai-docs/` and excluded from its git).
- `registry.json` which projects exist, where, in which mode. `config/redact.txt` patterns the privacy scan treats as private (one per line, regex).

Rules: absolute dates; one entry per problem or decision; nothing derivable from code; everything here may name people and machines, so it stays in this repository only.
"""

PRIVACY_PATTERNS = [
    (r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "email address"),
    (r"\b(?:sk|ghp|gho|ghu|ghs|ghr|xox[baprs])[-_][A-Za-z0-9_-]{16,}", "API token"),
    (r"\bAKIA[0-9A-Z]{16}\b", "AWS access key"),
    (r"(?i)\b(?:password|passwd|pwd|secret|api[_-]?key|token)\s*[:=]\s*\S{6,}", "credential assignment"),
    (r"(?i)\bbearer\s+[A-Za-z0-9._-]{20,}", "bearer token"),
    (r"-----BEGIN [A-Z ]*PRIVATE KEY-----", "private key"),
    (r"(?<![\w/])@[A-Za-z][A-Za-z0-9_.-]{2,}\b", "@handle"),
    (r"\b(?:\+?1[ -.]?)?\(?\d{3}\)?[ -.]\d{3}[ -.]\d{4}\b", "phone number"),
    (r"(?i)\b(?:my|our)\s+(?:manager|boss|coworker|colleague|teammate|director|VP|CEO|CTO)\b", "person by role"),
    (r"(?i)\b(?:blame|blamed|incompetent|lazy|toxic|political|politics|drama|feud)\b", "opinion about people or politics"),
]


def note(msg):
    print(msg)


def fail(msg, code=1):
    print(msg)
    sys.exit(code if STRICT else 0)


def today_date():
    """Today, or EVERLAST_TODAY (YYYY-MM-DD) so tests and the benchmark are reproducible."""
    pinned = (os.environ.get("EVERLAST_TODAY") or "").strip()
    if pinned:
        try:
            return dt.date.fromisoformat(pinned)
        except ValueError:
            pass
    return dt.date.today()


def today():
    return today_date().isoformat()


def slugify(title):
    s = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return s[:60] or "entry"


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def append(path, text):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "a", encoding="utf-8", newline="\n") as f:
        f.write(text)


def load_json(path, default):
    try:
        return json.loads(read(path))
    except Exception:
        return default


# Windows: every git.exe (and the ssh / credential helper it spawns) would otherwise get its own console window
# when the parent has none, which is the case for the detached SessionEnd sync. Evergreen does the same.
NO_WINDOW = 0x08000000 if os.name == "nt" else 0  # CREATE_NO_WINDOW


def run(cmd, cwd=None, timeout=60):
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout, creationflags=NO_WINDOW)
        return out.returncode, (out.stdout or "").strip(), (out.stderr or "").strip()
    except Exception as e:
        return 1, "", str(e)


def status_lines(cwd, pathspec=None):
    """`git status --porcelain` lines with the leading space intact (run() strips its output, which eats the first
    line's unstaged-change marker and shifts the path); None when the command fails."""
    try:
        cmd = ["git", "-c", "core.quotepath=off", "status", "--porcelain", "--untracked-files=all", "--"] + ([pathspec] if pathspec else [])
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60, creationflags=NO_WINDOW)
    except Exception:
        return None
    return [ln for ln in out.stdout.splitlines() if len(ln) > 3] if out.returncode == 0 else None


def author_email(cwd):
    """Whose commits count as the user's own: the identity git would commit with here (config or GIT_AUTHOR_EMAIL)."""
    rc, ident, _ = run(["git", "var", "GIT_AUTHOR_IDENT"], cwd=cwd)
    m = re.search(r"<([^>]*)>", ident) if rc == 0 else None
    return (m.group(1) if m else "").strip().lower()


# ---------------------------------------------------------------- config, vault, registry

def config():
    return load_json(os.path.join(PLUGIN_ROOT, "everlast.config.json"), {})


def vault_path():
    env = os.environ.get("EVERLAST_VAULT") or os.environ.get("EVAL_EVERLAST_VAULT")
    if env:
        return os.path.abspath(os.path.expanduser(os.path.expandvars(env)))
    local = os.path.join(os.getcwd(), ".everlast-vault")   # a workspace-local vault (evals, sandboxes)
    if os.path.isdir(local):
        return local
    v = config().get("vault")
    if isinstance(v, dict):
        v = v.get(os.name) or v.get("posix" if os.name != "nt" else "nt")
    if v:
        if os.name != "nt" and re.match(r"^[A-Za-z]:[\\/]", v):
            v = None
        else:  # expandvars: the shipped Windows default is %USERPROFILE%\everlast-vault (L-004)
            return os.path.abspath(os.path.expanduser(os.path.expandvars(v)))
    return os.path.join(os.path.expanduser("~"), "everlast-vault")


# ---------------------------------------------------------------- contribution choice (asked once at install)
# May this install send the plugin's own learnings back to the official repository as pull requests? The answer lives
# in the user's config dir (never in the plugin tree, which updates replace): %APPDATA%/everlast/settings.json on
# Windows, ~/.config/everlast/settings.json elsewhere. EVERLAST_CONTRIBUTE=yes|no overrides per session; DO_NOT_TRACK=1
# and CI=true count as no. Unanswered means nothing leaves unattended. Same shape as the Evergreen Protocol section 10.

OFFICIAL_REPO = "m4bwav/everlast"
SHAREABLE = ("LEARNINGS.md", "RESEARCH.md", "CHANGELOG.md", "TESTS.md")   # the only files a contribution may carry

CONTRIBUTE_QUESTION = (
    "May this install send the plugin's own learnings back to the official Everlast repository? "
    "'yes': when a skill's LEARNINGS, RESEARCH, CHANGELOG or TESTS file changes here, the diff is pushed as a draft pull "
    "request in your name that the maintainer reviews (those four file kinds only; never your vault, your projects' docs "
    "or transcripts); revoke at any time. 'no': nothing ever leaves this machine (no pull requests, no reports); updates "
    "still arrive with `git pull`. Answer with `everlast.py contribute yes` or `everlast.py contribute no`."
)


def settings_dir():
    if os.name == "nt":
        return os.path.join(os.environ.get("APPDATA") or os.path.join(os.path.expanduser("~"), "AppData", "Roaming"), "everlast")
    return os.path.join(os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config"), "everlast")


def settings_file():
    return os.path.join(settings_dir(), "settings.json")


def contribute_setting():
    """'yes', 'no', or None when the question has not been answered on this install."""
    env = (os.environ.get("EVERLAST_CONTRIBUTE") or "").strip().lower()
    if env in ("yes", "no"):
        return env
    if (os.environ.get("DO_NOT_TRACK") or "").strip() not in ("", "0", "false"):
        return "no"
    if (os.environ.get("CI") or "").strip().lower() in ("1", "true", "yes"):
        return "no"
    v = load_json(settings_file(), {}).get("contribute")
    return v if v in ("yes", "no") else None


def set_contribute(value):
    s = load_json(settings_file(), {})
    s["contribute"] = value
    s["decided_at"] = today()
    s["asked_by_version"] = plugin_version()
    write(settings_file(), json.dumps(s, indent=2) + "\n")


def plugin_version():
    return load_json(os.path.join(PLUGIN_ROOT, ".claude-plugin", "plugin.json"), {}).get("version", "0.0.0")


def cmd_contribute(a):
    if a.value in ("yes", "no"):
        set_contribute(a.value)
        print(f"contribute {a.value}: " + ("draft pull requests with this install's learnings are allowed; `contribute no` revokes it"
                                           if a.value == "yes" else "nothing leaves this machine; updates still arrive with `git pull`"))
        return
    v = contribute_setting()
    if v is None:
        print("contribute: not decided on this install. " + CONTRIBUTE_QUESTION)
    else:
        src = "EVERLAST_CONTRIBUTE" if os.environ.get("EVERLAST_CONTRIBUTE") else ("DO_NOT_TRACK/CI" if (os.environ.get("DO_NOT_TRACK") or os.environ.get("CI")) else settings_file())
        print(f"contribute {v} ({src})")


def shareable_changes():
    """Changed or untracked files in the plugin tree that a contribution may carry: the four log kinds, nowhere else."""
    lines = status_lines(PLUGIN_ROOT)
    if lines is None:
        return None
    paths = []
    for ln in lines:
        rel = ln[3:].strip().strip('"').replace("\\", "/")
        if " -> " in rel:
            rel = rel.split(" -> ", 1)[1]
        if os.path.basename(rel) in SHAREABLE and not rel.startswith("ai-docs/"):
            paths.append(rel)
    return paths


def official_remote():
    """The git remote of this clone that points at the official repository: `upstream` on a private fork, `origin`
    on a plain clone, None when neither does (an archive install)."""
    rc, out, _ = run(["git", "remote", "-v"], cwd=PLUGIN_ROOT)
    if rc != 0:
        return None
    for ln in out.splitlines():
        parts = ln.split()
        if len(parts) >= 2 and "(fetch)" in ln:
            url = parts[1].lower().rstrip("/")
            if url.endswith(".git"):
                url = url[:-4]
            tail = "/".join(url.replace(":", "/").split("/")[-2:])  # owner/repo from https or ssh forms, exact match
            if tail == OFFICIAL_REPO.lower():
                return parts[0]
    return None


def behind_official(fetch=False):
    """(remote, commits behind) using the last fetch (or a fresh one when fetch=True); (None, 0) when unknown."""
    rem = official_remote()
    if not rem:
        return None, 0
    if fetch:
        run(["git", "fetch", "-q", rem, "master"], cwd=PLUGIN_ROOT, timeout=60)
    rc, out, _ = run(["git", "rev-list", "--count", f"HEAD..{rem}/master"], cwd=PLUGIN_ROOT)
    return rem, (int(out) if rc == 0 and out.isdigit() else 0)


def cmd_pull(a):
    """Bring this clone up to date from the official repository (a merge on a fork, a fast-forward on a plain clone)."""
    rem = official_remote()
    if not rem:
        print(f"no remote points at {OFFICIAL_REPO}; add one: git remote add upstream https://github.com/{OFFICIAL_REPO}.git"); return
    rc, out, err = run(["git", "status", "--porcelain"], cwd=PLUGIN_ROOT)
    if out.strip() and not a.dry_run:
        print("working tree has changes; commit or stash them first (nothing pulled)"); return
    rem, n = behind_official(fetch=True)
    if n == 0:
        print(f"up to date with {rem}/master ({OFFICIAL_REPO})"); return
    rc, files, _ = run(["git", "diff", "--name-only", f"HEAD...{rem}/master"], cwd=PLUGIN_ROOT)
    reinstall = any(f.startswith(("skills/", "scripts/", "hooks/")) for f in files.splitlines())
    if a.dry_run:
        print(f"behind {rem}/master by {n} commit(s); would merge " + ("(skills/scripts/hooks change: reinstall the cached plugin afterwards)" if reinstall else "")); return
    rc, out, err = run(["git", "merge", "-q", "--no-edit", f"{rem}/master"], cwd=PLUGIN_ROOT, timeout=120)
    if rc != 0:
        print(f"merge failed: {err[:300]} (resolve by hand: keep this side for private files)"); run(["git", "merge", "--abort"], cwd=PLUGIN_ROOT); return
    print(f"merged {n} commit(s) from {rem}/master" + ("; skills, scripts or hooks changed: `claude plugin marketplace update` then uninstall and install so the cached copy picks it up" if reinstall else ""))


def cmd_publish(a):
    """Consent-gated: push this install's plugin learnings as a draft pull request on the official repository."""
    v = contribute_setting()
    unattended = a.if_changed
    if v != "yes":
        if unattended:
            return
        print("contribution is off on this install (`everlast.py contribute yes` to allow pull requests); updates still arrive with `git pull`"
              if v == "no" else "not decided on this install: " + CONTRIBUTE_QUESTION)
        return
    if not shutil.which("git"):
        print("" if unattended else "git is not installed; nothing published"); return
    if not os.path.isdir(os.path.join(PLUGIN_ROOT, ".git")):
        if not unattended: print(f"{PLUGIN_ROOT} is not a git clone; nothing published")
        return
    paths = shareable_changes()
    if not paths:
        if not unattended: print("nothing to publish (only LEARNINGS, RESEARCH, CHANGELOG and TESTS files travel)")
        return
    env = os.environ.get("EVERLAST_ENV") or platform.node() or "host"
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M")
    branch = f"learnings/{re.sub(r'[^A-Za-z0-9._-]+', '-', env)}-{stamp}"
    if a.dry_run:
        print(f"would push {len(paths)} file(s) on {branch} and open a draft pull request on {OFFICIAL_REPO}: " + ", ".join(paths)); return
    rc, head, _ = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=PLUGIN_ROOT)
    for c in (["git", "stash", "push", "-u", "-q", "-m", "everlast publish", "--"] + paths,
              ["git", "checkout", "-q", "-b", branch],
              ["git", "stash", "pop", "-q"],
              ["git", "add", "--"] + paths,
              ["git", "commit", "-q", "-m", f"everlast: learnings from {env} ({', '.join(os.path.basename(p) for p in paths)})"]):
        rc, out, err = run(c, cwd=PLUGIN_ROOT)
        if rc != 0:
            print(f"publish stopped at `{' '.join(c[:3])}`: {err[:200]}"); run(["git", "checkout", "-q", head], cwd=PLUGIN_ROOT); return
    rem = official_remote() or "origin"  # the branch goes to the repository the pull request targets
    rc, out, err = run(["git", "push", "-q", "-u", rem, branch], cwd=PLUGIN_ROOT, timeout=120)
    if rc != 0:
        print(f"push failed: {err[:200]} (branch {branch} kept locally)"); run(["git", "checkout", "-q", head], cwd=PLUGIN_ROOT); return
    body = (f"Learnings from an everlast install on `{env}`, opened with the owner's consent (`everlast.py contribute yes`). "
            f"Files: {', '.join(paths)}. No vault, project docs or transcripts. Reviewer: the repository owner.")
    if shutil.which("gh"):
        rc, out, err = run(["gh", "pr", "create", "--draft", "--repo", OFFICIAL_REPO, "--base", "master", "--head", branch,
                            "--title", f"Learnings from {env} ({stamp})", "--body", body], cwd=PLUGIN_ROOT, timeout=90)
        print(f"pull request: {out or err}"[:300])
    else:
        print(f"pushed {branch}; open the pull request on https://github.com/{OFFICIAL_REPO} by hand (gh is not installed)")
    run(["git", "checkout", "-q", head], cwd=PLUGIN_ROOT)


def registry_path():
    return os.path.join(vault_path(), "registry.json")


def registry():
    return load_json(registry_path(), {"everlast": "1.0", "projects": {}})


def save_registry(reg):
    write(registry_path(), json.dumps(reg, indent=2) + "\n")


def repo_slug(repo):
    base = os.path.basename(os.path.abspath(repo).rstrip("\\/"))
    return slugify(base) or "project"


def find_project(repo):
    """Registry entry for this repo (by path), or None."""
    ap = os.path.normcase(os.path.abspath(repo))
    for slug, p in registry().get("projects", {}).items():
        if os.path.normcase(os.path.abspath(p.get("path", ""))) == ap:
            return slug, p
    return None, None


def docs_root(repo, root="ai-docs", private=False, user=False):
    """The docs root a read or write should use, honouring the tier flags and the registry."""
    if user:
        return os.path.join(vault_path(), "user")
    slug, p = find_project(repo)
    if private:
        return os.path.join(vault_path(), "projects", slug or repo_slug(repo), "private")
    if p and p.get("mode") == "excluded" and p.get("store"):
        return p["store"]
    return os.path.join(os.path.abspath(repo), (p or {}).get("root") or root)


FRONTMATTER_RE = re.compile(r"^---\r?\n(.*?)\r?\n---\r?\n", re.S)


def unquote_yaml(v):
    """A YAML scalar as written by frontmatter(): plain, "double" (backslash escapes) or 'single' ('' escapes)."""
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        inner = v[1:-1]
        return re.sub(r"\\(.)", r"\1", inner) if v[0] == '"' else inner.replace("''", "'")
    return v


def split_yaml_list(inner):
    """Items of a flow list `[a, "b, with comma", 'c']`; commas inside quotes do not split."""
    items, cur, quote, i = [], "", None, 0
    while i < len(inner):
        c = inner[i]
        if quote:
            cur += c
            if c == "\\" and quote == '"' and i + 1 < len(inner):
                cur += inner[i + 1]
                i += 1
            elif c == quote:
                if quote == "'" and inner[i + 1:i + 2] == "'":
                    cur += "'"
                    i += 1
                else:
                    quote = None
        elif c in "\"'" and not cur.strip():
            quote = c
            cur += c
        elif c == ",":
            items.append(cur)
            cur = ""
        else:
            cur += c
        i += 1
    items.append(cur)
    return [unquote_yaml(x) for x in items if x.strip()]


def parse_frontmatter(text):
    m = FRONTMATTER_RE.match(text)
    meta = {}
    if not m:
        return meta, text
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                v = split_yaml_list(v[1:-1])
            else:
                v = unquote_yaml(v)
            meta[k.strip()] = v
    return meta, text[m.end():]


YAML_NEEDS_QUOTES = re.compile(r"^[\[\]{}&*!|>'\"%@`#,?]|^-\s|:\s|:$|\s#|^\s|\s$")


def yaml_scalar(v, in_list=False):
    """Quote only what YAML (Obsidian's properties panel) would misread: `: `, a leading indicator, commas in a list."""
    s = str(v)
    if not s:
        return '""' if in_list else ""
    if YAML_NEEDS_QUOTES.search(s) or (in_list and re.search(r"[,\[\]{}]", s)):
        return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'
    return s


def frontmatter_line(k, v):
    if isinstance(v, list):
        return f"{k}: [" + ", ".join(yaml_scalar(x, in_list=True) for x in v) + "]"
    return f"{k}: {yaml_scalar(v)}".rstrip()


def frontmatter(meta):
    return "\n".join(["---"] + [frontmatter_line(k, v) for k, v in meta.items()] + ["---"]) + "\n"


def set_fields(text, updates, after="verified"):
    """Change or add frontmatter keys in place and leave every other line as it was (a value of None removes the key);
    a new key goes after `after`."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return frontmatter({k: v for k, v in updates.items() if v is not None}) + text
    lines = m.group(1).splitlines()

    def index_of(key):
        for i, ln in enumerate(lines):
            if re.match(r"^" + re.escape(key) + r"\s*:", ln):
                return i
        return None
    for key, val in updates.items():
        i = index_of(key)
        if val is None:
            if i is not None:
                del lines[i]
            continue
        if i is not None:
            lines[i] = frontmatter_line(key, val)
        else:
            j = index_of(after) if after else None
            lines.insert(len(lines) if j is None else j + 1, frontmatter_line(key, val))
    return "---\n" + "\n".join(lines) + "\n---\n" + text[m.end():]


def as_list(v):
    if isinstance(v, list):
        return [str(x) for x in v if str(x).strip()]
    return [str(v)] if v and str(v).strip() else []


def entries(root, archive=False):
    """(relpath, meta, body) for every entry under root, or under root/archive with archive=True."""
    base = os.path.join(root, "archive") if archive else root
    for kind, d in DIRS.items():
        folder = os.path.join(base, d)
        if not os.path.isdir(folder):
            continue
        for name in sorted(os.listdir(folder)):
            if not name.endswith(".md"):
                continue
            p = os.path.join(folder, name)
            meta, body = parse_frontmatter(read(p))
            meta.setdefault("kind", kind)
            meta.setdefault("title", os.path.splitext(name)[0])
            meta.setdefault("status", "active")
            meta.setdefault("date", "")
            yield ("archive/" if archive else "") + d + "/" + name, meta, body


def adopt_loose_files(root):
    out = []
    for name in sorted(os.listdir(root)):
        if not name.endswith(".md") or name in ("INDEX.md", "HANDOFF.md", "README.md", "log.md", "PROFILE.md", "ENVIRONMENTS.md"):
            continue
        p = os.path.join(root, name)
        meta, _ = parse_frontmatter(read(p))
        kind = meta.get("kind") or ("plan" if name.upper().startswith("PLAN") else "note")
        title = meta.get("title") or re.sub(r"[_-]+", " ", os.path.splitext(name)[0]).strip()
        out.append((name, {"kind": kind, "title": title, "status": meta.get("status", "active"),
                           "date": meta.get("date", ""), "tags": meta.get("tags", [])}))
    return out


# ---------------------------------------------------------------- docs root commands

def scaffold(root, readme=README_TEMPLATE):
    os.makedirs(root, exist_ok=True)
    made = []
    for d in DIRS.values():
        p = os.path.join(root, d)
        if not os.path.isdir(p):
            os.makedirs(p)
            made.append(d + "/")
    if not os.path.exists(os.path.join(root, "HANDOFF.md")):
        write(os.path.join(root, "HANDOFF.md"), HANDOFF_TEMPLATE)
        made.append("HANDOFF.md")
    if not os.path.exists(os.path.join(root, "log.md")):
        write(os.path.join(root, "log.md"), LOG_HEADER + f"## [{today()}] init | scaffolded\n")
        made.append("log.md")
    if readme and not os.path.exists(os.path.join(root, "README.md")):
        write(os.path.join(root, "README.md"), readme)
        made.append("README.md")
    build_index(root)
    made.append("INDEX.md")
    return made


def cmd_init(a):
    root = docs_root(a.repo, a.root, getattr(a, "private", False), getattr(a, "user", False))
    made = scaffold(root)
    note(f"docs root ready at {root}: " + (", ".join(made) if made else "nothing to add"))
    adopted = adopt_loose_files(root)
    if adopted:
        note("adopted existing files into INDEX.md (kind inferred; add frontmatter to correct): " + ", ".join(n for n, _ in adopted))


def index_line(date, title, rel, flag, tags, summary):
    tag = (" `" + ",".join(tags) + "`") if tags else ""
    why = f": {summary}" if summary else ""
    return f"- {date or 'undated'} [{title}]({rel}){flag}{tag}{why}"


def entry_flag(meta, on=None):
    """What an index line says after the link: the status when not active, `(recheck due)` when stale, else nothing."""
    status = meta.get("status") or "active"
    if status != "active":
        return f" ({status})"
    return " (recheck due)" if is_stale(meta, on) else ""


def index_text(root, on=None):
    """INDEX.md as generated on the date `on` (default today); returns (text, number of entries)."""
    rows = []
    for rel, meta, _ in entries(root):
        rows.append((meta.get("date", ""), meta["kind"], entry_flag(meta, on), meta["title"], rel, as_list(meta.get("tags")), str(meta.get("summary") or "").strip()))
    for name, meta in adopt_loose_files(root):
        rows.append((meta["date"], meta["kind"], "" if meta["status"] == "active" else f" ({meta['status']})", meta["title"], name, as_list(meta["tags"]), ""))
    rows.sort(key=lambda r: (r[1], r[0]))
    lines = [INDEX_HEADER.rstrip()]
    current = None
    for date, kind, flag, title, rel, tags, summary in rows:
        if kind != current:
            lines.append(f"\n## {DIRS.get(kind, kind)}\n")
            current = kind
        lines.append(index_line(date, title, rel, flag, tags, summary))
    archived = sorted(((m.get("date", ""), m["kind"], entry_flag(m, on), m["title"], rel, as_list(m.get("tags")), str(m.get("summary") or "").strip())
                       for rel, m, _ in entries(root, archive=True)), key=lambda r: (r[1], r[0]))
    if archived:
        lines.append("\n## Archive\n")
        lines.extend(index_line(d, t, rel, f, tg, s) for d, _, f, t, rel, tg, s in archived)
    return "\n".join(lines).rstrip() + "\n", len(rows) + len(archived)


def build_index(root, on=None):
    text, n = index_text(root, on)
    write(os.path.join(root, "INDEX.md"), text)
    return n


def cmd_index(a):
    root = docs_root(a.repo, a.root, a.private, a.user)
    if not os.path.isdir(root):
        fail(f"no docs root at {root}; run init first")
    n = build_index(root)
    if os.path.exists(os.path.join(root, "log.md")):
        append(os.path.join(root, "log.md"), f"## [{today()}] index | rebuilt ({n} entries)\n")
    note(f"INDEX.md rebuilt: {n} entries ({root})")


PRIVATE_BLOCK = re.compile(r"<private>.*?</private>", re.S | re.I)


def strip_private_blocks(text):
    """Remove inline <private>...</private> blocks (the agentmemory convention) from text bound for a repo-safe file."""
    n = len(PRIVATE_BLOCK.findall(text))
    return (PRIVATE_BLOCK.sub("", text) if n else text), n


def privacy_hits(text, redact):
    hits = []
    for pat, label in PRIVACY_PATTERNS:
        for m in re.finditer(pat, text):
            hits.append((label, m.group(0)[:40]))
    for pat in redact:
        try:
            for m in re.finditer(pat, text, re.I):
                hits.append(("redact list", m.group(0)[:40]))
        except re.error:
            continue
    return hits


def redact_list():
    p = os.path.join(vault_path(), "config", "redact.txt")
    if not os.path.exists(p):
        return []
    return [l.strip() for l in read(p).splitlines() if l.strip() and not l.startswith("#")]


def cmd_note(a):
    root = docs_root(a.repo, a.root, a.private, a.user)
    if not os.path.isdir(root):
        if a.private or a.user:
            scaffold(root, readme=None)
        else:
            fail(f"no docs root at {root}; run init first")
    if a.kind not in KINDS:
        fail(f"kind must be one of {KINDS}")
    body = None
    if a.body_file:
        body = read(a.body_file)
    elif a.stdin:
        body = sys.stdin.read()
    if not body or not body.strip():
        body = TEMPLATES[a.kind]
    missing = [h for h in REQUIRED_HEADINGS[a.kind] if h not in body]
    if missing and not a.allow_missing:
        fail(f"body lacks required headings {missing}; pass --allow-missing to write anyway")
    if not (a.private or a.user):
        body, dropped = strip_private_blocks(body)  # inline <private>...</private> never reaches a repo-safe file
        if dropped:
            note(f"  ({dropped} <private> block(s) dropped from the repo-safe copy; write them with --private to keep them)")
    tags = [t.strip() for t in (a.tags or "").split(",") if t.strip()]
    aliases = [x.strip() for x in (a.aliases or "").split(",") if x.strip()] + [x.strip() for x in (a.alias or []) if x.strip()]
    if not (a.private or a.user) and not a.allow_private:
        hits = privacy_hits("\n".join([a.title, a.summary or ""] + aliases + [body]), redact_list())
        if hits:
            fail("privacy scan flagged this entry for the repo-safe root: " + "; ".join(f"{l} ({s})" for l, s in hits[:5])
                 + ". Write it with --private (sidecar), or --allow-private if the reviewer decided it is safe.")
    d = today()
    raw_sa = (a.stale_after or "").strip()
    if raw_sa.lower() == "never":
        stale_after = "never"   # timeless: never due for a recheck
    elif raw_sa:
        if not parse_date(raw_sa):
            fail("--stale-after takes YYYY-MM-DD, or never for a timeless entry")
        stale_after = parse_date(raw_sa).isoformat()
    else:
        stale_after = (today_date() + dt.timedelta(days=window_for(a.kind))).isoformat()
    rel = f"{DIRS[a.kind]}/{d}-{slugify(a.title)}.md"
    path = os.path.join(root, rel)
    if os.path.exists(path) and not a.force:
        fail(f"{rel} exists; use --force to overwrite or choose another title")
    meta = {"title": a.title, "kind": a.kind, "status": "active", "date": d, "verified": d, "stale_after": stale_after, "tags": tags}
    if aliases:
        meta["aliases"] = aliases   # other names: the exact error text, synonyms; search reads them, Obsidian shows them
    if getattr(a, "summary", None):
        meta["summary"] = a.summary.strip()   # one line, when to read it; shown in INDEX.md so the entry is not a bare link
    agent = a.agent or os.environ.get("EVERLAST_AGENT") or ""
    model = a.model or os.environ.get("EVERLAST_MODEL") or ""
    if agent:
        meta["agent"] = agent   # provenance, as agent decision records do: which tool wrote this
    if model:
        meta["model"] = model
    if a.private:
        meta["tier"] = "private"
    elif a.user:
        meta["tier"] = "user"
    if a.supersedes:
        meta["supersedes"] = a.supersedes
        old = os.path.join(root, a.supersedes)
        if os.path.exists(old):
            otext = read(old)
            om, _ = parse_frontmatter(otext)
            write(old, set_fields(otext, {"status": "superseded", "superseded_by": rel}, after="status"))
            append(os.path.join(root, "log.md"), f"## [{d}] supersede | {om.get('title', a.supersedes)} -> {a.title}\n")
            if not re.search(r"^[ \t>*-]*Related[ \t]*:", body, re.M | re.I):   # the typed edge, unless the author wrote a Related line
                link = os.path.relpath(old, os.path.dirname(path)).replace("\\", "/")
                otitle = re.sub(r"[\[\]]", "", str(om.get("title") or a.supersedes))
                body = body.rstrip("\n") + f"\n\nRelated: supersedes [{otitle}]({link})\n"
    heading = "" if re.match(r"\s*#[ \t]", body) else "\n# " + a.title + "\n"   # a body that brings its own H1 keeps it (T-20260923-3)
    write(path, frontmatter(meta) + heading + "\n" + body.lstrip())
    append(os.path.join(root, "log.md"), f"## [{d}] add | {a.kind}: {a.title}\n")
    build_index(root)
    note(f"wrote {rel} in {root}; INDEX.md and log.md updated")
    if missing:
        note(f"  (headings still to fill: {missing})")
    print(path)


def cmd_handoff(a):
    root = docs_root(a.repo, a.root, a.private, a.user)
    if not os.path.isdir(root):
        fail(f"no docs root at {root}; run init first")
    body = read(a.body_file) if a.body_file else sys.stdin.read()
    if not body.strip():
        fail("empty handoff body")
    if "## Next single action" not in body:
        fail("handoff needs a '## Next single action' section")
    if not (a.private or a.user) and not a.allow_private:
        hits = privacy_hits(body, redact_list())
        if hits:
            fail("privacy scan flagged the handoff for the repo-safe root: " + "; ".join(f"{l} ({s})" for l, s in hits[:5])
                 + ". Move those lines to a --private entry, or pass --allow-private.")
    n = len(body.splitlines())
    write(os.path.join(root, "HANDOFF.md"), body if body.startswith("# ") else "# Handoff\n\n" + body)
    append(os.path.join(root, "log.md"), f"## [{today()}] handoff | {n} lines\n")
    note(f"HANDOFF.md replaced ({n} lines) in {root}" + ("; over the 50-line budget, trim it" if n > 50 else ""))


def cmd_log(a):
    root = docs_root(a.repo, a.root, a.private, a.user)
    append(os.path.join(root, "log.md"), f"## [{today()}] {a.op} | {a.title}\n")
    note("logged")


def cmd_resolve(a):
    print(docs_root(a.repo, a.root, a.private, a.user))


# ---------------------------------------------------------------- check before use (freshness)
# After GitHub Copilot Memory: a stored fix cites its sources and is re-checked against the current code before use.
# `stale_after` follows Google's Open Knowledge Format v0.2 (ISO date; stale when today >= stale_after). `note` writes
# verified + the kind's window; an entry without the field falls back to verified (or date) + window, so entries
# written before 0.4.0 join the scheme unedited; `never` marks a timeless entry.

_WINDOWS = None


def stale_windows():
    global _WINDOWS
    if _WINDOWS is None:
        w = dict(DEFAULT_STALE_DAYS)
        cfg = config().get("stale_after_days")
        if isinstance(cfg, dict):
            for k, v in cfg.items():
                try:
                    if int(v) > 0:
                        w[str(k)] = int(v)
                except (TypeError, ValueError):
                    pass
        _WINDOWS = w
    return _WINDOWS


def window_for(kind):
    return stale_windows().get(kind or "", 120)


def parse_date(v):
    try:
        return dt.date.fromisoformat(str(v).strip()[:10])
    except (TypeError, ValueError):
        return None


def stale_due(meta):
    """The date an entry becomes due for a recheck, or None (timeless, or no usable date). A `verified` date later
    than `stale_after` (a hand edit) renews the entry by its window."""
    raw = str(meta.get("stale_after") or "").strip()
    if raw.lower() == "never":
        return None
    verified = parse_date(meta.get("verified")) or parse_date(meta.get("date"))
    due = parse_date(raw) if raw else None
    if due and not (verified and verified > due):
        return due
    return verified + dt.timedelta(days=window_for(meta.get("kind"))) if verified else None


def is_stale(meta, on=None):
    """Active and on or past its due date. Superseded, done and abandoned entries are history, never "due"."""
    if (meta.get("status") or "active") != "active":
        return False
    due = stale_due(meta)
    return bool(due) and (on or today_date()) >= due


STAMP_RE = re.compile(r"\(verified (\d{4}-\d{2}-\d{2})\)")


def stale_stamps(meta, body, on=None):
    """Per-fact stamps `(verified YYYY-MM-DD)` at least one window old, as (date, line) pairs."""
    if (meta.get("status") or "active") != "active":
        return []
    on = on or today_date()
    window = dt.timedelta(days=window_for(meta.get("kind")))
    out = []
    for line in body.splitlines():
        for s in STAMP_RE.findall(line):
            d = parse_date(s)
            if d and on >= d + window:
                out.append((s, line.strip()))
    return out


def section(body, heading):
    """The text under `## heading` up to the next `## ` heading, or None."""
    m = re.search(r"^##[ \t]+" + re.escape(heading) + r"[ \t]*(?:\r?\n|\Z)(.*?)(?=^##[ \t]|\Z)", body, re.M | re.S | re.I)
    return m.group(1).strip() if m else None


def add_to_section(text, heading, line):
    """Append a line to a `## heading` section (before a trailing `Related:` line); add the section when missing."""
    m = re.search(r"^##[ \t]+" + re.escape(heading) + r"[ \t]*$", text, re.M | re.I)
    if not m:
        return text.rstrip("\n") + f"\n\n## {heading}\n{line}\n"
    nxt = re.search(r"^##[ \t]", text[m.end():], re.M)
    end = m.end() + nxt.start() if nxt else len(text)
    lines = text[m.end():end].split("\n")
    at = next((i for i, ln in enumerate(lines) if ln.lstrip().startswith("Related:")), len(lines))
    while at > 1 and not lines[at - 1].strip():
        at -= 1
    lines.insert(max(at, 1), line)
    out = text[:m.end()] + "\n".join(lines) + text[end:]
    return out if out.endswith("\n") else out + "\n"


def in_vault(path):
    """True for anything inside the vault (private sidecars, the user tier, excluded-mode stores)."""
    try:
        v = os.path.normcase(os.path.realpath(vault_path()))
        p = os.path.normcase(os.path.realpath(path))
    except (OSError, ValueError):
        return False
    return p == v or p.startswith(v + os.sep)


def infer_root(path):
    """The docs root holding an entry file: the nearest folder above it with INDEX.md or log.md."""
    d = os.path.dirname(os.path.abspath(path))
    for _ in range(4):
        if os.path.exists(os.path.join(d, "INDEX.md")) or os.path.exists(os.path.join(d, "log.md")):
            return d
        d = os.path.dirname(d)
    return None


def find_entry(query, root):
    """(root, relpath) of the entry `query` names: a file path, a relpath, a file name, or part of a title.
    (None, message) when nothing or several entries match."""
    q = query.strip().strip('"')
    for cand in (q, os.path.join(root, q)):
        if cand.endswith(".md") and os.path.isfile(cand):
            ap = os.path.abspath(cand)
            inside = os.path.normcase(ap).startswith(os.path.normcase(os.path.abspath(root)) + os.sep)
            r = os.path.abspath(root) if inside else infer_root(ap)
            if r:
                return r, os.path.relpath(ap, r).replace("\\", "/")
    ql = q.lower().replace("\\", "/")
    found = [(rel, m) for rel, m, _ in list(entries(root)) + list(entries(root, archive=True))]
    exact = [rel for rel, m in found if ql in (rel.lower(), os.path.basename(rel).lower(),
                                               os.path.splitext(os.path.basename(rel))[0].lower(), str(m.get("title", "")).lower())]
    loose = exact or [rel for rel, m in found if ql in str(m.get("title", "")).lower() or ql in os.path.basename(rel).lower()]
    if len(loose) == 1:
        return os.path.abspath(root), loose[0]
    if not loose:
        return None, f"no entry in {root} matches '{query}' (give a path, a file name, or part of a title; --private or --user for the other tiers)"
    return None, f"'{query}' matches {len(loose)} entries; name one: " + ", ".join(loose[:6])


def kind_of(rel, meta):
    if meta.get("kind") in KINDS:
        return meta["kind"]
    folder = rel.replace("\\", "/").split("/")[-2] if "/" in rel else ""
    return next((k for k, d in DIRS.items() if d == folder), "note")


def cited_paths(body, repo, root, rel):
    """Backticked file paths an entry cites, resolved as the lint does: [(ref, absolute path or None)]."""
    out, seen = [], set()
    for ref in PATH_RE.findall(body):
        if ref.startswith(("http", "www")) or ref in seen:
            continue
        seen.add(ref)
        cands = [os.path.join(repo, ref), os.path.join(root, ref), os.path.join(root, os.path.dirname(rel), ref)]
        hit = next((c for c in cands if os.path.exists(c)), None)
        out.append((ref, os.path.abspath(hit) if hit else None))
    return out


def git_changes_since(repo, path, since):
    """Commits touching path from the start of `since` (YYYY-MM-DD) on: [(hash, date, subject)]; None outside git."""
    rc, out, _ = run(["git", "log", f"--since={since} 00:00:00", "--format=%h%x09%ad%x09%s", "--date=short", "--", path], cwd=repo, timeout=20)
    if rc != 0:
        return None
    return [tuple(ln.split("\t", 2)) for ln in out.splitlines() if ln.count("\t") >= 2]


def cmd_recheck(a):
    """Read-only: is the entry stale, which cited files changed in git since it was verified, and what proves it."""
    root = docs_root(a.repo, a.root, a.private, a.user)
    got, rel = find_entry(a.entry, root)
    if not got:
        fail(rel)
    root, on = got, today_date()
    meta, body = parse_frontmatter(read(os.path.join(root, rel)))
    kind, status = kind_of(rel, meta), meta.get("status") or "active"
    verified = str(meta.get("verified") or meta.get("date") or "")[:10]
    due = stale_due(dict(meta, kind=kind))
    print(f"recheck {rel} in {root}")
    print(f"  {meta.get('title') or rel}: {kind}, {status}; verified {verified or 'never'}; "
          f"stale_after {meta.get('stale_after') or ((due.isoformat() + ' (from the ' + kind + ' window)') if due else 'none')}")
    if status != "active":
        print(f"  {status}: history, not a current fix" + (f"; the current entry is {meta['superseded_by']}" if meta.get("superseded_by") else ""))
    elif due and on >= due:
        print(f"  STALE: recheck due since {due.isoformat()} ({(on - due).days} day(s) ago); confirm it before acting on it")
    else:
        print(f"  fresh: next recheck due {due.isoformat()}" if due else "  timeless (stale_after: never)")
    for s, line in stale_stamps(dict(meta, status=status, kind=kind), body, on)[:5]:
        print(f"  fact stamped {s} is at least one {kind} window old: {line[:110]}")
    repo = os.path.abspath(a.repo)
    cites = cited_paths(body, repo, root, rel)
    code = [(ref, p) for ref, p in cites if p and not (os.path.normcase(p) + os.sep).startswith(os.path.normcase(os.path.abspath(root)) + os.sep)]
    missing = [ref for ref, p in cites if not p and ("/" in ref or "\\" in ref)]
    in_git = bool(code) and run(["git", "rev-parse", "--show-toplevel"], cwd=repo, timeout=10)[0] == 0
    if not cites:
        print("  cites no file in backticks: re-read the code it describes")
    elif code and not in_git:
        print(f"  {repo} is not a git work tree, so changes cannot be dated; re-read: " + ", ".join(f"`{r}`" for r, _ in code))
    else:
        same = []
        for ref, p in code:
            commits = git_changes_since(repo, p, verified) if parse_date(verified) else None
            dirty = bool(status_lines(repo, p))
            if commits or dirty:
                last = f"last {commits[0][1]} {commits[0][0]} \"{commits[0][2][:60]}\"" if commits else ""
                print(f"  CHANGED since {verified}: `{ref}` ({len(commits or [])} commit(s){', ' + last if last else ''}{', uncommitted edits' if dirty else ''})")
            else:
                same.append(ref)
        if same:
            print(f"  unchanged since {verified or 'it was written'}: " + ", ".join(f"`{r}`" for r in same))
    for ref in missing:
        print(f"  MISSING: `{ref}` no longer exists (moved, renamed or deleted?)")
    vb = section(body, "Verified by")
    if vb:
        print("  Verified by:")
        for ln in vb.splitlines():
            print("    " + ln)
    else:
        print("  no Verified by section: re-read the entry's reasons and the files it names")
    print("  next: re-run the Verified-by command only if it is read-only or safe (a build, a test, a status or version query; "
          "never a deploy, delete, push, send, payment or change to shared state), otherwise re-read the cited files and ask the user; "
          f"then `everlast.py verify {rel}` if it holds, or `everlast.py verify {rel} --failed \"what broke\"`")


def cmd_verify(a):
    """Record a recheck: success renews verified and stale_after; --failed notes what broke and marks it due now."""
    root = docs_root(a.repo, a.root, a.private, a.user)
    got, rel = find_entry(a.entry, root)
    if not got:
        fail(rel)
    root, d, on = got, today(), today_date()
    path = os.path.join(root, rel)
    text = read(path)
    meta, _ = parse_frontmatter(text)
    kind, title = kind_of(rel, meta), meta.get("title") or os.path.splitext(os.path.basename(rel))[0]
    logp = os.path.join(root, "log.md")
    if a.failed is not None:
        what = (a.failed.strip() or "no detail given") + (f" ({a.note.strip()})" if a.note else "")
        if not in_vault(root) and not a.allow_private:
            hits = privacy_hits(what, redact_list())
            if hits:
                fail("privacy scan flagged the note for a repo-safe entry: " + "; ".join(f"{l} ({s})" for l, s in hits[:5])
                     + ". Say it without the name or credential, or pass --allow-private if a reviewer decided it is safe.")
        text = add_to_section(text, "Verified by", f"Recheck failed {d}: {what}")
        write(path, set_fields(text, {"stale_after": d}))
        append(logp, f"## [{d}] verify-failed | {title}: {what}\n")
        build_index(root)
        print(f"recorded a failed recheck in {rel} (stale_after {d}: the index shows it as recheck due); log.md and INDEX.md updated")
        print(f"next: find the fix that holds now, then record it with `everlast.py note <repo> --kind {kind} --title \"...\" --supersedes {rel}` "
              "(the old entry becomes superseded and the new one links it); until then do not act on the old fix")
        return
    never = str(meta.get("stale_after") or "").strip().lower() == "never"
    updates = {"verified": d}
    if not never:
        updates["stale_after"] = (on + dt.timedelta(days=window_for(kind))).isoformat()
    write(path, set_fields(text, updates))
    append(logp, f"## [{d}] verify | {title}" + (f": {a.note.strip()}" if a.note else "") + "\n")
    build_index(root)
    print(f"verified {rel}: verified {d}, stale_after {updates.get('stale_after', 'never')}; log.md and INDEX.md updated")


# ---------------------------------------------------------------- typed links
# Related: supersedes [title](path); builds on [title](path), [title](path); see also [title](path)
# Labels shared with the Evergreen Protocol; an unlabelled link counts as `see also`, so older Related lines stay valid.

LINK_RE = re.compile(r"(!?)\[([^\]\n]*)\]\(([^)\s]+)((?:\s+\"[^\"\n]*\")?)\)")
RELATED_RE = re.compile(r"^[ \t>*-]*(?:\*\*)?Related(?:\*\*)?[ \t]*:(?:\*\*)?[ \t]*(.*)$", re.M | re.I)


def is_relative_target(t):
    return bool(t) and not re.match(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:|#|/|\\)", t)


def split_outside_links(s, sep=";"):
    """Split on sep except inside [...] or (...), so a title holding a semicolon stays whole."""
    parts, cur, depth = [], "", 0
    for c in s:
        if c in "[(":
            depth += 1
        elif c in "])" and depth:
            depth -= 1
        if c == sep and depth == 0:
            parts.append(cur)
            cur = ""
        else:
            cur += c
    parts.append(cur)
    return parts


def related_links(body):
    """(label, title, target) for every link on a `Related:` line; an unlabelled link counts as `see also`."""
    out = []
    for m in RELATED_RE.finditer(body):
        for seg in split_outside_links(m.group(1)):
            seg = seg.strip()
            first = seg.find("[")
            if first < 0:
                continue
            label = re.sub(r"\s+", " ", seg[:first].strip().rstrip(":").strip().lower()) or "see also"
            for lm in LINK_RE.finditer(seg):
                out.append((label, lm.group(2), lm.group(3)))
    return out


def rewrite_links(text, old_dir, new_dir, moves):
    """Point relative links at the files' new homes: `moves` maps normcased old absolute paths to new ones, and a file
    that itself moved from old_dir to new_dir gets every relative link recomputed."""
    def fix(m):
        bang, label, target, title = m.groups()
        path, hashmark, frag = target.partition("#")
        if not is_relative_target(path):
            return m.group(0)
        old_abs = os.path.normpath(os.path.join(old_dir, unquote(path)))
        new_abs = moves.get(os.path.normcase(old_abs), old_abs)
        if new_abs == old_abs and os.path.normcase(old_dir) == os.path.normcase(new_dir):
            return m.group(0)
        try:
            rel = os.path.relpath(new_abs, new_dir).replace("\\", "/").replace(" ", "%20")
        except ValueError:
            return m.group(0)
        return m.group(0) if rel == path else f"{bang}[{label}]({rel}{hashmark}{frag}{title})"
    return LINK_RE.sub(fix, text)


PATH_RE = re.compile(r"`([A-Za-z0-9_./\\-]+\.[A-Za-z0-9]{1,6})`")


def lint_root(root, repo, stale_days, problems, scan=True, on=None):
    """Append (category, message) findings for one docs root. stale_days None means each kind's own window."""
    def warn(cat, msg):
        problems.append((cat, msg))
    on = on or today_date()
    for name, cap in (("INDEX.md", 120), ("HANDOFF.md", 50)):
        p = os.path.join(root, name)
        if os.path.exists(p):
            n = len(read(p).splitlines())
            if n > cap:
                warn("budget", f"{name}: {n} lines, budget {cap}")
        else:
            warn("index", f"{name} missing in {root} (run init)")
    idx = os.path.join(root, "INDEX.md")
    indexed = set(re.findall(r"\]\(([^)]+\.md)\)", read(idx))) if os.path.exists(idx) else set()
    titles, contradictions = {}, set()
    redact = redact_list() if scan else []
    for rel, meta, body in entries(root):
        kind = meta["kind"]
        if rel not in indexed:
            warn("index", f"{rel}: not in INDEX.md (run index)")
        for h in REQUIRED_HEADINGS.get(kind, []):
            if h not in body:
                warn("heading", f"{rel}: missing heading '{h}'")
        if re.search(r"<[A-Z][^>]{10,}>", body):
            warn("placeholder", f"{rel}: template placeholder text still present")
        key = re.sub(r"[^a-z0-9]", "", meta["title"].lower())
        if key in titles:
            warn("duplicate", f"{rel}: title duplicates {titles[key]} (merge or supersede)")
        titles[key] = rel
        if meta["status"] == "active":
            v = meta.get("verified") or meta.get("date")
            raw_sa = str(meta.get("stale_after") or "").strip()
            if v and not parse_date(v):
                warn("date", f"{rel}: bad date '{v}'")
            elif raw_sa and raw_sa.lower() != "never" and not parse_date(raw_sa):
                warn("date", f"{rel}: bad stale_after '{raw_sa}' (YYYY-MM-DD, or never for a timeless entry)")
            elif stale_days and raw_sa.lower() != "never":
                if v and parse_date(v) < on - dt.timedelta(days=stale_days):
                    warn("stale", f"{rel}: last verified {v}, older than {stale_days} days; `everlast.py recheck {rel}`, then verify or supersede")
            elif is_stale(meta, on):
                warn("stale", f"{rel}: recheck due since {stale_due(meta)} (verified {v}); `everlast.py recheck {rel}`, then verify or supersede")
            for s, line in stale_stamps(meta, body, on)[:3]:
                warn("stamp", f"{rel}: fact stamped (verified {s}) is at least one {kind} window ({window_for(kind)} days) old: {line[:80]}")
        for ref in (PATH_RE.findall(body) if meta["status"] == "active" else []):   # history may name files that are gone (L-005)
            if ref.startswith(("http", "www")):
                continue
            cand = [os.path.join(repo, ref), os.path.join(root, ref), os.path.join(root, os.path.dirname(rel), ref)]
            if ("/" in ref or "\\" in ref) and not any(os.path.exists(c) for c in cand):
                warn("path", f"{rel}: references `{ref}` which does not exist (dead path)")
        entry_dir = os.path.dirname(os.path.join(root, rel))
        for lm in LINK_RE.finditer(body):
            target = lm.group(3).split("#", 1)[0]
            if is_relative_target(target) and not os.path.exists(os.path.normpath(os.path.join(entry_dir, unquote(target)))):
                warn("link", f"{rel}: dead link [{lm.group(2)[:40]}]({lm.group(3)})")
        targets = [(lab, t) for lab, _, t in related_links(body)]
        sup = str(meta.get("supersedes") or "").strip()
        if sup:  # the frontmatter form, relative to the root (archive/ after a prune)
            sp = next((c for c in (os.path.join(root, sup), os.path.join(root, "archive", sup)) if os.path.isfile(c)), None)
            if sp:
                targets.append(("supersedes", os.path.relpath(sp, entry_dir).replace("\\", "/")))
            else:
                warn("link", f"{rel}: frontmatter supersedes {sup}, which does not exist")
        for label, target in targets:
            if label not in RELATED_LABELS:
                warn("related", f"{rel}: unknown Related label '{label}' (use {', '.join(RELATED_LABELS)})")
                continue
            t = target.split("#", 1)[0]
            tp = os.path.normpath(os.path.join(entry_dir, unquote(t))) if is_relative_target(t) else ""
            if not (tp.endswith(".md") and os.path.isfile(tp)) or label not in ("supersedes", "contradicts"):
                continue
            tstatus = parse_frontmatter(read(tp))[0].get("status") or "active"
            if label == "supersedes" and tstatus != "superseded":
                warn("supersedes", f"{rel}: supersedes {t}, whose status is {tstatus} (set status: superseded and superseded_by there, as `note --supersedes` does)")
            if label == "contradicts" and meta["status"] == "active" and tstatus == "active":
                pair = frozenset((os.path.normcase(os.path.join(root, rel)), os.path.normcase(tp)))
                if pair not in contradictions:
                    contradictions.add(pair)
                    other = os.path.relpath(tp, root).replace("\\", "/")
                    warn("contradiction", f"open contradiction: {rel} <-> {other} (both active: supersede one, or relabel the link `see also` once both are shown to hold)")
        if scan:
            for label, snippet in privacy_hits(body, redact)[:3]:
                warn("privacy", f"{rel}: privacy: {label} ({snippet}); move to the private sidecar (--private) or redact")
    logp = os.path.join(root, "log.md")
    if os.path.exists(logp) and len(read(logp).splitlines()) > 400:
        warn("log", f"log.md in {root} over 400 lines; archive older lines to log-ARCHIVE.md")


def cmd_lint(a):
    repo = os.path.abspath(a.repo)
    problems = []
    root = docs_root(a.repo, a.root, a.private, a.user)
    if not os.path.isdir(root):
        fail(f"no docs root at {root}")
    for name, cap in (("AGENTS.md", 400), ("CLAUDE.md", 200), ("CODEMAP.md", 250)):
        p = os.path.join(repo, name)
        if os.path.exists(p):
            n = len(read(p).splitlines())
            if n > cap:
                problems.append(("budget", f"{name}: {n} lines; always-on text costs every session (soft cap {cap}); move detail into entries"))
    slug, p = find_project(a.repo)
    lint_root(root, repo, a.stale_days, problems, scan=not (a.private or a.user) and (p or {}).get("mode") != "excluded")
    if a.all and not (a.private or a.user):
        priv = docs_root(a.repo, a.root, private=True)
        if os.path.isdir(priv):
            lint_root(priv, repo, a.stale_days, problems, scan=False)
    if p and p.get("mode") == "excluded":
        rc, out, _ = run(["git", "check-ignore", "-q", (p.get("root") or "ai-docs")], cwd=repo)
        if rc != 0:
            problems.append(("exclude", f"mode excluded but git does not ignore {p.get('root') or 'ai-docs'}/ (re-run project register; Claude Code rewrites .git/info/exclude, issue anthropics/claude-code#84954)"))
    if problems:
        print(f"lint: {len(problems)} finding(s)")
        for _, x in problems:
            print("  - " + x)
        if STRICT:
            sys.exit(1)
    else:
        print("lint: clean")


def cmd_scan(a):
    target = os.path.abspath(a.path)
    if os.path.isdir(os.path.join(target, "ai-docs")):
        target = os.path.join(target, "ai-docs")
    redact = redact_list()
    found = []
    files = [target] if os.path.isfile(target) else [os.path.join(dp, f) for dp, _, fs in os.walk(target) for f in fs if f.endswith(".md")]
    for f in files:
        for label, snippet in privacy_hits(read(f), redact):
            found.append({"file": os.path.relpath(f, target if os.path.isdir(target) else os.path.dirname(target)), "label": label, "match": snippet})
    if a.json:
        print(json.dumps(found, indent=2))
        return
    if not found:
        print(f"scan: clean ({len(files)} file(s), {len(redact)} redact pattern(s))")
        return
    print(f"scan: {len(found)} hit(s) in {target}")
    for h in found:
        print(f"  - {h['file']}: {h['label']} ({h['match']})")
    if STRICT:
        sys.exit(1)


# ---------------------------------------------------------------- search (lexical: BM25 over fields, aliases first)
# Embeddings are deferred by decision (ai-docs/decisions): grep-style search held up against vector search in 2026 tests,
# stdlib-only keeps every install portable, and bench/ says when to revisit.

STOPWORDS = frozenset("a about after all also an and any are as at be been but by can could did do does doing done for from had has have "
                      "how i if in into is it its just may me more most my no nor not of on once only or other our out over own same so "
                      "some such than that the their them then there these they this those through to too until up very was we were what "
                      "when where which while who whom why will with would you your".split())
WORD_RE = re.compile(r"[^\W_]+(?:[._\-][^\W_]+)*")
FIELD_WEIGHTS = (("title", 3.0), ("aliases", 3.0), ("tags", 2.0), ("summary", 2.0), ("body", 1.0))


def stem(w):
    """Light suffix stemming (s, es, ies, ed, ing, a final e) that never leaves fewer than three letters; words with
    digits (CS0103, 0x08000000) are code and stay as written."""
    if len(w) <= 3 or not w.isalpha():
        return w
    if w.endswith("ies") and len(w) > 4:
        w = w[:-3] + "y"
    elif w.endswith(("sses", "shes", "ches", "xes", "zes")):
        w = w[:-2]
    elif w.endswith("s") and not w.endswith(("ss", "us", "is")):
        w = w[:-1]
    for suffix in ("ing", "ed"):
        if w.endswith(suffix) and len(w) - len(suffix) >= 3:
            w = w[:-len(suffix)]
            if len(w) >= 4 and w[-1] == w[-2] and w[-1] not in "lsz":
                w = w[:-1]   # stopped -> stop, running -> run
            break
    if w.endswith("e") and len(w) >= 4:
        w = w[:-1]           # rename, renamed, renaming -> renam
    return w


def tokenize(text, stem_words=True):
    """Lowercase word tokens. An identifier or dotted name (CREATE_NO_WINDOW, Microsoft.DotNet.SDK.9, ShowInventory)
    counts whole and by its parts, so the exact string and its pieces both match."""
    out = []
    for m in WORD_RE.finditer(text or ""):
        word = m.group(0)
        parts = re.findall(r"[^\W_]+", word)
        if len(parts) > 1:
            out.append(word.lower())
        for p in parts:
            low = p.lower()
            pieces = re.split(r"(?<=[a-z0-9])(?=[A-Z])", p) if p != low else [p]
            if len(pieces) > 1:
                out.append(low)
            for piece in pieces:
                w = piece.lower()
                if w in STOPWORDS or (len(w) < 2 and not w.isdigit()):
                    continue
                out.append(stem(w) if stem_words else w)
    return out


def search_fields(meta, body):
    b = re.sub(r"\A\s*#[ \t]+[^\n]*\n", "", body)   # the H1 repeats the title
    b = LINK_RE.sub(lambda m: m.group(2), b)          # keep link text, drop paths
    return {"title": str(meta.get("title") or ""), "aliases": " ; ".join(as_list(meta.get("aliases"))),
            "tags": " ".join(as_list(meta.get("tags"))), "summary": str(meta.get("summary") or ""), "body": b}


def bm25_corpus(items):
    """Weighted term frequencies per (meta, body): title and aliases x3, tags and summary x2, body x1."""
    docs, df = [], {}
    for meta, body in items:
        fields, tf = search_fields(meta, body), {}
        for field, weight in FIELD_WEIGHTS:
            for t in tokenize(fields[field]):
                tf[t] = tf.get(t, 0.0) + weight
        for t in tf:
            df[t] = df.get(t, 0) + 1
        docs.append((tf, sum(tf.values())))
    avgdl = (sum(dl for _, dl in docs) / len(docs)) if docs else 1.0
    return docs, df, avgdl or 1.0


def bm25_scores(corpus, query, k1=1.2, b=0.75):
    docs, df, avgdl = corpus
    n = len(docs)
    terms = list(dict.fromkeys(tokenize(query)))
    out = []
    for tf, dl in docs:
        s = 0.0
        for t in terms:
            f = tf.get(t)
            if f:
                s += math.log(1 + (n - df[t] + 0.5) / (df[t] + 0.5)) * f * (k1 + 1) / (f + k1 * (1 - b + b * dl / avgdl))
        out.append(s)
    return out


def search_entries(roots, query, on=None):
    """Rank every entry (archive included) under roots, a list of (root, display) where display(path) is what a hit
    prints. A superseded entry keeps its place in the results but ranks below its successor (x0.5); done, abandoned
    and promoted x0.8; recheck due x0.9. Returns (hits best first, entries searched)."""
    on = on or today_date()
    docs = []
    for root, display in roots:
        for archived in (False, True):
            for rel, meta, body in entries(root, archive=archived):
                docs.append((root, display, rel, meta, body))
    scores = bm25_scores(bm25_corpus([(m, b) for _, _, _, m, b in docs]), query)
    hits = []
    for (root, display, rel, meta, body), s in zip(docs, scores):
        if s <= 0:
            continue
        status, stale = meta.get("status") or "active", is_stale(meta, on)
        s *= 0.5 if status == "superseded" else 0.8 if status != "active" else 0.9 if stale else 1.0
        flags = ["recheck due"] if stale else ([status] if status != "active" else [])
        if stale_stamps(meta, body, on):
            flags.append("stale facts")
        if rel.startswith("archive/"):
            flags.append("archived")
        path = os.path.join(root, rel)
        hits.append({"score": round(s, 3), "kind": meta.get("kind"), "date": str(meta.get("date") or ""), "title": str(meta.get("title") or rel),
                     "summary": str(meta.get("summary") or ""), "status": status, "flags": flags, "path": display(path), "file": os.path.abspath(path)})
    hits.sort(key=lambda h: (-h["score"], h["path"]))
    return hits, len(docs)


def under(path, base):
    return (os.path.normcase(os.path.abspath(path)) + os.sep).startswith(os.path.normcase(os.path.abspath(base)) + os.sep)


def search_roots(a):
    """[(root, display)] for the scope: the project's doc root, plus the sidecar (--private), the user tier (--user),
    or every registered project's roots and the user tier (--all)."""
    repo, vault = os.path.abspath(a.repo), vault_path()
    slug, proj = find_project(repo)
    here = docs_root(repo, a.root)

    def vault_rel(p):
        return "vault:" + os.path.relpath(p, vault).replace("\\", "/") if under(p, vault) else p

    def current(p):
        if under(p, repo):
            return os.path.relpath(p, repo).replace("\\", "/")
        if proj and proj.get("mode") == "excluded" and proj.get("link") is not False and under(p, here):
            return (proj.get("root") or "ai-docs") + "/" + os.path.relpath(p, here).replace("\\", "/")
        return vault_rel(p)

    def other(s, base):
        return lambda p: (f"{s}:" + os.path.relpath(p, base).replace("\\", "/")) if under(p, base) else vault_rel(p)
    roots = [(here, current)]
    if a.all:
        for s, pr in sorted(registry().get("projects", {}).items()):
            pub = pr.get("store") if pr.get("mode") == "excluded" and pr.get("store") else os.path.join(pr.get("path", ""), pr.get("root") or "ai-docs")
            roots.append((pub, current if s == slug else other(s, pr.get("path", ""))))
            roots.append((os.path.join(vault, "projects", s, "private"), vault_rel))
        roots.append((os.path.join(vault, "user"), vault_rel))
    else:
        if a.private:
            roots.append((docs_root(repo, a.root, private=True), vault_rel))
        if a.user:
            roots.append((docs_root(repo, a.root, user=True), vault_rel))
    seen, out = set(), []
    for r, disp in roots:
        key = os.path.normcase(os.path.realpath(r)) if r else ""
        if r and os.path.isdir(r) and key not in seen:
            seen.add(key)
            out.append((r, disp))
    return out


def cmd_search(a):
    roots = search_roots(a)
    if not roots:
        fail(f"no docs root to search from {os.path.abspath(a.repo)} (everlast-setup creates one)")
    hits, n = search_entries(roots, a.query)
    top = hits[:max(1, a.n)]
    if a.json:
        print(json.dumps({"query": a.query, "entries": n, "matches": len(hits), "hits": top}, indent=2))
        return
    if not hits:
        print(f"search: nothing matches \"{a.query}\" in {n} entries; try the exact error text, a file or tool name, or conclude it was not recorded")
        return
    print(f"search \"{a.query}\": {len(hits)} of {n} entries match; best {len(top)}:")
    for h in top:
        flags = "".join(f" ({f})" for f in h["flags"])
        print(f"  {h['score']:6.2f}  {h['kind'] or 'note':<8} {h['date'] or 'undated':<10}{flags}  {h['path']}: {h['summary'] or h['title']}")
    if any(h["path"].startswith("vault:") for h in top):
        print(f"  (vault: is {vault_path()})")


# ---------------------------------------------------------------- maintain (deterministic upkeep; judgment stays with a person or agent)

def duplicate_pairs(items):
    """Title near-duplicates within a kind: difflib ratio >= 0.85, or the same tags and >= 0.7."""
    by_kind = {}
    for rel, meta in items:
        if (meta.get("status") or "active") != "superseded":
            tags = frozenset(t.lower() for t in as_list(meta.get("tags")))
            by_kind.setdefault(meta.get("kind"), []).append((rel, str(meta.get("title") or "").lower(), tags))
    out = []
    sm = difflib.SequenceMatcher(None)
    for group in by_kind.values():
        for j in range(1, len(group)):
            rb, tb, gb = group[j]
            sm.set_seq2(tb)   # difflib indexes the second sequence once per title, then compares every earlier one
            for i in range(j):
                ra, ta, ga = group[i]
                sm.set_seq1(ta)
                if sm.real_quick_ratio() < 0.7 or sm.quick_ratio() < 0.7:
                    continue
                r = sm.ratio()
                if r >= 0.85 or (ga and ga == gb and r >= 0.7):
                    out.append((ra, rb, round(r, 2)))
    return out


def maintenance(root, repo, on=None, scan=True):
    """What `maintain` reports for one docs root, read-only (no git, no writes), so the SessionStart hook can count it."""
    on = on or today_date()
    items = list(entries(root))
    rep = {"recheck": [], "archive": [], "propose": [], "duplicates": [], "contradictions": [], "lint": []}
    for rel, meta, _ in items:
        status = meta.get("status") or "active"
        base = max([d for d in (parse_date(meta.get("date")), parse_date(meta.get("verified"))) if d], default=None)
        if status in ("done", "abandoned", "superseded") and base and (on - base).days > ARCHIVE_DAYS:
            rep["archive"].append(rel)
        due = stale_due(meta) if status == "active" else None
        if due and on >= due:
            rep["recheck"].append((rel, str(meta.get("title") or rel), due.isoformat()))
            if on >= due + dt.timedelta(days=window_for(meta.get("kind"))):
                rep["propose"].append(rel)
    rep["recheck"].sort(key=lambda r: r[2])
    rep["duplicates"] = duplicate_pairs([(rel, meta) for rel, meta, _ in items])
    problems = []
    lint_root(root, repo, None, problems, scan=scan, on=on)
    for cat, msg in problems:
        if cat == "contradiction":
            rep["contradictions"].append(msg)
        elif cat not in ("stale", "duplicate"):
            rep["lint"].append(msg)
    return rep


def maintenance_count(rep):
    return sum(len(rep[k]) for k in ("archive", "propose", "duplicates", "contradictions", "lint"))


def rewrite_frontmatter_paths(text, moved):
    """`supersedes:` and `superseded_by:` values (paths from the docs root) that moved to archive/."""
    m = FRONTMATTER_RE.match(text)
    if not m:
        return text

    def fix(lm):
        val = unquote_yaml(lm.group(2))
        return f"{lm.group(1)}: {yaml_scalar(moved[val])}" if val in moved else lm.group(0)
    block = re.sub(r"^(supersedes|superseded_by)[ \t]*:[ \t]*(.+?)[ \t]*$", fix, m.group(1), flags=re.M)
    return text[:m.start(1)] + block + text[m.end(1):]


def archive_entries(root, rels):
    """Move entries to root/archive/<same folder>/ and rewrite every relative link, and frontmatter supersedes path,
    that points at them or out of them. Returns (moved relpaths, number of files whose links changed). Never edits
    anything else; moving a file back and re-running `index` undoes it."""
    root = os.path.abspath(root)
    moves, plan = {}, []
    for rel in rels:
        src, dst = os.path.join(root, rel), os.path.join(root, "archive", rel)
        if os.path.isfile(src) and not os.path.exists(dst):
            moves[os.path.normcase(os.path.normpath(src))] = os.path.normpath(dst)
            plan.append((rel, src, dst))
    if not plan:
        return [], 0
    moved_rel = {rel: "archive/" + rel for rel, _, _ in plan}
    changed = 0
    for dp, _, files in os.walk(root):
        for f in files:
            if not f.endswith(".md") or (os.path.normcase(dp) == os.path.normcase(root) and f in ("INDEX.md", "log.md")):
                continue
            path = os.path.join(dp, f)
            new_home = moves.get(os.path.normcase(os.path.normpath(path)), path)
            text = read(path)
            new = rewrite_frontmatter_paths(rewrite_links(text, os.path.dirname(path), os.path.dirname(new_home), moves), moved_rel)
            if new != text:
                write(path, new)
                changed += 1
    for rel, src, dst in plan:
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.move(src, dst)
    return [rel for rel, _, _ in plan], changed


def cmd_maintain(a):
    repo = os.path.abspath(a.repo)
    root = docs_root(repo, a.root, a.private, a.user)
    if not os.path.isdir(root):
        fail(f"no docs root at {root}")
    slug, p = find_project(repo)
    scan = not (a.private or a.user) and (p or {}).get("mode") != "excluded"
    on = today_date()
    rep = maintenance(root, repo, on, scan)
    if a.apply and rep["archive"]:
        moved, relinked = archive_entries(root, rep["archive"])
        if moved:
            build_index(root, on)
            append(os.path.join(root, "log.md"), f"## [{today()}] prune | archived {len(moved)} entr{'y' if len(moved) == 1 else 'ies'} to archive/ (maintain --apply): {', '.join(moved)}\n")
            print(f"archived {len(moved)} entr{'y' if len(moved) == 1 else 'ies'} to archive/ (links rewritten in {relinked} file(s)); INDEX.md rebuilt; log.md: prune")
            for rel in moved:
                print(f"  - {rel} -> archive/{rel}")
        rep = maintenance(root, repo, on, scan)
    n = len(rep["recheck"]) + maintenance_count(rep)
    total = sum(1 for _ in entries(root))
    if not n:
        print(f"maintain {root}: nothing to do ({total} entries)")
        return
    print(f"maintain {root}: {n} item(s) in {total} entries" + ("" if a.apply else " (report only)"))
    if rep["recheck"]:
        print(f"  recheck due ({len(rep['recheck'])}): `everlast.py recheck <entry>`, then `verify`, `verify --failed`, or supersede")
        for rel, title, due in rep["recheck"]:
            print(f"    - {rel}: {title} (due {due})")
    if rep["archive"]:
        print(f"  archive ({len(rep['archive'])}): done, abandoned or superseded for more than {ARCHIVE_DAYS} days; `maintain --apply` moves them to archive/ and rewrites links")
        for rel in rep["archive"]:
            print(f"    - {rel}")
    if rep["propose"]:
        print(f"  archive proposed ({len(rep['propose'])}): more than a window past stale_after with no verify; decide by hand (verify, supersede, or set status done or abandoned)")
        for rel in rep["propose"]:
            print(f"    - {rel}")
    if rep["duplicates"]:
        print(f"  duplicate candidates ({len(rep['duplicates'])}): merge by hand, or supersede one")
        for x, y, r in rep["duplicates"]:
            print(f"    - {x} ~ {y} (title similarity {r})")
    if rep["contradictions"]:
        print(f"  open contradictions ({len(rep['contradictions'])}):")
        for msg in rep["contradictions"]:
            print(f"    - {msg}")
    if rep["lint"]:
        print(f"  lint ({len(rep['lint'])}):")
        for msg in rep["lint"]:
            print(f"    - {msg}")


# ---------------------------------------------------------------- projects

def is_link(p):
    """True for a symlink or a Windows junction (os.path.islink is False for junctions on 3.12+)."""
    return os.path.islink(p) or getattr(os.path, "isjunction", lambda _p: False)(p)


def link_dir(link, target):
    """Junction on Windows (no admin), symlink elsewhere. Returns True when the link exists afterwards."""
    if os.path.lexists(link):
        return True
    os.makedirs(os.path.dirname(link) or ".", exist_ok=True)
    if os.name == "nt":
        rc, _, err = run(["powershell", "-NoProfile", "-NonInteractive", "-Command", "New-Item -ItemType Junction -Path $args[0] -Target $args[1] | Out-Null", link, target])
        if rc != 0:
            rc, _, err = run(["cmd", "/c", "mklink", "/J", link, target])
        if rc != 0 and err:
            note(f"  junction error: {err[:200]}")
        return rc == 0
    try:
        os.symlink(target, link, target_is_directory=True)
        return True
    except OSError:
        return False


def ensure_exclude(repo, root):
    rc, gitdir, _ = run(["git", "rev-parse", "--git-dir"], cwd=repo)
    if rc != 0:
        return "not a git repository; nothing to exclude"
    gitdir = gitdir if os.path.isabs(gitdir) else os.path.join(repo, gitdir)
    rc2, gp, _ = run(["git", "rev-parse", "--git-path", "info/exclude"], cwd=repo)
    excl = os.path.join(repo, gp) if rc2 == 0 and gp and not os.path.isabs(gp) else (gp if rc2 == 0 and gp else os.path.join(gitdir, "info", "exclude"))
    line = f"/{root}"  # no trailing slash: on POSIX ai-docs is a symlink, which git treats as a file
    existing = read(excl) if os.path.exists(excl) else ""
    if line not in existing.splitlines():
        append(excl, ("" if existing.endswith("\n") or not existing else "\n") + f"# everlast: docs kept out of this repository\n{line}\n")
    rc, _, _ = run(["git", "check-ignore", "-q", root], cwd=repo)
    return f"{root}/ excluded via .git/info/exclude" if rc == 0 else f"wrote {excl} but git check-ignore still fails; check global excludes"


def cmd_project_register(a):
    repo = os.path.abspath(a.repo)
    if not os.path.isdir(repo):
        fail(f"no such directory {repo}")
    reg = registry()
    slug = a.slug or repo_slug(repo)
    old, _ = find_project(repo)
    if old and old != slug:
        slug = old
    for s, p in reg["projects"].items():
        if s == slug and os.path.normcase(os.path.abspath(p["path"])) != os.path.normcase(repo):
            slug = f"{slug}-{int(hashlib.sha1(repo.encode('utf-8')).hexdigest()[:4], 16) % 10000:04d}"
    prev = reg["projects"].get(slug, {})
    entry = {"path": repo, "mode": a.mode, "root": a.root, "registered": prev.get("registered") or today(), "private": f"projects/{slug}/private"}
    if a.mode == "repo":
        entry["sync"] = a.sync or prev.get("sync") or "push"
    priv = os.path.join(vault_path(), "projects", slug, "private")
    scaffold(priv, readme=None)
    notes = []
    if a.mode == "excluded":
        store = os.path.join(vault_path(), "projects", slug, "ai-docs")
        scaffold(store)
        entry["store"] = store
        link = os.path.join(repo, a.root)
        if os.path.isdir(link) and not is_link(link) and os.listdir(link) and not os.path.exists(os.path.join(store, ".moved")):
            for name in os.listdir(link):
                src, dst = os.path.join(link, name), os.path.join(store, name)
                if os.path.isdir(src) and os.path.isdir(dst):
                    for inner in os.listdir(src):  # the store is scaffolded first, so merge into its folders
                        shutil.move(os.path.join(src, inner), os.path.join(dst, inner))
                    os.rmdir(src)
                else:
                    shutil.move(src, dst)
            os.rmdir(link)
            write(os.path.join(store, ".moved"), today())
            notes.append(f"moved existing {a.root}/ contents into the vault store")
        if a.no_link:
            entry["link"] = False
            notes.append(f"no link requested; docs live only at {store}")
        else:
            if os.path.isdir(link) and not is_link(link) and not os.listdir(link):
                os.rmdir(link)
            ok = link_dir(link, store)
            entry["link"] = ok
            notes.append(f"{a.root}/ -> {store} ({'linked' if ok else 'LINK FAILED; docs live in the vault only'})")
        notes.append(ensure_exclude(repo, a.root))
    else:
        scaffold(os.path.join(repo, a.root))
        notes.append(f"{a.root}/ committed with the project; private entries go to {priv}")
        notes.append({"push": f"sync push: the SessionEnd hook commits {a.root}/ and pushes the branch when that is safe, else opens a pull request",
                      "pr": f"sync pr: the SessionEnd hook commits {a.root}/ and always opens a pull request",
                      "off": f"sync off: {a.root}/ is committed and pushed by hand"}[entry["sync"]])
    reg["projects"][slug] = entry
    save_registry(reg)
    print(f"registered {slug} ({a.mode}) at {repo}")
    for n in notes:
        print("  - " + n)


def cmd_project_status(a):
    slug, p = find_project(a.repo)
    if not p:
        print(f"unregistered: {os.path.abspath(a.repo)} (default mode repo, root ai-docs; run project register)")
        return
    print(f"{slug}: mode {p['mode']}, path {p['path']}, root {p.get('root')}, registered {p.get('registered')}")
    print(f"  public root: {docs_root(a.repo, p.get('root') or 'ai-docs')}")
    print(f"  private sidecar: {docs_root(a.repo, private=True)}")
    if p["mode"] == "excluded":
        rc, _, _ = run(["git", "check-ignore", "-q", p.get("root") or "ai-docs"], cwd=p["path"])
        print(f"  excluded from git: {'yes' if rc == 0 else 'NO (re-run project register)'}; linked: {p.get('link')}")
    else:
        st = project_git_state(p["path"], p.get("root") or "ai-docs")
        if st is None:
            print(f"  sync {p.get('sync') or 'push'}: not a git work tree")
        else:
            print(f"  sync {p.get('sync') or 'push'}: branch {st['branch'] or 'detached'}, upstream {st['upstream'] or 'none'}, remote {st['remote'] or 'none'}; "
                  f"{len(st['dirty_docs'])} uncommitted doc file(s), {st['unpushed_docs']} unpushed commit(s) touching the docs")


def cmd_project_list(a):
    reg = registry()
    if not reg["projects"]:
        print("no projects registered")
    for slug, p in sorted(reg["projects"].items()):
        print(f"{slug:30s} {p['mode']:9s} {('sync ' + (p.get('sync') or 'push')) if p['mode'] == 'repo' else 'vault':10s} {p['path']}")


# ---------------------------------------------------------------- project docs sync (mode repo)

SYNC_MODES = ("push", "pr", "off")
VAULT_REMOTE_QUESTION = ("the vault is local only (no remote); ask the user once: the URL of a private repository they already have "
                         "(`everlast.py vault remote <url>`), or permission to create one (`everlast.py vault remote --create [name]`, "
                         "runs `gh repo create --private` in their account). The vault names people and machines, so the remote must be "
                         "private; nothing is pushed until they choose.")


def host_label():
    return os.environ.get("EVERLAST_ENV") or platform.node() or "host"


def git_ident(cwd):
    return [] if run(["git", "config", "user.email"], cwd=cwd)[1] else ["-c", "user.name=everlast", "-c", "user.email=everlast@localhost"]


def change_summary(cwd, pathspec=None):
    """What a commit would carry, as (subject tail, body): `+new ~changed -gone` per file, so the log says what
    everlast added without opening the diff. Paths are relative to pathspec when one is given."""
    lines = status_lines(cwd, pathspec)
    if lines is None:
        return "", ""
    marks = []
    for ln in lines:
        code, rel = ln[:2], ln[3:].strip().strip('"').replace("\\", "/")
        if " -> " in rel:
            rel = rel.split(" -> ", 1)[1]
        if pathspec and rel.startswith(pathspec.replace("\\", "/") + "/"):
            rel = rel[len(pathspec) + 1:]
        marks.append(("+" if "?" in code or "A" in code else "-" if "D" in code else "~") + rel)
    marks.sort(key=lambda m: ("+", "~", "-").index(m[0]))  # new entries first: the subject line is what `git log --oneline` shows
    subject = ", ".join(marks)
    if len(subject) > 64:
        subject = subject[:60].rsplit(", ", 1)[0] + ", ..."
    return subject, "\n".join(marks)


def commit_paths(cwd, pathspec, prefix):
    """Stage and commit only the files under pathspec; other changed or staged files are left exactly as they were."""
    tail, body = change_summary(cwd, pathspec)
    if not tail:
        return False, "nothing to commit"
    run(["git", "add", "-A", "--", pathspec], cwd=cwd)
    rc, out, err = run(["git"] + git_ident(cwd) + ["commit", "-q", "-m", f"{prefix}: {tail}", "-m", body, "--", pathspec], cwd=cwd, timeout=60)
    return rc == 0, ("ok: " + tail if rc == 0 else (err or out)[:300])


def project_git_state(repo, root, fetch=False):
    """What a docs push needs to know about the project repository; None when it is not a git work tree."""
    rc, _, _ = run(["git", "rev-parse", "--show-toplevel"], cwd=repo, timeout=10)
    if rc != 0:
        return None
    rc, branch, _ = run(["git", "symbolic-ref", "--short", "-q", "HEAD"], cwd=repo)
    st = {"branch": branch if rc == 0 and branch else None, "upstream": None, "remote": None, "ahead": 0, "behind": 0,
          "dirty_docs": [], "unpushed_docs": 0, "foreign": []}
    st["dirty_docs"] = [ln[3:].strip() for ln in (status_lines(repo, root) or [])]
    rc, up, _ = run(["git", "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"], cwd=repo)
    if rc == 0 and up and "/" in up:
        st["upstream"], st["remote"] = up, up.split("/", 1)[0]
        if fetch:
            run(["git", "fetch", "-q", st["remote"]], cwd=repo, timeout=60)
        rc, ab, _ = run(["git", "rev-list", "--left-right", "--count", "HEAD...@{upstream}"], cwd=repo)
        if rc == 0 and len(ab.split()) == 2:
            st["ahead"], st["behind"] = (int(x) for x in ab.split())
        rc, n, _ = run(["git", "rev-list", "--count", "@{upstream}..HEAD", "--", root], cwd=repo)
        st["unpushed_docs"] = int(n) if rc == 0 and n.isdigit() else 0
        me = author_email(repo)
        rc, authors, _ = run(["git", "log", "--format=%ae", "@{upstream}..HEAD"], cwd=repo)
        st["foreign"] = sorted({x.strip().lower() for x in authors.splitlines() if x.strip() and x.strip().lower() != me}) if rc == 0 and me else []
    else:
        rc, rems, _ = run(["git", "remote"], cwd=repo)
        rems = [r.strip() for r in rems.splitlines() if r.strip()] if rc == 0 else []
        st["remote"] = "origin" if "origin" in rems else (rems[0] if len(rems) == 1 else None)
    return st


def remote_default_branch(repo, remote):
    rc, ref, _ = run(["git", "symbolic-ref", "-q", "--short", f"refs/remotes/{remote}/HEAD"], cwd=repo)
    if rc == 0 and ref and "/" in ref:
        return ref.split("/", 1)[1]
    rc, out, _ = run(["git", "ls-remote", "--symref", remote, "HEAD"], cwd=repo, timeout=30)
    m = re.search(r"ref: refs/heads/(\S+)\s+HEAD", out) if rc == 0 else None
    if m:
        return m.group(1)
    for cand in ("main", "master"):
        if run(["git", "rev-parse", "-q", "--verify", f"refs/remotes/{remote}/{cand}"], cwd=repo)[0] == 0:
            return cand
    return None


def github_slug(repo, remote):
    rc, url, _ = run(["git", "remote", "get-url", remote], cwd=repo)
    m = re.search(r"github\.com[:/]([^/\s]+/[^/\s]+?)(?:\.git)?/?$", url.strip()) if rc == 0 else None
    return m.group(1) if m else None


def docs_pull_request(repo, root, st, reason, dry_run=False):
    """Not sure enough to push the user's branch: put the doc root's current state on a fresh branch off the remote's
    default branch, push that branch, open a pull request. Only the doc root travels; the user's own commits stay local."""
    remote = st.get("remote")
    if not remote:
        return "no remote; committed locally only (push by hand)"
    base = remote_default_branch(repo, remote)
    if not base:
        return f"cannot tell the default branch of {remote}; committed locally only (push by hand)"
    branch = f"everlast/docs-{re.sub(r'[^A-Za-z0-9._-]+', '-', host_label())}-{dt.datetime.now():%Y%m%d-%H%M%S}"
    if dry_run:
        return f"would open a pull request ({reason}): {root}/ on {branch} against {remote}/{base}"
    run(["git", "fetch", "-q", remote, base], cwd=repo, timeout=60)
    wt = tempfile.mkdtemp(prefix="everlast-pr-")
    os.rmdir(wt)
    pushed = False
    try:
        rc, _, err = run(["git", "worktree", "add", "--detach", "-q", wt, f"{remote}/{base}"], cwd=repo, timeout=60)
        if rc != 0:
            return f"worktree failed: {err[:200]}; committed locally only"
        dst = os.path.join(wt, root)
        if os.path.isdir(dst):
            shutil.rmtree(dst)
        shutil.copytree(os.path.join(repo, root), dst, ignore=shutil.ignore_patterns(".git"))
        run(["git", "checkout", "-q", "-b", branch], cwd=wt)
        ok, msg = commit_paths(wt, root, f"everlast: {root} from {host_label()}")
        if not ok:
            return f"{root}/ already matches {remote}/{base}; nothing to push" if msg == "nothing to commit" else f"commit failed: {msg}"
        rc, _, err = run(["git", "push", "-q", "-u", remote, branch], cwd=wt, timeout=120)
        if rc != 0:
            return f"push of {branch} failed: {err[:200]} (branch kept locally)"
        pushed = True
        slug = github_slug(repo, remote)
        if slug and shutil.which("gh"):
            body = (f"Project docs (`{root}/`) written by everlast sessions on `{host_label()}`, opened as a pull request instead of a push "
                    f"because {reason}. Only `{root}/` changed; no code travels with it.")
            rc, out, err = run(["gh", "pr", "create", "--repo", slug, "--base", base, "--head", branch, "--title", f"everlast: {root} from {host_label()}", "--body", body], cwd=wt, timeout=90)
            return f"pull request ({reason}): {(out or err)[:200]}"
        return f"pushed {branch} ({reason}); open the pull request against {base} by hand" + (f": https://github.com/{slug}/compare/{base}...{branch}" if slug else "")
    finally:
        run(["git", "worktree", "remove", "--force", wt], cwd=repo, timeout=30)
        shutil.rmtree(wt, ignore_errors=True)
        if pushed:
            run(["git", "branch", "-D", branch], cwd=repo)  # the remote has it; a local copy would only clutter the branch list


def cmd_project_sync(a):
    """Mode repo: commit the doc root (nothing else), push the branch when that is safe, open a pull request when it is not."""
    repo = os.path.abspath(a.repo)
    slug, p = find_project(repo)
    quiet = a.if_changed
    if not p:
        if not quiet: print(f"unregistered: {repo} (project register first)")
        return
    if p["mode"] != "repo":
        if not quiet: print(f"{slug} is mode {p['mode']}; its docs live in the vault (vault sync)")
        return
    mode = p.get("sync") or "push"
    root = p.get("root") or "ai-docs"
    if mode == "off":
        if not quiet: print(f"sync is off for {slug} (project register --sync push|pr to change)")
        return
    if not shutil.which("git"):
        return
    if a.detach:
        args = [sys.executable, os.path.abspath(__file__), "project", "sync", repo] + (["--if-changed"] if quiet else []) + (["--pr"] if a.pr else [])
        rc, gitdir, _ = run(["git", "rev-parse", "--git-dir"], cwd=repo, timeout=10)
        if rc != 0:
            return
        gitdir = gitdir if os.path.isabs(gitdir) else os.path.join(repo, gitdir)
        flags = (getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | NO_WINDOW) if os.name == "nt" else 0
        log = open(os.path.join(gitdir, "everlast-sync.log"), "ab")
        subprocess.Popen(args, cwd=repo, stdout=log, stderr=log, stdin=subprocess.DEVNULL, creationflags=flags, start_new_session=(os.name != "nt"))
        return
    st = project_git_state(repo, root)
    if st is None:
        if not quiet: print(f"{repo} is not a git work tree; nothing to sync")
        return
    if not st["branch"]:
        print("detached HEAD; nothing committed or pushed"); return
    stamp = f"[{dt.datetime.now():%Y-%m-%d %H:%M}] {slug}"
    if st["dirty_docs"]:
        if a.dry_run:
            print(f"{stamp} would commit {len(st['dirty_docs'])} file(s) under {root}/: " + change_summary(repo, root)[0])
        else:
            ok, msg = commit_paths(repo, root, f"everlast: {root} from {host_label()}")
            print(f"{stamp} commit: {msg}")
            if not ok:
                return
            st = project_git_state(repo, root)
    elif quiet and st["unpushed_docs"] == 0:
        return
    if not st["remote"]:
        print(f"{stamp} no remote; committed locally only"); return
    if st["upstream"] and st["unpushed_docs"] == 0 and not st["dirty_docs"]:
        print(f"{stamp} {root}/ is already on {st['upstream']}"); return
    reason = None
    if a.pr or mode == "pr":
        reason = "--pr was given" if a.pr else f"sync mode is pr for {slug}"
    elif not st["upstream"]:
        if remote_default_branch(repo, st["remote"]) is None:  # an empty remote: nothing there to be unsure about
            if a.dry_run:
                print(f"{stamp} would push {st['branch']} to the empty remote {st['remote']} and set it as upstream"); return
            rc, out, err = run(["git", "push", "-q", "-u", st["remote"], "HEAD"], cwd=repo, timeout=120)
            print(f"{stamp} push: " + (f"ok ({st['branch']} -> {st['remote']}, upstream set)" if rc == 0 else err[:300])); return
        reason = f"branch {st['branch']} has no upstream"
    else:
        st = project_git_state(repo, root, fetch=not a.dry_run)
        if st["behind"]:
            reason = f"{st['branch']} is behind {st['upstream']} by {st['behind']} commit(s)"
        elif st["foreign"]:
            reason = f"the unpushed commits include work by {', '.join(st['foreign'])}"
    if reason is None:
        target = st["upstream"].split("/", 1)[1]
        if a.dry_run:
            print(f"{stamp} would push {st['branch']} -> {st['upstream']} ({st['ahead']} commit(s), {st['unpushed_docs']} touching {root}/)"); return
        rc, out, err = run(["git", "push", "-q", st["remote"], f"HEAD:refs/heads/{target}"], cwd=repo, timeout=120)
        if rc == 0:
            print(f"{stamp} push: ok ({st['branch']} -> {st['upstream']}, {st['unpushed_docs']} commit(s) touching {root}/)"); return
        reason = "the push was rejected: " + ((err.strip().splitlines() or ["unknown"])[-1][:120])
    print(f"{stamp} " + docs_pull_request(repo, root, st, reason, dry_run=a.dry_run))


# ---------------------------------------------------------------- vault

def cmd_vault_init(a):
    v = os.path.abspath(os.path.expanduser(a.path)) if a.path else vault_path()
    os.makedirs(v, exist_ok=True)
    made = ["user/" + m for m in scaffold(os.path.join(v, "user"), readme=None)]
    owner = a.owner or os.environ.get("USERNAME") or os.environ.get("USER") or "the owner"
    for name, text in (("README.md", VAULT_README.format(owner=owner)),
                       ("config/redact.txt", "# One regex per line. Matches make the privacy scan treat text as private (names of coworkers, internal hostnames, codenames).\n"),
                       (".gitignore", "*.tmp\n.DS_Store\nThumbs.db\n.sync.log\n"),
                       ("user/PROFILE.md", "# Profile\n\nHow this person wants AI agents to work, in any tool. Every rule carries its reason. Grows from corrections; never from web research.\n"),
                       ("user/ENVIRONMENTS.md", "# Environments\n\nThe machines and tools this person runs agents on: paths, ports, what works, what breaks. One section per machine and tool.\n")):
        p = os.path.join(v, name)
        if not os.path.exists(p):
            write(p, text)
            made.append(name)
    if not os.path.exists(registry_path() if not a.path else os.path.join(v, "registry.json")):
        write(os.path.join(v, "registry.json"), json.dumps({"everlast": "1.0", "owner": owner, "projects": {}}, indent=2) + "\n")
        made.append("registry.json")
    if not os.path.isdir(os.path.join(v, ".git")):
        rc, _, err = run(["git", "init", "-q"], cwd=v)
        made.append("git init" if rc == 0 else f"git init failed: {err}")
    print(f"vault at {v}: " + ", ".join(made))
    if run(["git", "remote"], cwd=v)[1].strip() == "":
        print("  " + VAULT_REMOTE_QUESTION)
    if a.path and os.path.normcase(v) != os.path.normcase(vault_path()):
        print(f"  set EVERLAST_VAULT={v} or everlast.config.json vault so the scripts find it")


def vault_git_state(v):
    rc, dirty, _ = run(["git", "status", "--porcelain"], cwd=v)
    rc2, remote, _ = run(["git", "remote", "get-url", "origin"], cwd=v)
    rc3, ab, _ = run(["git", "rev-list", "--left-right", "--count", "HEAD...@{upstream}"], cwd=v)
    ahead = behind = None
    if rc3 == 0 and ab:
        parts = ab.split()
        if len(parts) == 2:
            ahead, behind = parts
    return bool(dirty.strip()), (remote if rc2 == 0 else None), ahead, behind


def cmd_vault_status(a):
    v = vault_path()
    if not os.path.isdir(v):
        print(f"no vault at {v} (run vault init)")
        return
    dirty, remote, ahead, behind = vault_git_state(v)
    reg = registry()
    n_user = sum(1 for _ in entries(os.path.join(v, "user")))
    print(f"vault {v}: {len(reg.get('projects', {}))} project(s), {n_user} user-tier entries")
    print(f"  git: remote {remote or 'none'}; {'uncommitted changes' if dirty else 'clean'}; ahead {ahead or 0}, behind {behind or 0}")
    rl = redact_list()
    print(f"  redact patterns: {len(rl)}")


def cmd_vault_sync(a):
    v = vault_path()
    if not os.path.isdir(os.path.join(v, ".git")):
        fail(f"vault at {v} is not a git repository")
    if a.detach:
        args = [sys.executable, os.path.abspath(__file__), "vault", "sync"] + (["--if-changed"] if a.if_changed else []) + (["--message", a.message] if a.message else [])
        flags = 0
        if os.name == "nt":
            flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) | NO_WINDOW
        log = open(os.path.join(v, ".sync.log"), "ab")
        subprocess.Popen(args, cwd=v, stdout=log, stderr=log, stdin=subprocess.DEVNULL, creationflags=flags, start_new_session=(os.name != "nt"))
        return
    dirty, remote, _, _ = vault_git_state(v)
    if a.if_changed and not dirty:
        rc, _, _ = run(["git", "rev-list", "--count", "@{upstream}..HEAD"], cwd=v) if remote else (1, "", "")
        # nothing local to commit; still try a push of unpushed commits below
    if dirty:
        ok, msg = vault_commit(v, a.message)
        print(f"[{dt.datetime.now():%Y-%m-%d %H:%M}] commit: {msg}")
    if not remote:
        print("no remote; committed locally only")
        return
    rc, out, err = run(["git", "pull", "--rebase", "-q"], cwd=v, timeout=120)
    if rc != 0:
        print(f"pull --rebase failed: {err[:300]} (resolve by hand; nothing was pushed)")
        run(["git", "rebase", "--abort"], cwd=v)
        return
    rc, out, err = run(["git", "push", "-q"], cwd=v, timeout=120)
    print(f"push: {'ok' if rc == 0 else err[:300]}")


def cmd_vault_where(a):
    print(f"plugin root: {PLUGIN_ROOT}")
    print(f"vault: {vault_path()} ({'exists' if os.path.isdir(vault_path()) else 'missing'})")
    print(f"registry: {registry_path()}")
    print(f"config: {os.path.join(PLUGIN_ROOT, 'everlast.config.json')} ({'present' if os.path.exists(os.path.join(PLUGIN_ROOT, 'everlast.config.json')) else 'absent'}); EVERLAST_VAULT={os.environ.get('EVERLAST_VAULT', '')}")


def vault_commit(v, message=None):
    """Commit everything in the vault (it is private end to end); the message lists what changed."""
    tail, body = change_summary(v)
    if not tail:
        return False, "nothing to commit"
    run(["git", "add", "-A"], cwd=v)
    msg = message or f"everlast: vault from {host_label()}: {tail}"
    rc, out, err = run(["git"] + git_ident(v) + ["commit", "-q", "-m", msg, "-m", body], cwd=v, timeout=60)
    return rc == 0, ("ok: " + tail if rc == 0 else (err or out)[:300])


def cmd_vault_remote(a):
    """Back the vault up: point it at a private repository the user names, or create one with gh (always --private)."""
    v = vault_path()
    if not os.path.isdir(os.path.join(v, ".git")):
        fail(f"vault at {v} is not a git repository (vault init first)")
    dirty, remote, ahead, behind = vault_git_state(v)
    if not a.url and a.create is None:
        print(f"vault {v}: remote {remote or 'none'}" + ("" if remote else "\n  " + VAULT_REMOTE_QUESTION))
        return
    if a.url and a.create is not None:
        fail("give a URL or --create, not both")
    if a.dry_run:
        print(f"would " + (f"set origin to {a.url} and push" if a.url else f"run: gh repo create {a.create or 'everlast-vault'} --private --source {v} --remote origin --push, then verify it is private"))
        return
    if dirty or run(["git", "rev-parse", "-q", "--verify", "HEAD"], cwd=v)[0] != 0:
        ok, msg = vault_commit(v)
        print(f"commit: {msg}")
    if a.url:
        rc, _, err = run(["git", "remote", "set-url" if remote else "add", "origin", a.url], cwd=v)
        if rc != 0:
            print(f"remote not set: {err[:200]}"); return
        rc, branch, _ = run(["git", "symbolic-ref", "--short", "-q", "HEAD"], cwd=v)
        rc, _, err = run(["git", "push", "-q", "-u", "origin", branch or "HEAD"], cwd=v, timeout=180)
        print(f"remote origin = {a.url}; push: {'ok' if rc == 0 else err[:300]}")
        return
    if remote:
        print(f"the vault already has a remote ({remote}); `vault remote <url>` changes it, nothing created"); return
    if not shutil.which("gh"):
        print("gh is not installed; create a private repository by hand and run `vault remote <url>` (nothing created)"); return
    rc, _, err = run(["gh", "auth", "status"], timeout=30)
    if rc != 0:
        print("gh is not logged in (`gh auth login`); nothing created"); return
    name = a.create or "everlast-vault"
    rc, out, err = run(["gh", "repo", "create", name, "--private", "--source", v, "--remote", "origin", "--push"], cwd=v, timeout=300)
    if rc != 0:
        print(f"gh repo create failed: {(err or out)[:300]} (nothing pushed)"); return
    url = (out.strip().splitlines() or [""])[-1]
    slug = github_slug(v, "origin") or name
    rc, vis, _ = run(["gh", "repo", "view", slug, "--json", "isPrivate", "-q", ".isPrivate"], timeout=30)
    if rc == 0 and vis.strip().lower() != "true":
        run(["git", "remote", "remove", "origin"], cwd=v)
        print(f"created {url or slug} but it is NOT private (an organisation policy?); remote removed. Delete that repository and use a private host.")
        return
    print(f"created private repository {url or slug}; origin set and pushed" + ("" if rc == 0 else " (could not re-verify visibility with gh; check it)"))


# ---------------------------------------------------------------- export, pack

def cmd_export(a):
    target = os.path.abspath(os.path.expanduser(a.target))
    dst_root = os.path.join(target, ".agents", "skills")
    os.makedirs(dst_root, exist_ok=True)
    src_root = os.path.join(PLUGIN_ROOT, "skills")
    done = []
    for name in sorted(os.listdir(src_root)):
        src = os.path.join(src_root, name)
        dst = os.path.join(dst_root, name)
        if not os.path.isdir(src):
            continue
        if os.path.lexists(dst):
            done.append(f"{name} (already present)")
            continue
        if a.copy:
            shutil.copytree(src, dst)
            done.append(f"{name} (copied)")
        else:
            done.append(f"{name} ({'linked' if link_dir(dst, src) else 'LINK FAILED'})")
    print(f"exported to {dst_root}: " + ", ".join(done))
    print("then add the pointer block from templates/AGENTS.md.snippet to the target's AGENTS.md (Copilot also reads .github/copilot-instructions.md)")


def cmd_pack(a):
    out = os.path.abspath(a.out or os.path.dirname(PLUGIN_ROOT))
    os.makedirs(out, exist_ok=True)
    skip = ("__pycache__", ".git", "evals/results", ".sync.log")
    files = []
    for dp, dirs, fs in os.walk(PLUGIN_ROOT):
        dirs[:] = [d for d in dirs if d not in (".git", "__pycache__")]
        for f in fs:
            p = os.path.join(dp, f)
            rel = os.path.relpath(p, PLUGIN_ROOT).replace("\\", "/")
            if any(s in rel for s in skip) or f.endswith((".zip", ".plugin", ".pyc")):
                continue
            files.append((p, rel))
    zpath = os.path.join(out, f"everlast-protocol-{VERSION}.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for p, rel in files:
            z.write(p, "everlast-protocol/" + rel)
    ppath = os.path.join(out, "everlast-protocol.plugin")
    with zipfile.ZipFile(ppath, "w", zipfile.ZIP_DEFLATED) as z:
        for p, rel in files:
            z.write(p, rel)
    print(f"wrote {zpath} ({len(files)} files) and {ppath} (Cowork: Customize > Plugins > upload)")


# ---------------------------------------------------------------- promotion (unchanged from aidocs)

STOP = set("a an and are as at be by for from how in is it of on or that the this to use when with your you".split())


def keywords(text, n=8):
    words = re.findall(r"[a-z][a-z0-9+#.-]{2,}", text.lower())
    freq = {}
    for w in words:
        if w in STOP:
            continue
        freq[w] = freq.get(w, 0) + 1
    return [w for w, _ in sorted(freq.items(), key=lambda kv: -kv[1])[:n]]


def skill_roots(extra=None):
    home = os.path.expanduser("~")
    roots = [os.path.join(home, ".claude", "skills"), os.path.join(os.getcwd(), ".claude", "skills")]
    cache = os.path.join(home, ".claude", "plugins", "cache")
    if os.path.isdir(cache):
        roots.append(cache)
    for r in extra or []:
        roots.append(r)
    return [r for r in roots if os.path.isdir(r)]


def visible_skills(roots):
    out, seen = [], set()
    for root in roots:
        for dp, dirs, files in os.walk(root):
            if dp.count(os.sep) - root.count(os.sep) > 6:
                dirs[:] = []
            if "SKILL.md" in files:
                path = os.path.join(dp, "SKILL.md")
                try:
                    text = read(path)
                except Exception:
                    continue
                m = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.S)
                fm = m.group(1) if m else ""
                name = re.search(r"^name:\s*(.+)$", fm, re.M)
                name = name.group(1).strip() if name else os.path.basename(dp)
                if name in seen:
                    continue
                seen.add(name)
                d = re.search(r"^description:\s*(.*)", fm, re.S | re.M)
                out.append((name, (d.group(1) if d else "").strip().strip('"'), path))
    return out


def cmd_skill_budget(a):
    roots = skill_roots(a.roots)
    skills = visible_skills(roots)
    chars = sum(len(d) for _, d, _ in skills)
    tokens = chars // 4
    budget = int(a.context * 0.01)
    print(f"skills visible: {len(skills)} across {len(roots)} root(s); description chars {chars} (~{tokens} tokens)")
    print(f"listing budget at 1% of a {a.context}-token context: ~{budget} tokens -> "
          + ("OVER budget: Claude Code evicts the least-used skills from the listing silently" if tokens > budget else "within budget"))
    if a.verbose:
        for n, d, _ in sorted(skills, key=lambda x: -len(x[1])):
            print(f"  {len(d):5d}  {n}")


def cmd_promote_scan(a):
    root = docs_root(a.repo, a.root)
    if not os.path.isdir(root):
        fail(f"no docs root at {root}")
    logp = os.path.join(root, "log.md")
    dates_by_title = {}
    if os.path.exists(logp):
        for line in read(logp).splitlines():
            m = re.match(r"## \[(\d{4}-\d{2}-\d{2})\] (\w+) \| (?:(?:solution|decision|plan|note): )?(.+?)(?: -> .*)?$", line)
            if m and m.group(2) in ("add", "update", "supersede"):
                key = re.sub(r"[^a-z0-9]", "", m.group(3).lower())
                dates_by_title.setdefault(key, set()).add(m.group(1))
    cands, by_tag = [], {}
    for rel, meta, body in entries(root):
        if meta["status"] != "active":
            continue
        key = re.sub(r"[^a-z0-9]", "", meta["title"].lower())
        dates = dates_by_title.get(key, set())
        steps = len(re.findall(r"^(?:\d+\.|- )", body, re.M))
        if len(dates) >= a.min_dates and steps >= 3:
            cands.append({"kind": "recurrence", "title": meta["title"], "entries": [rel], "dates": sorted(dates), "steps": steps,
                          "text": meta["title"] + " " + " ".join(meta.get("tags", []) if isinstance(meta.get("tags"), list) else []) + " " + body})
        if meta["kind"] == "solution":
            for t in (meta.get("tags") or []):
                by_tag.setdefault(t, []).append((rel, meta["title"], body))
    for t, items in by_tag.items():
        if len(items) >= a.min_dates:
            cands.append({"kind": "cluster", "title": f"{t} solutions", "entries": [r for r, _, _ in items], "dates": [], "steps": None,
                          "text": " ".join(ti + " " + b for _, ti, b in items)})
    skills = visible_skills(skill_roots())
    chars = sum(len(d) for _, d, _ in skills)
    budget_tokens = int(a.context * 0.01)
    over = chars // 4 > budget_tokens
    out = []
    for c in cands:
        kws = keywords(c["text"])
        overlap = []
        for n, d, _ in skills:
            hits = sum(1 for k in kws if k in d.lower())
            if hits >= max(3, len(kws) // 2):
                overlap.append((n, hits))
        overlap.sort(key=lambda x: -x[1])
        verdict = "extend " + overlap[0][0] if overlap else ("blocked: listing over budget, retire one first" if over else "eligible")
        out.append({"kind": c["kind"], "title": c["title"], "entries": c["entries"], "dates": c["dates"], "steps": c["steps"],
                    "keywords": kws, "overlap": overlap[:3], "verdict": verdict})
    if a.json:
        print(json.dumps({"skills_visible": len(skills), "listing_tokens": chars // 4, "budget_tokens": budget_tokens, "candidates": out}, indent=2))
        return
    print(f"skills visible {len(skills)}, listing ~{chars // 4} tokens, budget ~{budget_tokens} ({'over' if over else 'ok'})")
    if not out:
        print("no skill candidates (need an entry with >= 3 steps touched on >= %d distinct dates, or >= %d solutions sharing a tag)" % (a.min_dates, a.min_dates))
        return
    for c in out:
        print(f"- [{c['kind']}] {c['title']}: {c['verdict']}")
        print(f"    entries {', '.join(c['entries'])}; dates {', '.join(c['dates']) or 'n/a'}; keywords {', '.join(c['keywords'])}")
        if c["overlap"]:
            print(f"    overlapping skills: {', '.join(n for n, _ in c['overlap'])}")


# ---------------------------------------------------------------- hooks

def marker_path(session_id):
    return os.path.join(tempfile.gettempdir(), f"everlast-prodded-{session_id or 'nosession'}")


def repo_has_changes(cwd):
    rc, out, _ = run(["git", "status", "--porcelain"], cwd=cwd, timeout=5)
    return rc == 0 and bool(out.strip())


def docs_touched_recently(root, hours=8):
    if not os.path.isdir(root):
        return None
    cutoff = dt.datetime.now() - dt.timedelta(hours=hours)
    for dp, _, files in os.walk(root):
        for f in files:
            if f.endswith(".md") and dt.datetime.fromtimestamp(os.path.getmtime(os.path.join(dp, f))) > cutoff:
                return True
    return False


def cmd_hook_run(a):
    try:
        payload = {} if sys.stdin.isatty() else json.loads(sys.stdin.buffer.read().decode("utf-8", "replace") or "{}")
    except Exception:
        payload = {}
    event = payload.get("hook_event_name", "") or a.event or ""
    cwd = payload.get("cwd") or os.getcwd()
    sid = payload.get("session_id", "")
    if event == "SessionStart":
        slug, p = find_project(cwd)
        root = docs_root(cwd)
        v = vault_path()
        bits = []
        if p:
            bits.append(f"project {slug} (mode {p['mode']})")
            if p["mode"] == "repo" and (p.get("sync") or "push") != "off":
                st = project_git_state(cwd, p.get("root") or "ai-docs")
                if st and not st["remote"]:
                    bits.append(f"{p.get('root') or 'ai-docs'}/ has no remote to back up to")
                elif st and (st["dirty_docs"] or st["unpushed_docs"]):
                    bits.append(f"{p.get('root') or 'ai-docs'}/: {len(st['dirty_docs'])} uncommitted file(s), {st['unpushed_docs']} unpushed commit(s); "
                                f"the SessionEnd hook pushes them (`everlast.py project sync .` to do it now)")
        elif os.path.isdir(root):
            bits.append("project docs present, unregistered (everlast-setup registers it)")
        if os.path.isdir(v):
            n_user = sum(1 for _ in entries(os.path.join(v, "user")))
            bits.append(f"user tier {n_user} entries at {os.path.join(v, 'user', 'INDEX.md')}; PROFILE.md and ENVIRONMENTS.md there")
            dirty, remote, ahead, behind = vault_git_state(v)
            if behind and behind != "0":
                bits.append(f"vault behind remote by {behind}; pull it")
            if not remote and os.path.isdir(os.path.join(v, ".git")):
                bits.append(VAULT_REMOTE_QUESTION)
        else:
            bits.append(f"no vault at {v} (everlast-vault init)")
        if contribute_setting() is None:
            bits.append("contribution not decided: ask the user once, then `everlast.py contribute yes|no`")
        rem, n = behind_official()  # from the last fetch; `everlast.py pull` fetches
        if n:
            bits.append(f"plugin behind the official repository by {n} commit(s); `everlast.py pull`")
        if os.path.isdir(root):  # check before use: read-only, no git, nothing written; silent when there is nothing to do
            try:
                rep = maintenance(root, cwd, scan=not (p and p.get("mode") == "excluded"))
                due, parts = rep["recheck"], []
                if due:
                    parts.append(f"recheck due: {len(due)} (" + "; ".join(t[:70] for _, t, _ in due[:3]) + ("; ..." if len(due) > 3 else "") + ")")
                if maintenance_count(rep):
                    parts.append(f"maintain: {maintenance_count(rep)}")
                if parts:
                    bits.append(" · ".join(parts) + (" (`everlast.py recheck <title>` before relying on one)" if due else ""))
            except Exception:
                pass
        if bits:
            print("[everlast] " + "; ".join(bits))
        h = os.path.join(root, "HANDOFF.md")
        if os.path.exists(h):
            text = read(h)
            if "## Next single action" in text and "<One thing." not in text:
                print("[everlast] HANDOFF.md from the last session (load INDEX.md entries only as the task needs them):")
                print("\n".join(text.splitlines()[:50]))
        return
    if event == "Stop":
        if payload.get("stop_hook_active"):
            return
        m = marker_path(sid)
        if os.path.exists(m):
            return
        root = docs_root(cwd)
        touched = docs_touched_recently(root)
        if touched is None or touched:
            return
        if not repo_has_changes(cwd):
            return
        write(m, today())
        reason = ("[everlast] The working tree changed this session and nothing in the project docs was written. "
                  "Run the everlast-capture checklist once: record any dead end, verified command, decision, or user-level lesson "
                  "(everlast.py note / handoff; --private for anything naming people or credentials, --user for lessons about the person or machine), "
                  "or reply that there is nothing worth recording, then stop.")
        print(json.dumps({"decision": "block", "reason": reason}))
        return
    if event == "SessionEnd":
        v = vault_path()
        if os.path.isdir(os.path.join(v, ".git")):
            a2 = argparse.Namespace(if_changed=True, detach=True, message=None)
            cmd_vault_sync(a2)
        slug, p = find_project(cwd)
        if p and p["mode"] == "repo":
            cmd_project_sync(argparse.Namespace(repo=cwd, if_changed=True, detach=True, pr=False, dry_run=False))
        if contribute_setting() == "yes":
            cmd_publish(argparse.Namespace(if_changed=True, dry_run=False))
        return


def hook_blocks(script):
    py = "python" if os.name == "nt" else "python3"  # never the pinned launcher (absent with Store, pyenv, uv, conda installs)
    cmd = f'{py} "{script}" hook run'
    return {
        "SessionStart": [{"hooks": [{"type": "command", "command": cmd, "timeout": 10}]}],
        "Stop": [{"hooks": [{"type": "command", "command": cmd, "timeout": 10}]}],
        "SessionEnd": [{"hooks": [{"type": "command", "command": cmd, "timeout": 5}]}],
    }


def settings_path(a):
    return a.settings or os.path.join(os.path.expanduser("~"), ".claude", "settings.json")


def cmd_hook_install(a):
    sp = settings_path(a)
    script = os.path.abspath(__file__).replace("\\", "/")
    data = load_json(sp, {})
    hooks = data.setdefault("hooks", {})
    for ev, blocks in hook_blocks(script).items():
        existing = hooks.setdefault(ev, [])
        if any("everlast.py" in h.get("command", "") for b in existing for h in b.get("hooks", [])):
            continue
        existing.extend(blocks)
    write(sp, json.dumps(data, indent=2) + "\n")
    note(f"installed everlast SessionStart, Stop and SessionEnd hooks in {sp} (not needed when installed as a Claude Code plugin)")


def cmd_hook_uninstall(a):
    sp = settings_path(a)
    if not os.path.exists(sp):
        return note("no settings file")
    data = load_json(sp, {})
    hooks = data.get("hooks", {})
    for ev in list(hooks):
        hooks[ev] = [b for b in hooks[ev] if not any("everlast.py" in h.get("command", "") or "aidocs.py" in h.get("command", "") for h in b.get("hooks", []))]
        if not hooks[ev]:
            del hooks[ev]
    write(sp, json.dumps(data, indent=2) + "\n")
    note(f"removed everlast (and legacy aidocs) hooks from {sp}")


def cmd_hook_print(a):
    print(json.dumps({"hooks": hook_blocks(os.path.abspath(__file__).replace("\\", "/"))}, indent=2))


# ---------------------------------------------------------------- main

def main():
    global STRICT
    for s in (sys.stdout, sys.stderr):  # Windows consoles and pipes default to a code page; the docs are UTF-8
        try:
            s.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--strict", action="store_true")
    sub = ap.add_subparsers(dest="cmd", required=True)

    def common(p, tiers=True):
        p.add_argument("repo")
        p.add_argument("--root", default="ai-docs")
        if tiers:
            g = p.add_mutually_exclusive_group()
            g.add_argument("--private", action="store_true", help="the project's private sidecar in the vault")
            g.add_argument("--user", action="store_true", help="the user tier in the vault")

    p = sub.add_parser("init"); common(p); p.set_defaults(fn=cmd_init)
    p = sub.add_parser("index"); common(p); p.set_defaults(fn=cmd_index)
    p = sub.add_parser("note"); common(p)
    p.add_argument("--kind", required=True); p.add_argument("--title", required=True)
    p.add_argument("--tags"); p.add_argument("--summary", help="one line: when to read this entry (shown in INDEX.md)"); p.add_argument("--body-file"); p.add_argument("--stdin", action="store_true")
    p.add_argument("--aliases", help="other names, comma-separated: synonyms, the tool's own words (search reads them)")
    p.add_argument("--alias", action="append", help="one alias taken verbatim, commas included (the exact error text); repeatable")
    p.add_argument("--stale-after", help="YYYY-MM-DD when a recheck falls due, or never; default today + the kind's window")
    p.add_argument("--supersedes"); p.add_argument("--force", action="store_true")
    p.add_argument("--agent", help="provenance: the tool that wrote this (default EVERLAST_AGENT)"); p.add_argument("--model", help="provenance: the model (default EVERLAST_MODEL)")
    p.add_argument("--allow-missing", action="store_true"); p.add_argument("--allow-private", action="store_true", help="write despite privacy hits (reviewed)")
    p.set_defaults(fn=cmd_note)
    p = sub.add_parser("handoff"); common(p); p.add_argument("--body-file"); p.add_argument("--stdin", action="store_true")
    p.add_argument("--allow-private", action="store_true"); p.set_defaults(fn=cmd_handoff)
    p = sub.add_parser("log"); common(p); p.add_argument("--op", required=True); p.add_argument("--title", required=True); p.set_defaults(fn=cmd_log)
    p = sub.add_parser("lint"); common(p); p.add_argument("--stale-days", type=int, default=None, help="one window for every kind (default: each kind's stale_after window)")
    p.add_argument("--all", action="store_true", help="also lint the private sidecar"); p.set_defaults(fn=cmd_lint)
    p = sub.add_parser("search", help="rank entries against a query (BM25 over title, aliases, tags, summary, body)")
    p.add_argument("query"); p.add_argument("repo", nargs="?", default="."); p.add_argument("--root", default="ai-docs")
    p.add_argument("--private", action="store_true", help="also the project's private sidecar"); p.add_argument("--user", action="store_true", help="also the user tier")
    p.add_argument("--all", action="store_true", help="every registered project, its sidecar, and the user tier")
    p.add_argument("-n", type=int, default=5, help="hits to print (default 5)"); p.add_argument("--json", action="store_true"); p.set_defaults(fn=cmd_search)
    for name, fn, hlp in (("recheck", cmd_recheck, "read-only: is the entry stale, which cited files changed since it was verified, what proves it"),
                          ("verify", cmd_verify, "record a recheck: renew verified and stale_after, or --failed with what broke")):
        p = sub.add_parser(name, help=hlp); p.add_argument("entry", help="a path, a file name, or part of the title")
        p.add_argument("repo", nargs="?", default="."); p.add_argument("--root", default="ai-docs")
        g = p.add_mutually_exclusive_group(); g.add_argument("--private", action="store_true"); g.add_argument("--user", action="store_true")
        if name == "verify":
            p.add_argument("--failed", metavar="WHAT_BROKE", help="the recheck failed: record what broke and mark the entry due now")
            p.add_argument("--note", help="what was re-run, or more detail"); p.add_argument("--allow-private", action="store_true")
        p.set_defaults(fn=fn)
    p = sub.add_parser("maintain", help="report upkeep; --apply archives old done/abandoned/superseded entries and rewrites links")
    p.add_argument("repo", nargs="?", default="."); p.add_argument("--root", default="ai-docs")
    g = p.add_mutually_exclusive_group(); g.add_argument("--private", action="store_true"); g.add_argument("--user", action="store_true")
    p.add_argument("--apply", action="store_true", help="do the deterministic part: archive and relink (never merges, deletes or edits content)")
    p.set_defaults(fn=cmd_maintain)
    p = sub.add_parser("scan"); p.add_argument("path"); p.add_argument("--json", action="store_true"); p.set_defaults(fn=cmd_scan)
    p = sub.add_parser("resolve"); common(p); p.set_defaults(fn=cmd_resolve)
    p = sub.add_parser("project"); ps = p.add_subparsers(dest="sub", required=True)
    q = ps.add_parser("register"); q.add_argument("repo"); q.add_argument("--mode", choices=["repo", "excluded"], required=True)
    q.add_argument("--slug"); q.add_argument("--no-link", action="store_true"); q.add_argument("--root", default="ai-docs")
    q.add_argument("--sync", choices=list(SYNC_MODES), help="mode repo: push the docs at session end (push, default; pull request when unsure), always pr, or off")
    q.set_defaults(fn=cmd_project_register)
    q = ps.add_parser("status"); q.add_argument("repo"); q.set_defaults(fn=cmd_project_status)
    q = ps.add_parser("list"); q.set_defaults(fn=cmd_project_list)
    q = ps.add_parser("sync", help="mode repo: commit the doc root only, push the branch when sure, open a pull request when not")
    q.add_argument("repo"); q.add_argument("--if-changed", action="store_true"); q.add_argument("--detach", action="store_true")
    q.add_argument("--pr", action="store_true", help="always the pull request route"); q.add_argument("--dry-run", action="store_true"); q.set_defaults(fn=cmd_project_sync)
    p = sub.add_parser("vault"); ps = p.add_subparsers(dest="sub", required=True)
    q = ps.add_parser("init"); q.add_argument("--path"); q.add_argument("--owner"); q.set_defaults(fn=cmd_vault_init)
    q = ps.add_parser("status"); q.set_defaults(fn=cmd_vault_status)
    q = ps.add_parser("sync"); q.add_argument("--if-changed", action="store_true"); q.add_argument("--detach", action="store_true"); q.add_argument("--message"); q.set_defaults(fn=cmd_vault_sync)
    q = ps.add_parser("where"); q.set_defaults(fn=cmd_vault_where)
    q = ps.add_parser("remote", help="back the vault up: <url> of a private repository, or --create [name] (gh repo create --private)")
    q.add_argument("url", nargs="?"); q.add_argument("--create", nargs="?", const="", help="create a private GitHub repository with gh (default name everlast-vault)")
    q.add_argument("--dry-run", action="store_true"); q.set_defaults(fn=cmd_vault_remote)
    p = sub.add_parser("contribute", help="asked once at install: may this install open pull requests with its learnings? (yes|no|status)")
    p.add_argument("value", nargs="?", choices=["yes", "no", "status"]); p.set_defaults(fn=cmd_contribute)
    p = sub.add_parser("pull", help="update this clone from the official repository (merge on a fork, fast-forward on a plain clone)")
    p.add_argument("--dry-run", action="store_true"); p.set_defaults(fn=cmd_pull)
    p = sub.add_parser("publish", help="consent-gated: push this install's plugin learnings as a draft pull request")
    p.add_argument("--if-changed", action="store_true"); p.add_argument("--dry-run", action="store_true"); p.set_defaults(fn=cmd_publish)
    p = sub.add_parser("export"); p.add_argument("target"); p.add_argument("--copy", action="store_true"); p.set_defaults(fn=cmd_export)
    p = sub.add_parser("pack"); p.add_argument("--out"); p.set_defaults(fn=cmd_pack)
    p = sub.add_parser("promote-scan"); common(p, tiers=False); p.add_argument("--min-dates", type=int, default=3)
    p.add_argument("--context", type=int, default=1000000); p.add_argument("--json", action="store_true"); p.set_defaults(fn=cmd_promote_scan)
    p = sub.add_parser("skill-budget"); p.add_argument("--context", type=int, default=1000000); p.add_argument("--roots", nargs="*")
    p.add_argument("--verbose", action="store_true"); p.set_defaults(fn=cmd_skill_budget)
    p = sub.add_parser("hook"); p.add_argument("action", choices=["run", "install", "uninstall", "print"]); p.add_argument("--settings"); p.add_argument("--event")
    p.set_defaults(fn=lambda a: {"run": cmd_hook_run, "install": cmd_hook_install, "uninstall": cmd_hook_uninstall, "print": cmd_hook_print}[a.action](a))

    a = ap.parse_args()
    STRICT = a.strict
    try:
        a.fn(a)
    except SystemExit:
        raise
    except Exception as e:
        print(f"everlast: {e}")
        sys.exit(1 if STRICT else 0)


if __name__ == "__main__":
    main()

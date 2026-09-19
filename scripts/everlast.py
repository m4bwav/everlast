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
  note     <repo> --kind K --title T [--tags a,b] [--summary "when to read it"] [--body-file F | --stdin] [--supersedes PATH] [--private | --user]
  handoff  <repo> (--body-file F | --stdin) [--private | --user]   replace HANDOFF.md
  index    <repo> [--private | --user]         rebuild INDEX.md
  lint     <repo> [--stale-days N] [--all]     budgets, headings, dead paths, stale, duplicates, privacy scan
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
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import re
import shutil
import platform
import subprocess
import sys
import tempfile
import zipfile

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

INDEX_HEADER = """# Index

Generated by `everlast.py index`; do not hand-edit (edit the entries' frontmatter instead). One line per entry: kind, status, date, title, tags. Load an entry only when its title or tags match the task. Continuity for the current work is in [HANDOFF.md](HANDOFF.md); the append-only history is [log.md](log.md).

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

Append-only. One line per operation: `## [YYYY-MM-DD] op | title` where op is one of add, update, supersede, prune, handoff, index. Newest at the bottom. Never edited, only appended; this is the history the entries themselves do not carry.

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


def today():
    return dt.date.today().isoformat()


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


def run(cmd, cwd=None, timeout=60):
    try:
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=timeout)
        return out.returncode, (out.stdout or "").strip(), (out.stderr or "").strip()
    except Exception as e:
        return 1, "", str(e)


def status_lines(cwd, pathspec=None):
    """`git status --porcelain` lines with the leading space intact (run() strips its output, which eats the first
    line's unstaged-change marker and shifts the path); None when the command fails."""
    try:
        cmd = ["git", "-c", "core.quotepath=off", "status", "--porcelain", "--untracked-files=all", "--"] + ([pathspec] if pathspec else [])
        out = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60)
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
        return os.path.abspath(os.path.expanduser(env))
    local = os.path.join(os.getcwd(), ".everlast-vault")   # a workspace-local vault (evals, sandboxes)
    if os.path.isdir(local):
        return local
    v = config().get("vault")
    if isinstance(v, dict):
        v = v.get(os.name) or v.get("posix" if os.name != "nt" else "nt")
    if v:
        if os.name != "nt" and re.match(r"^[A-Za-z]:[\\/]", v):
            v = None
        else:
            return os.path.abspath(os.path.expanduser(v))
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


def parse_frontmatter(text):
    m = re.match(r"^---\r?\n(.*?)\r?\n---\r?\n", text, re.S)
    meta = {}
    if not m:
        return meta, text
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            v = v.strip()
            if v.startswith("[") and v.endswith("]"):
                v = [x.strip().strip("'\"") for x in v[1:-1].split(",") if x.strip()]
            meta[k.strip()] = v
    return meta, text[m.end():]


def frontmatter(meta):
    lines = ["---"]
    for k, v in meta.items():
        if isinstance(v, list):
            v = "[" + ", ".join(v) + "]"
        lines.append(f"{k}: {v}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def entries(root):
    for kind, d in DIRS.items():
        folder = os.path.join(root, d)
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
            yield os.path.join(d, name).replace("\\", "/"), meta, body


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


def build_index(root):
    rows = []
    for rel, meta, _ in entries(root):
        rows.append((meta.get("date", ""), meta["kind"], meta["status"], meta["title"], rel, meta.get("tags", []), str(meta.get("summary") or "").strip()))
    for name, meta in adopt_loose_files(root):
        rows.append((meta["date"], meta["kind"], meta["status"], meta["title"], name, meta["tags"], ""))
    rows.sort(key=lambda r: (r[1], r[0]))
    lines = [INDEX_HEADER.rstrip()]
    current = None
    for date, kind, status, title, rel, tags, summary in rows:
        if kind != current:
            lines.append(f"\n## {DIRS.get(kind, kind)}\n")
            current = kind
        tag = (" `" + ",".join(tags) + "`") if tags else ""
        flag = "" if status == "active" else f" ({status})"
        why = f": {summary}" if summary else ""
        lines.append(f"- {date or 'undated'} [{title}]({rel}){flag}{tag}{why}")
    write(os.path.join(root, "INDEX.md"), "\n".join(lines).rstrip() + "\n")
    return len(rows)


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
    if not (a.private or a.user) and not a.allow_private:
        hits = privacy_hits(a.title + "\n" + body, redact_list())
        if hits:
            fail("privacy scan flagged this entry for the repo-safe root: " + "; ".join(f"{l} ({s})" for l, s in hits[:5])
                 + ". Write it with --private (sidecar), or --allow-private if the reviewer decided it is safe.")
    tags = [t.strip() for t in (a.tags or "").split(",") if t.strip()]
    d = today()
    rel = f"{DIRS[a.kind]}/{d}-{slugify(a.title)}.md"
    path = os.path.join(root, rel)
    if os.path.exists(path) and not a.force:
        fail(f"{rel} exists; use --force to overwrite or choose another title")
    meta = {"title": a.title, "kind": a.kind, "status": "active", "date": d, "verified": d, "tags": tags}
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
            om, ob = parse_frontmatter(read(old))
            om["status"] = "superseded"
            om["superseded_by"] = rel
            write(old, frontmatter(om) + ob)
            append(os.path.join(root, "log.md"), f"## [{d}] supersede | {om.get('title', a.supersedes)} -> {a.title}\n")
    write(path, frontmatter(meta) + "\n# " + a.title + "\n\n" + body.lstrip())
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


PATH_RE = re.compile(r"`([A-Za-z0-9_./\\-]+\.[A-Za-z0-9]{1,6})`")


def lint_root(root, repo, stale_days, problems, scan=True):
    warn = problems.append
    for name, cap in (("INDEX.md", 120), ("HANDOFF.md", 50)):
        p = os.path.join(root, name)
        if os.path.exists(p):
            n = len(read(p).splitlines())
            if n > cap:
                warn(f"{name}: {n} lines, budget {cap}")
        else:
            warn(f"{name} missing in {root} (run init)")
    idx = os.path.join(root, "INDEX.md")
    indexed = set(re.findall(r"\]\(([^)]+\.md)\)", read(idx))) if os.path.exists(idx) else set()
    titles = {}
    stale_cut = dt.date.today() - dt.timedelta(days=stale_days)
    redact = redact_list() if scan else []
    for rel, meta, body in entries(root):
        if rel not in indexed:
            warn(f"{rel}: not in INDEX.md (run index)")
        for h in REQUIRED_HEADINGS.get(meta["kind"], []):
            if h not in body:
                warn(f"{rel}: missing heading '{h}'")
        if re.search(r"<[A-Z][^>]{10,}>", body):
            warn(f"{rel}: template placeholder text still present")
        key = re.sub(r"[^a-z0-9]", "", meta["title"].lower())
        if key in titles:
            warn(f"{rel}: title duplicates {titles[key]} (merge or supersede)")
        titles[key] = rel
        if meta["status"] == "active":
            v = meta.get("verified") or meta.get("date")
            try:
                if v and dt.date.fromisoformat(v) < stale_cut:
                    warn(f"{rel}: last verified {v}, older than {stale_days} days; re-verify or mark superseded")
            except ValueError:
                warn(f"{rel}: bad date '{v}'")
        for ref in PATH_RE.findall(body):
            if ref.startswith(("http", "www")):
                continue
            cand = [os.path.join(repo, ref), os.path.join(root, ref), os.path.join(root, os.path.dirname(rel), ref)]
            if ("/" in ref or "\\" in ref) and not any(os.path.exists(c) for c in cand):
                warn(f"{rel}: references `{ref}` which does not exist (dead path)")
        if scan:
            for label, snippet in privacy_hits(body, redact)[:3]:
                warn(f"{rel}: privacy: {label} ({snippet}); move to the private sidecar (--private) or redact")
    logp = os.path.join(root, "log.md")
    if os.path.exists(logp) and len(read(logp).splitlines()) > 400:
        warn(f"log.md in {root} over 400 lines; archive older lines to log-ARCHIVE.md")


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
                problems.append(f"{name}: {n} lines; always-on text costs every session (soft cap {cap}); move detail into entries")
    slug, p = find_project(a.repo)
    lint_root(root, repo, a.stale_days, problems, scan=not (a.private or a.user) and (p or {}).get("mode") != "excluded")
    if a.all and not (a.private or a.user):
        priv = docs_root(a.repo, a.root, private=True)
        if os.path.isdir(priv):
            lint_root(priv, repo, a.stale_days, problems, scan=False)
    if p and p.get("mode") == "excluded":
        rc, out, _ = run(["git", "check-ignore", "-q", (p.get("root") or "ai-docs")], cwd=repo)
        if rc != 0:
            problems.append(f"mode excluded but git does not ignore {p.get('root') or 'ai-docs'}/ (re-run project register; Claude Code rewrites .git/info/exclude, issue anthropics/claude-code#84954)")
    if problems:
        print(f"lint: {len(problems)} finding(s)")
        for x in problems:
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
                shutil.move(os.path.join(link, name), os.path.join(store, name))
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
        flags = (getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)) if os.name == "nt" else 0
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
            flags = getattr(subprocess, "DETACHED_PROCESS", 0) | getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
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
    p.add_argument("--supersedes"); p.add_argument("--force", action="store_true")
    p.add_argument("--agent", help="provenance: the tool that wrote this (default EVERLAST_AGENT)"); p.add_argument("--model", help="provenance: the model (default EVERLAST_MODEL)")
    p.add_argument("--allow-missing", action="store_true"); p.add_argument("--allow-private", action="store_true", help="write despite privacy hits (reviewed)")
    p.set_defaults(fn=cmd_note)
    p = sub.add_parser("handoff"); common(p); p.add_argument("--body-file"); p.add_argument("--stdin", action="store_true")
    p.add_argument("--allow-private", action="store_true"); p.set_defaults(fn=cmd_handoff)
    p = sub.add_parser("log"); common(p); p.add_argument("--op", required=True); p.add_argument("--title", required=True); p.set_defaults(fn=cmd_log)
    p = sub.add_parser("lint"); common(p); p.add_argument("--stale-days", type=int, default=120); p.add_argument("--all", action="store_true", help="also lint the private sidecar"); p.set_defaults(fn=cmd_lint)
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

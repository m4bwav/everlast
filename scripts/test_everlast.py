#!/usr/bin/env python3
"""Self-test for everlast.py: runs the whole protocol against a temporary vault and two temporary repos.

python scripts/test_everlast.py      -> prints one line per check, exits 1 on the first failure.
Needs git on PATH. Uses no network. Leaves nothing behind.
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPT = os.path.join(HERE, "everlast.py")
PY = sys.executable


def run(*args, env=None, stdin=None):
    p = subprocess.run([PY, SCRIPT, *args], capture_output=True, text=True, encoding="utf-8", errors="replace", env=env, input=stdin, timeout=120)
    return p.returncode, (p.stdout + p.stderr)


def check(cond, name, detail=""):
    print(("ok   " if cond else "FAIL ") + name + (("  " + detail.strip()[:200]) if detail and not cond else ""))
    if not cond:
        sys.exit(1)


def main():
    tmp = tempfile.mkdtemp(prefix="everlast-test-")
    try:
        vault = os.path.join(tmp, "vault")
        r1 = os.path.join(tmp, "repo1")
        r2 = os.path.join(tmp, "repo2")
        for r in (r1, r2):
            os.makedirs(r)
            subprocess.run(["git", "init", "-q"], cwd=r, check=True)
        env = dict(os.environ, EVERLAST_VAULT=vault, GIT_AUTHOR_NAME="everlast-test", GIT_AUTHOR_EMAIL="test@example.invalid",
                   GIT_COMMITTER_NAME="everlast-test", GIT_COMMITTER_EMAIL="test@example.invalid")

        rc, out = run("vault", "init", "--owner", "Tester", env=env)
        check(os.path.isfile(os.path.join(vault, "user", "INDEX.md")) and os.path.isdir(os.path.join(vault, ".git")), "vault init scaffolds user tier and git", out)
        check(os.path.isfile(os.path.join(vault, "config", "redact.txt")), "vault init writes redact.txt", out)

        rc, out = run("project", "register", r1, "--mode", "repo", env=env)
        check("registered repo1 (repo)" in out and os.path.isfile(os.path.join(r1, "ai-docs", "INDEX.md")), "register repo mode", out)
        check(os.path.isdir(os.path.join(vault, "projects", "repo1", "private")), "repo mode creates private sidecar", out)

        rc, out = run("project", "register", r2, "--mode", "excluded", env=env)
        check("registered repo2 (excluded)" in out, "register excluded mode", out)
        link = os.path.join(r2, "ai-docs")
        check(os.path.isdir(link) and os.path.isfile(os.path.join(link, "INDEX.md")), "excluded mode links ai-docs into the repo", out)
        st = subprocess.run(["git", "status", "--porcelain"], cwd=r2, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
        check(st.strip() == "", "excluded ai-docs is invisible to git status", st)

        body = os.path.join(tmp, "b.md")
        with open(body, "w", encoding="utf-8") as f:
            f.write("## Problem\nx\n\n## Fix\ny\n\n## Verified by\n`echo ok` printed ok\n")
        rc, out = run("note", r1, "--kind", "solution", "--title", "Public fix", "--body-file", body, env=env)
        check(os.path.isfile(os.path.join(r1, "ai-docs", "solutions", out.strip().splitlines()[-1].split("solutions")[-1].strip("/\\"))) or "wrote solutions/" in out, "note writes to the project root", out)
        idx = open(os.path.join(r1, "ai-docs", "INDEX.md"), encoding="utf-8").read()
        check("Public fix" in idx, "INDEX.md lists the entry", idx)

        priv = os.path.join(tmp, "p.md")
        with open(priv, "w", encoding="utf-8") as f:
            f.write("## Problem\nmy manager rotated the token ghp_abcdefghijklmnopqrstuvwxyz0123456789\n\n## Fix\ny\n\n## Verified by\nz\n")
        rc, out = run("note", r1, "--kind", "solution", "--title", "Sensitive", "--body-file", priv, env=env)
        check("privacy scan flagged" in out and not os.path.exists(os.path.join(r1, "ai-docs", "solutions", "%s-sensitive.md" % __import__("datetime").date.today().isoformat())), "privacy gate refuses a repo-safe write", out)
        rc, out = run("note", r1, "--kind", "solution", "--title", "Sensitive", "--body-file", priv, "--private", env=env)
        check("private" in out and "wrote solutions/" in out, "--private writes to the sidecar", out)
        rc, out = run("note", r1, "--kind", "note", "--title", "About the user", "--body-file", body, "--user", "--allow-missing", env=env)
        check(os.path.join("vault", "user") in out.replace("/", os.sep) or "user" in out, "--user writes to the user tier", out)
        check(os.path.isdir(os.path.join(vault, "user", "notes")) and any(n.endswith("about-the-user.md") for n in os.listdir(os.path.join(vault, "user", "notes"))), "user tier entry exists", "")

        pb = os.path.join(tmp, "pb.md")
        with open(pb, "w", encoding="utf-8") as f:
            f.write("## Problem\nx <private>the client is Acme and Bob approved it</private>\n\n## Fix\ny\n\n## Verified by\nz\n")
        rc, out = run("note", r1, "--kind", "solution", "--title", "Inline private", "--body-file", pb, "--agent", "test-agent", env=env)
        written = open(out.strip().splitlines()[-1], encoding="utf-8").read()
        check("Acme" not in written and "agent: test-agent" in written and "block(s) dropped" in out, "<private> blocks are stripped from repo-safe writes; provenance recorded", out)
        rc, out = run("scan", os.path.join(vault, "projects", "repo1", "private"), env=env)
        check("hit(s)" in out and "API token" in out, "scan finds token and role mention", out)
        rc, out = run("lint", r1, "--all", env=env)
        check("lint:" in out, "lint runs", out)
        rc, out = run("lint", r2, env=env)
        check("does not ignore" not in out, "lint confirms exclusion holds", out)

        h = os.path.join(tmp, "h.md")
        with open(h, "w", encoding="utf-8") as f:
            f.write("# Handoff\n\n## Current state\nfine\n\n## Next single action\ndo x\n")
        rc, out = run("handoff", r1, "--body-file", h, env=env)
        check("HANDOFF.md replaced" in out, "handoff replaces", out)
        payload = json.dumps({"hook_event_name": "SessionStart", "cwd": r1, "session_id": "t"})
        rc, out = run("hook", "run", env=env, stdin=payload)
        check("[everlast] project repo1 (mode repo)" in out and "do x" in out, "SessionStart hook prints orientation and HANDOFF", out)

        rc, out = run("resolve", r1, "--private", env=env)
        check(out.strip().replace("/", os.sep).endswith(os.path.join("projects", "repo1", "private")), "resolve --private", out)

        rc, out = run("vault", "sync", "--message", "test", env=env)
        log = subprocess.run(["git", "log", "--oneline"], cwd=vault, capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
        check("test" in log, "vault sync commits locally without a remote", out + log)

        cfg_home = os.path.join(tmp, "cfg")
        env2 = dict(env, APPDATA=cfg_home, XDG_CONFIG_HOME=cfg_home)
        for k in ("EVERLAST_CONTRIBUTE", "DO_NOT_TRACK", "CI"):
            env2.pop(k, None)
        rc, out = run("contribute", env=env2)
        check("not decided" in out, "contribute is undecided on a fresh install", out)
        rc, out = run("publish", "--if-changed", env=env2)
        check(out.strip() == "", "undecided: unattended publish is silent and sends nothing", out)
        rc, out = run("publish", env=env2)
        check("not decided" in out, "undecided: explicit publish asks", out)
        rc, out = run("contribute", "no", env=env2)
        rc, out = run("publish", env=env2)
        check("contribution is off" in out, "no: publish refuses", out)
        rc, out = run("contribute", "yes", env=env2)
        rc, out = run("publish", "--dry-run", env=env2)
        check("would push" in out or "nothing to publish" in out, "yes: publish proceeds (dry run)", out)
        rc, out = run("contribute", env=dict(env2, DO_NOT_TRACK="1"))
        check("contribute no" in out, "DO_NOT_TRACK=1 reads as no", out)
        rc, out = run("pull", "--dry-run", env=env2)
        check("official" in out.lower() or "up to date" in out or "behind" in out, "pull knows whether an official remote exists", out)
        rc, out = run("project", "list", env=env)
        check("repo1" in out and "repo2" in out, "project list", out)

        # project sync (mode repo): commit only the doc root, push when sure, pull request when not
        def git(cwd, *args):
            return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=env).stdout.strip()
        with open(os.path.join(r1, "stray.txt"), "w", encoding="utf-8") as f:
            f.write("not a doc\n")
        rc, out = run("project", "sync", r1, env=env)
        check("commit: ok" in out and "no remote" in out, "sync commits the doc root without a remote", out)
        check("stray.txt" in git(r1, "status", "--porcelain") and "ai-docs" not in git(r1, "status", "--porcelain"), "sync leaves files outside the doc root uncommitted", git(r1, "status", "--porcelain"))
        subj = git(r1, "log", "-1", "--format=%s")
        check(subj.startswith("everlast: ai-docs from") and "+" in subj, "the commit subject lists what was added", subj)
        rc, out = run("project", "sync", r1, "--if-changed", env=env)
        check(out.strip() == "", "sync --if-changed is silent when there is nothing to do", out)
        bare = os.path.join(tmp, "remote1.git")
        subprocess.run(["git", "init", "-q", "--bare", bare], check=True)
        git(r1, "remote", "add", "origin", bare)
        rc, out = run("project", "sync", r1, env=env)
        check("push: ok" in out and "upstream set" in out, "an empty remote gets the branch pushed with an upstream", out)
        branch = git(r1, "symbolic-ref", "--short", "HEAD")
        rc, out = run("note", r1, "--kind", "solution", "--title", "Second note", "--body-file", body, env=env)
        check("wrote solutions/" in out, "second note written", out)
        rc, out = run("project", "sync", r1, "--dry-run", env=env)
        check("would commit" in out, "sync --dry-run reports the pending commit", out)
        rc, out = run("project", "sync", r1, env=env)
        check("commit: ok" in out and "push: ok" in out and "touching ai-docs/" in out, "sync pushes directly when the branch is a fast-forward of its upstream", out)
        check("second-note" in git(bare, "log", "-1", "--format=%s", branch), "the remote received the docs commit with the file name in the subject", git(bare, "log", "-1", "--format=%s", branch))
        other = os.path.join(tmp, "other")
        subprocess.run(["git", "clone", "-q", bare, other], check=True, env=env)
        with open(os.path.join(other, "code.txt"), "w", encoding="utf-8") as f:
            f.write("someone else pushed\n")
        git(other, "add", "code.txt"); git(other, "commit", "-q", "-m", "code change from elsewhere"); git(other, "push", "-q", "origin", "HEAD")
        rc, out = run("note", r1, "--kind", "solution", "--title", "Third note", "--body-file", body, env=env)
        check("wrote solutions/" in out, "third note written", out)
        rc, out = run("project", "sync", r1, env=env)
        check("is behind" in out and "pushed everlast/docs-" in out and "pull request" in out, "behind its upstream: sync pushes a docs-only branch for a pull request instead", out)
        pr_branches = git(bare, "branch", "--list", "everlast/docs-*")
        check("everlast/docs-" in pr_branches, "the remote has the pull request branch", pr_branches)
        check("code.txt" not in git(bare, "show", "--stat", "--format=", pr_branches.strip().lstrip("* ").split()[0]) and "third-note" in git(bare, "log", "-1", "--format=%s", pr_branches.strip().lstrip("* ").split()[0]), "the pull request branch carries only the doc root, on top of the remote's tip", "")
        check("everlast/docs-" not in git(r1, "branch", "--list") and git(r1, "symbolic-ref", "--short", "HEAD") == branch and "stray.txt" in git(r1, "status", "--porcelain"), "the working tree, branch and local branch list are untouched", "")
        rc, out = run("project", "sync", r1, "--pr", "--dry-run", env=env)
        check("would open a pull request" in out, "--pr forces the pull request route", out)
        rc, out = run("project", "register", r1, "--mode", "repo", "--sync", "off", env=env)
        check("sync off" in out, "register --sync off", out)
        rc, out = run("project", "sync", r1, env=env)
        check("sync is off" in out, "sync off does nothing", out)
        rc, out = run("project", "status", r1, env=env)
        check("sync off:" in out and "unpushed commit(s)" in out, "project status reports the sync mode and state", out)
        rc, out = run("project", "register", r1, "--mode", "repo", env=env)
        check("sync off" in out, "re-registering keeps the sync mode", out)
        rc, out = run("project", "register", r1, "--mode", "repo", "--sync", "push", env=env)
        rc, out = run("hook", "run", env=env, stdin=payload)
        check("unpushed commit(s)" in out and "SessionEnd hook pushes" in out, "SessionStart reports unpushed doc commits in mode repo", out)

        # vault remote: name a private repository, or create one
        rc, out = run("vault", "remote", env=env)
        check("local only" in out and "vault remote <url>" in out, "vault remote with no remote asks the question", out)
        rc, out = run("hook", "run", env=env, stdin=payload)
        check("local only" in out, "SessionStart says when the vault has no remote", out)
        bare2 = os.path.join(tmp, "vault-remote.git")
        subprocess.run(["git", "init", "-q", "--bare", bare2], check=True)
        rc, out = run("vault", "remote", bare2, env=env)
        check("push: ok" in out, "vault remote <url> sets origin and pushes", out)
        rc, out = run("vault", "status", env=env)
        check("vault-remote.git" in out.replace("\\", "/") and "ahead 0" in out, "vault status shows the new remote, nothing ahead", out)
        rc, out = run("vault", "remote", "--create", "--dry-run", env=env)
        check("already has a remote" in out or "would run: gh repo create" in out, "vault remote --create never runs gh when a remote exists (dry run)", out)
        rc, out = run("hook", "run", env=env, stdin=payload)
        check("local only" not in out, "SessionStart stops asking once the vault has a remote", out)
        check_040(tmp, env)
        print("all checks passed")
    finally:
        # junctions must be removed as links, not trees
        for link in (os.path.join(tmp, "repo2", "ai-docs"), os.path.join(tmp, "repo4", "ai-docs")):
            if os.path.lexists(link):
                try:
                    if os.name == "nt":
                        subprocess.run(["cmd", "/c", "rmdir", link], capture_output=True)
                    else:
                        os.unlink(link)
                except Exception:
                    pass
        shutil.rmtree(tmp, ignore_errors=True)


def write_file(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def read_file(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def git_at(cwd, env, date, *args):
    """git with the author and committer date pinned (recheck dates changes by commit)."""
    e = dict(env, GIT_AUTHOR_DATE=date + "T10:00:00", GIT_COMMITTER_DATE=date + "T10:00:00")
    return subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", env=e).stdout


def check_040(tmp, env):
    """0.4.0: stale_after and check before use (recheck, verify), search, typed links, stamps, maintain, the SessionStart
    suffix, the benchmark floor, and the two fixes ported from the fork (register merge, vault path variables)."""
    r3 = os.path.join(tmp, "repo3")
    os.makedirs(os.path.join(r3, "app"))
    subprocess.run(["git", "init", "-q"], cwd=r3, check=True)
    write_file(os.path.join(r3, "app", "helpers.py"), "def slugify(s):\n    return s\n")
    write_file(os.path.join(r3, "app", "other.py"), "X = 1\n")
    git_at(r3, env, "2026-05-01", "add", "-A")
    git_at(r3, env, "2026-05-01", "commit", "-q", "-m", "init")
    rc, out = run("project", "register", r3, "--mode", "repo", "--sync", "off", env=env)
    check("registered repo3" in out, "register a third repo for the 0.4.0 checks", out)
    docs = os.path.join(r3, "ai-docs")
    e_may = dict(env, EVERLAST_TODAY="2026-05-02")
    e_sep = dict(env, EVERLAST_TODAY="2026-09-23")

    # stale_after: note writes verified + the kind's window; --stale-after overrides; never is timeless
    sol = os.path.join(tmp, "sol.md")
    write_file(sol, "## Problem\n`python -m app.cli --selftest` failed: ImportError: cannot import name 'slugify' from 'app.helpers'.\n\n"
                    "## Fix\nRe-export `slugify` from `app/helpers.py`; `app/other.py` untouched.\n\n"
                    "## Verified by\n`python -m app.cli --selftest` printed `selftest ok`.\n")
    rc, out = run("note", r3, "--kind", "solution", "--title", "ImportError slugify from app.helpers", "--tags", "python,imports",
                  "--aliases", "cannot import name,slugify import", "--alias", "error: cannot import name 'slugify'",
                  "--summary", "read when the selftest fails with an ImportError", "--body-file", sol, env=e_may)
    spath = out.strip().splitlines()[-1]
    text = read_file(spath)
    check("stale_after: 2026-07-31" in text, "note writes stale_after = verified + 90 days for a solution", text[:400])
    check('aliases: [cannot import name, slugify import, "error: cannot import name \'slugify\'"]' in text,
          "aliases are written, and one holding ': ' is quoted for YAML", text[:500])
    note_b = os.path.join(tmp, "nb.md")
    write_file(note_b, "## Summary\nNaming rules.\n\n## Details\nPrefixes.\n")
    rc, out = run("note", r3, "--kind", "note", "--title", "Asset naming", "--stale-after", "never", "--body-file", note_b, env=e_may)
    check("stale_after: never" in read_file(out.strip().splitlines()[-1]), "--stale-after never marks a timeless entry", out)
    dec = os.path.join(tmp, "dec.md")
    write_file(dec, "## Context\nx\n\n## Decision\ny\n\n## Reasons\nz\n")
    rc, out = run("note", r3, "--kind", "decision", "--title", "Use JSON saves", "--stale-after", "2027-01-15", "--body-file", dec, env=e_may)
    check("stale_after: 2027-01-15" in read_file(out.strip().splitlines()[-1]), "--stale-after YYYY-MM-DD overrides the window", out)
    plan = os.path.join(tmp, "plan.md")
    write_file(plan, "## Goal\ng\n\n## Status\ns\n\n## Next single action\nn\n")
    rc, out = run("note", r3, "--kind", "plan", "--title", "Ship the demo", "--body-file", plan, env=e_may)
    ppath = out.strip().splitlines()[-1]
    check("stale_after: 2026-06-01" in read_file(ppath), "a plan's window is 30 days", read_file(ppath)[:300])
    rc, out = run("note", r3, "--kind", "plan", "--title", "Bad date", "--stale-after", "soon", "--body-file", plan, env=e_may)
    check("--stale-after takes" in out, "a bad --stale-after is refused", out)

    # the index flags what is due on the day it is generated; an entry with no stale_after falls back to its window
    old = os.path.join(docs, "notes", "2026-01-05-legacy-note.md")
    write_file(old, "---\ntitle: Legacy note\nkind: note\nstatus: active\ndate: 2026-01-05\nverified: 2026-01-05\ntags: [old]\n---\n\n# Legacy note\n\n## Summary\nWritten before 0.4.0.\n")
    def line(title):
        return next((ln for ln in read_file(os.path.join(docs, "INDEX.md")).splitlines() if "[" + title + "]" in ln), "")
    rc, out = run("index", r3, env=e_sep)
    check("(recheck due)" in line("ImportError slugify from app.helpers") and "(recheck due)" in line("Legacy note"),
          "INDEX.md shows (recheck due) for a stale solution and for an old entry without stale_after", line("Legacy note"))
    check("(recheck due)" not in line("Asset naming") and "(recheck due)" not in line("Use JSON saves"),
          "timeless and not-yet-due entries carry no flag", line("Asset naming"))

    # recheck: read-only; stale, cited files changed in git since verified, the Verified-by text
    write_file(os.path.join(r3, "app", "helpers.py"), "from app.text import slugify\n")
    git_at(r3, env, "2026-06-10", "add", "-A")
    git_at(r3, env, "2026-06-10", "commit", "-q", "-m", "move slugify to app.text")
    before = read_file(spath)
    rc, out = run("recheck", "slugify", r3, env=e_sep)
    check("STALE" in out and "CHANGED since 2026-05-02: `app/helpers.py`" in out and "move slugify" in out,
          "recheck reports stale and the cited file changed in git since verified", out)
    check("unchanged since 2026-05-02: `app/other.py`" in out and "selftest ok" in out and "verify" in out,
          "recheck lists unchanged files and prints the Verified-by text and the next step", out)
    check(read_file(spath) == before, "recheck writes nothing", "")
    rc, out = run("recheck", "no-such-entry", r3, env=e_sep)
    check("no entry" in out and rc == 0, "recheck fails soft on an unknown entry", out)

    # verify --failed: the dated line lands in Verified by, the entry is due now, the log says verify-failed
    rc, out = run("verify", "slugify", r3, "--failed", "selftest now raises ImportError from app.text", env=e_sep)
    text = read_file(spath)
    check("Recheck failed 2026-09-23: selftest now raises ImportError from app.text" in text.split("## Verified by", 1)[1]
          and "stale_after: 2026-09-23" in text, "verify --failed appends to Verified by and sets stale_after to today", text)
    log = read_file(os.path.join(docs, "log.md"))
    check("verify-failed | ImportError slugify from app.helpers" in log and "--supersedes" in out, "verify --failed logs and says what to do next", out + log[-300:])
    check("(recheck due)" in line("ImportError slugify from app.helpers"), "after a failed recheck the index flags the entry", line("ImportError slugify from app.helpers"))
    rc, out = run("verify", "slugify", r3, "--failed", "the token ghp_abcdefghijklmnopqrstuvwxyz0123456789 expired", env=e_sep)
    check("privacy scan flagged" in out, "verify --failed runs the privacy gate on a repo-safe entry", out)

    # verify: renews verified and stale_after, logs, clears the flag
    rc, out = run("verify", spath, r3, "--note", "selftest ok after the new import", env=e_sep)
    text = read_file(spath)
    check("verified: 2026-09-23" in text and "stale_after: 2026-12-22" in text, "verify sets verified to today and stale_after to today + window", text[:400])
    check("verify | ImportError slugify from app.helpers: selftest ok" in read_file(os.path.join(docs, "log.md"))
          and "(recheck due)" not in line("ImportError slugify from app.helpers"), "verify logs and clears the index flag", line("ImportError slugify from app.helpers"))
    rc, out = run("verify", "Asset naming", r3, env=e_sep)
    check("stale_after never" in out and "stale_after: never" in read_file(os.path.join(docs, "notes", "2026-05-02-asset-naming.md")),
          "verify keeps a timeless entry timeless", out)

    # the other tiers: recheck, verify and search with --user and --private, and search --all
    tier_body = os.path.join(tmp, "tier.md")
    write_file(tier_body, "## Problem\nThe laptop dock drops the second monitor.\n\n## Fix\nUpdate the dock firmware.\n\n## Verified by\n`dockctl --version` printed 2.4.\n")
    rc, out = run("note", r3, "--kind", "solution", "--title", "Dock drops the second monitor", "--tags", "hardware", "--body-file", tier_body, "--user", env=e_may)
    rc, out = run("recheck", "Dock drops", r3, "--user", env=e_sep)
    check("STALE" in out and os.path.join("vault", "user") in out.replace("/", os.sep), "recheck finds a user-tier entry with --user", out)
    rc, out = run("verify", "Dock drops", r3, "--user", env=e_sep)
    check("verified solutions/" in out and "verify | Dock drops the second monitor" in read_file(os.path.join(env["EVERLAST_VAULT"], "user", "log.md")),
          "verify writes the user tier's entry and log with --user", out)
    rc, out = run("note", r3, "--kind", "solution", "--title", "Staging deploy key rotation", "--body-file", tier_body, "--private", env=e_may)
    rc, out = run("recheck", "deploy key", r3, "--private", env=e_sep)
    check("STALE" in out and "private" in out, "recheck finds a sidecar entry with --private", out)
    rc, out = run("search", "dock firmware monitor", r3, env=e_sep)
    check("nothing matches" in out, "search stays in the project root by default", out)
    rc, out = run("search", "dock firmware monitor", r3, "--user", env=e_sep)
    check("vault:user/solutions/" in out and "(vault: is" in out, "search --user reaches the user tier and labels vault paths", out)
    rc, out = run("search", "Public fix second note", r3, "--all", "-n", "10", env=e_sep)
    check("repo1:ai-docs/solutions/" in out, "search --all reaches every registered project", out)

    # search: aliases, stemming, code tokens, supersede ranking, flags
    sup = os.path.join(tmp, "sup.md")
    write_file(sup, "## Problem\nThe selftest import broke after slugify moved.\n\n## Fix\nImport `slugify` from `app/text.py`.\n\n## Verified by\n`python -m app.cli --selftest` printed `selftest ok`.\n")
    rc, out = run("note", r3, "--kind", "solution", "--title", "Import slugify from app.text", "--tags", "python,imports",
                  "--supersedes", os.path.relpath(spath, docs).replace("\\", "/"), "--body-file", sup, env=e_sep)
    newp = out.strip().splitlines()[-1]
    check("Related: supersedes [ImportError slugify from app.helpers](2026-05-02-importerror-slugify-from-app-helpers.md)" in read_file(newp)
          and "status: superseded" in read_file(spath), "note --supersedes marks the old entry and adds a typed Related line", read_file(newp))
    rc, out = run("search", "slugify import", r3, "--json", env=e_sep)
    hits = json.loads(out)["hits"]
    check(hits and hits[0]["title"] == "Import slugify from app.text" and any("superseded" in h["flags"] for h in hits),
          "search ranks the current entry above the one it superseded, which stays flagged", out[:600])
    rc, out = run("search", "cannot import name", r3, "--json", env=e_sep)
    check(json.loads(out)["hits"] and json.loads(out)["hits"][0]["title"] == "ImportError slugify from app.helpers", "search finds an entry through its aliases", out[:400])
    rc, out = run("search", "saving", r3, env=e_sep)
    check("use-json-saves" in out, "search stems words (saving finds saves)", out)
    rc, out = run("search", "zebra quantum", r3, env=e_sep)
    check("nothing matches" in out and rc == 0, "search with no match says so and fails soft", out)
    rc, out = run("search", "app.helpers", r3, env=e_sep)
    check("importerror-slugify" in out and "(superseded)" in out, "search prints kind, date, flags and the relative path", out)

    # typed Related lint, dead links, open contradictions, per-fact stamps
    d1 = os.path.join(docs, "decisions", "2026-09-01-nightly-builds.md")
    d2 = os.path.join(docs, "decisions", "2026-09-02-tagged-builds-only.md")
    write_file(d1, "---\ntitle: Nightly builds\nkind: decision\nstatus: active\ndate: 2026-09-01\nverified: 2026-09-01\ntags: [release]\n---\n\n# Nightly builds\n\n"
                   "## Context\nx\n\n## Decision\ny\n\n## Reasons\nThe store allows it (verified 2026-01-02).\n\nRelated: contradicts [Tagged builds only](2026-09-02-tagged-builds-only.md); fixes [a](2026-09-02-tagged-builds-only.md)\n")
    write_file(d2, "---\ntitle: Tagged builds only\nkind: decision\nstatus: active\ndate: 2026-09-02\nverified: 2026-09-02\ntags: [release]\n---\n\n# Tagged builds only\n\n"
                   "## Context\nIndex lines look like `[title](path): when to read it`.\n\n```\n[an example in a block](nowhere.md)\n```\n\n## Decision\ny\n\n## Reasons\nz\n\nRelated: contradicts [Nightly builds](2026-09-01-nightly-builds.md); supersedes [Use JSON saves](2026-05-02-use-json-saves.md); see also [gone](../notes/missing.md)\n")
    run("index", r3, env=e_sep)
    rc, out = run("lint", r3, env=e_sep)
    check("unknown Related label 'fixes'" in out, "lint reports an unknown Related label", out)
    check("dead link [gone](../notes/missing.md)" in out, "lint reports a Related target that does not exist", out)
    check("(path)" not in out and "nowhere.md" not in out, "lint ignores example links inside inline code and fenced blocks", out)
    check("supersedes 2026-05-02-use-json-saves.md, whose status is active" in out, "lint reports a supersedes target that is not superseded", out)
    check(out.count("open contradiction") == 1, "lint reports an active contradicts pair once", out)
    check("fact stamped (verified 2026-01-02)" in out, "lint reports a per-fact stamp older than the window", out)
    rc, out = run("search", "store allows", r3, env=e_sep)
    check("(stale facts)" in out, "search flags an entry holding a stale fact stamp", out)
    hist = os.path.join(docs, "solutions", "2026-09-10-old-layout.md")
    write_file(hist, "---\ntitle: Old layout\nkind: solution\nstatus: superseded\ndate: 2026-09-10\nverified: 2026-09-10\ntags: [layout]\n---\n\n# Old layout\n\n"
                     "## Problem\nx\n\n## Fix\nEdit `app/gone.py`.\n\n## Verified by\nran\n")
    live = os.path.join(tmp, "live.md")
    write_file(live, "# Own heading\n\n## Problem\nx\n\n## Fix\nEdit `app/gone2.py`.\n\n## Verified by\nran\n")
    rc, out = run("note", r3, "--kind", "solution", "--title", "Layout fix", "--body-file", live, env=e_sep)
    text = read_file(out.strip().splitlines()[-1])
    check(text.count("\n# ") == 1 and "# Own heading" in text, "note keeps a body's own H1 instead of adding a second one", text[:300])
    run("index", r3, env=e_sep)
    rc, out = run("lint", r3, env=e_sep)
    check("app/gone2.py" in out and "app/gone.py`" not in out, "lint reports dead paths in active entries only, not in history", out)

    # SessionStart: a short suffix when something is due, nothing written
    r4_clean = os.path.join(tmp, "repo-clean")
    os.makedirs(r4_clean)
    subprocess.run(["git", "init", "-q"], cwd=r4_clean, check=True)
    run("project", "register", r4_clean, "--mode", "repo", "--sync", "off", env=env)
    payload = json.dumps({"hook_event_name": "SessionStart", "cwd": r3, "session_id": "t3"})
    snap = sorted(os.listdir(os.path.join(docs, "solutions")))
    idx_before = read_file(os.path.join(docs, "INDEX.md"))
    rc, out = run("hook", "run", env=dict(env, EVERLAST_TODAY="2027-02-01"), stdin=payload)
    first = out.splitlines()[0] if out.strip() else ""
    check("recheck due: " in first and "Legacy note" in first and "maintain: " in first,
          "SessionStart appends recheck due (titles) and the maintain count", first)
    rc, out = run("hook", "run", env=dict(env, EVERLAST_TODAY="2026-05-02"), stdin=json.dumps({"hook_event_name": "SessionStart", "cwd": r4_clean, "session_id": "t4"}))
    check("recheck due" not in out and "maintain:" not in out, "SessionStart adds nothing when the doc set is clean", out)
    check(sorted(os.listdir(os.path.join(docs, "solutions"))) == snap and read_file(os.path.join(docs, "INDEX.md")) == idx_before,
          "SessionStart writes no file", "")

    # maintain: report, then --apply archives old done/abandoned/superseded entries and rewrites every link to them
    donep = os.path.join(docs, "plans", "2026-03-01-old-rollout.md")
    write_file(donep, "---\ntitle: Old rollout\nkind: plan\nstatus: done\ndate: 2026-03-01\nverified: 2026-03-01\ntags: [release]\n---\n\n# Old rollout\n\n"
                      "## Goal\ng\n\n## Status\ndone\n\n## Next single action\nnone\n\nRelated: builds on [Nightly builds](../decisions/2026-09-01-nightly-builds.md)\n")
    write_file(os.path.join(docs, "decisions", "2026-09-03-release-cadence.md"),
               "---\ntitle: Release cadence\nkind: decision\nstatus: active\ndate: 2026-09-03\nverified: 2026-09-03\ntags: [release]\n---\n\n# Release cadence\n\n"
               "## Context\nx\n\n## Decision\ny\n\n## Reasons\nz\n\nRelated: builds on [Old rollout](../plans/2026-03-01-old-rollout.md#goal)\n")
    write_file(os.path.join(docs, "decisions", "2026-09-04-nightly-builds-again.md"),
               "---\ntitle: Nightly builds again\nkind: decision\nstatus: active\ndate: 2026-09-04\nverified: 2026-09-04\ntags: [release]\n---\n\n# Nightly builds again\n\n## Context\nx\n\n## Decision\ny\n\n## Reasons\nz\n")
    write_file(os.path.join(docs, "HANDOFF.md"), "# Handoff\n\nSee [the old rollout](plans/2026-03-01-old-rollout.md).\n\n## Next single action\nx\n")
    run("index", r3, env=e_sep)
    rc, out = run("maintain", r3, env=e_sep)
    check("archive (1)" in out and "plans/2026-03-01-old-rollout.md" in out and "report only" in out, "maintain reports the archive set", out)
    check("duplicate candidates" in out and "nightly-builds" in out and "open contradictions (1)" in out, "maintain reports duplicates and open contradictions", out)
    check(os.path.exists(donep), "maintain without --apply moves nothing", "")
    rc, out = run("maintain", r3, "--apply", env=e_sep)
    moved = os.path.join(docs, "archive", "plans", "2026-03-01-old-rollout.md")
    check(os.path.exists(moved) and not os.path.exists(donep) and "archived 1 entry" in out, "maintain --apply moves the entry to archive/ in the same layout", out)
    check("(../archive/plans/2026-03-01-old-rollout.md#goal)" in read_file(os.path.join(docs, "decisions", "2026-09-03-release-cadence.md"))
          and "(archive/plans/2026-03-01-old-rollout.md)" in read_file(os.path.join(docs, "HANDOFF.md"))
          and "(../../decisions/2026-09-01-nightly-builds.md)" in read_file(moved), "maintain --apply rewrites links to, and inside, the moved entry", read_file(moved))
    idx = read_file(os.path.join(docs, "INDEX.md"))
    check("## Archive" in idx and "(archive/plans/2026-03-01-old-rollout.md) (done)" in idx and "prune | archived 1 entry" in read_file(os.path.join(docs, "log.md")),
          "the index lists archived entries under Archive and the log says prune", idx[-600:])
    rc, out = run("lint", r3, env=e_sep)
    check("old-rollout" not in out, "no dead link is left after the archive move", out)

    # the fork's two fixes: register merges an existing ai-docs into the store; vault paths expand variables
    r4 = os.path.join(tmp, "repo4")
    os.makedirs(os.path.join(r4, "ai-docs", "plans"))
    os.makedirs(os.path.join(r4, "ai-docs", "decisions"))
    write_file(os.path.join(r4, "ai-docs", "plans", "2026-09-01-pre-written.md"), "---\ntitle: Pre-written plan\nkind: plan\n---\n\n## Goal\nx\n")
    write_file(os.path.join(r4, "ai-docs", "decisions", "2026-09-01-pre-decided.md"), "---\ntitle: Pre-decided\nkind: decision\n---\n\n## Context\nx\n")
    subprocess.run(["git", "init", "-q"], cwd=r4, check=True)
    rc, out = run("project", "register", r4, "--mode", "excluded", env=env)
    store = os.path.join(env["EVERLAST_VAULT"], "projects", "repo4", "ai-docs")
    check(os.path.isfile(os.path.join(store, "plans", "2026-09-01-pre-written.md")) and not os.path.exists(os.path.join(store, "plans", "plans"))
          and os.path.isfile(os.path.join(store, "decisions", "2026-09-01-pre-decided.md")),
          "register --mode excluded merges an existing ai-docs/ into the store instead of nesting plans/plans", out)
    rc, out = run("vault", "where", env=dict(env, EVERLAST_VAULT=os.path.join("$EVERLAST_TEST_BASE", "v2"), EVERLAST_TEST_BASE=tmp))
    check(os.path.join(tmp, "v2") in out, "vault paths expand environment variables", out)

    # the benchmark floor: search at least matches the index scan and stays above the first run's level
    p = subprocess.run([PY, os.path.join(HERE, "bench_everlast.py"), "--json"], capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=120)
    try:
        b = json.loads(p.stdout)
    except ValueError:
        b = None
    check(b is not None, "the benchmark runs", p.stdout[-300:] + p.stderr[-300:])
    s, i = b["methods"]["search"], b["methods"]["index"]
    check(s["recall_at_3"] >= i["recall_at_3"] and s["recall_at_3"] >= BENCH_FLOOR_R3,
          f"benchmark: search Recall@3 {s['recall_at_3']} >= index {i['recall_at_3']} and >= floor {BENCH_FLOOR_R3}", json.dumps(b["methods"]))
    st = b["staleness"]["search"]
    check(st["flagged_share"] == 1.0 and st["current_first_share"] >= 5 / 6,
          f"benchmark: search flags every out-of-date hit and puts the current entry first ({st['current_first']}/{st['stale_probes']})", json.dumps(st))


BENCH_FLOOR_R3 = 0.90   # first run 2026-09-23: 0.93 (38 of 41); one query of slack (T-20260923-1)


if __name__ == "__main__":
    main()

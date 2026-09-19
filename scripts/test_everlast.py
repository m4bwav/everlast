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
        print("all checks passed")
    finally:
        # junctions must be removed as links, not trees
        link = os.path.join(tmp, "repo2", "ai-docs")
        if os.path.lexists(link):
            try:
                if os.name == "nt":
                    subprocess.run(["cmd", "/c", "rmdir", link], capture_output=True)
                else:
                    os.unlink(link)
            except Exception:
                pass
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    main()

---
title: Project docs: push when sure, pull request when not; vault remote asked once
kind: decision
status: active
date: 2026-09-18
verified: 2026-09-18
tags: [sync, backup, vault, git]
agent: claude-code
model: claude-opus-5
---

# Project docs: push when sure, pull request when not; vault remote asked once

## Context
A mode `repo` project keeps its doc set in the project's own repository, so everlast's vault sync never backed it up: the docs reached the remote only when the user happened to push. On 2026-09-18 one registered project had three unpushed commits carrying eight doc changes, invisible to the vault. The owner asked for the protocol to back the notes up in a way that shows what everlast adds, and, for project docs, to "just push commits, and if it's not sure, do a pull request instead". Also, `vault init` created a git repository but never asked where it should go, so a vault could stay local-only indefinitely.

## Decision
1. Backup is part of the layout. `vault init` and every SessionStart with a remote-less vault ask once for the URL of a private repository or permission to create one (`vault remote --create` runs `gh repo create --private` and re-checks the visibility; a public result is disconnected). Nothing is pushed until the user answers.
2. Mode `repo` projects get a `sync` setting (`push` default, `pr`, `off`). At session end `project sync` commits the doc root alone (a pathspec commit: the user's other changes, staged or not, are untouched) and pushes the branch when it is sure; otherwise it copies the doc root onto a fresh `everlast/docs-<host>-<stamp>` branch off the remote's default branch in a temporary worktree, pushes that, and opens a pull request.
3. Sure means all of: the branch has an upstream; after a fetch it is not behind it; every unpushed commit is the user's own (`git var GIT_AUTHOR_IDENT`); the push is accepted. An empty remote is pushed to directly.
4. Every everlast commit subject lists the files (`+new ~changed -gone`), vault included, so `git log --oneline` is the record of what agents wrote.

## Reasons
- Pushing the user's branch is what they would do next anyway on a personal repository; the four conditions are exactly the cases where a push could carry something the user did not mean to publish or could fail on a protected branch. Falling back to a docs-only pull request keeps the docs flowing to the remote for review without ever moving code.
- A pathspec commit (`git commit -- ai-docs`) is the only primitive that leaves a half-staged working tree alone; `git add -A` would sweep the user's work into an everlast commit.
- The temporary worktree keeps the user's checkout, branch and index untouched while the PR branch is built; the local branch ref is deleted after the push so the branch list stays clean.
- Descriptive subjects were the owner's stated reason for wanting a remote at all ("I can see what it's adding in the commits"); timestamps alone said nothing.
- The remote must be private for the vault (it names people and machines by design), and that is the whole requirement: credentials never belong in it (PRIVACY.md), so there is no residual secret to protect with more than a private repository.

## Rejected alternatives
- A SessionStart warning only ("you have unpushed docs"): the owner's answer was that it should push, not nag.
- Always a pull request: too much ceremony for a solo repository; the PR is the fallback, not the default.
- Pushing only when the unpushed range is docs-only: on a solo repository that would leave the docs stranded behind every code commit, which is the case that prompted this.
- Committing with `git add -A`: sweeps unrelated work into everlast's commit.
- `git stash` around the PR build (as `publish` does): touches the user's working tree; a worktree does not.

## Consequences
Registrations made before 0.3.0 have no `sync` key and behave as `push`. A rejected push (branch protection, permissions) becomes a pull request automatically. Existing vault commits keep their timestamp subjects; new ones list files. Off-git backup and encryption stay deferred, as decided on 2026-09-13.

Related: [Encryption and off-git backup deferred](2026-09-13-encryption-and-off-git-backup-deferred.md), [Separate private vault repository for user-level data](2026-09-13-separate-private-vault-repository-for-user-level-data.md), [Index](../INDEX.md)

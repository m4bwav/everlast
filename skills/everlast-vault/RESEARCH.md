# Research: everlast-vault

Findings that back [SKILL.md](SKILL.md). Changes they caused are logged in [CHANGELOG.md](CHANGELOG.md); procedural lessons live in [LEARNINGS.md](LEARNINGS.md); test runs and their evidence in [TESTS.md](TESTS.md); schedule and state in `evergreen.json`. Protocol: MAINTENANCE.md.

Topic: cross-tool installation of agent skills and plugins, private git-backed knowledge stores, redaction and encryption at rest for agent notes. Tier `fast`. Last refresh 2026-09-27 (the first real four-track pass; the 2026-09-13 entry was a scaffold); next due per `evergreen.json`. General memory and capture research lives in the everlast-capture unit's RESEARCH.md; this file keeps what backs the vault, install and privacy claims.

## Current understanding

- One export covers six tools: Codex, Copilot (CLI and VS Code), OpenCode, Windsurf, Cursor and Gemini CLI all read `~/.agents/skills` (each tool's skills docs, read 2026-09-27). Gemini treats it as an alias of `~/.gemini/skills` that wins within a tier; a second link into a tool's own folder can list each skill twice. Cursor's Cloud Agents sync only `~/.cursor/skills` (R-20260927-2).
- The vercel-labs `npx skills` CLI is the community cross-tool installer (`-g`, `-a <agent>`, `--copy`, `update`); flags unchanged (R-20260927-2).
- Claude Code: per the docs (2.1.283), a plugin from a marketplace added from a local directory, with a relative source (everlast's `"source": "./"`), loads in place, but 2.1.281 on the owner's PC copied it into the cache even on a fresh install (L-001); edits apply at the next session or `/reload-plugins`, no version bump or reinstall. Git-hosted and copied installs are cached under `cache/<mp>/<plugin>/<version>/`; the version comes from the manifest first, else the marketplace entry, else the commit SHA, and `claude plugin update` skips a plugin whose computed version is unchanged (code.claude.com/docs/en/plugins/loading, read 2026-09-27; R-20260927-3).
- Cowork loads skills, commands, agents and hooks (`hooks/hooks.json`), local MCP servers when the session runs on the user's computer, and ignores LSP, output styles, themes and `settings`; a plugin with a top-level `bin/` cannot be installed. Install from a file is Customize > Plugins > Add > Upload plugin with a zip (200 MB cap). A plugin on the claude.ai account also loads in Claude Code as `<name>@synced` (2.1.273+), and a local install of the same name wins (claude.com/docs/plugins/platform-support, read 2026-09-27; R-20260927-1). Whether everlast's SessionEnd `sync` reaches the vault from Cowork's environment is untested.
- `gh repo create --private` works as the skill uses it; changing visibility with `gh repo edit` needs `--accept-visibility-change-consequences` (R-20260927-2).
- Credential scanning: Betterleaks (the Gitleaks author's successor, MIT, 2026-02; reads Gitleaks configs; 98.6% recall on CredData as reported by its authors) replaces Gitleaks, which takes security fixes only (v8.30.1, 2026-03-21). TruffleHog verifies live credentials, which matters less for notes. None of them looks for people, opinions or internal names, so everlast's regex scan plus `config/redact.txt` stays the gate and a credential scanner is an optional second pass (R-20260927-4).
- Every pattern scanner has blind spots at token boundaries (arXiv 2609.02983: a Gitleaks allowlist defect, confirmed by maintainers, dropped detection to 0.52 for keys ending in a hyphen). everlast's patterns catch the boundary cases tested; three common key shapes (GitHub fine-grained `github_pat_`, npm `npm_`, Google `AIza`) were missing and were added with a test (R-20260927-5).
- Encryption at rest, not built: git-crypt is slow-moving but alive (0.8.0, 2025-09-23); sops+age is active (v3.13.3, 2026-07-23) but encrypts markdown only in binary mode, so encrypted notes no longer diff; gocryptfs has had no release since v2.6.1 (2024-08-10) and needs cppcryptfs on Windows (R-20260927-6).
- Peers: `/pii-check` (clewisdev/skills; audits git history, handoff and session notes before a repo goes public) and small git-backed memory plugins (sqs-agent-memory, claude-device-sync with ChaCha20, claude-memory-sync, receipts-wiki) have low adoption and no evals; GitHub MCP secret scanning needs paid Secret Protection on private repos; Presidio (NER for person names, active, 2.2.364) would break the stdlib-only rule (R-20260927-7).

## Open questions

- (resolved 2026-09-29) In-place loading already works on 2.1.281 in the VS Code extension; `installPath` is the misleading part (L-001, anthropics/claude-code#96223). Still open: does the Desktop app's Code tab still run the cache copy after 2.1.284, and does a local git marketplace install the checked-out branch (#92280)?
- Do Cowork's hooks run the SessionEnd `sync` in Cowork's environment, and can it reach the vault path? Needs a live Cowork session.
- Does an old `~/.cursor/skills` or `~/.gemini/skills` link beside the `~/.agents/skills` export list the skills twice in Cursor or Gemini CLI? Check on the next machine that has both.
- Should `vault remote` scan the vault's `git log -p` before its first push to a new remote, as `/pii-check` does for history? SKILL.md now says to run the scan before the first push; it scans the tree, not history.
- Should `scan` shell out to `betterleaks dir` when it is on PATH? Only if the regex scan misses a real credential in use.

## Search plan

Four tracks; every refresh runs at least one query on each (scope each to the period since the last refresh; add the year). Protocol §4 explains the tracks and how tooling, practice and testing findings are judged.

Subject (the goal and the latest thinking on reaching it):

- `site:code.claude.com plugins loading OR discover-plugins OR install`; `site:claude.com/docs plugins platform-support` (Cowork components, upload path, synced plugins)
- `"~/.agents/skills" cursor OR gemini-cli OR copilot OR codex OR opencode OR windsurf docs <year>`; each tool's own skills page (cursor.com/docs/skills, geminicli.com/docs/cli/skills, developers.openai.com/codex/skills, docs.github.com Copilot add-skills, opencode.ai/docs/skills, docs.windsurf.com cascade/skills)
- `sops OR git-crypt OR gocryptfs OR age release <year>` on each project's GitHub releases page

Tooling (skills, plugins, MCP servers, scripts, knowledge graphs built for this subject):

- vercel-labs/skills README (agent table, flags); `skills.sh/api/search?q=sync` and `q=vault`
- `"git-backed" OR "private repo" memory "claude code" plugin OR skill <year> site:github.com`
- `betterleaks OR gitleaks OR trufflehog release <year>`; `https://registry.modelcontextprotocol.io/v0/servers?search=secret&updated_since=<last_checked>`

Practice (how others use AI agents on this goal, and everything in between):

- `"pii-check" OR secrets OR redact "agent memory" OR "session notes" <year>`; anthropics/skills discussions
- `"memory" git sync "claude code" skills "private repo" OR dotfiles <year>`; hn.algolia.com `agent memory git sync` by date

Testing (how work on this subject is verified, and how skills for it are tuned):

- `site:arxiv.org secret detection benchmark OR scanner evaluation <year>`; llody9977/secret-scanner-benchmark
- the Betterleaks CredData numbers; `path:SKILL.md privacy scan test` on GitHub; code.claude.com/docs/en/plugin-evals for graders

Best sources (primary first): code.claude.com plugin docs (loading, discover-plugins, plugin-evals), claude.com/docs/plugins, each tool's skills docs, GitHub release pages and NEWS files, arXiv. Noisy: agensi.io, getclaudeskills, appsecsanta and other SEO summaries of skills or scanners.

## Findings log

Newest first. One entry per material finding; a quiet refresh gets one entry saying so. `Track` is subject, tooling, practice, or testing.

### R-20260927-7 · 2026-09-27 · Practice and minor tooling: `/pii-check`, small git-backed memory plugins, GitHub MCP secret scanning, Presidio
- summary: `/pii-check` (clewisdev/skills, anthropics/skills discussion #1295, 2026-06-09) audits git history, handoff files, session notes, username paths and inferred PII before a repo goes public; it overlaps everlast `scan` and adds a history pass. Git-backed memory peers (sqs-agent-memory, claude-device-sync with ChaCha20-encrypted git, claude-memory-sync, receipts-wiki) have low stars and no evals. GitHub MCP secret scanning (public preview 2026-03-17) needs GitHub Secret Protection, paid on private repos. Presidio (2.2.364, 2026-07-22) finds person names with NER but needs spaCy models. None adopted; the first-push scan is now in SKILL.md.
- track: practice, tooling
- sources: https://github.com/anthropics/skills/discussions/1295, https://github.com/letsloose501/sqs-agent-memory, https://github.com/hmennen90/claude-device-sync, https://github.blog/changelog/2026-03-17-secret-scanning-in-ai-coding-agents-via-the-github-mcp-server/, https://dev.to/saaro_net/presidio-2026-pii-detection-and-anonymization-for-gdpr-compliant-ai-pipelines-4441
- magnitude: 0.25
- applied: C-20260927-1 (SKILL.md Privacy scan, the first-push line)

### R-20260927-6 · 2026-09-27 · Subject: encryption options, git-crypt is alive, sops cannot diff markdown, gocryptfs is quiet and not native on Windows
- summary: git-crypt 0.8.0 shipped 2025-09-23, so "stagnant" overstated it. sops v3.13.3 (2026-07-23) is active but handles `.md` only in binary mode, where textconv diffs do not work (getsops/sops#1968); "per-file encryption that still diffs" holds only for YAML, JSON, ENV and INI. gocryptfs's last release is v2.6.1 (2024-08-10), Linux and macOS only (cppcryptfs on Windows), which matters on the owner's Windows machine.
- track: subject
- sources: https://github.com/AGWA/git-crypt/blob/master/NEWS.md, https://github.com/getsops/sops/releases, https://github.com/getsops/sops/issues/1968, https://github.com/rfjakob/gocryptfs/releases
- magnitude: 0.3
- applied: C-20260927-1 (SKILL.md Later: encryption and other backups)

### R-20260927-5 · 2026-09-27 · Testing: pattern scanners miss keys at token boundaries; everlast's scan missed three key shapes
- summary: A mutation test of Gitleaks 8.21.2 and TruffleHog 3.82 (arXiv 2609.02983, 2026-09-02) found a Gitleaks terminator-allowlist defect, confirmed by maintainers, that missed most credential types; detection fell to 0.52 for a key ending in a hyphen; llody9977/secret-scanner-benchmark scores six scanners on a seeded corpus. A probe of everlast's `PRIVACY_PATTERNS` on 2026-09-27: keys with a trailing hyphen, inside backticks and inside a link URL are caught; GitHub fine-grained tokens (`github_pat_`), npm tokens (`npm_` plus 36) and Google API keys (`AIza` plus 35) were not. The three patterns were added with a test that also checks an npm config name is not flagged; no new hits on the plugin's docs or the owner's vault.
- track: testing
- sources: https://arxiv.org/abs/2609.02983, https://github.com/llody9977/secret-scanner-benchmark
- magnitude: 0.35
- applied: plugin C-20260927-1 (scripts/everlast.py `PRIVACY_PATTERNS`, scripts/test_everlast.py `check_scan_key_shapes`)

### R-20260927-4 · 2026-09-27 · Tooling: Betterleaks succeeds Gitleaks; no scanner replaces the regex gate
- summary: The original Gitleaks author launched Betterleaks (MIT, Aikido-sponsored, created 2026-02-03, v1.1.1 by 2026-03-17), a drop-in that reads Gitleaks configs and reports 98.6% recall on CredData; Gitleaks is feature-complete, security fixes only (v8.30.1, 2026-03-21). `betterleaks dir <path>` scans a plain folder (README, read 2026-09-27). None detects people, opinions or internal names. Response: point (an optional second pass for credentials).
- track: tooling
- sources: https://www.helpnetsecurity.com/2026/03/19/betterleaks-open-source-secrets-scanner/, https://github.com/betterleaks/betterleaks, https://github.com/gitleaks/gitleaks/releases
- magnitude: 0.35
- applied: C-20260927-1 (SKILL.md Privacy scan)

### R-20260927-3 · 2026-09-27 · Subject: a local-directory marketplace loads the plugin in place; uninstall and install are not needed
- summary: The Claude Code plugin loading reference: relative-path plugins in a marketplace added from a local directory "load in place ... edits take effect at the next session start or `/reload-plugins`, and you don't need to increase the version". Everlast's marketplace entry uses `"source": "./"`. Not borne out on the owner's PC with 2.1.281 (L-001): both the old and a fresh install were cached copies. Git-hosted and copied installs are cached per computed version (manifest `version`, then the marketplace entry, then the commit SHA); bump or omit `version`, then `claude plugin update`. `claude plugin install X@mp` does not refresh a local-directory marketplace. SKILL.md's "marketplace update, uninstall, install" after a source edit was right only for copied installs.
- track: subject
- sources: https://code.claude.com/docs/en/plugins/loading, https://code.claude.com/docs/en/discover-plugins
- magnitude: 0.45
- applied: C-20260927-1 (SKILL.md A new machine, step 2); plugin C-20260927-1 (PORTABILITY.md Claude Code row)

### R-20260927-2 · 2026-09-27 · Subject: Cursor and Gemini CLI also read `~/.agents/skills`
- summary: Cursor's skills docs list `~/.agents/skills/` as a global location; Gemini CLI treats `~/.agents/skills/` as an alias of `~/.gemini/skills/` that wins within a tier; Codex, Copilot, OpenCode and Windsurf confirm the shared path. `EVERLAST export ~` alone covers all six, the extra links were redundant and can list skills twice; Cursor Cloud Agents sync only `~/.cursor/skills`. Unchanged: `npx skills add -g -a`, `--copy`, `update`; `gh repo create --private`.
- track: subject
- sources: https://cursor.com/docs/skills, https://geminicli.com/docs/cli/skills/, https://developers.openai.com/codex/skills, https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills, https://opencode.ai/docs/skills/, https://docs.windsurf.com/windsurf/cascade/skills, https://github.com/vercel-labs/skills
- magnitude: 0.4
- applied: C-20260927-1 (SKILL.md A new machine, step 4); plugin C-20260927-1 (PORTABILITY.md, INSTALL-PROMPT.txt, README.md, PROTOCOL.md §6)

### R-20260927-1 · 2026-09-27 · Subject: Cowork loads plugin hooks; the upload path changed; account plugins sync into Claude Code
- summary: Anthropic's platform-support table (read 2026-09-27) marks Hooks (`hooks/hooks.json`) "Loads" in Cowork, ignored only in Chat. Install from a file is Customize > Plugins > Add > Upload plugin with a zip of the folder (200 MB). Cowork can add GitHub-repo marketplaces, private ones included. A plugin on the claude.ai account loads in Claude Code as `<name>@synced` (2.1.273+); a local install of the same name wins. SKILL.md said hooks do not run in Cowork: a core claim wrong. Whether the SessionEnd `sync` can reach the vault from Cowork's environment is untested, so the skill still keeps Step 0 and a manual `sync` there.
- track: subject
- sources: https://claude.com/docs/plugins/platform-support, https://code.claude.com/docs/en/plugins/loading#synced-plugins
- magnitude: 0.65
- applied: C-20260927-1 (SKILL.md A new machine, step 3); plugin C-20260927-1 (PORTABILITY.md Cowork row)

### R-20260913-1 · 2026-09-13 · Initial research
- Summary: scaffold only; no research was run when the unit was created. The first real pass is R-20260927-1 to R-20260927-7.
- Track: subject
- Sources: none
- Magnitude: n/a (initial)
- Applied: C-20260913-1

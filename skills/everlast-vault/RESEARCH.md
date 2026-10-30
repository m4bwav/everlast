# Research: everlast-vault

Findings that back [SKILL.md](SKILL.md). Changes they caused are logged in [CHANGELOG.md](CHANGELOG.md); procedural lessons live in [LEARNINGS.md](LEARNINGS.md); test runs and their evidence in [TESTS.md](TESTS.md); schedule and state in `evergreen.json`. Protocol: MAINTENANCE.md.

Topic: cross-tool installation of agent skills and plugins, private git-backed knowledge stores, redaction and encryption at rest for agent notes. Tier `fast`. Last refresh 2026-10-23 (four-track pass; the first real one was 2026-09-27); next due per `evergreen.json`. General memory and capture research lives in the everlast-capture unit's RESEARCH.md; this file keeps what backs the vault, install and privacy claims.

## Current understanding

- One export covers six tools: Codex, Copilot (CLI and VS Code), OpenCode, Windsurf, Cursor and Gemini CLI all read `~/.agents/skills` (each tool's skills docs, read 2026-09-27). Gemini treats it as an alias of `~/.gemini/skills` that wins within a tier; a second link into a tool's own folder can list each skill twice. Cursor's Cloud Agents sync only `~/.cursor/skills` (R-20260927-2).
- The vercel-labs `npx skills` CLI is the community cross-tool installer (`-g`, `-a <agent>`, `--copy`, `update`); flags unchanged (R-20260927-2).
- Claude Code: per the docs (2.1.283), a plugin from a marketplace added from a local directory, with a relative source (everlast's `"source": "./"`), loads in place, but 2.1.281 on the owner's PC copied it into the cache even on a fresh install (L-001); edits apply at the next session or `/reload-plugins`, no version bump or reinstall. Git-hosted and copied installs are cached under `cache/<mp>/<plugin>/<version>/`; the version comes from the manifest first, else the marketplace entry, else the commit SHA, and `claude plugin update` skips a plugin whose computed version is unchanged (code.claude.com/docs/en/plugins/loading, read 2026-09-27; R-20260927-3). On 2.1.295 the CLI still loads a local clone in place and prints `Read from: <folder>` in `claude plugin list`, `installPath` still names the cache, and the Desktop app's Code tab runs the cache copy (#96223, open); `CLAUDE_CODE_PLUGIN_DIRS` loads a folder as `<name>@inline` and is the user-reported Desktop route (R-20261017-1).
- Cowork loads skills, commands, agents and hooks (`hooks/hooks.json`), local MCP servers when the session runs on the user's computer, and ignores LSP, output styles, themes and `settings`; a plugin with a top-level `bin/` cannot be installed. Install from a file is Customize > Plugins > Add > Upload plugin with a zip (200 MB cap). A plugin on the claude.ai account also loads in Claude Code as `<name>@synced` (2.1.273+), and a local install of the same name wins (claude.com/docs/plugins/platform-support, read 2026-09-27; R-20260927-1). Whether everlast's SessionEnd `sync` reaches the vault from Cowork's environment is untested.
- `gh repo create --private` works as the skill uses it; changing visibility with `gh repo edit` needs `--accept-visibility-change-consequences` (R-20260927-2).
- Credential scanning: Betterleaks (the Gitleaks author's successor, MIT, 2026-02; reads Gitleaks configs; 98.6% recall on CredData as reported by its authors) replaces Gitleaks, which takes security fixes only (v8.30.1, 2026-03-21). TruffleHog verifies live credentials, which matters less for notes. None of them looks for people, opinions or internal names, so everlast's regex scan plus `config/redact.txt` stays the gate and a credential scanner is an optional second pass (R-20260927-4). Since 0.6.5 the scan also catches prefixed key names (`AWS_SECRET_ACCESS_KEY=`) and a password given in prose; GitHub push protection blocks Anthropic keys by default only where secret scanning is on, which a private vault without paid Secret Protection does not get (R-20261017-2).
- Every pattern scanner has blind spots at token boundaries (arXiv 2609.02983: a Gitleaks allowlist defect, confirmed by maintainers, dropped detection to 0.52 for keys ending in a hyphen). everlast's patterns catch the boundary cases tested; three common key shapes (GitHub fine-grained `github_pat_`, npm `npm_`, Google `AIza`) were missing and were added with a test (R-20260927-5).
- Encryption at rest, not built: git-crypt is slow-moving but alive (0.8.0, 2025-09-23); sops+age is active (v3.13.3, 2026-07-23) but encrypts markdown only in binary mode, so encrypted notes no longer diff; gocryptfs has had no release since v2.6.1 (2024-08-10) and needs cppcryptfs on Windows (R-20260927-6).
- Peers: `/pii-check` (clewisdev/skills; audits git history, handoff and session notes before a repo goes public) and small git-backed memory plugins (sqs-agent-memory, claude-device-sync with ChaCha20, claude-memory-sync, receipts-wiki) have low adoption and no evals; GitHub MCP secret scanning needs paid Secret Protection on private repos; Presidio (NER for person names, active, 2.2.364) would break the stdlib-only rule (R-20260927-7).

## Open questions

- (answered 2026-10-17, R-20261017-1, from a user report on 2.1.295 in #96223; not re-probed, this PC's CLI is 2.1.281) `installPath` still names the cache on 2.1.289+; the `Read from:` line of `claude plugin list` shows the in-place load, and step 2 now names it. Still open: Betterleaks 2.0 stable (rc.2 adds an explicit `--config`): re-check the scan flags when it ships; and does the `CLAUDE_CODE_PLUGIN_DIRS` route work in the Desktop app on the owner's PC?
- (resolved 2026-09-29) In-place loading already works on 2.1.281 in the VS Code extension; `installPath` is the misleading part (L-001, anthropics/claude-code#96223). Still open: does the Desktop app's Code tab still run the cache copy after 2.1.284, and does a local git marketplace install the checked-out branch (#92280)?
- Do Cowork's hooks run the SessionEnd `sync` in Cowork's environment, and can it reach the vault path? Needs a live Cowork session.
- Does an old `~/.cursor/skills` or `~/.gemini/skills` link beside the `~/.agents/skills` export list the skills twice in Cursor or Gemini CLI? And does Cursor follow the export's junctions or symlinks at all (forum user reports say it does not follow symlinked global skills, R-20261017-3; `--copy` would be the fallback)? Check on the next machine that has Cursor.
- Should `vault remote` scan the vault's `git log -p` before its first push to a new remote, as `/pii-check` does for history? SKILL.md now says to run the scan before the first push; it scans the tree, not history.
- Should `scan` shell out to `betterleaks dir` when it is on PATH? Only if the regex scan misses a real credential in use.

## Search plan

Four tracks; every refresh runs at least one query on each (scope each to the period since the last refresh; add the year). Protocol §4 explains the tracks and how tooling, practice and testing findings are judged.

Subject (the goal and the latest thinking on reaching it):

- `site:code.claude.com plugins loading OR discover-plugins OR install`; `site:claude.com/docs plugins platform-support` (Cowork components, upload path, synced plugins)
- `"~/.agents/skills" cursor OR gemini-cli OR copilot OR codex OR opencode OR windsurf docs <year>`; each tool's own skills page (cursor.com/docs/skills, geminicli.com/docs/cli/skills, learn.chatgpt.com/docs/build-skills, docs.github.com Copilot add-skills, opencode.ai/docs/skills, docs.windsurf.com cascade/skills)
- `sops OR git-crypt OR gocryptfs OR age release <year>` on each project's GitHub releases page
- Official forums, announcements first, then known issues since `last_checked`: github.com/anthropics/claude-code/issues?q=label:area:plugins+sort:updated-desc (no Discussions), forum.cursor.com/tag/skills (`.rss` for new posts), github.com/vercel-labs/skills/issues?q=sort:updated-desc (Discussions return 404), github.com/orgs/community/discussions/categories/code-security and github.blog/changelog/label/application-security/ (secret scanning). Staff posts are primary, user posts are leads.

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

- R-20261030-1 (quiet check, all tracks): nothing newer since last_checked for everlast-vault; subject, tooling, practice, testing: nothing new. Sources: web searches (Claude Code changelog, arXiv agent memory, Dependabot changelog, npm compromises). m 0. applied: none.

Newest first. One entry per material finding; a quiet refresh gets one entry saying so. `Track` is subject, tooling, practice, or testing.

### R-20261023-1 · 2026-10-23 · Tooling: Betterleaks 2.0 replaces `dir` with `fs`; install-path issues unchanged
- Summary: Betterleaks v2.0.0-rc.3 and rc.4 (10-19, 10-20) stop shelling out to git, drop `--staged`/`--log-opts` (pipe `git diff` into `betterleaks stdin --git-diff`) and, per docs/v2_migration.md, replace the `dir`/`directory`/`file` commands with `filesystem` or `fs` (a bare existing path also selects a filesystem scan). The stable release is still v1.9.0 (09-29), where `betterleaks dir` is right, so the SKILL.md command would break on 2.0 final. Response: adopt; the privacy-scan paragraph names both forms. Other tooling: trufflehog 3.99.3/3.99.4, vercel-labs/skills 1.7.3 (promoted `skills sync` to stable) and 1.7.4 (restored `experimental_sync` as the advertised command); the pinned `npx skills@1.7.0` still works, no bump. gitleaks, sops 3.13.3, age 1.3.2, gocryptfs 2.6.1 unchanged. Subject: anthropics/claude-code#96223 still open (last activity 10-12) and #102186 open (10-17); Claude Code 2.1.303 to 2.1.310 add nothing on `installPath` or local-marketplace loading (2.1.305 names plugins "Claude Desktop mounts by path" only in a managed-permissions fix; an open lead on whether Desktop can load a clone, not acted on). GitHub secret scanning (10-20): revocation now covers base64-encoded GitHub tokens, audit-log field change on 11-12; no new detector bearing on the scan. Practice and testing: nothing new.
- Track: tooling, subject
- Sources: https://github.com/betterleaks/betterleaks/blob/main/docs/v2_migration.md, https://github.com/betterleaks/betterleaks/releases, https://github.com/vercel-labs/skills/releases, https://github.com/trufflesecurity/trufflehog/releases, https://github.com/anthropics/claude-code/issues/96223, https://github.com/anthropics/claude-code/releases/tag/v2.1.305, https://github.blog/changelog/2026-10-20-updates-to-github-secret-scanning
- Magnitude: 0.3
- Applied: C-20261023-1 (SKILL.md privacy scan paragraph)

### R-20261017-1 · 2026-10-17 · Subject: `installPath` still names the cache on 2.1.295 while the CLI loads in place; Desktop keeps the cache copy; a user-reported in-place route
- Summary: anthropics/claude-code#96223 (open, no staff reply) gained a Windows 11 confirmation on 10-12 with Desktop's bundled 2.1.295: the Code tab runs the cache copy, hooks modules included, through edits, commits, `/reload-plugins` and new sessions, while the CLI's `claude plugin list` prints `Read from: <source folder>` and `installed_plugins.json` `installPath` still names `cache/<mp>/<name>/<version>`. That answers the open question: the 2.1.289 stale-copy fix did not change `installPath`, so L-001 stands. The commenter's route: disable the marketplace install and set `CLAUDE_CODE_PLUGIN_DIRS=<plugin folder>` and `CLAUDE_CODE_PLUGIN_DIR_WATCH=1` in the `env` block of `~/.claude/settings.json`; the plugin then loads as `<name>@inline` with live reload (the loading docs list `CLAUDE_CODE_PLUGIN_DIRS` as an `@inline` origin that outranks a marketplace install of the same name). Claude Code 2.1.297 to 2.1.302 change nothing in local-directory installs (2.1.302: `claude plugin` subcommands no longer lose a settings write on early exit, reftable marketplaces stop re-cloning, PowerShell finds plugin `bin/` commands, faster Windows startup with many plugins; 2.1.300: `/reload-plugins` sees a plugin installed from another terminal; 2.1.299: a spurious synced-plugin path error and stale account plugins in Cowork cloud sessions). New issue #102186 (10-14, 2.1.300, open): an interrupted copy into the cache is later treated as already cached and loads with components missing (`Skills (0)`); workaround: delete the version folder, then `claude plugin update`; it matters only for a copied install. #93108 open (update compares only the version string), #89111 closed not planned, #92280 open with no reply. The loading and platform-support pages are unchanged (new detail: 25 self-added marketplaces per account, 5,000 files per plugin).
- Track: subject
- Sources: https://github.com/anthropics/claude-code/issues/96223, https://github.com/anthropics/claude-code/issues/102186, https://github.com/anthropics/claude-code/issues/93108, https://github.com/anthropics/claude-code/issues/92280, https://code.claude.com/docs/en/changelog, https://code.claude.com/docs/en/plugins/loading, https://claude.com/docs/plugins/platform-support
- Magnitude: 0.35
- Applied: C-20261017-1 (SKILL.md A new machine or a new agent product, step 2), LEARNINGS.md L-001 evidence, Open questions

### R-20261017-2 · 2026-10-17 · Testing and tooling: the scan missed prefixed key names and passwords in prose; GitHub blocks Anthropic keys by default
- Summary: Scott Spence's redaction hardening (2026-04, new to this file) seeded fingerprinted fake secrets into config, log and source fixtures and found misses that everlast's scan shared, checked against `PRIVACY_PATTERNS` on 2026-10-17: the `credential assignment` regex needed the bare keyword right before `:` or `=`, so `AWS_SECRET_ACCESS_KEY=<40 chars>` and `aws_secret_access_key: ...` passed, and so did "my password is hunter22". Fixed in the plugin script (prefixed and suffixed name parts, `access_key`; a `credential in prose` pattern that needs a digit or symbol in the value), with positives and negatives in the self-test. GitHub push protection now blocks `anthropic_service_api_key` and `anthropic_user_api_key` by default where secret scanning is on, free public repositories included (10-13); the post does not say private repositories without paid Secret Protection are covered, so the private vault still relies on everlast's scan, whose `sk-` pattern already catches `sk-ant-` keys.
- Track: testing, tooling
- Sources: https://scottspence.com/posts/hardening-redaction-in-my-pi, https://github.blog/changelog/2026-10-13-secret-scanning-blocks-anthropic-keys-by-default-adds-salesforce
- Magnitude: 0.35
- Applied: everlast-protocol:C-20261017-1 (scripts/everlast.py PRIVACY_PATTERNS, scripts/test_everlast.py); Current understanding (credential scanning)

### R-20261017-3 · 2026-10-17 · Tooling and practice (quiet): versions unchanged; an age-encrypted sync peer; scrub-at-write design; a Cursor symlink lead
- Summary: vercel-labs/skills still 1.7.2 (10-09; flags unchanged, adds `sync --include/--exclude`); Betterleaks 1.9.0 Latest, 2.0.0-rc.2 (10-07) the newest pre-release with more breaking changes (custom configs need an explicit `--config`, `GITLEAKS_*` aliases removed, value fingerprints replace location ignores, a new JSON envelope), so keep `betterleaks dir` on 1.x; Gitleaks v8.30.1, TruffleHog v3.99.2 (dedupe and OAuth2 verification only), sops v3.13.3, git-crypt 0.8.0 and gocryptfs v2.6.1 unchanged. Cursor, Gemini CLI and Codex docs still list `~/.agents/skills`; Cursor Cloud Agents still sync only `~/.cursor/skills`; Codex's skills page moved to learn.chatgpt.com/docs/build-skills. Peers with no adoption signal: clync (Rust, syncs `~/.claude` through a private git repo encrypted with age, key in a password manager: the reference if encryption at rest is ever built), claude-sync, claude-nomad, claude-autosync, GuardBee secret-scanner and llm-data-guard on the MCP registry. Practice: a dev.to design (olund, 2026-08) scrubs at session end before disk with regex plus an entropy rule, typed `<REDACTED:kind:hash>` markers and an encrypted sidecar; its entropy catch-all was 64% false positives, mostly long paths, which argues against adding one here. Lead, user posts only: forum.cursor.com threads (2026-02) report that Cursor does not follow symlinked global skills; `export` uses junctions on Windows and symlinks elsewhere, so a Cursor machine should be checked. Testing: nothing new (arXiv 2604.03070 and 2606.04141 predate the window).
- Track: tooling, practice, testing
- Sources: https://github.com/vercel-labs/skills/releases, https://github.com/betterleaks/betterleaks/releases, https://github.com/trufflesecurity/trufflehog/releases, https://learn.chatgpt.com/docs/build-skills, https://docs.rs/crate/clync/0.4.1, https://dev.to/olund/an-agent-that-remembers-everything-is-a-secret-leak-with-a-good-memory-2ncj, https://forum.cursor.com/tag/skills
- Magnitude: 0.15
- Applied: note (Open questions: the Cursor link question; Search plan)

### R-20261011-1 · 2026-10-11 · Subject and tooling: plugin install fixes in Claude Code 2.1.289 to 2.1.296; installer and scanner versions
- Summary: 2.1.289 fixed `plugin list`, `plugin eval` and `plugin update` showing a stale copy of a plugin installed from a local folder marketplace, which may change the `installPath` caveat in "A new machine" step 2 (L-001); not re-probed, since this machine's CLI on PATH is 2.1.281. anthropics/claude-code#96223 (the Desktop app runs the cache copy) is still open with no reply. Also 2.1.292 `claude plugin install --marketplace <source>` in one command, 2.1.295 Windows drive-letter casing for project-scope plugins, 2.1.296 HTTPS retry for `owner/repo` installs on Windows. Tooling: `npx skills` is at 1.7.2 (Codex global skills now go to `~/.agents/skills`; Pi counts as a universal agent; the skill pins 1.7.0); Betterleaks 1.9.0 is the latest stable, 2.0.0-rc.2 is breaking (`-v` means validate; CSV and SARIF removed), so keep `betterleaks dir` on 1.x; GitHub's AI secret-detection model (10-07) needs paid GHSP or GHAS for push protection. Practice and testing: nothing new.
- Track: subject, tooling
- Sources: https://code.claude.com/docs/en/changelog, https://github.com/anthropics/claude-code/issues/96223, https://github.com/vercel-labs/skills/releases, https://github.com/betterleaks/betterleaks/releases, https://github.blog/changelog/2026-10-07-purpose-built-model-for-leaked-secret-detection/
- Magnitude: 0.35 (step 2's caveat may be outdated in the CLI; re-probe on 2.1.289+ before editing)
- Applied: RESEARCH.md only (Open questions)

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

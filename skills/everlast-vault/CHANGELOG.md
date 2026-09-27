# Changelog: everlast-vault

Every change to [SKILL.md](SKILL.md) and its companions, newest first, each with the reason. Reasons cite findings in [RESEARCH.md](RESEARCH.md) (`R-`), lessons in [LEARNINGS.md](LEARNINGS.md) (`L-`), and test runs in [TESTS.md](TESTS.md) (`T-`). State in `evergreen.json`. Protocol: MAINTENANCE.md.

Entry shape: `### C-YYYYMMDD-n · date · one-line summary`, then `because:` (IDs or "user request"), `files:` (file and section), and a sentence on what changed. Cite section headings, not line numbers.

### C-20260927-1 · 2026-09-27 · First research refresh: Cowork runs hooks, one export covers six tools, local installs load in place, scanner and encryption facts corrected
- because: R-20260927-1, R-20260927-2, R-20260927-3, R-20260927-4, R-20260927-6, R-20260927-7
- files: SKILL.md (A new machine or a new agent product, steps 2, 3 and 4; Privacy scan; Later: encryption and other backups), RESEARCH.md (written from the template: Current understanding, Open questions, Search plan, R-20260927-1 to 7)
- Step 2: a plugin installed from the local clone loads in place, so a source edit needs no reinstall; git-URL installs update with `claude plugin update`. Step 3: Cowork loads hooks and the upload path is Customize > Plugins > Add > Upload plugin; `sync` by hand stays until SessionEnd is proven in Cowork. Step 4: Cursor and Gemini CLI read `~/.agents/skills`, so the extra links are dropped (except Cursor Cloud Agents). Privacy scan: run before the vault's first push; Betterleaks named as an optional credential pass; boundary blind spots named. Encryption: git-crypt is not stagnant, sops cannot diff markdown, gocryptfs is quiet and not native on Windows.

### C-20260926-1 · 2026-09-26 · Description under 1,024 characters with 12 quoted phrases (1,313 to 1,015)
- because: the owner's request (tidy the everlast skill descriptions with skill-tidy without losing function or trigger coverage); skill-tidy lint ST005, ST007, ST013; plugin C-20260926-3
- files: SKILL.md (description)
- 'install everlast' and 'new machine' became 'install everlast on a new machine'; 'is the vault backed up' merged into 'back up the vault'; 'push the learnings', 'privacy check' and 'what projects are registered' moved into the prose; 'private' appears once in the summary instead of three times, which took the closest sibling (everlast-setup) from 0.36 to 0.28 in `tidy.py check` (OK).

### C-20260918-1 · 2026-09-18 · Back it up: `vault remote` (a private repository the user names, or one created with gh), asked once; project docs sync noted
- because: the owner's request (ask for a repository or permission to create a private one; keep the notes backed up where the commits show what was added); plugin C-20260918-2
- files: SKILL.md description (remote, new trigger phrases), new section Back it up (ask once), section Keep it current (project sync, descriptive commit subjects), section A new machine step 5
- The remote must be private; nothing is pushed until the user answers; a repository that comes out public is disconnected by the script.

### C-20260913-1 · 2026-09-13 · Created as an evergreen unit
- because: user request
- files: SKILL.md, RESEARCH.md, LEARNINGS.md, evergreen.json (skills: also TESTS.md and evals/evals.json)
- Initial version. Tier `fast`, interval 14d. See R-20260913-1 for the research basis; the first test run, for a skill, is logged in TESTS.md.

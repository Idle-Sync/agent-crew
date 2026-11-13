---
description: Put an agent-crew (an issue fixer and a PR reviewer) on a GitHub repo, on this machine or in GitHub Actions. Asks the repo, mode, always-on or not, the GitHub account for each agent and the models, then sets it up. Usage: /agent-crew:setup [owner/repo]
argument-hint: [owner/repo]
allowed-tools: Bash, Read, AskUserQuestion
---

Set up an agent-crew. The `crew` CLI does the work; you collect the choices, show them, and run it. Talk plainly and briefly.

Repo given: $ARGUMENTS

1. **Install the CLI once.** If `command -v crew` fails, run `bash "${CLAUDE_PLUGIN_ROOT}/scripts/crew" install` and show its output. It needs `gh`, `jq`, `tmux` and `python3`; if one is missing, say which and how to install it, and stop.
2. **Ask, in one AskUserQuestion call** (skip what $ARGUMENTS already answers; `gh auth status` lists the GitHub logins on this machine):
   - **Repo:** `owner/repo`.
   - **Mode:** *On this machine* (two Claude Code sessions in tmux, using this machine's Claude login) or *GitHub Actions* (runs in the repo's CI with a Claude token or API key you add as a secret; nothing runs here).
   - **Always-on** (only for this machine): *Yes* (starts at boot, resumes the same conversation; needs systemd) or *No* (runs until you stop it or the machine restarts).
   - **Accounts:** *One account for both* (simplest; the reviewer posts verdicts as comments, because GitHub does not let an account approve its own PR) or *A second account for the reviewer* (formal approvals; that account gets write access to this repo only). Offer the logins `gh auth status` shows.
   - **Models:** *Default* (whatever Claude Code uses here), or a model per agent.
3. **Repo-specific rules (optional):** ask whether the repo has rules the crew must follow that are not already in its README, CONTRIBUTING or CLAUDE.md. If yes, write them to `~/.config/agent-crew/repos/<slug>.rules.md` and pass `--rules`.
4. **Show the exact command** and what it will change (repo settings to merge commits only, labels it adds, a collaborator invite if a second account is used, what starts where), and ask for a yes.
5. **Run** `crew assign <owner/repo> --mode <local|ci> [--sticky|--no-sticky] --fixer-account <a> --reviewer-account <b> [--fixer-model m] [--reviewer-model m] [--rules file]`.
6. **Report:** for local mode, the output of `crew status` (the two sessions and their Remote Control links) and how to watch them (`tmux attach -t <slug>-fixer`). For GitHub Actions, the setup PR link and the secrets to add before merging it. Mention `crew pause <slug>`, `crew status`, and where alerts and the daily digest go (`NOTIFY_CMD` in `~/.config/agent-crew/crew.conf`, printed to the journal when empty).

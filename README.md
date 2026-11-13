# agent-crew

Two Claude Code agents that maintain a GitHub repo for you:

- **The fixer** works through the open issues by priority, fixes each at its root cause, and opens one PR per issue with the reasoning and the test results.
- **The reviewer** reviews every PR the way a senior reviewer would, posts a verdict, merges what passes, resolves merge conflicts itself, files the minor points as one follow-up issue, and cuts a release at most once a day.

They run **on your machine** (as two Claude Code sessions, optionally always-on and resumed after every restart) or **in GitHub Actions** (nothing runs locally). Each agent can use its own GitHub account, or both can share one.

## Install

```
claude plugin marketplace add Idle-Sync/agent-crew
claude plugin install agent-crew@agent-crew
```

Then, in Claude Code, run `/agent-crew:setup` and answer its questions. It installs the `crew` command the first time.

Needs `gh` (logged in), `jq`, `tmux` and `python3`. Always-on mode needs systemd user services (Linux).

## How it works

```
GitHub ──(every 3 min, crew poll)──► new issue ──► fixer, only when it is idle
                                     new PR head ─► reviewer

fixer ──► branch + worktree ──► root-cause fix ──► tests ──► PR ("Closes #N")
reviewer ──► reads the issue, the diff and the code around it ──► verdict
             ├─ Merge ──────────────────► merge commit
             ├─ Merge with follow-ups ──► merge + one P3 issue with the minor points
             └─ Changes needed ─────────► inline comments; the fixer picks them up from GitHub
```

- **GitHub is the only channel between the agents.** The reviewer never types into the fixer's session; the fixer reads its queue from GitHub after every task, so it is never interrupted in the middle of one.
- **The fixer's order:** issues by priority label (`P0`, `P1`, `P2`, `P3`, oldest first in each), then its PRs with changes requested. Reviewed PRs jump the queue once one has waited two days or three are waiting. Issues titled `idea:` or labelled `idea` are left for you; so are `status: needs-decision` and `status: needs-info`.
- **The reviewer** merges with merge commits only (the setup turns squash and rebase merging off), resolves conflicts by merging the base branch into the PR branch, and releases following the repo's own release docs, or with a tag and a GitHub release when there are none. It never publishes to a package registry itself.
- **Both** follow the repo's README, CONTRIBUTING and CLAUDE.md, keep their own state file so nothing is lost when their context is compacted, write terse progress lines in their terminal and answer you fully when you talk to them directly, and never run `rm -rf`.

The full instructions are in [`briefs/fixer.md`](briefs/fixer.md) and [`briefs/reviewer.md`](briefs/reviewer.md). Add rules for one repo with `--rules <file>`.

## The `crew` command

| Command | What it does |
|---|---|
| `crew assign <owner/repo>` | put a crew on a repo (`--mode local\|ci`, `--sticky\|--no-sticky`, `--fixer-account`, `--reviewer-account`, `--fixer-model`, `--reviewer-model`, `--rules`, `--slug`, `--no-github-setup`) |
| `crew status` | every session: busy or idle, minutes since it last did something, context use, Remote Control link |
| `crew pause <slug>` / `crew resume <slug>` | let both agents finish their step and wait / carry on |
| `crew notify <session> <text>` | send a session a message (the fixer only takes it when idle) |
| `crew unassign <slug>` | stop a crew; its clones and state stay on disk |
| `crew rollover [session]` | continue a session in a fresh conversation from its brief and state.md |

Three timers run in the background: `crew poll` (every 3 minutes) hands new work to the agents, `crew watch` (every 10 minutes) alerts you when an agent is down, stuck on a permission prompt, busy with no activity for 30 minutes, or past 90% of its context, and `crew digest` (21:00) sends a daily summary per repo: what merged and was released, open PRs and how long they have waited, and issues waiting on your decision.

Settings live in `~/.config/agent-crew/crew.conf`. Set `NOTIFY_CMD` to any command that takes a message as its last argument (a chat bot, a push service) to receive the alerts and the digest; when empty they go to the timers' logs (`journalctl --user -u agent-crew-digest`).

## Long-running agents and context

An always-on agent's conversation keeps growing. From 70% of the context window (`CTX_WINDOW` in `crew.conf`) the plugin tells the agent to wrap up: finish the task it is on, keep its `state.md` current, and at the next clean break run `crew rollover`, which continues it in a fresh conversation that starts from its brief and `state.md`. It aims to be done by about 75%; nothing is ever cut off mid-task. The old conversation stays on disk and is listed in `previous-sessions.tsv` in the agent's state folder.

## Accounts

- **One account for both agents:** simplest. GitHub does not let an account approve its own PR, so the reviewer posts its verdict as a comment and still merges.
- **A second account for the reviewer:** formal approvals and change requests. `crew assign` gives that account write access to the assigned repo only (needed to merge and release).

Each local session gets its account's token through `GH_TOKEN`, so the two never mix, and neither changes your shell's active `gh` login.

## GitHub Actions mode

`crew assign <owner/repo> --mode ci` opens a PR in the repo that adds two workflows built on [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) and the two briefs. Before merging it, add the secrets its description lists: `CLAUDE_CODE_OAUTH_TOKEN` (from `claude setup-token`) or `ANTHROPIC_API_KEY`, plus a GitHub token per agent. Each run does one task and stops; the reviewer also runs once a day to decide on a release.

## Your Claude account

The crew runs the official Claude Code with **your own** login or API key; it never stores, proxies or shares credentials. Two always-on agents use your plan's limits like any other Claude Code sessions, so watch your usage, and use `crew pause` when you need to.

## Unattended sessions and permissions

Local sessions run with `--dangerously-skip-permissions` in their own folders, because nobody is there to approve each command. Claude Code still asks about a few commands it cannot check in advance; the plugin's `PermissionRequest` hook approves those **only in sessions the crew started** (it checks `AGENT_CREW_SESSION`) and logs each one to `~/.local/state/agent-crew/approved.log`. Other Claude Code sessions are not affected. Give each agent's GitHub account no more access than the repos it works on.

## Issues and ideas

Read [ISSUES.md](ISSUES.md), then open one at https://github.com/Idle-Sync/agent-crew/issues.

## License

MIT

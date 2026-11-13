---
description: Show every agent-crew on this machine (sessions, busy or idle, last activity, context use, Remote Control links) and, for each crew's repo, open PRs and anything waiting on the owner. Usage: /agent-crew:status
allowed-tools: Bash
---

Run `crew status`. If `crew` is not installed, say so and point to `/agent-crew:setup`.

Then, for each crew's repo (from `~/.config/agent-crew/repos/*.conf`), run `gh pr list --repo <repo>` and `gh issue list --repo <repo> --label "status: needs-decision"`.

Reply briefly: one line per session (state, idle for, context), then per repo the open PRs with their review state and the issues waiting on the owner. Flag anything that looks wrong: a session down, busy with no activity for a long time, context above 90%, or a PR waiting more than two days.

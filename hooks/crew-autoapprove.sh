#!/usr/bin/env bash
# PermissionRequest hook. Crew sessions run unattended in bypass mode, but Claude Code
# still shows a prompt for some commands it cannot check in advance, and a prompt
# nobody answers stalls the agent. Approve it, but only in a session the crew started
# (the launcher sets AGENT_CREW_SESSION); every other session is left untouched.
input=$(cat)
[ -n "${AGENT_CREW_SESSION:-}" ] || exit 0
log="${XDG_STATE_HOME:-$HOME/.local/state}/agent-crew/approved.log"
mkdir -p "$(dirname "$log")"
printf '%s\t%s\t%s\n' "$(date '+%F %T')" "$AGENT_CREW_SESSION" \
  "$(printf '%s' "$input" | jq -c '{tool: .tool_name, input: (.tool_input|tostring|.[0:300])}' 2>/dev/null)" >> "$log"
printf '{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"}}}\n'

#!/usr/bin/env bash
# PermissionRequest hook, opt-in. Crew sessions run unattended in bypass mode, but Claude Code
# still prompts for a few commands it cannot check in advance, and an unanswered prompt stalls
# the agent (`crew watch` alerts you when that happens). With AUTO_APPROVE_PROMPTS=yes in
# crew.conf, those prompts are approved, only in sessions the crew started (AGENT_CREW_SESSION),
# and each one is logged with tokens masked. Off by default: approving is your decision.
input=$(cat)
[ -n "${AGENT_CREW_SESSION:-}" ] || exit 0
conf="${XDG_CONFIG_HOME:-$HOME/.config}/agent-crew/crew.conf"
grep -qE '^AUTO_APPROVE_PROMPTS="?yes"?' "$conf" 2>/dev/null || exit 0
log="${XDG_STATE_HOME:-$HOME/.local/state}/agent-crew/approved.log"
mkdir -p "$(dirname "$log")"
what=$(printf '%s' "$input" | jq -c '{tool: .tool_name, input: (.tool_input|tostring|.[0:200])}' 2>/dev/null \
  | sed -E 's/(gh[pousr]_|github_pat_|sk-ant-)[A-Za-z0-9_-]+/\1***/g; s/((TOKEN|KEY|SECRET|PASSWORD)[A-Za-z_]*=)[^ "]+/\1***/gI')
printf '%s\t%s\t%s\n' "$(date '+%F %T')" "$AGENT_CREW_SESSION" "$what" >> "$log"
printf '{"hookSpecificOutput":{"hookEventName":"PermissionRequest","decision":{"behavior":"allow"}}}\n'

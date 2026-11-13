#!/usr/bin/env bash
# PostToolUse + UserPromptSubmit hook, active only in sessions the crew started
# (AGENT_CREW_SESSION). A suggestion, never a hard stop: from 70% of the context window the
# agent wraps up, keeps state.md current and, at the next clean task boundary, runs
# `crew rollover` to continue in a fresh conversation; aim for about 75%.
set -u
input=$(cat)
s=${AGENT_CREW_SESSION:-}
[ -n "$s" ] || exit 0
slug=${s%-*}; role=${s##*-}
state="${XDG_STATE_HOME:-$HOME/.local/state}/agent-crew/$slug/$role"
[ -d "$state" ] || exit 0
[ -f "$state/rollover" ] && exit 0

window=200000
conf="${XDG_CONFIG_HOME:-$HOME/.config}/agent-crew/crew.conf"
[ -f "$conf" ] && w=$(sed -n 's/^CTX_WINDOW=\([0-9]*\).*/\1/p' "$conf" | tail -1) && [ -n "$w" ] && window=$w

tp=$(jq -r '.transcript_path // empty' <<<"$input")
[ -n "$tp" ] && [ -f "$tp" ] || exit 0
used=$(tail -n 400 "$tp" | jq -r 'select(.type=="assistant") | .message.usage | select(. != null) | ((.input_tokens // 0) + (.cache_read_input_tokens // 0) + (.cache_creation_input_tokens // 0))' 2>/dev/null | tail -n 1)
case "$used" in ''|*[!0-9]*) exit 0 ;; esac
pct=$(( used * 100 / window ))
[ "$pct" -ge 70 ] || exit 0

base="Your context is at ${pct}%. Time to wrap up: finish the task you are on as normal (do not cut it short, do nothing destructive), keep $state/state.md current (queue, open PRs, anything noticed but not recorded), and at the next clean task boundary, before starting anything new, run: crew rollover. That restarts you in a fresh conversation that continues from state.md. Aim to have rolled over by about 75%; this is a suggestion, not a hard limit."

case "$(jq -r '.hook_event_name // empty' <<<"$input")" in
  UserPromptSubmit)
    jq -cn --arg m "Before you act on this message: $base" '{hookSpecificOutput:{hookEventName:"UserPromptSubmit", additionalContext:$m}}' ;;
  PostToolUse)
    level=$([ "$pct" -ge 75 ] && echo 75 || echo 70)
    [ "$(cat "$state/.rollover-notice" 2>/dev/null)" = "$level" ] && exit 0
    echo "$level" > "$state/.rollover-notice"
    jq -cn --arg m "$base" '{hookSpecificOutput:{hookEventName:"PostToolUse", additionalContext:$m}}' ;;
esac
exit 0

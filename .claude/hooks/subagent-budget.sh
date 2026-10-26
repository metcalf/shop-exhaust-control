#!/usr/bin/env bash
# PreToolUse on Agent: don't start a subagent unless the 5h window has room for it to finish (plus the main
# session acting on its result and wrapping up) before the 85% wrap-up cap in rate-limits-budget.sh.
# Nightly runs deny; attended sessions ask. Every spawn is logged to .claude/usage-log.tsv to calibrate the cap.
cap=70   # last night's full phase 2 draft cost ~10 points; a reviewer is estimated at 4-8, plus 2-3 to wrap up
in=$(cat)
type=$(jq -r '.tool_input.subagent_type // "general-purpose"' <<<"$in")
fh=$(jq -r '.fh // 0' "$CLAUDE_PROJECT_DIR/.claude/usage.json" 2>/dev/null); fh=${fh%.*}
printf '%s\tspawn\t%s\t%s\t%s\n' "$(date +%FT%T)" "${fh:-?}" "$type" "$(jq -r .session_id <<<"$in")" \
  >>"$CLAUDE_PROJECT_DIR/.claude/usage-log.tsv"
[ "${fh:-0}" -le "$cap" ] && exit 0
reason="5h usage is ${fh}%, above the ${cap}% subagent cap; a $type run may not finish before the 85% wrap-up."
if [ "${SHOP_NIGHTLY:-}" = 1 ]; then
  decision=deny; reason="$reason Don't start it this session: record it as the first next action in STATE.md and wrap up."
else
  decision=ask
fi
jq -nc --arg d "$decision" --arg r "$reason" \
  '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: $d, permissionDecisionReason: $r}}'

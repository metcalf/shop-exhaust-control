#!/usr/bin/env bash
flag=/tmp/claude-wrapup-$(date -v-6H +%F); [ -f "$flag" ] && exit 0
fh=$(jq -r '.fh // 0' "$CLAUDE_PROJECT_DIR/.claude/usage.json" 2>/dev/null); fh=${fh%.*}
hm=$(date +%H%M)
if [ "${fh:-0}" -ge 85 ] || { [ "$hm" -ge 0230 ] && [ "$hm" -lt 0700 ]; }; then
  touch "$flag"
  echo '{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"Usage budget nearly spent. Finish the current step, do the CLAUDE.md end-of-session steps (update STATE.md, log decisions, commit), then stop."}}'
fi

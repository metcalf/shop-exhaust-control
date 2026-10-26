#!/usr/bin/env bash
# SubagentStop: log 5h usage when a subagent finishes, paired with the spawn line from subagent-budget.sh.
in=$(cat)
type=$(jq -r '.agent_type // empty' <<<"$in"); [ -n "$type" ] || exit 0   # skip internal/untyped agents
fh=$(jq -r '.fh // "?"' "$CLAUDE_PROJECT_DIR/.claude/usage.json" 2>/dev/null)
printf '%s\tstop\t%s\t%s\t%s\n' "$(date +%FT%T)" "${fh%.*}" "$type" \
  "$(jq -r .session_id <<<"$in")" >>"$CLAUDE_PROJECT_DIR/.claude/usage-log.tsv"

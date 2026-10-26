#!/usr/bin/env bash
# SubagentStop: log 5h usage when a subagent finishes, paired with the spawn line from subagent-budget.sh.
in=$(cat)
fh=$(jq -r '.fh // "?"' "$CLAUDE_PROJECT_DIR/.claude/usage.json" 2>/dev/null)
printf '%s\tstop\t%s\t%s\t%s\n' "$(date +%FT%T)" "${fh%.*}" "$(jq -r '.agent_type // "?"' <<<"$in")" \
  "$(jq -r .session_id <<<"$in")" >>"$CLAUDE_PROJECT_DIR/.claude/usage-log.tsv"

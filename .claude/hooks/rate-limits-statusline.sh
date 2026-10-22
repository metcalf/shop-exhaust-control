in=$(cat)
dir=$(jq -r '.workspace.project_dir // .workspace.current_dir' <<<"$in")
jq '{t: now, fh: .rate_limits.five_hour.used_percentage, wk: .rate_limits.seven_day.used_percentage}' \
  <<<"$in" > "$dir/.claude/usage.json" 2>/dev/null
jq -r '"5h: \(.rate_limits.five_hour.used_percentage // "?")%"' <<<"$in"

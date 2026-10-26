in=$(cat)
dir=$(jq -r '.workspace.project_dir // .workspace.current_dir' <<<"$in")
# Write via a temp file: the budget hooks read usage.json concurrently and would see an empty file as 0%.
jq '{t: now, fh: .rate_limits.five_hour.used_percentage, wk: .rate_limits.seven_day.used_percentage}' \
  <<<"$in" > "$dir/.claude/usage.json.$$" 2>/dev/null && mv "$dir/.claude/usage.json.$$" "$dir/.claude/usage.json"
jq -r '"5h: \(.rate_limits.five_hour.used_percentage // "?")%"' <<<"$in"

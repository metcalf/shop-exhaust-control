#!/usr/bin/env bash
# Nightly unattended Claude session. Run by launchd (scripts/com.metcalf.shop-exhaust-nightly.plist);
# the wake comes from `pmset repeat` at 22:00, after the 21:59 job time, so launchd runs the missed job on wake.
#
# Runs interactive Claude in a detached tmux (own socket, -L shop-nightly) rather than -p, so the statusline
# keeps .claude/usage.json current for the budget hooks. Claude creates $NIGHTLY_DONE as its last action and the
# Stop hook (.claude/hooks/nightly-stop.sh) then closes tmux; ending a turn without it (waiting on a subagent)
# keeps the session open. The watchdog here kills it after NIGHTLY_IDLE_SECS with no transcript activity (main
# or subagent) or NIGHTLY_MAX_SECS total.
# Watch live: tmux -L shop-nightly attach -t nightly   (detach: C-b d)
set -uo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
logdir="$HOME/Library/Logs/shop-exhaust-nightly"
mkdir -p "$logdir"
exec >>"$logdir/$(date +%F).log" 2>&1
echo "=== $(date) nightly start"

# launchd gives a bare PATH. claude is the native install (~/.local/bin); the nodenv shim fails without NODENV_VERSION.
export PATH="$HOME/.local/bin:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

pmset -g batt | grep -q "'AC Power'" || { echo "on battery, skipping"; exit 0; }

lock="$logdir/.lock"
mkdir "$lock" 2>/dev/null || { echo "previous run still going ($lock), skipping"; exit 0; }
trap 'rmdir "$lock"' EXIT

cd "$repo"
# Don't let an unattended run commit Andrew's work in progress.
[ -z "$(git status --porcelain)" ] || { echo "working tree dirty, skipping"; git status --short; exit 0; }

# Overrides are for testing only; launchd sets none of them.
max_secs=${NIGHTLY_MAX_SECS:-18000}
idle_secs=${NIGHTLY_IDLE_SECS:-1200}
prompt=${NIGHTLY_PROMPT:-'Unattended nightly session; Andrew is not available, so do not ask questions interactively.
Follow the CLAUDE.md "Start of every session" steps, then work the next actions in STATE.md that are yours.
Respect the gates: never start a phase whose gate is not recorded in docs/decisions.md. If everything left is
blocked on Andrew, do only prep work that is allowed in the current phase (or nothing), and say so in STATE.md.
Batch new questions into docs/open-questions.md. Never purchase, push, or touch anything outside this repo.
Subagents (e.g. the gate reviewer) are allowed: end your turn to wait for one and you will be resumed when it
finishes. A hook refuses a spawn when the 5h budget is too low; then record it as the next action instead.
Finish with the CLAUDE.md "End of every session" steps (update STATE.md, log decisions, commit). Then, only once
nothing is left running, signal the end of the session with the Bash command: touch "$NIGHTLY_DONE"'}

tmx() { tmux -L shop-nightly "$@"; }
tmx kill-server 2>/dev/null
start=$(date +%s)
sid=$(uuidgen | tr A-Z a-z)
echo "session: $sid"
done_file="$logdir/done-$sid"
proj="$(direnv exec "$repo" sh -c 'echo $CLAUDE_CONFIG_DIR' 2>/dev/null)/projects/$(pwd | tr / -)"
# direnv exec applies .envrc (CLAUDE_CONFIG_DIR). caffeinate -s holds the system awake while on AC.
SHOP_NIGHTLY=1 NIGHTLY_DONE="$done_file" tmx new-session -d -s nightly -x 220 -y 50 -c "$repo" \
  direnv exec "$repo" caffeinate -i -s claude --no-chrome --session-id "$sid" --permission-mode auto \
  ${NIGHTLY_MODEL:+--model "$NIGHTLY_MODEL"} "$prompt"

# Newest write to the session's transcript or any of its subagents' transcripts.
last_activity() {
  /usr/bin/stat -f %m "$proj/$sid.jsonl" "$proj/$sid"/subagents/*.jsonl 2>/dev/null | sort -n | tail -1
}
while tmx has-session -t nightly 2>/dev/null; do
  now=$(date +%s); act=$(last_activity); act=${act:-$start}
  if (( now - start > max_secs )); then why="still running after ${max_secs}s"
  elif (( now - act > idle_secs )); then why="no transcript activity for ${idle_secs}s"
  else sleep 30; continue; fi
  echo "watchdog: $why, killing"; tmx capture-pane -p -t nightly; tmx kill-server; break
done
[ -f "$done_file" ] && { echo "claude signalled done"; rm -f "$done_file"; }

transcript="$proj/$sid.jsonl"
echo "transcript: $transcript"
[ -f "$transcript" ] && jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="text") | .text' \
  "$transcript" | tail -40
echo "usage: $(cat .claude/usage.json 2>/dev/null)"
echo "=== $(date) nightly end ($(( ($(date +%s) - start) / 60 )) min)"

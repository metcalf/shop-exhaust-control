#!/usr/bin/env bash
# Nightly unattended Claude session. Run by launchd (scripts/com.metcalf.shop-exhaust-nightly.plist);
# the wake comes from `pmset repeat` (see scripts/README.md).
#
# Runs interactive Claude in a detached tmux (own socket, -L shop-nightly) rather than -p, so the statusline
# keeps .claude/usage.json current for the budget hook. The Stop hook (.claude/hooks/nightly-stop.sh) closes
# tmux when Claude ends its turn; a watchdog here kills it after NIGHTLY_MAX_SECS.
# Watch live: tmux -L shop-nightly attach -t nightly   (detach: C-b d)
set -uo pipefail

repo="$(cd "$(dirname "$0")/.." && pwd)"
logdir="$HOME/Library/Logs/shop-exhaust-nightly"
mkdir -p "$logdir"
exec >>"$logdir/$(date +%F).log" 2>&1
echo "=== $(date) nightly start"

# launchd gives a bare PATH; claude is a nodenv shim.
export PATH="$HOME/.nodenv/shims:/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin"

pmset -g batt | grep -q "'AC Power'" || { echo "on battery, skipping"; exit 0; }

lock="$logdir/.lock"
mkdir "$lock" 2>/dev/null || { echo "previous run still going ($lock), skipping"; exit 0; }
trap 'rmdir "$lock"' EXIT

cd "$repo"
# Don't let an unattended run commit Andrew's work in progress.
[ -z "$(git status --porcelain)" ] || { echo "working tree dirty, skipping"; git status --short; exit 0; }

# Overrides are for testing only; launchd sets none of them.
max_secs=${NIGHTLY_MAX_SECS:-18000}
prompt=${NIGHTLY_PROMPT:-'Unattended nightly session; Andrew is not available, so do not ask questions interactively.
Follow the CLAUDE.md "Start of every session" steps, then work the next actions in STATE.md that are yours.
Respect the gates: never start a phase whose gate is not recorded in docs/decisions.md. If everything left is
blocked on Andrew, do only prep work that is allowed in the current phase (or nothing), and say so in STATE.md.
Batch new questions into docs/open-questions.md. Never purchase, push, or touch anything outside this repo.
The session closes as soon as you end your turn, so do all work in the foreground and do not wait on background
tasks. Finish with the CLAUDE.md "End of every session" steps (update STATE.md, log decisions, commit), then stop.'}

tmx() { tmux -L shop-nightly "$@"; }
tmx kill-server 2>/dev/null
start=$(date +%s)
# direnv exec applies .envrc (CLAUDE_CONFIG_DIR). caffeinate -s holds the system awake while on AC.
SHOP_NIGHTLY=1 tmx new-session -d -s nightly -x 220 -y 50 -c "$repo" \
  direnv exec "$repo" caffeinate -i -s claude --permission-mode auto ${NIGHTLY_MODEL:+--model "$NIGHTLY_MODEL"} "$prompt"

while tmx has-session -t nightly 2>/dev/null; do
  if (( $(date +%s) - start > max_secs )); then
    echo "watchdog: still running after ${max_secs}s, killing"; tmx capture-pane -p -t nightly; tmx kill-server; break
  fi
  sleep 30
done

transcript=$(ls -t "$HOME/.claude-morgan/projects/$(pwd | tr / -)"/*.jsonl 2>/dev/null | head -1)
echo "transcript: $transcript"
[ -n "$transcript" ] && jq -r 'select(.type=="assistant") | .message.content[]? | select(.type=="text") | .text' \
  "$transcript" | tail -40
echo "usage: $(cat .claude/usage.json 2>/dev/null)"
echo "=== $(date) nightly end ($(( ($(date +%s) - start) / 60 )) min)"

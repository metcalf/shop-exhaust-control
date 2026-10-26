#!/usr/bin/env bash
# Nightly unattended Claude session. Run by launchd (scripts/com.metcalf.shop-exhaust-nightly.plist);
# the wake comes from `pmset repeat` (see scripts/README.md).
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

prompt='Unattended nightly session; Andrew is not available, so do not ask questions interactively.
Follow the CLAUDE.md "Start of every session" steps, then work the next actions in STATE.md that are yours.
Respect the gates: never start a phase whose gate is not recorded in docs/decisions.md. If everything left is
blocked on Andrew, do only prep work that is allowed in the current phase (or nothing), and say so in STATE.md.
Batch new questions into docs/open-questions.md. Never purchase, push, or touch anything outside this repo.
Finish with the CLAUDE.md "End of every session" steps (update STATE.md, log decisions, commit), then stop.'

# direnv exec applies .envrc (CLAUDE_CONFIG_DIR). caffeinate -s holds the system awake while on AC.
direnv exec "$repo" caffeinate -i -s \
  claude -p "$prompt" --permission-mode auto
echo "=== $(date) nightly end (exit $?)"

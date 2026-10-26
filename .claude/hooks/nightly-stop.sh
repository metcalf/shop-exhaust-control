#!/usr/bin/env bash
# In the unattended nightly session (scripts/nightly.sh), close tmux once Claude has signalled it's done by
# creating $NIGHTLY_DONE. Ending a turn without it (e.g. to wait on a subagent) leaves the session open; the
# idle watchdog in nightly.sh covers a session that never signals. No-op in normal sessions.
[ "${SHOP_NIGHTLY:-}" = 1 ] && [ -n "${NIGHTLY_DONE:-}" ] && [ -f "$NIGHTLY_DONE" ] || exit 0
nohup sh -c 'sleep 3; tmux -L shop-nightly kill-server' >/dev/null 2>&1 &

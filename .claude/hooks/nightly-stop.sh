#!/usr/bin/env bash
# In the unattended nightly session (scripts/nightly.sh), the first time Claude ends its turn the work is done:
# close the tmux server so the session exits. No-op in normal sessions.
[ "${SHOP_NIGHTLY:-}" = 1 ] || exit 0
nohup sh -c 'sleep 3; tmux -L shop-nightly kill-server' >/dev/null 2>&1 &

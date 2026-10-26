# scripts

## Nightly run (`nightly.sh`)

launchd starts `nightly.sh` at 22:00. It exits on battery or a dirty tree, then runs interactive Claude (auto mode,
`.envrc` applied, under `caffeinate`) in a detached tmux on its own socket, so the statusline keeps
`.claude/usage.json` current for the budget hook. `.claude/hooks/nightly-stop.sh` (gated on `SHOP_NIGHTLY=1`) closes
tmux when Claude ends its turn; a watchdog kills it after 5 h. Logs: `~/Library/Logs/shop-exhaust-nightly/`
(summary plus the transcript path). Watch live: `tmux -L shop-nightly attach -t nightly` (detach `C-b d`).
Test without the real prompt: `NIGHTLY_MODEL=haiku NIGHTLY_MAX_SECS=240 NIGHTLY_PROMPT='...' scripts/nightly.sh`.

Install:

```sh
mkdir -p ~/Library/Logs/shop-exhaust-nightly
cp scripts/com.metcalf.shop-exhaust-nightly.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.metcalf.shop-exhaust-nightly.plist
sudo pmset repeat wakeorpoweron MTWRFSU 21:58:00   # replaces any existing pmset repeat
```

Test now: `launchctl kickstart gui/$(id -u)/com.metcalf.shop-exhaust-nightly`.
Remove: `launchctl bootout gui/$(id -u)/com.metcalf.shop-exhaust-nightly` and `sudo pmset repeat cancel`.

Notes:
- The pmset wake can't be conditioned on power; on battery the Mac wakes, the script exits, and it sleeps again.
- Requires `brew install tmux`. claude is run from `~/.local/bin` (native install); the nodenv shim fails under launchd.
- `--no-chrome` skips the first-run Claude in Chrome dialog, which would otherwise block the session.
- Lid closed without an external display may still force sleep despite `caffeinate`; test it.

# scripts

## Nightly run (`nightly.sh`)

launchd starts `nightly.sh` at 22:00. It exits on battery, exits if the tree is dirty, and otherwise runs
`claude -p` in auto mode with `.envrc` applied, under `caffeinate`. Logs: `~/Library/Logs/shop-exhaust-nightly/`.

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
- The statusline doesn't run under `-p`; `nightly.sh` writes `.claude/usage.json` from the stream's `rate_limit_event`,
  but that arrived once per run in testing, so mid-run readings are not guaranteed.
- Lid closed without an external display may still force sleep despite `caffeinate`; test it.

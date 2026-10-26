# scripts

## Nightly run (`nightly.sh`)

launchd starts `nightly.sh` at 21:59; the Mac wakes at 22:00, and launchd runs a job missed during sleep on wake. It exits on battery or a dirty tree, then runs interactive Claude (auto mode,
`.envrc` applied, under `caffeinate`) in a detached tmux on its own socket, so the statusline keeps
`.claude/usage.json` current for the budget hooks. Claude may run subagents (it ends its turn to wait for them).
As its last action it creates `$NIGHTLY_DONE`; `.claude/hooks/nightly-stop.sh` then closes tmux. A watchdog kills
the session after 20 min with no transcript writes (main or subagent) or 5 h total. `.claude/hooks/subagent-budget.sh`
refuses a subagent above 70% 5h usage (asks, in attended sessions); spawn/finish usage is logged to
`.claude/usage-log.tsv` for calibrating that cap. Logs: `~/Library/Logs/shop-exhaust-nightly/`
(summary plus the transcript path). Watch live: `tmux -L shop-nightly attach -t nightly` (detach `C-b d`).
Test without the real prompt (add `NIGHTLY_IGNORE_POWER=1` on battery): `NIGHTLY_MODEL=haiku NIGHTLY_MAX_SECS=240 NIGHTLY_PROMPT='...' scripts/nightly.sh`.

Install:

```sh
mkdir -p ~/Library/Logs/shop-exhaust-nightly
cp scripts/com.metcalf.shop-exhaust-nightly.plist ~/Library/LaunchAgents/
launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.metcalf.shop-exhaust-nightly.plist
sudo pmset repeat wakeorpoweron MTWRFSU 22:00:00   # after the 21:59 job time, so the job is already due at wake
```

Test now: `launchctl kickstart gui/$(id -u)/com.metcalf.shop-exhaust-nightly`.
Remove: `launchctl bootout gui/$(id -u)/com.metcalf.shop-exhaust-nightly` and `sudo pmset repeat cancel`.

Notes:
- The pmset wake can't be conditioned on power; on battery the Mac wakes, the script exits, and it sleeps again.
- Requires `brew install tmux`. claude is run from `~/.local/bin` (native install); the nodenv shim fails under launchd.
- `--no-chrome` skips the first-run Claude in Chrome dialog, which would otherwise block the session.
- Lid closed without an external display may still force sleep despite `caffeinate`; test it.

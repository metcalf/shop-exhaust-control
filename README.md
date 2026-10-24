# Shop Exhaust Fan Controller

An ESP32 (ESP-IDF) controller for the woodshop exhaust fan. It runs the fan from particulate sensing and dust collector activity, with local physical controls and Home Assistant reporting. This is the pilot for a Claude-led design process; a dust collector controller follows it.

## Getting started
1. `git init`, then commit this skeleton.
2. Fill in `docs/site-survey.md` (★ items at minimum) and drop photos in `docs/site/`.
3. Answer what you can in `docs/open-questions.md`.
4. Open Claude Code in this directory and say: *"Read CLAUDE.md and STATE.md, then review the site survey and start phase 1."*

Claude follows `CLAUDE.md`: it keeps `STATE.md` current, batches questions, and stops for your approval at each gate (G1–G5).

## Layout
| Path | Purpose |
|------|---------|
| `CLAUDE.md` | Operating instructions for Claude (process, gates, safety rules, conventions) |
| `STATE.md` | Current phase, next actions, blockers |
| `docs/context.md` | Kickoff brief: design thinking already done |
| `docs/site-survey.md` | Your inputs about the shop, fan and preferences |
| `docs/requirements.md` | Requirements with IDs and acceptance criteria |
| `docs/interfaces.md` | I/O, Home Assistant entities, and the shared `DC_RUNNING` interface |
| `docs/decisions.md` | Decision log and gate approvals |
| `docs/open-questions.md` | Batched questions with default assumptions |
| `docs/process-notes.md` | Lessons for the DC project |
| `.claude/agents/` | Subagent definitions: `reviewer` (independent gate reviews), `sourcing` (parts research) |
| `bom.csv` | Bill of materials |
| `firmware/`, `pcb/`, `electrical/`, `mech/`, `reviews/`, `sourcing/` | Created as phases begin |

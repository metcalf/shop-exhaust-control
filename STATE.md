# Project State

**Updated:** 2026-10-24
**Phase:** 0, site survey
**Waiting on:** Andrew to complete `docs/site-survey.md` (★ items at minimum) and add photos to `docs/site/`

## Next actions
1. **Andrew:** fill in the site survey and answer what you can in `docs/open-questions.md`.
2. **Claude:** review the survey, close or update the open questions, then draft the requirements in full, including acceptance criteria.
3. **Claude:** present the requirements for **G1**.

## Blockers
- Q-15 (does the fan's control port give true off, and what's its fail state?) needs a bench test before G2. It decides whether there's any mains switching.
- Q-14 (KiCad install) blocks phase 3 PCB work only.

## Log
- 2026-10-22: Repo created from the kickoff conversation. See `docs/context.md`.
- 2026-10-23: Setup review with Andrew. Firmware moved to bare ESP-IDF; network stack extracted to `metcalf/esp-iot-core` and adopted in hvac_control (D-007). Custom PCB with third-party assembly, mains allowed under documented rules (D-008). Interaction model proposed: Auto, timed holds and scenes on a physical panel plus ambient indicator. Dropped phase budgets, BOM alternates, HVLP assumptions; pruned decision log. Fan identified (CLOUDLINE PRO S6).
- 2026-10-24: Pruned `site-survey.md` and `open-questions.md` of items already answered in the repo (Q-02, Q-06 closed from context/D-009) and de-duplicated the two, so each question is answered in one place. KiCad not installed on this Mac (Q-14 updated).
- 2026-10-24: Proposed the PCB/electrical toolchain (D-010): kiutils-generated KiCad schematic, easyeda2kicad parts, rendered-image and netlist-assertion checks, creepage DRC rules, scripted placement, with Freerouting and Quilter compared as layout candidates; WireViz for off-board wiring.

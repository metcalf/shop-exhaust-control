# Project State

**Updated:** 2026-10-25
**Phase:** 1, requirements: drafted, awaiting **G1**
**Waiting on:** Andrew to review `docs/requirements.md` and approve G1; answer Q-15, Q-19, Q-20, Q-21; decide D-013 (always-on fan power)

## Next actions
1. **Andrew:** review requirements (start with IR-05/D-013, FR-02 walk-in delay P-02, FR-08 spray run-on, SR-04, §8 parameters). Approve G1 or mark changes.
2. **Andrew:** answer Q-19…Q-21; bench-test the remaining half of Q-15 (fail state, port pinout and levels) before G2.
3. **Claude, after G1:** architecture: block diagram, node location (panel end vs fan end) and what crosses the ceiling cable, `docs/interfaces.md` complete, control-logic state machine spec; then run the reviewer for G2.
4. **Claude, before phase 3 PCB:** brief PCBA vendor comparison (Q-14 answer); JLCPCB is the default.

## Blockers
- Q-15 fail state and port electrical details block G2 (SR-08, PCB fan interface).
- D-013 / Q-19 (mains change to un-switch the fan) is reviewed at G3; it doesn't block architecture.

## Log
- 2026-10-22: Repo created from the kickoff conversation. See `docs/context.md`.
- 2026-10-23: Setup review with Andrew. Firmware moved to bare ESP-IDF; network stack extracted to `metcalf/esp-iot-core` and adopted in hvac_control (D-007). Custom PCB with third-party assembly, mains allowed under documented rules (D-008). Interaction model proposed: Auto, timed holds and scenes on a physical panel plus ambient indicator. Fan identified (CLOUDLINE PRO S6).
- 2026-10-24: Pruned survey and open questions; KiCad not installed (Q-14). Proposed PCB/electrical toolchain (D-010) and mechanical toolchain (D-011, build123d, outsourced PA12; Q-18).
- 2026-10-25: Site survey complete; applied answers Q-03…Q-18. Requirements drafted in full for G1: site summary, FR/NFR/SR/IR with ACs (AC-01…AC-25), and a parameter table (P-nn) with sourced initial values. New: FR-18 (tach fault), NFR-09…NFR-11, SR-08 (fail state), IR-04 (ceiling cable), IR-05 (always-on fan power). Decisions D-012 (SPS30 + SGP41 in v1), D-013 (un-switch the fan from the lighting relay, proposed), D-014 (panel above miter station). New questions Q-19…Q-21.

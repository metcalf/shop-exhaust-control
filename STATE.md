# Project State

**Updated:** 2026-10-25
**Phase:** 2, architecture (G1 approved 2026-10-25); not started
**Waiting on:** Andrew to schedule the start of phase 2 (paused at his request)

## Next actions
1. **Claude, when Andrew schedules it:** architecture: block diagram, control-logic state machine spec, complete `docs/interfaces.md` (fan interface with fail-off and isolation, SEN65 and VOC baseline handling, BLE message format, power budget including SEN65 peaks), cost estimate against $300; then run the reviewer for G2.
2. **Claude, before phase 3 PCB:** brief PCBA vendor comparison, including JLCPCB Economic tier rules (Q-14, NFR-05).
3. **Andrew (optional):** Q-22, a meter check of fan-port GND to the mains prongs.

## Blockers
- None.

## Log
- 2026-10-22: Repo created from the kickoff conversation. See `docs/context.md`.
- 2026-10-23: Setup review with Andrew. Firmware moved to bare ESP-IDF; network stack extracted to `metcalf/esp-iot-core` and adopted in hvac_control (D-007). Custom PCB with third-party assembly, mains allowed under documented rules (D-008). Interaction model proposed: Auto, timed holds and scenes on a physical panel plus ambient indicator. Fan identified (CLOUDLINE PRO S6).
- 2026-10-24: Pruned survey and open questions; KiCad not installed (Q-14). Proposed PCB/electrical toolchain (D-010) and mechanical toolchain (D-011, build123d, outsourced PA12; Q-18).
- 2026-10-25: Site survey complete; applied answers Q-03…Q-18. Requirements drafted in full for G1: site summary, FR/NFR/SR/IR with ACs (AC-01…AC-25), and a parameter table (P-nn) with sourced initial values. New: FR-18 (tach fault), NFR-09…NFR-11, SR-08 (fail state), IR-04 (ceiling cable), IR-05 (always-on fan power). Decisions D-012 (SPS30 + SGP41 in v1), D-013 (un-switch the fan from the lighting relay, proposed), D-014 (panel above miter station). New questions Q-19…Q-21.
- 2026-10-25 (later): Applied Q-15 (port pinout, PWM 5 kHz open-drain, unplugged = full speed), Q-19 (unswitched receptacle; D-013 accepted, no rewiring), Q-20 (vacant → off on sensor fault), Q-21 ($300 ceiling, aim for the economic PCBA tier). Added SR-09 (isolate the fan port until it's shown to be SELV) and AC-26. Lutron 15-min occupancy timeout noted; walk-in delay P-02 dropped. FR-08/AC-10: measure VOC pickup from spraying downstream of the sensor instead of assuming none.
- 2026-10-25: Added FR-19 (Andrew): vacant Auto limited to P-22 speed (60 %) and P-21 runtime (2 h after vacancy), with a "clear-down incomplete" notice; AC-27.
- 2026-10-25: Moved the controller to the north/exhaust end (D-015 replaces D-014) so the sensors see every source, including the lathe. DC link is BLE advertising with no wired or MQTT path (D-016); P-24 link timeout. IR-01/02/04, NFR-09, FR-15, AC-22 updated; Q-23 for the exact spot. Single vs. separate DC panel deferred to the DC project.
- 2026-10-25: Q-23: under-cabinet mount at the north wall, < 10 ft of cable; NFR-09 adds ≥ 3 ft from the hood, inlet facing the room.
- 2026-10-25: Coarse dust sensor moved into v1 (Andrew), logged alongside the SPS30, with control use behind a flag (FR-17, P-25/P-26, AC-28). Added an SHT4x for SGP41 humidity compensation (FR-20). HA publishes all raw sensor channels.
- 2026-10-25: FR-10: duty is continuous. NFR-10 dropped (parameters compiled in, OTA to change). SR-08 reversed to fail-off: node unpowered/booting holds the fan off, powered from the fan side of the barrier; AC-18 updated.
- 2026-10-25: Nightly unattended run added (`scripts/`, see `scripts/README.md`); budget hook now wraps up via `STATE.md`.
- 2026-10-25: Q-24: single SEN65 module (PM, VOC/NOx, RH/T); coarse sensor and SHT4x dropped (D-012 rewritten). FR-14 requires the VOC baseline to survive module sleep; FR-08 sleeps the module during Spray's minimum run-on to protect it from overspray.
- 2026-10-25: **G1 approved** (Andrew). Paused before phase 2 at Andrew's request while he sets up scheduling.

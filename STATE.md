# Project State

**Updated:** 2026-10-28
**Phase:** 2, architecture. **Ready for G2 sign-off:** all three blocking review findings are resolved (B-1 D-027, B-2 D-028, B-3 fixed). Should-fix items are triaged below.
**Waiting on:** Andrew's G2 approval

## Next actions
1. **Andrew, G2:** approve `docs/architecture.md`, `docs/control-logic.md`, `docs/interfaces.md` and D-017…D-028 (D-019 enclosure form and D-023 fail-off interface are "needs Andrew"). Review: `reviews/G2-review.md`.
2. **Claude, hardware findings before the phase 3 schematic:** S-2 (worst-case fan-side current from datasheet maxima; needs Q-26), S-4 (isolation-domain table, every barrier crossing), S-5 (`DC_IN` resistor/CTR/pull-up at 12 VDC, 12 VAC, 26.4 VAC), S-13 (SEN65 back-powered through I²C with its rail off). S-14 and S-17 are done; S-1 accepted (D-028).
3. **Claude, firmware backlog, handled at implementation rather than as doc revisions (process note 2026-10-28):** S-3 overspeed / tach at 0 %, S-6 frozen-sequence DC frames (record in D-021 when the DC project starts), S-7 SprayRunOn upper bound while occupied (FR-08 change, ask Andrew then), S-8, S-9, S-10, S-11, S-12, S-15, S-16 (MQTT keepalive ≤ 30 s; check `BaseMqttClient`).
4. **Claude, before phase 3 PCB:** PCBA vendor comparison including JLCPCB Economic tier rules (Q-14, NFR-05), plus `docs/architecture.md` §9.
5. **Andrew:** Q-31 (2 kΩ loaded leakage check, before layout), Q-26 (port current, before schematic), Q-27 (mounting, before mech).

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
- 2026-10-25 (nightly): Phase 2 started; the nightly schedule was taken as the "Andrew schedules it" trigger, since G1 is recorded. G2 draft: `docs/architecture.md` (block diagram, partitioning, firmware structure, mechanical concept, failure modes, traceability, cost ≈ $265), `docs/control-logic.md` (modes, AutoDemand, sampler with an overrun-bounded clear-down rule, faults, output shaping, design constants C-nn, host-test plan), `docs/interfaces.md` completed (BLE payload v1.0, GPIO plan, fan-powered fail-off isolated fan interface, power budget, HA entities, mechanical interfaces). Decisions D-017…D-023. Questions Q-25…Q-28. No mains anywhere in the design (D-018), so SR-01a isn't triggered.
- 2026-10-26: Nightly harness: subagents allowed; session closes on an explicit done signal, idle watchdog, subagent spawns gated at 70% 5h usage (`scripts/README.md`).
- 2026-10-26: Applied Q-28 (D-024: Auto press and new holds/scenes override Spray and its run-on; a sensor fault drops only PM/VOC demand, P-19 dropped; `fan_port` fault into FR-18) and wired opto `DC_RUNNING` backup input used for AC-06 (D-025, amends D-016/IR-01). Q-25: fan hard-wired to a 4-pos terminal, no USB-C (D-026). Fixed the 24 VAC input TVS (≥ 40 V standoff). G2 reviewer started.
- 2026-10-26: G2 reviewer run: 3 blocking (B-1 resets end Spray, SR-03; B-2 SR-09 basic-only barrier with unknown SELV and lid-off service; B-3 high PM classed as `sensor_range` fault). Fixed B-3 in control-logic §6 and AC-02 test; Q-29/Q-30 for B-1/B-2.
- 2026-10-28: Applied Q-29 (D-027: hold/scene and remaining time survive non-power resets via RTC memory; OTA not deferred; stuck tasks just reboot) and Q-22/Q-30 (D-028: port treated as SELV, basic barrier kept, Q-31 loaded check before layout). S-1 fan power-up burst accepted. S-14 boot-config items added to architecture §9; S-17 TVS → SMBJ48CA. Review triaged into hardware-now / firmware-backlog after Andrew's process note.
- 2026-10-28: Display 2.0" → 2.8" 240×320 IPS, no touch (Andrew; D-022 amended). Power budget ≈ 1.5 W typical, cost ≈ $270.

# Project State

**Updated:** 2026-11-09
**Phase:** 3, detailed design (**G2 approved 2026-10-28**). D-029 order: vendor check ✓ → schematic ✓ → priced parts list ✓ → **stopped for Andrew** → layout, mech, firmware.
**Waiting on:** Andrew: Q-33 (OK to start layout; assembly-route costs now in `sourcing/priced-parts.md`) and Q-35 (MSP2833/MSP2834 proposed) block layout. Q-34 and Q-36 answered.

## Next actions (in order; each is Claude's unless marked)
1. **Andrew:** answer Q-33 (layout OK; route A/B/C) and Q-35 (display). Optional: Q-37 (skip blocked nightlies).
2. Once Q-33 is OK'd: **layout**.
   - Fix the footprints against the LCSC drawings, using `easyeda2kicad` (in `.venv`) where stock ones differ (design.md O-3).
   - Settle O-4 (input bulk cap for hot-plug) and O-6 (GPIO47/48 voltage; it now also affects the MSP283x backlight high level). Adapt J6 to the Q-35 display: if MSP283x, a 1×14 socket with VCC from +5V, LED straight from GPIO47, and Q3 removed (`sourcing/off-board.md` §2a). Update check.py, design.md §7 and O-2.
   - Write the creepage DRC rules from `pcb/SAFETY.md` and lay out the 2-layer board.
   - Run DRC, export Gerbers/BOM/CPL. After layout starts the `.kicad_sch` becomes the source (D-035); keep running `pcb/gen/check.py` on it.
3. After layout: mech (build123d, positions from the `.kicad_pcb`), then the firmware host-tested logic.
4. **Firmware backlog, for implementation later (not now):**
   - G2 review items: S-3 overspeed / tach at 0 %; S-6 frozen-sequence DC frames (record in D-021 when the DC project starts); S-7 SprayRunOn upper bound while occupied (an FR-08 change, ask Andrew then); S-8, S-9, S-10, S-11, S-12, S-15; S-16 MQTT keepalive ≤ 30 s (check `BaseMqttClient`).
   - S-14 boot config: TWDT panic, RTC WDT, LEDC at duty 0 before routing.
   - SEN rail power-cycle sequence (design.md §4).

## Schematic status (where it stopped)
- `pcb/gen/run.sh` regenerates `pcb/exhaust.kicad_sch`, runs ERC (0 violations) and the netlist assertions (all pass), and exports the SVG and raw BOM to `pcb/reports/`. 134 parts, 40 unique LCSC parts.
- G2 review hardware items folded in: S-2 (fan side ≤ 4.3 mA at datasheet max), S-4 (`pcb/SAFETY.md`, every crossing asserted), S-5 (D-036), S-14 (EN RC, BOOT/EN switches, strapping pins asserted unconnected), S-13 and S-17 (already applied). Interfaces §2.2–2.3 still name the LTV-814; D-036 supersedes it, and the doc gets updated at layout.
- Generator draws wires within blocks and power symbols for GND/+3V3/+5V (D-038, at Andrew's request during his schematic review). Netlist unchanged.
- Known cosmetic issues: field text on rotated parts needs GUI touch-up; placement wasn't laid out for wiring, so some blocks are still label-heavy.

## Notes for an unattended run
- If Q-33 is still unanswered, there's no layout, mech or firmware work allowed (D-029).
- CLAUDE.md's phase table still puts sourcing after the full detailed design. D-029 (Andrew) overrides that for this project. Don't edit CLAUDE.md.
- No mains anywhere (D-018), so G3 is light: receptacle, the listing of Andrew's own supply (Q-36) and the 24 VAC hookup.

## Blockers
- Layout is blocked on Q-33 (D-029 checkpoint) and Q-35 (display).

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
- 2026-10-28: Phase 3 reordered (D-029, Andrew): schematic and a priced parts list come before layout, mech and firmware.
- 2026-10-28: Power: single external 5 V USB-C for power and flash/log, 3.3 V only, load-switched sensor rail; NFR-04 USB-C mouth exception (D-030, Andrew; supersedes D-020, amends D-018). Indicator count/drive under discussion.
- 2026-10-28: Indicator plain RGB (3 FETs), short strip along a display edge, no illuminated encoder; SEN65 load switch kept for recovery, S-13 applied, `SEN_PWR_EN` polarity fixed (D-031).
- 2026-10-28: Field wiring on fixed 3.5 mm screw terminals, not pluggable (D-032, Andrew).
- 2026-10-28: Read the rollitup Cloudline/ESP32 thread: PC817 at 1 kHz isn't validated there; H11L1 at 5 kHz stays unless cost says otherwise (`sourcing/fan-pwm-thread.md`).
- 2026-10-28: Q-31 (≈ 60 µA leakage) confirms SELV (D-028). Q-26: stock controller draws ≈ 9.3 mA from the port, so the fail-off budget fits (D-023). Q-27: Andrew proposes the fridge side panel by the hood (D-033 proposed; Q-32 for measurements and NFR-09).
- 2026-10-28: Q-32: fridge-panel mount accepted (D-033): ~18" from the hood edge, center ~60" up, inlet ≈ 2 ft from the hood; NFR-09 and IR-04 amended. Kids' workbench below.
- 2026-10-28: **G2 approved** (Andrew). D-019 and D-023 accepted with it. Phase 3 started; STATE set up for the nightly run (vendor check → toolchain → schematic → priced parts list, then stop for Andrew).
- 2026-10-28: No panel lock (Andrew). Front carries display, controls and the light strip (wrapping the room-side corner); sensor inlet on the bay's corner-side (north) end, sheltered, not facing down (D-033, Andrew). NFR-09 reworded to placement criteria (open inlet, no strong draft, outlet separated, AC-17) instead of a fixed distance and direction.
- 2026-10-28 (nightly): Phase 3 vendor check (JLC Standard, since the module is Standard Only; D-034), KiCad 10 toolchain with a sandbox workaround (D-035), generated schematic (ERC clean, netlist assertions pass) with G2 hardware items S-2/S-4/S-5/S-14 folded in, D-036 (bridge + PC817C inputs), D-037 (SY8089 buck, VBUS sense). Priced parts list: board ≈ $156 for 2, total ≈ $276–352. Stopped for Andrew (Q-33…Q-36).
- 2026-10-29: Q-34 (SEN65 at Mouser) and Q-36 (Andrew's own supply and cable) applied; total ≈ $266–296. Q-33 follow-up: assembly-route costing (Economic with the module hand-soldered saves ≈ $0–20; DIY on a bare PCB with stencil saves ≈ $30–85). Q-35: proposed the LCDwiki MSP2833/MSP2834 (IPS verified, ILI9341V); no verified-IPS 2.8" ST7789 generic was found.
- 2026-11-01 (nightly): No-op. Q-33 and Q-35 still open, nothing new from Andrew since 2026-10-29; D-029 blocks layout, mech and firmware, and no other phase-3 prep is allowed before them. No changes to design files.
- 2026-11-05 (nightly): No-op again. Q-33 and Q-35 still open, no repo changes since 2026-11-01; D-029 still blocks layout, mech and firmware. Added Q-37 (skip blocked nightly runs in `scripts/nightly.sh`). No changes to design files.
- 2026-11-06 (nightly): No-op, the third in a row. Q-33, Q-35 and Q-37 are still open and nothing has been committed since 2026-11-05. D-029 still blocks layout, mech and firmware. No changes to design files.
- 2026-11-07 (nightly): No-op, the fourth in a row. Q-33, Q-35 and Q-37 are still open and nothing has been committed since 2026-11-06. D-029 still blocks layout, mech and firmware. No changes to design files.
- 2026-11-08 (nightly): No-op, the fifth in a row. Q-33, Q-35 and Q-37 are still open and nothing has been committed since 2026-11-07. D-029 still blocks layout, mech and firmware. No changes to design files.
- 2026-11-09: Removed VBUS_SENSE (Andrew; D-039): divider and filter cap gone, GPIO2 unconnected and spare.

# Project State

**Updated:** 2026-11-10
**Phase:** 3, detailed design (**G2 approved 2026-10-28**). **Architecture changed by D-054/D-056 (accepted 2026-11-10):** Waveshare ESP32-S3-Touch-LCD-3.5 + minimal carrier PCB. The custom board in `pcb/` (schematic and placement) is now reference only.
**Waiting on:** nothing blocking.
Blocked-on: none

## Next actions (D-056: Waveshare 3.5 + carrier)
1. **Andrew:** review the carrier schematic (`pcb/carrier/carrier.kicad_sch`, notes in `pcb/carrier/DESIGN.md`). ERC 0, netlist assertions pass and are mutation-checked.
2. **Andrew, when the boards arrive:** `docs/bench-plan-routeB.md` (stock demo and I²C scan, AXP2101 power-on with no cell, breadboarded LTV-817/AO3400A fan stage). Write the results into that file. Step 2 decides whether the PWRON one-shot gets fitted.
3. Carrier layout: outline from the Waveshare STEP (J8 orientation; the zip is in Waveshare's wiki, not committed), barrier rules and keepouts copied from the main board, LED edge at the enclosure wall.
4. Mech stack-up: landscape panel, all cables out the left side, SEN65 behind the panel on the right with its flow path sealed to the wall, no hatch (D-057), stepped wall at the USB-C (D-056). Confirm the USB-C side from the STEP (the drawing suggests the board mounts rotated 180°), then firmware (ST7796 SPI, FT6336, AXP2101 init: input limit ≥ 1.5 A, REG22[1] off; RMT LED; FanPort with presence).

## Previous route-B actions (2.8B, superseded by D-056)
- Carrier schematic for the 2.8B is in `pcb/carrier/` (ERC 0, assertions pass); it becomes the starting point for step 3.

## Superseded custom-board actions (kept for reference)
1. **Andrew:** upload `pcb/exhaust-placed.kicad_pcb` (with its `.kicad_pro` and `.kicad_dru`) to Quilter, then drop the routed board in as `pcb/exhaust-quilter.kicad_pcb`. Answer Q-38 and Q-39 (`pcb/LAYOUT.md` §3 lists the assumptions A1–A8).
2. **Freerouting candidate:** once Q-38 allows the jar, run `pcb/layout/route_freerouting.sh`. It routes, adds GND pours and writes DRC and renders for `pcb/exhaust-freerouting.kicad_pcb`. The jar is already in `pcb/tools/bin/` (gitignored); the script header has the download line.
3. **Each routed candidate:** `kicad-cli pcb drc --refill-zones` against `exhaust.kicad_dru` (copy the `.kicad_pro`/`.kicad_dru` next to it under its basename). Both must pass; Andrew picks one. Then: silk cleanup, Gerbers/BOM/CPL, the barrier screenshot and record in `pcb/SAFETY.md`, and the chosen board becomes `pcb/exhaust.kicad_pcb`.
4. If Q-39 moves parts: edit `POS` in `pcb/layout/place.py`, rerun `pcb/layout/run.sh`, and re-export for both routers.
5. **Mech** (build123d) starts from the locked placement once Q-39 is answered, since mirroring or moving parts changes the enclosure. Read positions from the `.kicad_pcb`. Then the firmware host-tested logic.
   - At bring-up, confirm O-6 with `espefuse.py summary` (VDD_SPI 3.3 V).
6. **Firmware backlog, for implementation later (not now):**
   - G2 review items: S-3 overspeed / tach at 0 %; S-6 frozen-sequence DC frames (record in D-021 when the DC project starts); S-7 SprayRunOn upper bound while occupied (an FR-08 change, ask Andrew then); S-8, S-9, S-10, S-11, S-12, S-15; S-16 MQTT keepalive ≤ 30 s (check `BaseMqttClient`).
   - S-14 boot config: TWDT panic, RTC WDT, LEDC at duty 0 before routing.
   - SEN65 reset-and-retry at startup; I²C bus recovery and module reset on `sensor_no_data` (D-047).
   - Touch UI (`docs/control-logic.md` §8): FT6336G on its own 100 kHz I²C bus (D-048).

## Layout status (where it stopped)
- `pcb/layout/run.sh`: schematic netlist → `check.py` (passes) → project footprints → locked placement → DRC: **0 errors**. 96 silk warnings, 2 intentional TP footprint mismatches, 203 unrouted. Renders: `pcb/reports/render/placed-{front,back}.png`.
- `pcb/exhaust.kicad_sch` is the source now (D-035, D-051). `pcb/gen/run.sh` checks it and only regenerates with `REGENERATE=1`. Don't edit `build.py`.
- Barrier: netclasses, plus clearance and creepage rules, plus keepouts; mutation-checked (`pcb/LAYOUT.md` §4). Placement minimums: 6.16 mm node↔field, 2.18 mm field↔field.
- A KiCad lock file (`pcb/~exhaust.kicad_sch.lck`, 20:36) was present at the start of this run. If the schematic was open in the GUI, reload it before saving, or the footprint-field changes (D-051) get overwritten.

## Schematic status (where it stopped)
- `pcb/gen/run.sh` regenerates `pcb/exhaust.kicad_sch`, runs ERC (0 violations) and the netlist assertions (all pass), and exports the SVG and raw BOM to `pcb/reports/`. 100 parts, 28 unique LCSC parts.
- G2 review hardware items folded in: S-2 (fan side ≤ 4.1 mA at datasheet max), S-4 (`pcb/SAFETY.md`, every crossing asserted), S-5 (D-036), S-14 (EN RC, BOOT/EN recovery pads per D-041, strapping pins asserted unconnected), S-13 and S-17 (already applied). Interfaces §2.2–2.3 still name the LTV-814; D-036 supersedes it, and the doc gets updated at layout.
- Generator draws wires within blocks and power symbols for GND/+3V3/+5V (D-038, at Andrew's request during his schematic review). Netlist unchanged.
- Known cosmetic issues: field text on rotated parts needs GUI touch-up; placement wasn't laid out for wiring, so some blocks are still label-heavy.

## Notes for an unattended run
- Everything left is waiting on Andrew (Quilter upload, Q-38, Q-39). Don't hand-route a final board or upload anything to Quilter. Mech waits for Q-39.
- CLAUDE.md's phase table still puts sourcing after the full detailed design. D-029 (Andrew) overrides that for this project. Don't edit CLAUDE.md.
- No mains anywhere (D-018), so G3 is light: receptacle, the listing of Andrew's own supply (Q-36) and the 24 VAC hookup.

## Blockers
- Freerouting can't run unattended until Q-38 is answered. Quilter is Andrew's upload.

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
- 2026-11-09: Removed the VBUS polyfuse, kept `+5V` at one 10 µF (USB sink limit), swapped the buck to AP63203WU-7 (Andrew; D-040). O-4 closed. ERC 0, netlist assertions pass. Standard PCBA for 2 boards ≈ $154, total ≈ $264–294.
- 2026-11-09: EN/BOOT tact switches replaced by two screwdriver pad pairs, each with its own GND pad (Andrew; D-041). ERC 0, netlist assertions pass. Standard PCBA for 2 boards ≈ $153, total ≈ $263–293.
- 2026-11-09: Removed the three SMF15A fan-line TVS diodes (Andrew; D-042). ERC 0, netlist assertions pass. Standard PCBA for 2 boards ≈ $151, total ≈ $261–291.
- 2026-11-09: Removed tach series diode D5; separate presence opto kept for flexibility across fans (Andrew; D-043). ERC 0, netlist assertions pass. Standard PCBA for 2 boards ≈ $149, total ≈ $259–289.
- 2026-11-09: Removed the fan-side HT7550 and `+5F`; the fan interface runs from `+10V_F` (Andrew; D-044). ERC 0, netlist assertions pass. Standard PCBA for 2 boards ≈ $145, total ≈ $255–285.
- 2026-11-09: Optos changed to LTV-817S-TA1-C (Basic; Andrew; D-045). Added SEN_SDA and SEN_SCL test pads. ERC 0, netlist assertions pass. Standard PCBA for 2 boards still ≈ $145.
- 2026-11-09: Removed the SMBJ48CA TVS diodes from J-OCC and J-DC (Andrew; D-046). ERC 0, netlist assertions pass. Standard PCBA for 2 boards ≈ $143, total ≈ $253–283.
- 2026-11-09: Removed the SEN65 power switch; sensor on `+3V3`, GPIO10 spare (Andrew; D-047). ERC 0, netlist assertions pass. Cost unchanged at ≈ $143 for 2 boards.
- 2026-11-09: Touch-only panel on the Elecrow DLS29028B; encoder, buttons and backlight FET removed; J6 1×14 on `+5V`; 2N7002 touch I²C shifters (Andrew; D-048, Q-35). ERC 0, netlist assertions pass. 2-board PCBA ≈ $135, project ≈ $242–267. The physical-controls design is recorded in `docs/physical-controls-record.md`.
- 2026-11-09: J-FAN split into two 2-pos KF128L (J2 + J7); each AC input's 2 × 2.7 k → one 10 k 1206 Basic (Andrew; D-049). ERC 0, netlist assertions pass. 2-board PCBA ≈ $133, project ≈ $240–265. `sourcing/priced-parts.md` assembly-routes section (2026-10-29) is stale; refresh from the live JLC quote at G4.
- 2026-11-09: Kept the fan-side opto barrier (Andrew; D-050). Non-isolated, ferrite and capacitive-coupling options logged as rejected (≈ $4 saving vs. touch-panel noise risk). No design change.
- 2026-11-09: Schematic approved (Andrew; Q-33, D-029 checkpoint passed). Layout unblocked for the nightly run, with Q-33's defaults (route-agnostic, no EPAD vias, MJF).
- 2026-11-09 (nightly): Layout started per D-010. Footprints checked against LCSC drawings and datasheets (O-3, O-5 closed; LED and bridge pin maps fixed; D-051). Schematic is now the source. Placement scripted and locked: 72 × 123 mm, barrier netclasses, creepage and clearance rules, keepouts; DRC 0 errors, rules mutation-checked (D-052 proposed). DSN exported. Freerouting was blocked by the permission classifier (Q-38). Placement review in Q-39. Interfaces §2.2–2.3 now match the schematic.
- 2026-11-09: Layout plan in STATE aligned with D-010: scripted placement, then a Quilter candidate (Andrew uploads) and a Freerouting candidate from the same locked placement.
- 2026-11-09: D-010 (PCB/electrical toolchain) accepted (Andrew).
- 2026-11-10: Evaluated the Waveshare ESP32-S3-Touch-LCD-2.8B as a replacement for the custom PCB (Andrew). The schematic shows GPIO16 is touch INT, not a spare as the docs say, and the SEN65 clashes with the IMU at 0x6B. That leaves four usable pins (43, 44, 4 after lifting R24, and 0 for output only), which is enough without FAN_PRESENT and DC_IN. Fail-off needs a relay NC contact. D-053 proposed; Q-40…Q-43.
- 2026-11-10: Costed route B (Andrew): Waveshare board + minimal carrier PCB keeps every signal and the D-023 fail-off. No S3 module on our board means JLC Economic applies (every S3 module is "Standard Only", checked live). Electronics ≈ $65–100 per unit. D-054 proposed; Q-40 reframed, Q-44/Q-45 added.
- 2026-11-10: Andrew chose route B, stripped down (D-054 accepted): LTV-817 for PWM, desolder the QMI8658, lift R24 for OCC. FAN_PRESENT and DC_IN dropped. The carrier has no Extended parts (JLC Economic, ≈ $9.71 in fees); one unit's electronics ≈ $58–87.
- 2026-11-10: Indicator: on-board side-view SK6812SIDE-A on the carrier edge, not an off-board strip (Q-45, D-055). One Extended part, ≈ $3–4.50 per order. Display: stay on the 2.8B (480×640 RGB). No up-front stress test (Andrew): the UI is simple; tune PCLK, bounce buffers and partial refresh in firmware if drift shows up.
- 2026-11-10: Docs amended for route B (D-054/D-055): requirements §1, §3, FR-18 (fan-port fault dropped), NFR-04/05, IR-01, AC-06/07; interfaces §1, §2 (J7 pin map read from the Waveshare schematic), §3 power, §5 mech; architecture block diagram, §3, §4, §5, §6, §7, §8 (≈ $215), §9; control-logic drops `dc_wired`, `fan_port`, C-16, C-31.
- 2026-11-10: Carrier schematic generated (`pcb/carrier/`, reusing `pcb/gen/sch.py`): header J1 per the Waveshare J7 map, LTV-817 fail-off stage, tach, OCC, SEN65 (DNP pull-up pads), 2N7002 → 470 Ω → 6 × SK6812SIDE-A. ERC 0; carrier `check.py` passes and is mutation-checked. SK6812SIDE-A footprint from easyeda2kicad, pads remapped to `LED:SK6812`. `pcb/SAFETY.md` notes the carrier's three crossings.
- 2026-11-10: Switched to the Waveshare 3.5 (D-056, Andrew): SPI panel frees ten header GPIOs, IMU at 0x6A so no rework, FAN_PRESENT and DC_IN return. AXP2101 power-on at VBUS insertion is eFuse-dependent, so the carrier gets a PWRON one-shot. USB-C exposed through a stepped enclosure wall (Andrew).
- 2026-11-10: Updated for the 3.5 (D-056): pin plan GPIO38–42/21, J8 Rev 2.0 numbering (V1 rows swapped, same positions), FR-18 fan-port fault and the D-025 wired DC input restored across requirements, interfaces, architecture and control logic; AXP2101 power-on documented with a DNP PWRON one-shot. Carrier regenerated: five barrier optos, one-shot, J8 header; ERC 0, assertions pass. Bench plan rewritten (AXP2101 power-on check replaces the rework steps). Board price $25.99–32.99 (Waveshare store).
- 2026-11-10: Mech direction from Andrew: landscape panel, wiring out the left, SEN65 behind the panel on the right facing the room, possibly no separate bay. Logged as D-057 (proposed); Q-46 asks to amend NFR-03/NFR-04.
- 2026-11-10: D-057 accepted (Andrew, Q-46): NFR-04 amended (SEN65 flow path sealed to the wall, inside the one enclosure); NFR-03 relaxed, no hatch (open the enclosure for everything); AC-14/AC-15 amended; D-019 superseded.

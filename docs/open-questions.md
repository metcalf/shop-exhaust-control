# Open Questions

Claude batches questions here. Each has an ID, why it matters, and the default Claude assumes if it's left unanswered.

**Andrew:** write your answer in the `Answer` cell and leave the row in place.
**Claude (each session start):** move answered rows to Answered with the date, apply them, and record where in `Applied to`.

| ID | Question | Why it matters | Default if unanswered | Blocks | Answer |
|----|----------|----------------|-----------------------|--------|--------|
| Q-37 | Nightly no-ops: 2026-11-01 and 2026-11-05 both found only Q-33/Q-35 open and changed nothing. Want me to add the skip to this repo's `scripts/nightly.sh` now (skip when STATE.md has `Blocked-on: andrew` and nothing has been committed since the last nightly), rather than waiting for the DC repo? | Each blocked run costs a session start and usage for nothing. | No change: runs continue nightly and no-op until you answer Q-33/Q-35. | Nothing (tooling only) | |
| Q-38 | The nightly's permission classifier blocked running the downloaded Freerouting jar (code from an external source). Can you either allow `java -jar pcb/tools/bin/freerouting-*.jar` in this repo's settings, or run `pcb/layout/route_freerouting.sh` yourself? It's one command: route, pours, DRC and renders | D-010's comparison candidate. Quilter doesn't depend on it | Until then there's no Freerouting candidate; Quilter (your upload of `pcb/exhaust-placed.kicad_pcb`) is the only route | Freerouting candidate (STATE 2d) | |
| Q-39 | Placement review (`pcb/LAYOUT.md` §3, D-052): (a) Is the indicator's room side the **right** side, seen from the front? (b) Is the rear the service side with the lid off (test and recovery pads are on the back)? (c) Can you check the KF128L wire entry against the part or drawing: I assumed the side with the drawn openings, facing up? (d) Are the 72 × 123 mm outline, top cable entry, and display holes doubling as mounting holes OK for the enclosure? | Mirroring or moving after routing means re-routing. The outline sets the enclosure | (a) right, (b) rear, (c) as drawn, (d) as placed | Routing changes, mech start | |
| Q-40 | **Which route?** (A) Waveshare + off-the-shelf modules (D-053), (B) Waveshare + minimal carrier PCB (D-054), (C) lean all-custom (current board, Economic PCBA, module hand-soldered). See `docs/eval-offtheshelf-board.md` | Reopens architecture: board, enclosure, display firmware, BOM. Layout is paused until you answer | (B) | Layout, mech, Q-38/Q-39 (moot if yes) | |
| Q-41 | *(Route A only)* Fail-off: OK with a 5 V relay module (coil always on while powered, NC across speed–GND_F) plus a 3V3 pull-up holding the PWM opto lit through boot? Or accept fail-**full** when the node is dead (no relay)? | SR-08. PC817 modules can only pull the line low while lit, so an unpowered node means full speed without the relay | Relay; SR-08 reworded to "passive NC contact" | Module list, SR-08 | |
| Q-42 | SEN65 and the on-board QMI8658 IMU are both at I²C 0x6B on the same bus. (a) Hot-air off the IMU (U6, LGA-14; we don't use it), or (b) a TCA9548A mux breakout (0x70, no rework)? | Neither part's address can move, so without one of these the SEN65 doesn't work | (b) TCA9543A on the carrier for route B; (a) for route A | Wiring, firmware I²C | |
| Q-43 | `FAN_PRESENT` and wired `DC_IN`: drop both (BLE-only DC link; tach fault only), or add a PCF8574A module (0x38, ~$2) on the I²C bus for them? | Both dropped means FR-18's fan-port fault goes and D-025 reverts. The expander keeps them at the cost of one module and polling | Route B: keep both on a PCA9536 (0x41) on the carrier. Route A: drop both | FR-18, IR-01, AC-06 | |
| Q-44 | Route B: keep the H11L1 for fan PWM (Extended, about $2.40–4 more per order) or try the Basic LTV-817 with a 2.2 kΩ gate pull-up and a bench duty check? | PWM fidelity at 5 kHz versus the last Extended fee on the fan side | Keep H11L1 | Carrier schematic | |
| Q-45 | Route B: indicator as an off-board WS2812-class strip on a 3-pin terminal, with a 2N7002 level shifter on the carrier? | The carrier sits behind the display, so on-board LEDs wouldn't show. A strip can wrap the corner (D-033) | Yes, off-board strip | Carrier schematic, mech | |

## Answered

| ID | Question | Answer | Answered | Applied to |
|----|----------|--------|----------|------------|
| Q-33 | D-029 checkpoint: OK to start layout? Assembly route? | Schematic approved; start layout. Defaults taken: route-agnostic layout (no EPAD back-solder vias), route picked at G4 from a live JLC quote, enclosure stays MJF | 2026-11-09 | D-029 status, STATE |
| Q-35 | Display module? | Elecrow DLS29028B (MSP2834), with touch used as the only control. Physical controls dropped. | 2026-11-09 | D-048, J6, `pcb/design.md` §7, requirements §3/FR-01 |
| Q-34 | SEN65 stock / SEN66 fallback | In stock at Mouser. | 2026-10-29 | `sourcing/priced-parts.md` (buy at Mouser; SEN65 stays) |
| Q-36 | Raspberry Pi supply cable reach | Andrew supplies the power supply and cable from stock. | 2026-10-29 | `sourcing/priced-parts.md` (supply and cable $0); model to confirm at G3 (listing, ≥ 5 V / 1.5 A) |
| Q-32 | Fridge-panel mount measurements | (a) ~18" from hood edge to panel face; (b) panel ~24" deep; (c) center ~60" up (intake ~66"), a few inches from the panel's front edge; (d) the bench below is the kids' workbench. | 2026-10-28 | D-033 accepted; NFR-09, IR-04, requirements §10; interfaces §5; architecture §5; D-015, D-019 |
| Q-31 | Loaded leakage check, fan port GND to earth | ~0.6 V across 10 kΩ (≈ 60 µA). | 2026-10-28 | D-028 confirmed; SR-09, interfaces §2, §2.1 |
| Q-26 | Stock controller current from the fan's +10 V | 13.7 mA in GND with the fan off, 9.3 mA at full speed. | 2026-10-28 | D-023, interfaces §2.1 (≈ 9.3 mA from red; the extra ≈ 4.4 mA at fan-off is the 2.2 kΩ speed pull-up) |
| Q-27 | Mounting spot under the north cabinets | Proposes the side of the refrigerator panel next to the hood instead: easier reach, near the airflow, a bit less visible but visible from most relevant places. | 2026-10-28 | D-033 (proposed); follow-up Q-32 |
| Q-30 | Fan-port SELV evidence for G2 review B-2 | Unplugged: open circuit on resistance and diode checks. Plugged in: ~65 VAC to neutral/ground, presumably capacitive coupling on an isolated supply. | 2026-10-28 | D-028; SR-09, interfaces §2, §2.1; Q-31 confirms |
| Q-29 | Resume Spray across resets (G2 review B-1) | Persist the current scene and time in scene in RTC memory, generally. Don't defer OTA. Don't add in-place recovery of a stuck sensor task; just reboot. | 2026-10-28 | D-027; NFR-07, AC-18, control-logic §2, §10, architecture §4, §6 |
| Q-22 | Port GND to plug prongs, unplugged | Open circuit on both resistance and diode checks. | 2026-10-28 | D-028, SR-09 |
| Q-28 | G2 design calls (a)–(f) | (a) Auto press goes straight back to Auto, no long press. (b) Yes. (c) A sensor fault removes only PM/VOC demand; DC and occupancy demand unaffected. (d) No: respect user overrides. (e) Yes. (f) Keep the opto-isolated wired DC input as a backup; test AC-06 with it instead of BLE. | 2026-10-26 | D-024, D-025; FR-08, FR-18, SR-04, IR-01, AC-05/06/07/20, P-19 dropped; control-logic §2, §4, §6, §8–10; interfaces §1, §2.3, §4; architecture §1–3, §6–8 |
| Q-25 | USB-C contact map of the fan cable | Skip USB-C; provide 4 terminals to hard-wire into. | 2026-10-26 | D-026, D-020 amended; interfaces §2, §2.1, §5; architecture §1, §3, §6, §8, §9 |
| Q-24 | Humidity for VOC compensation / sensor choice | Build around the SEN65 and drop the coarse sensor, for one airflow path. Gas-only mode isn't needed: PM sampling stops only when dust is high, when the fan is at max anyway. | 2026-10-25 | D-012, FR-14, FR-17 (dropped), FR-20, NFR-02/03/04, SR-04, FR-08 |
| Q-23 | Exact north-end mounting spot and cable length | Under the cabinets, < 10 ft of cable. | 2026-10-25 | D-015, IR-04, NFR-09 (≥ 3 ft from hood) |
| Q-15 | S6 control port fail state, pinout and levels | Unplugged → full speed. Black GND, red +10 V (low current), yellow speed (2.2 kΩ pull-up to +10 V, pulled low by the controller; 5 kHz PWM, 20/46/100 % at levels 1/4/10), white tach (50 % square, ~30/75/144 Hz at levels 1/4/10; 10 kΩ pull-up to the controller's 5 V). Not scoped: mains grounding relationship unknown. | 2026-10-25 | FR-10, FR-18, SR-08, SR-09 (new), `interfaces.md` §2 |
| Q-19 | Unswitched receptacle for the fan? | Yes, one is available in the cabinet. | 2026-10-25 | D-013 (accepted), IR-05 |
| Q-20 | PM sensor fault while vacant | Fan can stop when unoccupied. Occupancy is a Lutron sensor with a 15-min delay. | 2026-10-25 | SR-04, FR-07, P-20 dropped; P-02 walk-in delay dropped (Andrew: floor during walk-ins is fine) |
| Q-21 | Budget | Proceed with a $300 upper limit, ideally well below. Fit JLCPCB Economic PCBA or similar. Enclosure printing should be inexpensive. | 2026-10-25 | NFR-05, NFR-08, P-17 |
| Q-03 | DC boost semantics | Boost to 60 % immediately when the DC turns on, sustained 5 min after it turns off. A floor: Auto can go higher. | 2026-10-25 | FR-09, P-10, P-11 |
| Q-05 | Fuel-burning appliances sharing the shop's air? | None anywhere in the building. | 2026-10-25 | SR-06 (plus garage makeup-air limitation) |
| Q-07 | Fallback on sensor fault | Run at low speed and show a fault; indicator flashes red (only when occupied). | 2026-10-25 | SR-04, FR-15, P-19; vacant case is Q-20 |
| Q-08 | PMS5003 or SPS30? | SPS30 | 2026-10-25 | D-012, NFR-02, P-06 |
| Q-09 | VOC in v1 or v2? | v1 | 2026-10-25 | D-012, FR-14 (now M, also drives Auto) |
| Q-10 | Panel and indicator location | Above the miter saw, mid-shop; LV wire along the ceiling to the fan; DC wiring reaches the miter blast gate anyway. | 2026-10-25 | D-014, later replaced by D-015 (north end) |
| Q-11 | Budget ceiling | ~$100 hoped, can exceed. | 2026-10-25 | NFR-08; follow-up Q-21 |
| Q-12 | Interim `DC_RUNNING` source? | No; wait for the DC controller. | 2026-10-25 | IR-01, `interfaces.md` §1 |
| Q-14 | KiCad install and PCBA vendor | KiCad installed (`/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli`). JLCPCB is the default, but do brief market research to recommend a vendor. | 2026-10-25 | D-010; vendor research is a Claude action before phase 3 PCB (STATE.md) |
| Q-15 (part) | Does 0 % PWM give true off? | Yes. The fan also provides a tach signal. | 2026-10-25 | FR-10, FR-18, D-013; fail state still open (Q-15 above) |
| Q-16 | 24 VAC signal source; can it power the node? | Transformer that switches with the lights, near the fan. Node gets its own always-on supply. | 2026-10-25 | FR-07, D-013 |
| Q-18 | Enclosing mains in the printed enclosure | (a): no mains in the printed enclosure unless constraints force it. | 2026-10-25 | SR-01 |
| Q-06 | Occupancy signal for sensor sleep | The 24 VAC lighting signal near the fan (Q-16) | 2026-10-24 | D-009, FR-07 |
| Q-02 | Does the Lobo DC vent outdoors or recirculate? | Recirculates through an aftermarket pleated filter | 2026-10-24 | FR-09, SR-06 |
| Q-17 | Should Auto fail to occupied if the occupancy input fails? | Treat the lighting signal as correct; no failure handling. Display shows occupancy. | 2026-10-24 | FR-02, FR-07 |
| Q-13 | Extract `hvac_control/components/wifi`? | Yes: `metcalf/esp-iot-core`, submodule at `components/esp-iot-core` | 2026-10-23 | D-007 |
| Q-04 | Which finishes are sprayed? | No spray guns; occasional aerosol cans only. | 2026-10-23 | SR-02 |
| Q-01 | Exhaust fan motor and speed-control type | AC Infinity CLOUDLINE PRO S6 (EC motor, PWM control port) | 2026-10-23 | FR-10 |

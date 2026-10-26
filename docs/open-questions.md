# Open Questions

Claude batches questions here. Each has an ID, why it matters, and the default Claude assumes if it's left unanswered.

**Andrew:** write your answer in the `Answer` cell and leave the row in place.
**Claude (each session start):** move answered rows to Answered with the date, apply them, and record where in `Applied to`.

| ID | Question | Why it matters | Default if unanswered | Blocks | Answer |
|----|----------|----------------|-----------------------|--------|--------|
| Q-22 | Optional, 2 min with a meter: with the S6 **unplugged from mains**, resistance from the control port's black (GND) wire to each plug prong (L, N, ground). | Open circuit to L/N would support treating the port as SELV, but it isn't proof. It shapes SR-09. | Isolate the fan interface regardless (cheap: two optos); the measurement is a sanity check | — | |
| Q-26 | Optional: current the stock controller draws from the fan's red +10 V (meter in series on red, fan on, at levels 1 and 10). | The fail-off interface (D-023) draws ≈ 4–5 mA typical, ≤ 8 mA worst case from that pin. | Assume ≥ 8 mA is available (the stock controller runs a 78L05, an MCU and level LEDs from it); confirm on the bench (AC-18) | — | |
| Q-27 | Mounting spot measurements under the north cabinets: cabinet bottom depth, face-frame lip/recess depth, clear height below (to counter or whatever is underneath), and distance from the hood's edge. A photo with a tape measure is enough. | Enclosure size and bracket (D-019, `docs/interfaces.md` §5). | 12" deep cabinet bottom, ¾" recess lip, ≥ 15" clear below, ≥ 3 ft to the hood | Phase 3 mech | |
| Q-29 | G2 review B-1: a reset (OTA reboot, Wi-Fi/BLE stack panic, sensor-task watchdog) currently ends Spray, and if vacant Auto then turns the fan off, which breaks SR-03. Proposal: keep Spray/SprayRunOn state in RTC memory and resume it after any non-power-on reset (an NFR-07 exception); defer OTA reboots during Spray/run-on; recover a stuck sensor task without rebooting. OK? | NFR-07 is an approved requirement; this amends it. | As proposed | G2 | |
| Q-30 | G2 review B-2: SR-09 isolation is basic only (3.0 mm), and lid-off flashing and AC-18's scope ground touch the fan side while its SELV status is unknown. Cheapest fix is Q-22 (now needed before G2), extended: with the S6 **plugged in**, AC and DC volts from port GND and +10 V to receptacle earth and neutral; with it **unplugged**, ohms from port GND to each prong. | If the port isn't shown to be SELV, the barrier goes reinforced (≥ 4 mm plus slot, reinforced-rated optos), with a fan-side cover and an "unplug J-FAN before lid-off" rule. | Go reinforced anyway if unmeasured (costs board area, not much money) | G2 | |

## Answered

| ID | Question | Answer | Answered | Applied to |
|----|----------|--------|----------|------------|
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

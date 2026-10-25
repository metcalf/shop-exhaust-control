# Open Questions

Claude batches questions here. Each has an ID, why it matters, and the default Claude assumes if it's left unanswered.

**Andrew:** write your answer in the `Answer` cell and leave the row in place.
**Claude (each session start):** move answered rows to Answered with the date, apply them, and record where in `Applied to`.

| ID | Question | Why it matters | Default if unanswered | Blocks | Answer |
|----|----------|----------------|-----------------------|--------|--------|
| Q-15 | *Remaining half (0 % = off and tach confirmed):* what does the S6 do (a) with the control cable unplugged, (b) with the cable plugged in but the controller end unpowered? And, bench with a scope on the stock controller: port pinout, supply voltage the fan provides, PWM level and frequency, tach pulses per rev. | With D-013 the port is the only way the fan turns off, so this is the node-dead fail state (SR-08). The pinout and levels size the PCB interface. | Assume the fan runs at full speed with no signal (worst case for noise, safe for air); hold the line low through boot; HA alerts on node offline. | G2 | |
| Q-19 | For D-013: is there an unswitched receptacle in the fan cabinet, or will you rewire the relay out of the fan receptacle's feed? Does anything else depend on that relay (the hood light, say)? | IR-05: the fan must keep power after the lights go off for vacant clear-down and Spray run-on. Mains change, so G3. | Rewire so the cabinet receptacle is always-on; the 24 VAC transformer stays as the occupancy signal | G3 | |
| Q-20 | PM sensor fault while **vacant** (your Q-07 answer covers occupied): keep running at low speed indefinitely, or run P-20 (60 min) after the lights go off and then stop? | A dead sensor while you're away for a week would otherwise run the fan the whole time. Low-speed S6 power is small, so this is mostly about preference. | Run 60 min after vacancy, then off; HA alert stays active | SR-04 | |
| Q-21 | Budget. Rough estimate for v1 as specified: SPS30 ~$50, SGP41 ~$10, display/encoder/buttons ~$20, LED indicator ~$10, listed supply ~$15, PCB + PCBA (5-board minimum, setup and extended-part fees) ~$50–80, outsourced SLS/MJF enclosure ~$50–100, cable and connectors ~$20. Total **~$225–300** (prices unchecked; G4 confirms). Getting near $100 means dropping the custom PCB for a dev board (D-008 fallback), PMS5003 instead of SPS30, or a cheaper enclosure. Which do you want: a ~$300 ceiling with the current scope, or cuts? | NFR-08 / P-17 | Keep scope; report against $100; flag anything that pushes the total past $300 | G2 | |

## Answered

| ID | Question | Answer | Answered | Applied to |
|----|----------|--------|----------|------------|
| Q-03 | DC boost semantics | Boost to 60 % immediately when the DC turns on, sustained 5 min after it turns off. A floor: Auto can go higher. | 2026-10-25 | FR-09, P-10, P-11 |
| Q-05 | Fuel-burning appliances sharing the shop's air? | None anywhere in the building. | 2026-10-25 | SR-06 (plus garage makeup-air limitation) |
| Q-07 | Fallback on sensor fault | Run at low speed and show a fault; indicator flashes red (only when occupied). | 2026-10-25 | SR-04, FR-15, P-19; vacant case is Q-20 |
| Q-08 | PMS5003 or SPS30? | SPS30 | 2026-10-25 | D-012, NFR-02, P-06 |
| Q-09 | VOC in v1 or v2? | v1 | 2026-10-25 | D-012, FR-14 (now M, also drives Auto) |
| Q-10 | Panel and indicator location | Above the miter saw, mid-shop; LV wire along the ceiling to the fan; DC wiring reaches the miter blast gate anyway. | 2026-10-25 | D-014, FR-15, IR-04 |
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

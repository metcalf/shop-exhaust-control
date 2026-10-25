# Open Questions

Claude batches questions here. Each has an ID, why it matters, and the default Claude assumes if it's left unanswered.

**Andrew:** write your answer in the `Answer` cell and leave the row in place.
**Claude (each session start):** move answered rows to Answered with the date, apply them, and record where in `Applied to`.

| ID | Question | Why it matters | Default if unanswered | Blocks | Answer |
|----|----------|----------------|-----------------------|--------|--------|
| Q-03 | Exact boost semantics: delay before boosting, boost level, behavior after the DC stops | FR-09 | Boost to max after 2 min of DC run; hold 5 min after the DC stops | FR-09 | Boost to 60% immediately when the DC turns on and sustain for 5 minutes after it turns off. This sets a minimum level--auto can still increase beyond 60% during that time. |
| Q-05 | Any fuel-burning appliances sharing the shop's air? | Backdraft risk (SR-06) | Assume none, and document the assumption | SR-06 | No fuel-burning appliances anywhere in the building. |
| Q-07 | Fallback on sensor fault: last manual speed, low speed, or off? | SR-04 | Run at low speed and show a fault | SR-04 | Run at low speed and show a fault. Can use the air quality indicator to flash red (only when occupied) to signal fault. |
| Q-08 | PMS5003 or SPS30? | Sensor life vs. cost. Comms differ (SPS30 is I²C/UART with a cleaning command). | Evaluate in architecture; lean SPS30 if the cost difference is under about $40 | G2 | SPS30 assuming no other reasons to push towards PMS5003 |
| Q-09 | VOC sensing in v1 or v2? | Scope | v2 | FR-14 | v1 |
| Q-10 | Where do the panel and the ambient indicator live? The fan is at one end of an 11' × 33' shop, with dust made mid-shop. | Wiring, enclosure, and whether the indicator is visible from the saws | Decide in architecture with the layout; lean toward panel at the main work area, indicator visible from the saws | FR-01, FR-15 | I think panel mid-shop above the miter saw is probably a convenient choice unless you're concerned about it being too close to the dust source/vibration. I'll be running wire from the dust collector to the blast gate there anyway at some point. I can run low voltage wire from there to the exhaust fan along the ceiling|
| Q-11 | Budget ceiling for v1? | Sensor choice, enclosure, speed control | No explicit cap; flag anything over $300 | NFR-08 | I'm hoping the whole thing comes in around $100, but can exceed that. |
| Q-12 | Is an interim `DC_RUNNING` source wanted before the DC controller exists? (e.g. a CT clamp on the DC circuit) | Lets the boost work now | Yes, a CT clamp | IR-01 | No, OK to wait for the DC controller. |
| Q-14 | KiCad isn't installed on this Mac (checked 2026-10-24). Will you install KiCad 9 here, or is phase 3 run on another machine? I need `kicad-cli` for ERC, DRC and Gerber/PCBA export. PCBA vendor preference? | Can't verify the PCB without it | Install KiCad 9; JLCPCB | Phase 3 PCB | KiCad installed (/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli). I've used JLCPCB for PCBs before so would be my default for PCBA, but you should do some relatively brief research on the current state of the market to recommend a vendor. |
| Q-15 | Does the CLOUDLINE PRO S6's control port give true off at 0% PWM, and what does the fan do when the control signal is lost (unplugged, node dead)? | Decides whether we switch mains at all, and the fail state (SR-04) | Bench-test before G2; assume port-only control with no mains switch | FR-10, G2 | 0% PWM turns the fan off. The fan also provides a tachometer signal we may want to capture for monitoring. |
| Q-16 | Where is the 24 VAC lighting signal, and is it the lighting control circuit or a transformer that switches with the lights? Could it also power the node? | Occupancy input (FR-07), possibly power | Use it as an isolated occupancy input only; the node has its own always-on supply | FR-07 | Transformer that switches with the lights near the exhaust fan. Node should have it's own always-on supply. |
| Q-18 | If any mains ends up inside the enclosure (on-board supply or relay, D-008), how should it be enclosed? Standard PA12 isn't flame-rated, so it can't serve as the fire enclosure (IEC 62368-1). Options: (a) no mains in the printed enclosure: listed external supply, fan switched by its own plug or control port; (b) flame-retardant PA12 (e.g. EOS PA 2241 FR; vendor availability unchecked); (c) listed polycarbonate box for mains with a printed panel enclosure for the UI. | Enclosure material, cost, and whether the on-board mains option is worth it | (a). Keep the printed enclosure low-voltage; revisit after Q-15 | G2, G3 | Assume (a) unless other constraints force us to reconsider |

## Answered

| ID | Question | Answer | Answered | Applied to |
|----|----------|--------|----------|------------|
| Q-06 | Occupancy signal for sensor sleep: lights, motion, or something else? | The 24 VAC lighting signal near the fan; source details in Q-16 | 2026-10-24 | D-009, FR-07 |
| Q-02 | Does the Lobo DC vent outdoors or recirculate? | Recirculates through an aftermarket pleated filter (from `docs/context.md`) | 2026-10-24 | FR-09, SR-06 |
| Q-17 | Should Auto fail to occupied if the occupancy input fails? | Treat the lighting signal as correct; no failure handling or panel-implies-occupied logic. The display shows occupancy (e.g. "Vacant"). | 2026-10-24 | FR-02, FR-07 |
| Q-13 | OK to extract `hvac_control/components/wifi` into its own repo? Submodule or IDF component manager? | Yes: extracted to `metcalf/esp-iot-core`, submodule at `components/esp-iot-core` | 2026-10-23 | D-007 |
| Q-04 | Which finishes are sprayed (waterborne or solvent)? | No spray guns; occasional aerosol cans only. No vapor-rated fan; electronics out of the airstream. | 2026-10-23 | SR-02 |
| Q-01 | What motor and speed-control type does the exhaust fan have? (survey §2) | AC Infinity CLOUDLINE PRO S6 (EC motor, PWM control port); details in Q-15 | 2026-10-23 | FR-10 |

# Open Questions

Claude batches questions here; Andrew answers inline. Each question has an ID, why it matters, and the default Claude will assume if it's left unanswered. Mark answered questions **[ANSWERED yyyy-mm-dd]** and move them to the bottom.

| ID | Question | Why it matters | Default if unanswered | Blocks |
|----|----------|----------------|-----------------------|--------|
| Q-03 | Exact boost semantics: delay before boosting, boost level, behavior after the DC stops | FR-09 | Boost to max after 2 min of DC run; hold 5 min after the DC stops | FR-09 |
| Q-05 | Any fuel-burning appliances sharing the shop's air? | Backdraft risk (SR-06) | Assume none, and document the assumption | SR-06 |
| Q-07 | Fallback on sensor fault: last manual speed, low speed, or off? | SR-04 | Run at low speed and show a fault | SR-04 |
| Q-08 | PMS5003 or SPS30? | Sensor life vs. cost. Comms differ (SPS30 is I²C/UART with a cleaning command). | Evaluate in architecture; lean SPS30 if the cost difference is under about $40 | G2 |
| Q-09 | VOC sensing in v1 or v2? | Scope | v2 | FR-14 |
| Q-10 | Where do the panel and the ambient indicator live? The fan is at one end of an 11' × 33' shop, with dust made mid-shop. | Wiring, enclosure, and whether the indicator is visible from the saws | Decide in architecture with the layout; lean toward panel at the main work area, indicator visible from the saws | FR-01, FR-15 |
| Q-11 | Budget ceiling for v1? | Sensor choice, enclosure, speed control | No explicit cap; flag anything over $300 | NFR-08 |
| Q-12 | Is an interim `DC_RUNNING` source wanted before the DC controller exists? (e.g. a CT clamp on the DC circuit) | Lets the boost work now | Yes, a CT clamp | IR-01 |
| Q-14 | KiCad isn't installed on this Mac (checked 2026-10-24). Will you install KiCad 9 here, or is phase 3 run on another machine? I need `kicad-cli` for ERC, DRC and Gerber/PCBA export. PCBA vendor preference? | Can't verify the PCB without it | Install KiCad 9; JLCPCB | Phase 3 PCB |
| Q-15 | Does the CLOUDLINE PRO S6's control port give true off at 0% PWM, and what does the fan do when the control signal is lost (unplugged, node dead)? | Decides whether we switch mains at all, and the fail state (SR-04) | Bench-test before G2; assume port-only control with no mains switch | FR-10, G2 |
| Q-16 | Where is the 24 VAC lighting signal, and is it the lighting control circuit or a transformer that switches with the lights? Could it also power the node? | Occupancy input (FR-07), possibly power | Use it as an isolated occupancy input only; the node has its own always-on supply | FR-07 |
| Q-18 | If any mains ends up inside the enclosure (on-board supply or relay, D-008), how should it be enclosed? Standard PA12 isn't flame-rated, so it can't serve as the fire enclosure (IEC 62368-1). Options: (a) no mains in the printed enclosure: listed external supply, fan switched by its own plug or control port; (b) flame-retardant PA12 (e.g. EOS PA 2241 FR; vendor availability unchecked); (c) listed polycarbonate box for mains with a printed panel enclosure for the UI. | Enclosure material, cost, and whether the on-board mains option is worth it | (a). Keep the printed enclosure low-voltage; revisit after Q-15 | G2, G3 |

## Answered

| ID | Question | Why it matters | Default if unanswered | Blocks |
|----|----------|----------------|-----------------------|--------|
| Q-06 | **[ANSWERED 2026-10-24, from D-009 / FR-07]** The 24 VAC lighting signal near the fan; source details in Q-16. Was: occupancy signal for sensor sleep: lights, motion, or something else? | FR-07 | — | FR-07 |
| Q-02 | **[ANSWERED 2026-10-24, from `docs/context.md`]** Recirculates through an aftermarket pleated filter. Was: does the Lobo DC vent outdoors or recirculate? | Recirculating: boost catches fines that get past the filter. Venting: depressurization and backdraft risk, makeup air. | — | FR-09, SR-06 |
| Q-17 | **[ANSWERED 2026-10-24]** Treat the lighting signal as correct; no failure handling or panel-implies-occupied logic. The display shows occupancy (e.g. "Vacant"). Was: should Auto fail to occupied if the input fails? | FR-02, FR-07 | — | FR-07 |
| Q-13 | **[ANSWERED 2026-10-23]** Yes: extracted to `metcalf/esp-iot-core`, submodule at `components/esp-iot-core`. OK to extract `hvac_control/components/wifi` into its own repo (consumed by hvac_control, this project and the DC controller)? Submodule or IDF component manager? | Shared network stack instead of three forks; requires edits to hvac_control | Yes; separate git repo pulled in as an IDF managed component via git URL. Claude drafts the extraction as a branch in hvac_control for your review. | Phase 3 firmware |
| Q-04 | **[ANSWERED 2026-10-23]** No spray guns; occasional aerosol cans only. No vapor-rated fan; electronics out of the airstream (SR-02). Which finishes are sprayed (waterborne or solvent)? | Determines whether the fan must be suitable for flammable vapors (SR-02) | Assume solvent is possible and design conservatively | SR-02 |
| Q-01 | **[ANSWERED 2026-10-23]** AC Infinity CLOUDLINE PRO S6 (EC motor, PWM control port); details in Q-15. What motor and speed-control type does the exhaust fan have? (survey §2) | It decides the whole speed-control design: relay taps vs. 0–10 V vs. triac vs. VFD | None. This blocks. | FR-10, G1 |

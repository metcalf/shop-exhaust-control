# Open Questions

Claude batches questions here; Andrew answers inline. Each question has an ID, why it matters, and the default Claude will assume if it's left unanswered. Mark answered questions **[ANSWERED yyyy-mm-dd]** and move them to the bottom.

| ID | Question | Why it matters | Default if unanswered | Blocks |
|----|----------|----------------|-----------------------|--------|
| Q-01 | What motor and speed-control type does the exhaust fan have? (survey §2) | It decides the whole speed-control design: relay taps vs. 0–10 V vs. triac vs. VFD | None. This blocks. | FR-10, G1 |
| Q-02 | Does the Lobo DC vent outdoors or recirculate? | Recirculating: boost catches fines that get past the filter. Venting: depressurization and backdraft risk, makeup air. | Recirculates (it has an aftermarket pleated filter) | FR-09, SR-06 |
| Q-03 | Exact boost semantics: delay before boosting, boost level, behavior after the DC stops | FR-09 | Boost to max after 2 min of DC run; hold 5 min after the DC stops | FR-09 |
| Q-04 | Which finishes are sprayed (waterborne or solvent)? | Determines whether the fan must be suitable for flammable vapors (SR-02) | Assume solvent is possible and design conservatively | SR-02 |
| Q-05 | Any fuel-burning appliances sharing the shop's air? | Backdraft risk (SR-06) | Assume none, and document the assumption | SR-06 |
| Q-06 | Occupancy signal for sensor sleep: lights, motion, or something else? | FR-07 | A Home Assistant motion or lights entity if one exists; otherwise sleep after N hours of clean readings with the fan off | FR-07 |
| Q-07 | Fallback on sensor fault: last manual speed, low speed, or off? | SR-04 | Run at low speed and show a fault | SR-04 |
| Q-08 | PMS5003 or SPS30? | Sensor life vs. cost. Comms differ (SPS30 is I²C/UART with a cleaning command). | Evaluate in architecture; lean SPS30 if the cost difference is under about $40 | D-004 |
| Q-09 | VOC sensing in v1 or v2? | Scope | v2 | FR-14 |
| Q-10 | Where do the physical controls live: at the fan, at the shop entry, or both? | Wiring and enclosure | At the fan | FR-01 |
| Q-11 | Budget ceiling for v1? | Sensor choice, enclosure, speed control | No explicit cap; flag anything over $300 | NFR-08 |
| Q-12 | Is an interim `DC_RUNNING` source wanted before the DC controller exists? (e.g. a CT clamp on the DC circuit) | Lets the boost work now | Yes, a CT clamp | IR-01 |

## Answered
_(none yet)_

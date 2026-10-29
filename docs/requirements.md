# Requirements — Shop Exhaust Fan Controller

**Status:** APPROVED at G1 (Andrew, 2026-10-25). Changes now need a decision entry and Andrew's OK. Amended 2026-10-26 from Andrew's Q-28 answers: FR-08, FR-18, SR-04, IR-01, AC-05, AC-06, AC-07, AC-20, P-19 (D-024, D-025). Amended 2026-10-28 from Q-29/Q-30 and G2 review S-1: NFR-07, SR-08, SR-09, AC-18 (D-027, D-028); NFR-04 USB-C exception (D-030). Amended 2026-10-28: NFR-09 (placement criteria instead of a fixed distance and direction) and IR-04 location (D-033).

**Conventions**
- IDs: `FR` functional, `NFR` non-functional, `SR` safety, `IR` interface. IDs are never reused; dropped entries stay with a note.
- Priority: **M** must, **S** should, **C** could (v2 candidate).
- Every requirement has at least one acceptance criterion (AC) in §7.
- Numeric thresholds live in the parameter table (§8) as `P-nn`. Each has an initial value with its source; final values are set at commissioning (phase 6) from logged data.

## 1. Purpose and scope
Automatically control the shop exhaust fan (AC Infinity CLOUDLINE PRO S6) based on air quality, occupancy and dust collector activity, with local physical controls, an ambient air-quality indicator, and Home Assistant reporting.

**In scope:** fan speed control (including off) through the S6 control port, PM and VOC sensing, occupancy from the 24 VAC lighting signal, the `DC_RUNNING` link from the DC controller (BLE), panel and ambient indicator, Home Assistant integration, the custom PCB, enclosure and mounting, and the site wiring changes the controller needs (IR-05).

**Out of scope (v1):** DC control (separate project), makeup-air control, Home Assistant control of the fan (FR-16), CO/combustion monitoring, and any life-safety function (SR-05).

## 2. Site summary (from `docs/site-survey.md`)
- Shop 11'2" × 30'9½", ceiling 8'10½" (≈ 3,050 ft³). Doors and window usually closed.
- **Exhaust:** S6 inline above a Broan PM300SS hood (fan removed, stock mesh/baffle filter is the intake) in a wall cabinet at the north (sink) end. 6" duct, ~10', two swept 90°s, gravity damper and wall cap. S6 is rated ≈ 400 CFM free air; the delivered flow here will be lower and is measured at commissioning (from the PM decay rate, FR-05).
- **Makeup air:** one 6" duct with a spring-loaded backdraft damper, at the ceiling at the south (DC/jointer) end, from the garage, which vents to outside. Air crosses the full length of the shop, past the work area, to the fan.
- **Fan power today:** 120 V receptacle in the cabinet, switched by a relay driven by a 24 VAC transformer on the lighting circuit, so the fan loses power when the lights go off. An unswitched receptacle is available in the cabinet (Q-19, IR-05).
- **Lighting/occupancy:** the lights are controlled by a Lutron occupancy sensor with a 15-minute timeout. The 24 VAC transformer switches with them, so "occupied" begins when the lights turn on and ends 15 min after the last motion.
- **Fan control today:** stock single-button AC Infinity controller on the S6's port, cable run down to the pegboard below the cabinet. Port measured by Andrew (Q-15, `docs/interfaces.md` §2): 5 kHz PWM on a line the fan pulls up to +10 V; unplugged = full speed.
- **Main work area:** miter station mid-shop (east wall), table saw opposite; ~18' horizontally from the fan. The controller (panel, indicator and sensors) goes at the **north end**, near the exhaust (D-015).
- **Dust and fume sources:** table saw, miter saw, router table, jointer, planer, band saw (poorly collected); sanding (hand and orbital with vacuum) from minutes to hours; metal grinding/cutting away from the intake; soldering, lathe oil smoke, acetone/alcohol, occasional epoxy and glue; occasional aerosol-can finishing at varying locations.
- **Occupancy pattern:** mostly weekdays 9–5, plus frequent short walk-ins to grab tools.
- **No fuel-burning appliances** anywhere in the building (Q-05). Radiant floor heat; exhaust heat loss is a minor concern.

## 3. Users and interaction model
- **User:** Andrew, the only person working in the shop.
- **Auto** is the resting state; the sensors do most of the work. While **occupied**, the fan holds a low ventilation floor and rises with air quality, VOCs and DC boost. The fan turns **off only when the shop is vacant** and the air-quality criteria are met. Normal running favors low, quiet speeds; high speed only when needed (survey §2).
- A **hold** sets a level for a duration ("max for 20 min", "off for 1 h"), then returns to Auto. Entry on the encoder: press, turn to set level, press, turn to set time, press. Each step defaults to the last value used, so repeating a hold is three presses.
- A **scene** is a named hold plus what happens after it. The set is expected to grow. Initial: **Quiet** (speed capped for a time), **Boost** (max for a time), **Spray** (max, then run-on per FR-08, even if vacant).
- **Panel:** rotary encoder with push, about 4 unlit buttons, a small display (2.8", D-022; D-009). Initial buttons: **Auto** (cancel to Auto), **Quiet**, **Boost**, spare. Scenes without a button start from the encoder menu.
- **Ambient indicator:** a color indicator readable down the length of the shop, showing the air-quality band.

## 4. Functional requirements

| ID | Requirement | Pri | Status | Source |
|----|-------------|-----|--------|--------|
| FR-01 | Local physical controls provide Auto, timed holds at a chosen level, and scenes (§3). A button-assigned action takes one press. A hold that reuses the last level and duration takes at most three presses. Button-to-action assignments are configuration, separate from the control logic. | M | Proposed | D-009 |
| FR-02 | **Auto.** While occupied, the fan runs at no less than the ventilation floor (P-01) from the moment occupancy begins. Quick walk-ins run the floor for the 15-min Lutron timeout, which is acceptable (Andrew, 2026-10-25). Speed rises above the floor as PM rises above the on-threshold (P-03), reaching full speed at P-05, and falls back as PM drops below the off-threshold (P-04). While vacant, the same thresholds decide between running and off, within the vacant limits of FR-19. Speed changes don't chatter on noisy readings; the mechanism (hysteresis, debouncing, ramped or decaying speed) is a design choice tuned against recorded traces. | M | Proposed | context, D-009, survey §1–2 |
| FR-03 | *Dropped 2026-10-24:* folded into FR-02. | — | Dropped | |
| FR-04 | The PM sensor duty cycle adapts to concentration: continuous at low levels, sparse at high levels (P-07), with each sample preceded by at least the settling time (P-06). | M | Proposed | Andrew's design |
| FR-05 | During clear-down, sample scheduling balances PM sensor on-time against fan overrun (run time past the true off-threshold crossing). The balance is set by one tunable parameter (P-23); sampling more densely as readings approach P-04 is the expected way to buy a lower overrun cheaply. *Could:* predict the crossing from a fitted decay rate. The fitted rate is reported (FR-12), since it also measures delivered airflow. | S | Proposed | context |
| FR-06 | A saturated PM reading (at or above the sensor's range limit) is treated as "high" and handled at the slowest sample rate. | M | Proposed | context |
| FR-07 | Occupancy is the 24 VAC lighting-transformer signal near the fan (Q-16): present = occupied. The lights follow a Lutron occupancy sensor with a 15-min timeout, so vacancy is reported 15 min after the last motion; the controller adds no further vacancy delay. It drives Auto (FR-02) and the indicator (FR-15). The PM sensor sleeps when the shop is vacant and the fan is off. The signal is trusted as correct; no failure handling (Q-17). | M | Proposed | Q-06, Q-16, Q-17 |
| FR-08 | The **Spray** scene commands full speed immediately, independent of sensors (SR-03). When its timer ends, the fan stays at full speed until both the minimum run-on (P-09) has elapsed and the VOC and PM criteria are met, then returns to Auto. Pressing Auto, or starting another hold or scene, ends Spray and its run-on at once: an explicit user override (D-024). Runs whether occupied or vacant. The sensor module sleeps from the start of Spray until just before the P-09 minimum run-on ends (overspray would foul its optics, and the fan is at full anyway), then wakes to judge clearance. P-09 is a floor that doesn't rely on the VOC reading. With the sensors at the north end (D-015), most spraying is upstream of them, so the VOC reading should track the vapor leaving; spraying right by the hood is the exception. AC-10 measures it. | M | Proposed | safety discussion, survey §8 |
| FR-09 | **DC boost.** While `DC_RUNNING` is asserted and for P-11 after it de-asserts, Auto runs the fan at no less than P-10. This is a floor: air quality may drive it higher. Holds and scenes override it. | S | Proposed | Q-03 |
| FR-10 | Fan speed, including off, is set through the S6's control port by pulling the speed line low with a 5 kHz PWM (high-time duty = speed; held low = off, held high or open = full; Q-15). The stock controller's levels 1/4/10 are 20/46/100 % duty. No mains switching of the fan by the controller. Speed is continuous in duty between those points (Andrew, bench). | M | Proposed | Q-15 |
| FR-11 | The panel display shows the current state (Auto, or hold/scene with time remaining), occupancy (e.g. "Vacant"), fan speed, PM and VOC readings, DC boost, and active faults and maintenance prompts. | M | Proposed | D-009 |
| FR-12 | Home Assistant (MQTT discovery) exposes PM (all SEN65 mass and number channels), VOC and NOx indices plus their raw signals, temperature and humidity (module readings, enclosure offset tuned at commissioning), fan commanded speed and tach RPM, current state, occupancy, DC input, run hours, PM sensor duty, fitted decay rate, faults (with reason) and maintenance prompts. Readings are published at full sample rate while they change, so HA history can be exported and replayed as host-test traces. Read-only: no control from HA in v1 (FR-16). | S | Proposed | context |
| FR-13 | Faults (FR-18, SR-04), node offline (MQTT last-will), and maintenance prompts are exposed as HA entities suitable for HA-app notifications. Maintenance prompts include a **hood filter cleaning reminder** from accumulated PM exposure at the intake (PM × fan airflow over time), threshold P-14, cleared from the panel. The node only exposes the entities; notification automations live in HA. | S | Proposed | survey §2, §4 |
| FR-14 | **VOC sensing (v1)** from the SEN65's VOC index (MOX, index not concentration; D-012). VOC is only measured while the module is in measurement mode, so it's available whenever PM is sampled continuously (low dust, Spray clearance) and not during sparse sampling or sleep; at those times the fan is already high or the shop is vacant. In Auto, a VOC index above P-12 raises the fan to at least P-13 until it falls below the off-level; it also gates the end of Spray run-on (FR-08). The VOC learned baseline is preserved across module sleep (algorithm-state backup/restore, or a host-side baseline on the raw signal), so a restart in still-dirty air doesn't learn the vapor as "normal". Covers solvents, soldering, glues and finishes; lathe oil smoke is expected to show mostly as PM. | M | Proposed | Q-09, D-012, survey §5 |
| FR-15 | An ambient indicator, located with the panel at the north end, shows the air-quality band (good / elevated / high, P-15) and is readable from anywhere in the shop. It flashes red for an active fault while occupied (Q-07), and is dark while vacant. | S | Proposed | context, Q-07, D-015 |
| FR-16 | *Dropped 2026-10-24:* Home Assistant control of scenes and holds. HA is read-only for v1. | — | Dropped | |
| FR-17 | *Dropped 2026-10-25 (Andrew):* coarse dust sensor. One sensor module, one airflow path (D-012). v2 candidate. | — | Dropped | |
| FR-20 | **Temperature and humidity** come from the SEN65 and are reported to HA as diagnostics. Its temperature compensation is tuned once at commissioning for enclosure self-heating; no separate RH/T sensor. | C | Proposed | D-012, Q-24 |
| FR-19 | **Vacant limits.** While vacant, Auto (including PM, VOC and DC demand) runs the fan no faster than P-22 and for no longer than P-21 after vacancy begins, then turns it off until the next occupancy. If the limit cuts the fan off while PM or VOC is still above its off-threshold, a "clear-down incomplete" notice is raised on the panel and in HA (it points to a fouled sensor or a persistent source). Spray keeps full speed through P-09 even when vacant; any VOC/PM-gated extension past P-09 counts against P-21. Explicit holds aren't limited: they have their own duration. | M | Proposed | Andrew, 2026-10-25 |
| FR-18 | The fan's tach is monitored (square wave, ~30 Hz at level 1, ~75 Hz at level 4, ~144 Hz at level 10; Q-15). A **fan fault** is raised when the fan is commanded on and the tach frequency is zero, or far below the expected frequency for the command, for P-16. A **fan-port fault** is raised when the fan side of the interface loses power for a few seconds: the fan cable is disconnected (the fan then runs at full speed, SR-08) or the fan has lost mains. | S | Proposed | Q-15, Q-28 (e) |

## 5. Non-functional requirements

| ID | Requirement | Pri | Status |
|----|-------------|-----|--------|
| NFR-01 | All control logic runs locally; full function with Wi-Fi, the MQTT broker and Home Assistant unavailable. | M | Proposed |
| NFR-02 | The SEN65 (D-012) has an expected service life ≥ 5 years in this shop given the duty cycling, by analysis from logged duty. Its fan cleaning runs on a schedule. The module is a cleanable, replaceable consumable. | S | Proposed |
| NFR-03 | The sensor module can be removed or cleaned without tools, or with a single tool, in under 5 minutes, without opening the electronics compartment. | S | Proposed |
| NFR-04 | The air-quality sensors (the single SEN65 module, with one inlet/outlet airflow path) are the only components exposed to shop air. They sit in a sensor bay open to the room, thermally separated from the electronics, with no air path into the electronics compartment. The electronics compartment has no ventilation openings, gasketed seams and sealed or gasketed panel controls, and is designed to IP5X intent (not tested), except the external USB-C receptacle's mouth (gasketed around its shell, facing away from the room; D-030, Andrew 2026-10-28). | M | Proposed |
| NFR-05 | The custom PCB is assemblable by a third-party PCBA service, aiming to fit JLCPCB's Economic PCBA tier (or a comparable low-cost tier): SMT on one side, basic/preferred parts wherever possible, through-hole parts left for hand soldering. The tier's current rules are checked in the phase 3 vendor research. Any mains section on it meets SR-01a. | S | Proposed |
| NFR-06 | Firmware is ESP-IDF (C++) on `esp-iot-core` (D-007). The control logic is a hardware-independent module covered by host-run unit tests on simulated and recorded sensor traces. | M | Proposed |
| NFR-07 | After power loss (power-on or brown-out reset), the node returns to Auto without intervention; no hold or scene resumes. After any other reset (software, panic, watchdog, OTA reboot), it resumes the active hold or scene, including Spray and its run-on, with its remaining time (D-027). The fan is not driven on during boot before the logic decides it should be. | M | Proposed |
| NFR-08 | v1 parts and fabrication cost ≤ $300 (hard ceiling, Q-21), aiming well below it ($100 was the original hope, Q-11). Estimate reported at G2, actual at G4. Cost is a tiebreaker in part and vendor choices. | S | Proposed |
| NFR-09 | The sensor module sits near the exhaust end so they sample the air the fan is removing, from every source in the shop (D-015), but outside the hood's direct capture (≈ 2 ft from the hood's edge on the refrigerator side panel, D-033). The inlet has open air in front of it, doesn't face down (Sensirion guidance), and sees no strong directed airflow (< 1 m/s across the module); the outlet is separated from the inlet so the module doesn't re-ingest its own exhaust. Inlet direction is otherwise a design choice. Fan-induced airflow doesn't shift readings materially (AC-17). | M | Proposed |
| NFR-10 | *Dropped 2026-10-25 (Andrew):* runtime-adjustable parameters. v1 compiles `P-nn` values and button assignments in and changes them by OTA (NFR-11), kept in one config header separate from the logic. Revisit if commissioning needs faster iteration. | — | Dropped |
| NFR-11 | Firmware updates over the air via `esp-iot-core`; USB flashing works without exposing any mains (SR-01a). | S | Proposed |

## 6. Safety requirements

| ID | Requirement | Pri | Status |
|----|-------------|-----|--------|
| SR-01 | Every off-the-shelf component carrying line voltage is UL-listed/recognized or equivalent and rated for its load, including motor inrush. v1 default: no mains inside the custom enclosure; the node runs from a listed external supply (Q-18 (a)). | M | Proposed |
| SR-01a | If any mains ends up on the custom PCB, it meets IEC 62368-1 creepage/clearance, with reinforced insulation to all accessible low voltage (including USB), documented in `pcb/SAFETY.md`. | M | Conditional |
| SR-02 | The controller electronics sit outside the exhaust airstream. A vapor-rated fan is not required for occasional aerosol use (Q-04). | M | Proposed |
| SR-03 | The Spray scene delivers full exhaust regardless of any sensor, sensor fault, or network state. | M | Proposed |
| SR-04 | On PM sensor fault (no data, CRC/framing errors, or out-of-range readings for P-18), the fault shows on the panel and indicator (FR-15) and in HA, and Auto drops the demand that comes from the module (PM and VOC). Demand from occupancy (the P-01 floor) and DC boost (FR-09) is unaffected, within the FR-19 vacant limits (Q-28 (c), D-024). So with the shop vacant and no DC boost the fan goes off (Q-20; vacancy already lags 15 min, FR-07). PM and VOC share one module, so a module fault drops both; Spray run-on then uses P-09 alone. | M | Proposed |
| SR-05 | Documentation and the panel make no health claims: air-quality control is a convenience function, not respiratory protection or a life-safety system. | M | Proposed |
| SR-06 | No fuel-burning appliances in the building (Q-05), so backdrafting isn't a design driver. Documented limitations: makeup air comes from the garage, so a combustion source running there (e.g. a vehicle) would be drawn into the shop; and with doors closed the single 6" makeup duct limits flow and depressurizes the shop. Revisit if either changes. | M | Proposed |
| SR-07 | Any mains wiring design (including the IR-05 site change) is reviewed at G3, with points needing licensed-electrician verification flagged. | M | Proposed |
| SR-08 | Fail states. Measured (Q-15): cable unplugged → the fan runs at full speed (fan behavior; can't be changed). Required: with the node **unpowered**, in reset, or booting, the fan is held **off** (Andrew, 2026-10-25). The hold-off must work with no node power, so it's powered from the fan side of the isolation barrier (SR-09) and the node actively releases it to run the fan. A dead node is reported by HA as offline (FR-13). Accepted exception (Andrew, 2026-10-28): when fan mains returns with the node unpowered, a brief burst before the fan-side hold-off is up is OK (D-028). | M | Proposed |
| SR-09 | The S6 control port's isolation from mains is unverified (Andrew didn't scope it for that reason). Until it's shown to be SELV, the node isolates the fan interface (speed and tach) from its own circuits, the panel and USB, rated at least basic insulation for 120 V. This also avoids a ground loop through the fan cable. Evidence so far (Q-22, Q-30): unplugged, port GND is open to L, N and earth (resistance and diode); plugged in, ~65 VAC open-circuit to N/earth, consistent with Y-capacitor coupling from an isolated supply. Q-31 confirmed it: ~0.6 V across 10 kΩ, ≈ 60 µA, well under the 0.5 mA ES1 touch-current limit (D-028). | M | Proposed |

## 7. Interface requirements
Details in `docs/interfaces.md`.

| ID | Requirement | Pri | Status |
|----|-------------|-----|--------|
| IR-01 | Receives `DC_RUNNING` from the DC controller over BLE advertising (D-016) and on an opto-isolated wired input kept as a backup (D-025); either one asserts it. No BLE advertisement for P-24 means the BLE path reads "DC not running". No MQTT path. No interim source before the DC controller exists (Q-12). | S | Proposed |
| IR-02 | The `DC_RUNNING` message (`docs/interfaces.md` §1) is reusable unchanged by the DC controller. Its format has room for more DC status and a reverse direction, so that a shared panel (deferred to the DC project) can be added without breaking it. | M | Proposed |
| IR-03 | HA entities use the `shop_exhaust_` prefix and the naming in `docs/interfaces.md`. | S | Proposed |
| IR-04 | Wiring between the controller and the fan cabinet (fan port, 24 VAC occupancy, low-voltage supply) is low-voltage only and works over at least 10 ft of cable (refrigerator side panel beside the hood, D-033). | M | Proposed |
| IR-05 | **Site change:** the fan plugs into the existing unswitched receptacle in the cabinet, and the node's listed supply has always-on 120 V, so the fan can clear down after the lights go off. The 24 VAC transformer stays as the occupancy source. No mains rewiring (D-013, Q-19). | M | Proposed |

## 8. Parameters
Initial values let the logic be host-tested now; commissioning replaces them. Compiled in and changed by OTA (NFR-10 dropped).

| ID | Parameter | Initial | Source of initial value |
|----|-----------|---------|-------------------------|
| P-01 | Occupied ventilation floor | Lowest speed that runs steadily and Andrew finds quiet; placeholder 20 % | Survey §2 (prefer low speed); set at commissioning |
| P-02 | *(dropped 2026-10-25: no walk-in delay; the floor starts with occupancy)* | | |
| P-03 | PM on-threshold | PM2.5 35 µg/m³ | US EPA 24-h PM2.5 standard as a reference point; readings are relative (context) |
| P-04 | PM off-threshold | PM2.5 12 µg/m³ | Clean indoor 5–20 µg/m³ (context) |
| P-05 | PM level for full speed | PM2.5 150 µg/m³ | Placeholder; tune from traces |
| P-06 | PM settling before a valid sample | 30 s | SEN6x start-up is 30 s typ (datasheet Table 2) |
| P-07 | Sparse sampling at high PM | 30 s sample every 5–10 min | Andrew's design (context) |
| P-08 | *(reserved)* | | |
| P-09 | Spray minimum run-on at full speed | 20 min | ~3 air changes of the ~1,500 ft³ between miter station and fan at an assumed 200–400 CFM delivered |
| P-10 | DC boost floor | 60 % | Q-03 |
| P-11 | DC boost hold after `DC_RUNNING` drops | 5 min | Q-03 |
| P-12 | VOC index on / off | 150 / 120 | VOC index: 100 = learned baseline; placeholder |
| P-13 | VOC demand speed | 60 % | Placeholder; same as DC boost |
| P-14 | Hood filter cleaning reminder | Set after 1–2 months of logged exposure | Survey §2 (no cleaning schedule today) |
| P-15 | Indicator bands (PM2.5) | good < P-03 ≤ elevated < P-05 ≤ high | Follows the control thresholds |
| P-16 | Fan fault debounce | 30 s | Placeholder |
| P-17 | Cost ceiling | $300 | Q-21 |
| P-18 | PM sensor fault debounce | 60 s | Placeholder |
| P-19 | *(dropped 2026-10-26: a sensor fault only removes PM/VOC demand; the occupied floor P-01 remains, Q-28 (c))* | | |
| P-20 | *(dropped 2026-10-25: vacant → off on PM sensor fault, Q-20)* | | |
| P-21 | Max Auto runtime while vacant | 2 h after vacancy | About 2× the 35–70 min full-shop clear-down estimate (§10); vacancy already lags last motion by 15 min |
| P-24 | `DC_RUNNING` link timeout | 10 s | ≥ 10 missed advertisements at the ~0.5–1 s interval (`interfaces.md` §1) |
| P-25 | *(dropped with FR-17)* | | |
| P-26 | *(dropped with FR-17)* | | |
| P-23 | Clear-down overrun target (sets the sensor-life vs. overrun balance) | 5 min | Placeholder: small next to a 35–70 min clear-down; pick from the AC-03 trade-off curve |
| P-22 | Max Auto speed while vacant | 60 % | Placeholder: quieter for the house overnight while still clearing; tune from FR-05 decay data |

## 9. Acceptance criteria
Format: test method, then pass condition. "Sim" = host unit test of the control logic on synthetic or recorded traces. "Bench" = assembled node off-site. "In-situ" = installed in the shop.

| AC | Verifies | Method | Pass condition |
|----|----------|--------|----------------|
| AC-01 | FR-02 | Sim: occupancy and PM step, ramp and noisy traces | Floor starts within 2 s of occupancy; speed follows P-03…P-05; off only when vacant and PM < P-04; ≤ 1 speed-direction reversal per 2 min on a noisy-but-flat trace |
| AC-02 | FR-04, FR-06 | Sim: constant traces at low, high and saturated PM | Continuous sampling below P-03; ≤ 10 % duty at saturation; no sample used before P-06 of settling |
| AC-03 | FR-05 | Sim: exponential decay traces at two decay rates, sweeping P-23 | Report sensor on-time and fan overrun for each run (the trade-off curve, used to pick P-23 at commissioning); at the initial P-23, mean overrun ≤ P-23; fitted decay rate within 20 % of the trace's |
| AC-04 | FR-07 | Sim + bench (24 VAC applied/removed) | Occupancy follows the input within 2 s; PM sensor asleep when vacant and fan off |
| AC-05 | FR-08, SR-03 | Sim; bench and in-situ with Wi-Fi off and PM/VOC sensors unplugged | Full speed within 2 s of starting Spray; after the timer ends, run-on ≥ P-09 and until PM/VOC criteria met (with sensors present); an Auto press or a new hold/scene ends Spray or its run-on at once |
| AC-06 | FR-09, IR-01 | Sim; bench with the wired `DC_RUNNING` input energized and released (`docs/interfaces.md` §2.3) | Speed ≥ P-10 within 2 s of assertion and for P-11 after release; PM demand above P-10 still wins |
| AC-07 | FR-10, FR-18 | Bench with the S6 | Commanded 0 % stops the fan; each commanded step changes tach RPM monotonically; tach or fan-port fault raised within P-16 + 5 s with the fan's mains unplugged; fan-port fault raised with the fan cable disconnected |
| AC-08 | FR-01, FR-11 | Bench: scripted walk-through | Each button action in 1 press; repeat-last hold in ≤ 3 presses; display shows all FR-11 fields; reassigning a button needs no logic change |
| AC-09 | FR-12, FR-13, IR-03 | Bench with HA | All listed entities appear via discovery with the right names; LWT marks the node unavailable within 60 s of power-off; a recorded HA history exports and replays in the host tests |
| AC-10 | FR-14, FR-08 | Sim; in-situ IPA/acetone wipe (or a short aerosol burst) at three spots: near the sensor, mid-way to the fan, and at the fan end, with the fan at full | Fan rises to ≥ P-13 on index > P-12 and returns after it falls below the off-level. Record peak index and time-to-clear at each spot; if the fan-end release barely registers, P-09 alone governs Spray run-on for downstream spraying |
| AC-11 | FR-15 | In-situ, lights on, daytime | Andrew can name the band color from both ends of the shop; fault flash visible; indicator dark when vacant |
| AC-12 | NFR-01 | In-situ with the AP or broker down for ≥ 1 h | Auto, holds, scenes, display and indicator all work; node reconnects unaided |
| AC-13 | NFR-02 | Analysis after 1 month of logged duty | Projected SEN65 operating hours/year × 5 years within its rated life |
| AC-14 | NFR-03 | In-situ, timed | Sensor module out and back in < 5 min with ≤ 1 tool, electronics compartment closed |
| AC-15 | NFR-04, SR-02 | Design review at G2/G3 + inspection after 1 month | No ventilation openings in the electronics compartment; no visible dust inside |
| AC-16 | NFR-06 | CI/host test run | Control-logic tests pass on the host with no ESP-IDF headers; output committed |
| AC-17 | NFR-09 | In-situ steady-dust test (context: validation test) | Mean PM shifts < 20 % between fan off and each fan speed, holding the source steady; result logged |
| AC-18 | NFR-07, SR-08 | Bench with the S6: power-cycle, forced panic, watchdog reset and OTA reboot during a hold and during Spray; scope the speed line (fan side) through reset; remove node power entirely; with the node unpowered, cycle fan mains and record what the fan does | Power-cycle returns to Auto; software/panic/watchdog/OTA resets resume the hold or Spray with its remaining time (± boot time); speed line held low (fan off) from node power-up through boot and with the node unpowered; fan power-up behavior recorded (a brief burst is accepted); duty at the fan within ±2 % of command across 5–100 % |
| AC-26 | SR-09 | G2/G3 design review; bench hipot or insulation-resistance check of the isolation barrier if no isolated part is certified | Fan-side circuits have no galvanic connection to node ground, panel or USB; barrier part ratings documented |
| AC-19 | NFR-11 | Bench | OTA update succeeds and the node comes back in Auto; a changed P-nn value takes effect after OTA |
| AC-27 | FR-19 | Sim: vacant with PM pinned high; vacant Spray with VOC pinned high; vacant hold | Speed ≤ P-22 while vacant in Auto; off at P-21 with "clear-down incomplete" raised; Spray full through P-09 then off at P-21; hold runs its full duration; limits reset on next occupancy |
| AC-28 | FR-14 | Sim; bench with a real SEN65 | After a sleep/wake cycle in elevated VOC, the index still reads elevated (baseline preserved); VOC demand is ignored while the module isn't measuring |
| AC-20 | SR-04 | Sim; bench by unplugging the PM sensor | Fault shown within P-18 + 5 s; PM/VOC demand removed; occupied → P-01 floor, vacant → off; DC boost still applied in both (within FR-19) |
| AC-21 | SR-01, SR-01a, SR-07 | G3 review | Listed parts for all mains; `pcb/SAFETY.md` complete if any on-board mains; electrician checkpoints flagged |
| AC-22 | IR-01, IR-02 | Bench with a test DC-side node; in-situ once the DC controller exists | Boost asserted ≤ 3 s after the DC side asserts; released P-24 after its advertisements stop; RSSI margin logged from the DC position with the DC motor running; Wi-Fi, MQTT and OTA work with scanning active; no false assertion from other BLE devices |
| AC-23 | IR-04, IR-05 | In-situ | Fan runs with lights off; all controller–cabinet signals work over the installed cable |
| AC-24 | NFR-05, NFR-08 | G2 estimate, G4 BOM and PCBA quote | Total ≤ P-17; board quotes in the economic tier, or the reason it can't is recorded |
| AC-25 | SR-05, SR-06 | Doc review at G1 and G6 | Limitations and non-life-safety statement present in README and panel help/about screen |

## 10. Assumptions and notes
- **Sensors:** one Sensirion SEN65 module: PM (mass and number), VOC and NOx indices, RH/T (D-012). One airflow path to design for. Coarse dust and a separate RH/T sensor were considered and dropped.
- **Sensor placement (D-015):** air enters at the south end and leaves at the north, so a mid-shop sensor is blind to the lathe, the north bench and spraying north of it. Near the exhaust, the sensor sees everything the fan removes, and it's the last place to clear, which makes the off decision conservative. The cost is slower detection of upstream sources; the DC-collected machines are covered by DC boost (FR-09) and by the DC's recirculation mixing the room. Sanding with the vacuum is the main uncovered case, with a lag of minutes. Mounted on the refrigerator side panel beside the hood (D-033): ~18" laterally from the hood's edge, near the panel's front edge, center ~60" up (hood intake ~66"), so the inlet is ≈ 2 ft from the hood (NFR-09), within 10 ft of cable of the fan cabinet. The bench below is the kids' workbench (glue, markers), which will show as local VOC/PM. AC-17 checks it.
- **Clear-down time:** fully mixed, dropping from 1,000 to 12 µg/m³ takes ln(83) ≈ 4.4 air changes, roughly 35–70 min for the whole shop at 200–400 CFM delivered. The real number comes from FR-05.
- Open questions are in `docs/open-questions.md`.

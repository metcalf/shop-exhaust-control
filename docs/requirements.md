# Requirements — Shop Exhaust Fan Controller

**Status:** DRAFT, phase 1 not started. Entries marked `Proposed` come from the kickoff conversation (`docs/context.md`) and need confirmation against the site survey. Claude completes this in phase 1, and Andrew signs off at **G1**.

**Conventions**
- IDs: `FR` functional, `NFR` non-functional, `SR` safety, `IR` interface.
- Priority: **M** must, **S** should, **C** could (v2 candidate).
- Every requirement gets at least one acceptance criterion (AC) in section 7.
- Thresholds shown as `‹TBD›` are set from the survey or commissioning data, never guessed.

## 1. Purpose and scope
Automatically control the shop exhaust fan based on air quality and dust collector activity, with local physical controls and Home Assistant reporting.

**In scope:** fan on/off and speed control, PM sensing, local controls and indicators, the DC-running input, Home Assistant integration, enclosure and mounting.

**Out of scope (v1):** DC control (separate project), makeup-air control, life-safety functions, CO and combustion monitoring.

## 2. Users and operating modes
- **User:** Andrew, the only person working in the shop.
- **Modes (proposed):**
  - **Off:** fan off, sensing optional.
  - **Auto:** sensor- and DC-driven.
  - **On:** manual, fixed speed.
  - **Spray:** forced full exhaust, with sensor-based run-on after leaving spray mode.

## 3. Functional requirements

| ID | Requirement | Pri | Status | Source |
|----|-------------|-----|--------|--------|
| FR-01 | A local physical mode selector provides at least Off / Auto / On / Spray. | M | Proposed | context: analog-first UI |
| FR-02 | In Auto, the fan turns on when PM exceeds an on-threshold ‹TBD› and turns off below an off-threshold ‹TBD›, with hysteresis. | M | Proposed | context |
| FR-03 | Turn-off requires N ‹TBD› consecutive below-threshold samples. | M | Proposed | context |
| FR-04 | The PM sensor duty cycle adapts to concentration: continuous at low levels, sparse at high levels, with each sample preceded by ≥30 s of sensor fan settling. | M | Proposed | Andrew's design |
| FR-05 | During clear-down, the sample interval shortens as readings fall. *Could:* predict the threshold crossing from a fitted decay rate. | S | Proposed | context |
| FR-06 | A pegged (saturated) PM reading is treated as "high" and handled as the slowest sample rate. | M | Proposed | context |
| FR-07 | The sensor sleeps when the shop is unoccupied, per occupancy signal ‹TBD›. | S | Proposed | laser life |
| FR-08 | Spray mode commands full exhaust immediately, independent of sensors. On exit, the fan runs until air-quality criteria are met or a minimum run-on ‹TBD› elapses, whichever is later. | M | Proposed | safety discussion |
| FR-09 | When the DC-running input has been active ‹TBD› minutes, Auto mode raises fan speed to a boost level ‹TBD›. Behavior after the DC stops ‹TBD›. | S | Proposed | Andrew's DC feature list |
| FR-10 | Fan speed is controllable in at least ‹TBD› steps, or continuously, depending on the fan's motor and speed-control type (site survey §2). | S | Proposed | |
| FR-11 | Local indicators show mode, fan state and fault. | M | Proposed | analog-first UI |
| FR-12 | Home Assistant exposes PM readings, fan state and speed, mode, DC-input state, run hours and faults. | S | Proposed | |
| FR-13 | Home Assistant can send alerts for faults and maintenance (e.g. sensor fault, mesh cleaning reminder). | C | Proposed | |
| FR-14 | Optional VOC sensing (SGP41-class) extends spray-mode run-on. | C | Proposed | v2 candidate |

## 4. Non-functional requirements

| ID | Requirement | Pri | Status |
|----|-------------|-----|--------|
| NFR-01 | All control logic runs locally; full function with Wi-Fi and Home Assistant unavailable. | M | Proposed |
| NFR-02 | PM sensor service life of at least ‹TBD› years in this shop, given the duty cycling. The sensor is treated as a cleanable or replaceable consumable. | S | Proposed |
| NFR-03 | The sensor can be removed or cleaned without tools, or with a single tool, in under 5 minutes. | S | Proposed |
| NFR-04 | Enclosure dust ingress protection suitable for a woodshop (IP5X or better for electronics). | M | Proposed |
| NFR-05 | v1 is built from off-the-shelf modules and listed components; no custom PCB. | S | Proposed |
| NFR-06 | Firmware is ESPHome-based, with the control logic covered by automated tests on simulated sensor traces. | M | Proposed |
| NFR-07 | Recovers to the selected mode after power loss without manual intervention. | M | Proposed |
| NFR-08 | Budget ≤ ‹TBD›. | S | Open |

## 5. Safety requirements

| ID | Requirement | Pri | Status |
|----|-------------|-----|--------|
| SR-01 | Every component carrying line voltage is UL-listed or equivalent and rated for the fan's load, including motor inrush. | M | Proposed |
| SR-02 | If solvent-based finishes are sprayed (survey §5), the fan and anything in the exhaust airstream must be suitable for flammable vapors. The controller electronics sit outside the airstream. | M | Conditional |
| SR-03 | Spray mode doesn't depend on any sensor, firmware decision or network to deliver full exhaust. | M | Proposed |
| SR-04 | On sensor fault, the system indicates the fault locally and falls back to ‹TBD: last manual speed / run at low speed / off›. | M | Open |
| SR-05 | Air-quality control is documented as a convenience function, not a respiratory-protection or life-safety system. | M | Proposed |
| SR-06 | If the shop contains fuel-burning appliances (survey §1), exhaust operation must not cause backdrafting. Makeup air is addressed, or the limitation is documented. | M | Conditional |
| SR-07 | Mains wiring design is reviewed at gate G3. Points that need electrician verification are flagged. | M | Proposed |

## 6. Interface requirements
See `docs/interfaces.md` for the details.

| ID | Requirement | Pri | Status |
|----|-------------|-----|--------|
| IR-01 | Accepts a DC-running input, with the electrical form ‹TBD: dry contact preferred› and a path through Home Assistant as an alternative. | S | Proposed |
| IR-02 | The DC-running signal definition is reusable unchanged by the future DC controller. | M | Proposed |
| IR-03 | Home Assistant entities follow the naming in `docs/interfaces.md`. | S | Proposed |

## 7. Acceptance criteria
Filled in during phase 1. Format: `AC-nn → requirement ID(s) — test method — pass condition`.

| AC | Verifies | Method | Pass condition |
|----|----------|--------|----------------|
| AC-01 | FR-02, FR-03 | Simulation with recorded or synthetic PM traces | Fan state transitions match the expected sequence; no chatter |
| AC-02 | FR-04, FR-05, FR-06 | Simulation | Duty cycle within ‹TBD› of target at each concentration band; no sample used before settling |
| AC-03 | FR-08, SR-03 | Bench and in-situ, network disconnected and sensor unplugged | Full exhaust within ‹TBD› s of selecting Spray |
| AC-04 | NFR-01 | In-situ with Wi-Fi disabled | All modes function |
| AC-05 | Mounting (context: validation test) | Steady-dust test, fan off vs. on at each speed | Reading shift < ‹TBD›% |
| … | | | |

## 8. Assumptions and open items
- Open questions live in `docs/open-questions.md`. Requirements depending on them stay `Open` or carry ‹TBD›.
- **Working assumption:** the PM sensor is a PMS5003. Re-evaluate against the SPS30 during architecture (D-004).

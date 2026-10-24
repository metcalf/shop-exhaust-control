# Requirements — Shop Exhaust Fan Controller

**Status:** DRAFT, phase 1 not started. Entries marked `Proposed` come from the kickoff conversation (`docs/context.md`) and need confirmation against the site survey. Claude completes this in phase 1, and Andrew signs off at **G1**.

**Conventions**
- IDs: `FR` functional, `NFR` non-functional, `SR` safety, `IR` interface.
- Priority: **M** must, **S** should, **C** could (v2 candidate).
- Every requirement gets at least one acceptance criterion (AC) in section 7.
- Thresholds shown as `‹TBD›` are set from the survey or commissioning data, never guessed.

## 1. Purpose and scope
Automatically control the shop exhaust fan based on air quality and dust collector activity, with local physical controls and Home Assistant reporting.

**In scope:** fan speed control (including off), PM and VOC sensing, an ambient air-quality indicator, local controls and indicators, the DC-running input, Home Assistant integration, enclosure and mounting.

**Out of scope (v1):** DC control (separate project), makeup-air control, life-safety functions, CO and combustion monitoring.

## 2. Users and interaction model
- **User:** Andrew, the only person working in the shop.
- **Interaction model (proposed, not settled):** no fixed mode list.
  - **Auto** is the resting state, and the sensors should do most of the work. While the shop is **occupied**, the fan never drops below a low ventilation floor ‹TBD›; speed rises above it with air quality and DC boost. The fan turns **off only when the shop is vacant** and the air-quality criteria are met.
  - A **hold** sets a level for a duration ("max for 20 min", "off for 1 h"), then returns to Auto. Entry on the encoder: press, turn to set level, press, turn to set time, press. Each step defaults to the last value used, so repeating a hold is three quick presses.
  - A **scene** is a named hold plus what happens after it. The set is expected to grow with use. Initial examples: **Quiet** (speed capped for a time), **Boost** (max for a time), **Spray** (max, then a decaying run-on, possibly via Auto, even if vacant).
  - **Panel:** a rotary encoder with push, about 4 buttons and a small display (about 2"). Initial button assignment: **Auto** (cancel to Auto), **Quiet**, **Boost**, and one spare. Assignments are expected to change with use. Scenes without a button are started from the encoder menu. The display shows state, readings and time remaining, and hosts hold and scene setup.
  - **Ambient indicator:** a color indicator readable down the length of the shop (e.g. an addressable LED bar, bright light washing on the surrounding wall). Color shows the air-quality band.

## 3. Functional requirements

| ID | Requirement | Pri | Status | Source |
|----|-------------|-----|--------|--------|
| FR-01 | Local physical controls provide Auto, timed holds at a chosen level, and scenes (§2). A button-assigned action takes one press. A hold that reuses the last level and duration takes at most three presses. Button-to-action assignments are configuration, separate from the control logic. | M | Proposed | context: physical controls |
| FR-02 | In Auto, while occupied, the fan runs at no less than a ventilation floor ‹TBD› and rises above it when PM exceeds an on-threshold ‹TBD›, returning to the floor below an off-threshold ‹TBD›. While vacant, the same thresholds decide between running and off. Speed changes don't chatter on noisy readings; the mechanism (hysteresis, sample debouncing, ramped or decaying speed) is a design choice tuned against recorded traces. | M | Proposed | context |
| FR-03 | *Dropped 2026-10-24:* folded into FR-02 as a no-chatter outcome; debouncing is a design choice, not a requirement. | — | Dropped | |
| FR-04 | The PM sensor duty cycle adapts to concentration: continuous at low levels, sparse at high levels, with each sample preceded by ≥30 s of sensor fan settling. | M | Proposed | Andrew's design |
| FR-05 | During clear-down, the sample interval shortens as readings fall. *Could:* predict the threshold crossing from a fitted decay rate. | S | Proposed | context |
| FR-06 | A pegged (saturated) PM reading is treated as "high" and handled as the slowest sample rate. | M | Proposed | context |
| FR-07 | An occupancy input (the 24 VAC lighting signal near the fan, to be confirmed in Q-16) drives Auto (FR-02). The PM sensor sleeps once the shop is vacant and the fan is off. The signal is assumed reliable; no failure handling (Q-17). | M | Proposed | laser life |
| FR-08 | The Spray scene commands full exhaust immediately, independent of sensors. When it ends, the fan runs until air-quality criteria are met or a minimum run-on ‹TBD› elapses, whichever is later. | M | Proposed | safety discussion |
| FR-09 | When the DC-running input has been active ‹TBD› minutes, Auto raises fan speed to a boost level ‹TBD›. Behavior after the DC stops ‹TBD›. | S | Proposed | Andrew's DC feature list |
| FR-10 | Fan speed, including off, is set through the CLOUDLINE PRO S6's EC control port (PWM, ‹TBD› steps or continuous). Mains switching only if the port can't reach true off or a safe fail state (Q-15). | S | Proposed | |
| FR-11 | The panel shows the current state (Auto, hold or scene, with time remaining), occupancy (e.g. "Vacant"), fan speed, air-quality readings and faults. | M | Proposed | context: physical controls |
| FR-12 | Home Assistant exposes air-quality readings, fan state and speed, current state (Auto/hold/scene), DC-input state, run hours and faults. | S | Proposed | |
| FR-13 | Home Assistant can send alerts for faults and maintenance (e.g. sensor fault, mesh cleaning reminder). | C | Proposed | |
| FR-14 | VOC sensing (SGP41-class) extends run-on after the Spray scene. | S | Proposed | context: VOC section |
| FR-15 | An ambient air-quality indicator is readable from anywhere in the shop (11' × 33'). | S | Proposed | context: goal |
| FR-16 | *Dropped 2026-10-24:* Home Assistant control of scenes and holds. Revisit later; HA stays read-only for v1. | — | Dropped | |
| FR-17 | If a continuously running coarse dust sensor is fitted (Q-08), the PM sensor is suspended while the coarse reading is high and resumes once it falls to near zero ‹TBD›; Auto treats a high coarse reading as "high". | C | Proposed | Andrew, 2026-10-24 |

## 4. Non-functional requirements

| ID | Requirement | Pri | Status |
|----|-------------|-----|--------|
| NFR-01 | All control logic runs locally; full function with Wi-Fi and Home Assistant unavailable. | M | Proposed |
| NFR-02 | PM sensor service life of at least ‹TBD› years in this shop, given the duty cycling. The sensor is treated as a cleanable or replaceable consumable. | S | Proposed |
| NFR-03 | The sensor can be removed or cleaned without tools, or with a single tool, in under 5 minutes. | S | Proposed |
| NFR-04 | Enclosure dust ingress protection suitable for a woodshop (IP5X or better for electronics). | M | Proposed |
| NFR-05 | The custom PCB is assemblable by a third-party PCBA service. Any mains section on it meets documented creepage/clearance and isolation rules (`pcb/SAFETY.md`). | S | Proposed |
| NFR-06 | Firmware is ESP-IDF (C++). The control logic is a hardware-independent module covered by host-run unit tests on simulated sensor traces. | M | Proposed |
| NFR-07 | After power loss, returns to Auto without manual intervention; an active hold or scene is not resumed. | M | Proposed |
| NFR-08 | Budget ≤ ‹TBD›. | S | Open |

## 5. Safety requirements

| ID | Requirement | Pri | Status |
|----|-------------|-----|--------|
| SR-01 | Every off-the-shelf component carrying line voltage is UL-listed/recognized or equivalent and rated for the fan's load, including motor inrush. Mains on the custom PCB meets SR-01a. | M | Proposed |
| SR-01a | Mains sections of the custom PCB meet IEC 62368-1 creepage/clearance, with reinforced insulation between mains and any accessible low-voltage circuit; the rules followed and their verification are documented in `pcb/SAFETY.md`. | M | Proposed |
| SR-02 | The controller electronics sit outside the exhaust airstream (aerosol propellant and overspray). A vapor-rated fan is not required for occasional aerosol use (Q-04). | S | Proposed |
| SR-03 | The Spray scene doesn't depend on any sensor or network to deliver full exhaust. | M | Proposed |
| SR-04 | On sensor fault, the system indicates the fault locally and falls back to ‹TBD: last manual speed / run at low speed / off›. | M | Open |
| SR-05 | Air-quality control is documented as a convenience function, not a respiratory-protection or life-safety system. | M | Proposed |
| SR-06 | If the shop contains fuel-burning appliances (survey §1), exhaust operation must not cause backdrafting. Makeup air is addressed, or the limitation is documented. | M | Conditional |
| SR-07 | Any mains wiring design is reviewed at gate G3. Points that need electrician verification are flagged. | M | Proposed |

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
| AC-01 | FR-02 | Simulation with recorded or synthetic PM traces | Fan state transitions match the expected sequence; no chatter |
| AC-02 | FR-04, FR-05, FR-06 | Simulation | Duty cycle within ‹TBD› of target at each concentration band; no sample used before settling |
| AC-03 | FR-08, SR-03 | Bench and in-situ, network disconnected and sensor unplugged | Full exhaust within ‹TBD› s of starting Spray |
| AC-04 | NFR-01 | In-situ with Wi-Fi disabled | Auto, holds and scenes all function |
| AC-05 | Mounting (context: validation test) | Steady-dust test, fan off vs. on at each speed | Reading shift < ‹TBD›% |
| … | | | |

## 8. Assumptions and open items
- Open questions live in `docs/open-questions.md`. Requirements depending on them stay `Open` or carry ‹TBD›.
- **Working assumption:** the PM sensor is a PMS5003. Re-evaluate against the SPS30, and whether to add a continuously running coarse sensor, during architecture (Q-08).

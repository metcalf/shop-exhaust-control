# PCB safety and isolation record

> **Route B (D-054, 2026-11-10): the carrier PCB (`pcb/carrier/`) replaces the custom main board.** Same rules, fewer domains. The carrier has two field domains, **Fan** (GND_F, +10V_F, FAN_SPD, FAN_TACH_F, Q_FAN_G, TACH_LED_A) and **OCC** (OCC_*). The DC domain and the presence opto are gone. Barrier crossings on the carrier are exactly three LTV-817S-TA1-C (UL 1577 5 kVrms, E113898): U1 node LED → fan output (PWM, pulls Q1's gate to GND_F), U2 fan LED → node (tach), U3 OCC LED → node. `pcb/carrier/gen/check.py` asserts it (`pcb/carrier/reports/netlist-check.txt`). Spacing rules below carry over unchanged; the carrier `.kicad_dru` and the layout record go here before G3. The original board's record follows for reference.


**No mains on the board or in the enclosure** (D-018, SR-01). The only connection to mains is the listed 5 V USB-C adapter (LPS), which plugs into the cabinet receptacle. IEC 62368-1 reinforced-insulation rules for a mains section don't apply. This file records the isolation barriers between the low-voltage domains (G2 review S-4) and how each is checked. A licensed electrician should verify the receptacle and the 24 VAC hookup at install (G3), not this board.

This controller is a convenience control, not a life-safety device. Air-quality sensing here does not, on its own, protect anyone's health.

## Domains

| Domain | Nets | Source | Class |
|--------|------|--------|-------|
| Node | GND, +5V, +3V3, all GPIO nets | USB-C adapter (LPS, SELV) | SELV; touchable via USB-C and the panel |
| Fan | GND_F, +10V_F, FAN_SPD, FAN_TACH_F, Q_FAN_G, TACH_LED_A, PRES_LED_A | Fan's control port; SELV on measured evidence (Q-22, Q-30, Q-31, D-028); ~65 VAC capacitive float on GND_F | SELV, separate ground |
| OCC | OCC_* | Lighting transformer's Class 2 secondary, 24 VAC | SELV (Class 2) |
| DC | DCI_* | DC controller's contact or output, 12–24 V AC/DC | SELV |

## Barrier crossings (all of them)
`pcb/gen/check.py` asserts that only these parts touch two domains, and that each touches exactly two:

| Part | Crosses | Isolation rating |
|------|---------|------------------|
| U4 H11L1S-TA1-L | Node (LED) → Fan (output, powered from +10V_F) | UL 1577 5 kVrms |
| U5 LTV-817S-TA1-C | Fan (LED) → Node (tach output) | UL 1577 5 kVrms (E113898) |
| U6 LTV-817S-TA1-C | Fan (LED) → Node (presence output) | UL 1577 5 kVrms (E113898) |
| U7 LTV-817S-TA1-C | OCC (LED) → Node | UL 1577 5 kVrms (E113898) |
| U8 LTV-817S-TA1-C | DC (LED) → Node | UL 1577 5 kVrms (E113898) |

Nothing else crosses: no Y capacitors, no shared pours, no resistors, no shield or mounting-hole connections. Mounting holes are non-plated and unconnected, with plastic or nylon fasteners where they sit near a barrier.

## Spacing rules (enforced in layout DRC)

| Between | Creepage / clearance | Basis |
|---------|----------------------|-------|
| Node ↔ Fan | ≥ 3.0 mm | Basic insulation for ≤ 150 V working voltage, pollution degree 2 (IEC 62368-1 tables). Kept even though the port is SELV, because it also blocks the fan cable's ground loop and the ~65 VAC float (D-028) |
| Node ↔ OCC, Node ↔ DC | ≥ 3.0 mm | Same rule, for uniformity: field wiring, unknown grounding |
| Fan ↔ OCC ↔ DC | ≥ 1.5 mm (functional) | All SELV. Adjacent terminal blocks are allowed: separate blocks, at least one empty pitch or a slot between domains where the layout allows |

Each domain gets its own copper island, with no pour across a barrier. Under each opto, add a routed slot in the barrier gap if layout needs extra creepage. Layout records how each spacing was checked (DRC rule plus a measured screenshot) here before G3.

**How it's enforced (layout, 2026-11-09):** domains are netclasses (`FAN`, `OCC`, `DCI`, node = the rest) in `pcb/exhaust.kicad_pro`; `pcb/exhaust.kicad_dru` sets clearance **and** creepage constraints at the values above; keepout rule areas (no tracks, vias or pour) cover the barrier bands (`pcb/layout/place.py`). Placed board, before routing: 0 violations; smallest node↔field distance 6.16 mm (U4 row gap), smallest field↔field 2.18 mm. Mutation check: raising the rules makes exactly these rules fire (`pcb/LAYOUT.md` §4). Still to do before G3: DRC on the chosen routed board, and the measured screenshot.

## Status
- Schematic: domains and crossings asserted by `pcb/gen/check.py` (`pcb/reports/netlist-check.txt`).
- Layout: placement locked with the barrier rules and keepouts in place; DRC clean at placement (`pcb/LAYOUT.md`). Routed candidates pending.

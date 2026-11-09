# PCB safety and isolation record

**No mains on the board or in the enclosure** (D-018, SR-01). The only connection to mains is the listed 5 V USB-C adapter (LPS), which plugs into the cabinet receptacle. IEC 62368-1 reinforced-insulation rules for a mains section don't apply. This file records the isolation barriers between the low-voltage domains (G2 review S-4) and how each is checked. A licensed electrician should verify the receptacle and the 24 VAC hookup at install (G3), not this board.

This controller is a convenience control, not a life-safety device. Air-quality sensing here does not, on its own, protect anyone's health.

## Domains

| Domain | Nets | Source | Class |
|--------|------|--------|-------|
| Node | GND, +5V, +3V3, +3V3_SEN, all GPIO nets | USB-C adapter (LPS, SELV) | SELV; touchable via USB-C and the panel |
| Fan | GND_F, +10V_F, FAN_SPD, FAN_TACH_F, Q_FAN_G, TACH_LED_A, PRES_LED_A | Fan's control port; SELV on measured evidence (Q-22, Q-30, Q-31, D-028); ~65 VAC capacitive float on GND_F | SELV, separate ground |
| OCC | OCC_* | Lighting transformer's Class 2 secondary, 24 VAC | SELV (Class 2) |
| DC | DCI_* | DC controller's contact or output, 12–24 V AC/DC | SELV |

## Barrier crossings (all of them)
`pcb/gen/check.py` asserts that only these parts touch two domains, and that each touches exactly two:

| Part | Crosses | Isolation rating |
|------|---------|------------------|
| U4 H11L1S-TA1-L | Node (LED) → Fan (output, powered from +10V_F) | UL 1577 5 kVrms |
| U5 PC817C-S | Fan (LED) → Node (tach output) | UL 1577 5 kVrms |
| U6 PC817C-S | Fan (LED) → Node (presence output) | UL 1577 5 kVrms |
| U7 PC817C-S | OCC (LED) → Node | UL 1577 5 kVrms |
| U8 PC817C-S | DC (LED) → Node | UL 1577 5 kVrms |

Nothing else crosses: no Y capacitors, no shared pours, no resistors, no shield or mounting-hole connections. Mounting holes are non-plated and unconnected, with plastic or nylon fasteners where they sit near a barrier.

## Spacing rules (enforced in layout DRC)

| Between | Creepage / clearance | Basis |
|---------|----------------------|-------|
| Node ↔ Fan | ≥ 3.0 mm | Basic insulation for ≤ 150 V working voltage, pollution degree 2 (IEC 62368-1 tables). Kept even though the port is SELV, because it also blocks the fan cable's ground loop and the ~65 VAC float (D-028) |
| Node ↔ OCC, Node ↔ DC | ≥ 3.0 mm | Same rule, for uniformity: field wiring, unknown grounding |
| Fan ↔ OCC ↔ DC | ≥ 1.5 mm (functional) | All SELV. Adjacent terminal blocks are allowed: separate blocks, at least one empty pitch or a slot between domains where the layout allows |

Each domain gets its own copper island, with no pour across a barrier. Under each opto, add a routed slot in the barrier gap if layout needs extra creepage. Layout records how each spacing was checked (DRC rule plus a measured screenshot) here before G3.

## Status
- Schematic: domains and crossings asserted by `pcb/gen/check.py` (`pcb/reports/netlist-check.txt`).
- Layout: not started (D-029).

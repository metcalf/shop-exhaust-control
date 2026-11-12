# PCB safety and isolation record

**Board:** the carrier PCB (`pcb/carrier/`) on a Waveshare ESP32-S3-Touch-LCD-3.5 (route B: D-054, D-056). The custom main board it replaced was removed from the tree (D-061). Its record is in git history (`git show b0cada4:pcb/SAFETY.md`).

**No mains on the board or in the enclosure** (D-018, SR-01). The only connection to mains is the listed 5 V USB-C adapter (LPS), which plugs into the cabinet receptacle. IEC 62368-1 reinforced-insulation rules for a mains section don't apply. This file records the isolation barriers between the low-voltage domains (G2 review S-4) and how each is checked. A licensed electrician should verify the receptacle and the 24 VAC hookup at install (G3), not this board.

This controller is a convenience control, not a life-safety device. Air-quality sensing here does not, on its own, protect anyone's health.

## Domains

| Domain | Nets | Source | Class |
|--------|------|--------|-------|
| Node | GND, +5V, +3V3, all GPIO nets (Waveshare J8) | USB-C adapter (LPS, SELV) | SELV; touchable via USB-C and the panel |
| Fan | GND_F, +10V_F, FAN_SPD, FAN_TACH_F, Q_FAN_G, TACH_LED_A, PRES_LED_A | Fan's control port; SELV on measured evidence (Q-22, Q-30, Q-31, D-028); ~65 VAC capacitive float on GND_F | SELV, separate ground |
| OCC | OCC_* | Lighting transformer's Class 2 secondary, 24 VAC | SELV (Class 2) |
| DC | DCI_* | DC controller's contact or output, 12–24 V AC/DC | SELV |

## Barrier crossings (all of them)
`pcb/carrier/gen/check.py` asserts that only these parts touch two domains, and that each touches exactly two (`pcb/carrier/reports/netlist-check.txt`):

| Part | Crosses | Isolation rating |
|------|---------|------------------|
| U1 LTV-817S-TA1-C | Node (LED) → Fan (PWM: pulls Q1's gate to GND_F) | UL 1577 5 kVrms (E113898) |
| U2 LTV-817S-TA1-C | Fan (LED) → Node (tach) | UL 1577 5 kVrms (E113898) |
| U3 LTV-817S-TA1-C | Fan (LED) → Node (presence) | UL 1577 5 kVrms (E113898) |
| U4 LTV-817S-TA1-C | OCC (LED) → Node | UL 1577 5 kVrms (E113898) |
| U5 LTV-817S-TA1-C | DC (LED) → Node | UL 1577 5 kVrms (E113898) |

Nothing else crosses: no Y capacitors, no shared pours, no resistors, no shield or mounting-hole connections. Mounting holes are non-plated and unconnected. **Use nylon screws and spacers at all four holes**, because the Waveshare SMT standoffs they thread into are probably on its GND, and the left holes sit next to field copper.

## Spacing rules (enforced in layout DRC)

| Between | Creepage / clearance | Basis |
|---------|----------------------|-------|
| Node ↔ Fan | ≥ 3.0 mm | Basic insulation for ≤ 150 V working voltage, pollution degree 2 (IEC 62368-1 tables). Kept even though the port is SELV, because it also blocks the fan cable's ground loop and the ~65 VAC float (D-028) |
| Node ↔ OCC, Node ↔ DC | ≥ 3.0 mm | Same rule, for uniformity: field wiring, unknown grounding |
| Fan ↔ OCC ↔ DC | ≥ 1.5 mm (functional) | All SELV. Separate terminal blocks with a gap between domains |

Each domain gets its own copper island, with no pour across a barrier. Under each opto, add a routed slot in the barrier gap if layout needs extra creepage.

**How it's enforced:**
- **DRC rules:** domains are netclasses (`FAN`, `OCC`, `DCI`, node = the rest) in `pcb/carrier/carrier.kicad_pro`. `pcb/carrier/carrier.kicad_dru` sets clearance **and** creepage constraints at the values above.
- **Keepouts:** rule areas (no tracks, vias or pour) cover the barrier band and the field-field gaps (`pcb/carrier/layout/place.py`). The barrier band runs down the opto column and turns left under J8, so the field side is the board's lower-left (D-061).
- **Check:** `pcb/carrier/layout/run.sh` runs DRC. Placed board: 0 errors apart from unrouted pads (`pcb/carrier/LAYOUT.md`).
- **Still to do before G3:**
  1. A mutation check on the carrier rules (tighten a limit and see it fire).
  2. DRC on the routed board.
  3. A measured screenshot of the barrier.
- **Board-to-board:** field copper on the carrier top faces the Waveshare's back-side parts across at least 0.2 mm of air (mech tests). Those parts are node domain, so the 3.0 mm node↔field clearance also applies across that gap.
  - **Open:** air clearance from field parts and pads on the carrier front to the Waveshare's node parts above them. Check it with the routed board before G3; field parts may need to move from under Waveshare parts, or the field copper go to the back.

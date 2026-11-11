# Carrier layout (D-010, D-056, D-058, D-059, D-060)

**Pipeline:** `pcb/carrier/layout/run.sh`
1. Schematic checks.
2. Mech handoff from `mech/out/carrier_layout.json`.
3. Locked placement into `pcb/carrier/carrier-placed.kicad_pcb`.
4. DRC with the barrier rules (`carrier.kicad_dru`, copied from the main board).
5. Renders in `pcb/carrier/reports/`.

**Status (2026-11-11):** placed, not routed.
- **DRC:** 0 errors apart from the 125 unconnected pads (unrouted). 70 warnings: silk overlaps and silk over copper. 0 footprint errors.
- **Board:** 88.24 × 56.8 mm, 2-layer (D-059). Sized by the enclosure, which is now the glass outline: the terminals reach the left wall and the LEDs the right wall.
- **Anchors:** groups are tied to what they serve, so an outline change moves them with it. The right-edge groups follow W, the PWRON one-shot follows J1, and J5 and the SEN65 decoupling follow the keep-flat edge.
- **Mech export:** part extents go to `reports/placed-parts.json`. The mech tests use it to check each display-side part, at its datasheet height, against the Waveshare parts above it.

## What the script asserts
- **J8 match:** J1 pins 1, 2, 3, 23, 31 and 32 land on the Waveshare J8 positions read from the STEP, within 0.01 mm.
  - Pin 1 is at the USB-C end (Waveshare pinout image).
  - Rev 2.0 odd pins are on the inner row.
- **LED faces:** each LED's light face reaches the right edge. The face is the body side opposite the pads, per the SK6812SIDE-A datasheet's pad drawing.
- **J5 entry** faces +x, toward the SEN65. Worked out from the pad geometry: the GH side-entry tabs are at the mating end.
- **Terminal wire entries** face the left wall. Worked out from the KF128L footprint's wire-opening silk, which was the entry side on the old board.

## Placement
- **Barrier:**
  - The five LTV-817S sit on x = 21.0, with field pads at x ≈ 16 and node pads at x ≈ 26. Pad to pad is 7.0 mm.
  - They're packed at a 5.6 mm pitch from y 11.55, in the one column the Waveshare back leaves clear for a 4.0 mm part (D-060). Margins to the Waveshare are 0.2 to 0.76 mm, checked by mech tests.
  - A 5 mm keepout band (x 18.5–23.5) blocks tracks, vias and pour.
  - Field-to-field gaps (fan|OCC, OCC|DC) are 1.5 mm keepouts. fan|OCC is straight. OCC|DC is Z-shaped: it runs from the opto gap down between J3 and U5, then out to the left edge between the OCC and DC parts.
  - U1 is turned the other way from the rest: its LED is on the node side.
- **Field islands (left):**
  - Fan: J2 and J7, R5, Q1, C2, R6, R8.
  - OCC: J3, D2, R10.
  - DC: J4, D3, R12.
  - Terminals are on the back (THT) and inboard: pins at x 11, wire entries facing the left wall, 7.6 mm in from the inner wall (Andrew, D-060). Nothing else is on the back left of them except the two screw heads.
  - Field parts are on the front, left of the terminal pins and clear of the USB pocket edge (x < 3.6).
- **Node:**
  - Opto partners R3, R4, R7, R9, R11, C3, R13 and C4 sit next to each opto.
  - The PWRON one-shot (DNP) is by J8 pin 23.
  - J5 and the SEN65 decoupling are left of the keep-flat zone.
  - The indicator driver (Q3, R16–R18, C7) is by the first LED.
  - Test pads are on the back, centre-bottom.
- **Back face behind the SEN65** (x ≥ 69): a rule area forbids footprints on B.Cu. The only things there are J1's THT stubs (trim flush) and the right-hand nylon screw heads.
- **Camera:** the outline is drawn on User.Drawings. The camera module isn't shipped (D-059). The mech test checks every part height against the Waveshare's actual solids.
- **J1:** DNP. Andrew fits loose pins through J8 and the carrier, seated flush on the socket face (D-059).
- **USB pocket edge:** the carrier left edge under the USB-C pocket is kept free of display-side parts (`usb_pocket_front` in the mech handoff).
- **Opto heights:** Q-48 answered (b), re-placed per D-060. The tightest margin is 0.2 mm (U2/U3, against a 0.9 mm Waveshare part).

## For Andrew's review (ASSUME)
- **Holes in field zones:** the two left mounting holes sit in the fan (top) and DC (bottom) islands. They need nylon M2 screws and spacers, because the Waveshare SMT standoffs are probably on its GND.
- **J5 cable:** the SEN65 connector faces −x into the bay beside the module (D-059), so a short GH 6-pin cable (about 5 cm) reaches J5.
- **Silk:** cleanup waits until after routing.
- **Routing:** not done. Quilter, Freerouting or Andrew. If Freerouting, the Q-38 jar-permission issue applies again.

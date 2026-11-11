# Carrier layout (D-010, D-056, D-058)

**Pipeline:** `pcb/carrier/layout/run.sh`
1. Schematic checks.
2. Mech handoff from `mech/out/carrier_layout.json`.
3. Locked placement into `pcb/carrier/carrier-placed.kicad_pcb`.
4. DRC with the barrier rules (`carrier.kicad_dru`, copied from the main board).
5. Renders in `pcb/carrier/reports/`.

**Status (2026-11-10):** placed, not routed.
- **DRC:** 0 errors apart from the 125 unconnected pads (unrouted). 66 warnings: silk overlaps and silk over copper. 0 footprint errors.
- **Board:** 91.4 × 57.0 mm, 2-layer. Sized by the enclosure: the terminals reach the left wall and the LEDs the right wall.

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
  - A 5 mm keepout band (x 18.5–23.5) blocks tracks, vias and pour.
  - Field-to-field gaps (fan|OCC, OCC|DC) are 1.5 mm keepouts.
  - U1 is turned the other way from the rest: its LED is on the node side.
- **Field islands (left):**
  - Fan: J2 and J7, R5, Q1, C2, R6, R8.
  - OCC: J3, D2, R10.
  - DC: J4, D3, R12.
  - Terminals are on the back (THT). Their bodies end 8.2 mm from the left edge.
- **Node:**
  - Opto partners R3, R4, R7, R9, R11, C3, R13 and C4 sit next to each opto.
  - The PWRON one-shot (DNP) is by J8 pin 23.
  - J5 and the SEN65 decoupling are left of the keep-flat zone.
  - The indicator driver (Q3, R16–R18, C7) is by the first LED.
  - Test pads are on the back, centre-bottom.
- **Back face behind the SEN65** (x ≥ 69): a rule area forbids footprints on B.Cu. The only things there are J1's THT stubs (trim flush) and the right-hand nylon screw heads.
- **Camera keepout:** the Waveshare camera outline (if fitted) is drawn on User.Drawings. Only low parts go under it, and none are tall today.

## For Andrew's review (ASSUME)
- **Holes in field zones:** the two left mounting holes sit in the fan (top) and DC (bottom) islands. They need nylon M2 screws and spacers, because the Waveshare SMT standoffs are probably on its GND.
- **J5 cable:** the SEN65 connector faces the rear wall, so the GH cable loops round the module (about 8–10 cm). Check that a standard JST GH 6-pin cable of that length is on hand.
- **Silk:** cleanup waits until after routing.
- **Routing:** not done. Quilter, Freerouting or Andrew. If Freerouting, the Q-38 jar-permission issue applies again.

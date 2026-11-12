# Carrier layout (D-010, D-056, D-058, D-059, D-060, D-061)

**Pipeline:** `pcb/carrier/layout/run.sh`
1. Schematic checks.
2. Mech handoff from `mech/out/carrier_layout.json`.
3. Locked placement into `pcb/carrier/carrier-placed.kicad_pcb`.
4. DRC with the barrier rules (`carrier.kicad_dru`, from `pcb/SAFETY.md`).
6. Routing candidate: `pcb/carrier/layout/route_freerouting.sh` (Freerouting, headless). Shared code is in `pcb/common/`.
5. Renders in `pcb/carrier/reports/`.

**Status (2026-11-11):** placed, not routed.
- **DRC:** 0 errors apart from the 125 unconnected pads (unrouted). 65 warnings: silk overlaps and silk over copper. 0 footprint errors.
- **Board:** 88.24 × 56.8 mm, 2-layer (D-059). Sized by the enclosure, which is now the glass outline: the LEDs reach the right wall.
- **Anchors:** groups are tied to what they serve, so an outline change moves them with it. The right-edge groups follow W, the optos follow the Waveshare column, the field groups follow the terminal column, and J5, the PWRON one-shot and the SEN65 decoupling follow the keep-flat edge.
- **Mech export:** part extents go to `reports/placed-parts.json`. The mech tests use it to check each display-side part, at its datasheet height, against the Waveshare parts above it.

## What the script asserts
- **J8 match:** J1 pins 1, 2, 3, 23, 31 and 32 land on the Waveshare J8 positions read from the STEP, within 0.01 mm.
  - Pin 1 is at the USB-C end (Waveshare pinout image).
  - Rev 2.0 odd pins are on the inner row.
- **LED faces:** each LED's light face reaches the right edge. The face is the body side opposite the pads, per the SK6812SIDE-A datasheet's pad drawing.
- **J5 entry** faces +x, toward the SEN65. Worked out from the pad geometry: the GH side-entry tabs are at the mating end.
- **Terminal wire entries** face the left wall. Worked out from the KF128L footprint's wire-opening silk, which was the entry side on the old board.

## Placement
Board coordinates: origin top-left seen from the front, +y down.
- **Barrier (D-061):**
  - **Optos:** the five LTV-817S sit in a column at x 48.6 (frame E x 4.5, the board centre). Field pads face left (x ≈ 43.6), node pads face right (x ≈ 53.6); pad to pad is 7.0 mm.
  - **Why this column:** it's the longest run the Waveshare back leaves clear for a 13 mm wide, 4.0 mm part (frame E x −2…11, y −19.25…+19.69).
  - **Opto y:** 15.9, 21.5, 27.1 (fan), 33.7 (OCC) and 44.6 (DC). Margins to the Waveshare are 0.26 mm or more, checked by mech tests.
  - **Keepout:** a 5 mm band blocks tracks, vias and pour. It runs down the opto column (x 46.1–51.1) and turns left under J8 (y 8.5–13.5), so the field side is the lower-left of the board. J1's pads end 5 mm above the field.
  - **Field-to-field gaps:** fan|OCC (y 29.65–31.15) and OCC|DC (y 41.0–42.5) are straight 1.5 mm keepouts.
  - **U1** is turned the other way from the rest: its LED is on the node side.
- **Field islands (lower left):**
  - **Fan:** J2, J7, R5, Q1, C2, R6, R8.
  - **OCC:** J3, D2, R10.
  - **DC:** J4, D3, R12.
  - **Terminals:** on the back (THT), mid-board. Pins are at x 33.0 and the wire entries face the left wall, 29.6 mm in from the inner wall (Andrew, D-061). Nothing else is on the back left of them except the two screw heads.
  - **Field parts:** on the front, either side of the terminal pins.
    - D3 sits left of J4 because the Waveshare part above the other side leaves too little room for the MB10S, taken as 2.7 mm tall (ASSUME, to be checked against the datasheet).
    - The top-left corner above the J8 band carries no copper.
- **Node:**
  - **Opto partners:** R3, R4, R7, R9, R11, C3, R13 and C4 sit 9.5 mm right of the opto column.
  - **PWRON one-shot (DNP):** right of them, anchored to the keep-flat edge.
  - **SEN65:** J5 and its decoupling are left of the keep-flat zone.
  - **Indicator driver** (Q3, R16–R18, C7): by the first LED.
  - **Test pads:** on the back at the bottom edge, right of the opto column and left of the SEN65 (frame E x 8.6–14.2, y −25.4…−15.8). With the back panel off they're reachable, clear of the field wiring.
- **Back face behind the SEN65** (x ≥ 69): a rule area forbids footprints on B.Cu. The only things there are J1's THT stubs (trim flush) and the right-hand nylon screw heads.
- **Camera:** the outline is drawn on User.Drawings. The camera module isn't shipped (D-059). The mech test checks every part height against the Waveshare's actual solids.
- **J1:** DNP. Andrew fits loose pins through J8 and the carrier, seated flush on the socket face (D-059).
- **USB pocket edge:** the carrier left edge under the USB-C pocket is kept free of display-side parts (`usb_pocket_front` in the mech handoff).
- **Opto heights:** Q-48 answered (b). Re-placed per D-061: the tightest margin is now 0.26 mm (U4).
- **3D node↔field clearance (Q-49):** not yet checked against the Waveshare's node-side parts above the field zone.

## For Andrew's review (ASSUME)
- **Holes:** use nylon M2 screws and spacers at all four holes, because the Waveshare SMT standoffs are probably on its GND. The bottom-left hole is in the DC island.
- **J5 cable:** the SEN65 connector faces −x into the bay beside the module (D-059), so a short GH 6-pin cable (about 5 cm) reaches J5.
- **Silk:** cleanup waits until after routing.
- **Routing:** not done.
  - **Freerouting:** Andrew has allowed the jar (2026-11-11); run `route_freerouting.sh`.
  - **Quilter:** Andrew uploads `carrier-placed.kicad_pcb`. Every footprint is written locked (`SetLocked`); before the upload, confirm that's how Quilter identifies fixed parts.

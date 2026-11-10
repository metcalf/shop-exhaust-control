# Layout (v1): locked placement for routing

Process per D-010 (accepted 2026-11-09): scripted, locked placement → Quilter (Andrew uploads) and Freerouting candidates from the same placement → both must pass our DRC → Andrew picks one and touches it up.

**Status (2026-11-09, nightly):** placement done and locked in `pcb/exhaust-placed.kicad_pcb` (the Quilter input). DRC: 0 errors; the warnings are silkscreen only, plus TP2/TP8 differing from the library (courtyard removed on purpose, see §4). 203 unconnected items, because nothing is routed yet. **The Freerouting candidate isn't routed:** the permission classifier blocked running the downloaded Freerouting jar in the unattended session (Q-38). `pcb/route/exhaust.dsn` is exported and `pcb/layout/route_freerouting.sh` does the rest in one command.

## 1. Source and pipeline
- `pcb/exhaust.kicad_sch` is the source from this commit on (D-035). `pcb/gen/build.py` is frozen; `pcb/gen/check.py` still runs on the netlist.
- `pcb/layout/run.sh`: netlist from the schematic → `check.py` → `footprints.py` (project library) → `place.py` → `exhaust-placed.kicad_pcb` (+ `.kicad_pro`/`.kicad_dru` copies, since KiCad pairs them by basename) → DRC to `pcb/reports/drc-placed.rpt`.
- `pcb/layout/route_freerouting.sh`: DSN export → Freerouting 2.5.0 headless → SES import → node GND pour on both layers → DRC (`--refill-zones`) → top/bottom renders. Output: `pcb/exhaust-freerouting.kicad_pcb`.
- Placement lives in the `POS` table in `place.py`. To move a part, edit it there and rerun, so mech keeps reading positions from the board (D-011).

## 2. Footprints (design.md O-3, closed)
Fetched with `easyeda2kicad` by LCSC number (raw copies in `pcb/lib/lcsc.pretty`). The project library `pcb/lib/exhaust.pretty` is built by `pcb/layout/footprints.py`:

| Part | Stock placeholder | Result |
|------|-------------------|--------|
| H11L1S (C7435535) | SMDIP-6 W9.53 | LCSC SOP-6 LS10.2 (pads at ±4.38, 6.16 mm gap between rows) |
| LTV-817S (C109227) | SMDIP-4 W9.53 | LCSC SOP-4 LS10.3 (pads at ±5.0, 7.0 mm gap) |
| MB10S (C2488) | Vishay MBLS | LCSC MBS, **renumbered**: MDD datasheet 1 +, 2 −, 3/4 ~ → symbol MB6S 1/2 ~, 3 +, 4 − |
| RGB 3528 (C601699) | Cree PLCC4 CCW | LCSC footprint, **renumbered**: datasheet 4 anode, 1 R, 2 G, 3 B → symbol LED_ARGB 1 A, 2 R, 3 G, 4 B. The stock one would have put +5 V on a cathode |
| KF128L (C474930) | Phoenix PT-1,5 | LCSC: same 3.5 mm pitch, 1.4 mm drill (stock 1.2) |
| Inductor (C135262) | Bourns SRN4018 | The part is a Murata LQH44PN2R2MP0L; LCSC 4 × 4 footprint |
| ESP32-S3-WROOM-1 | stock | Stock, minus the 12 EPAD thermal-via PTH pads (Q-33: no EPAD vias) and minus its 48 × 21 mm antenna keepout (replaced on the board, §3) |
| USB-C HRO, JST GH, TSOT-23-6, 1×14 socket | stock | Pad-for-pad match with the LCSC footprints; stock kept |

Silk polarity dots on the two renumbered parts still mark **datasheet** pin 1 (R cathode on the LED, + on the bridge). Check the CPL rotations of D2–D9 in JLC's placement preview at order time.

## 3. Placement decisions (ASSUMPTIONS for Andrew's review)
Board **72 × 123 mm**, 2-layer, front (F.Cu) faces the display. Front view: cable entries at the top, sensor bay below.

| # | Assumption | Why | Cost to change |
|---|-----------|-----|----------------|
| A1 | Display module on our board via J6 (8.5 mm socket), header at the **bottom**; the module's four Ø3.2 holes (44.00 × 76.08) are also **the board's mounting holes** (H1–H4, NPTH), one standoff stack per corner to the enclosure | One set of bosses holds both boards. The glass sits ≈ 14.4 mm above our board | Moving the display means moving J6 and the holes; mech follows |
| A2 | Field terminals J3 (OCC), J4 (DC), J2 + J7 (fan) and USB-C J1 along the **top edge**, wire entry up | Interfaces §5: cable entry top or back. The screws must be reachable, so the terminals can't sit under the display | Rotating the terminals for back entry is mechanical only |
| A3 | KF128L wire entry is the footprint's +y side (the side with the drawn openings), rotated 180° to face up. **Not confirmed against the drawing** | The easyeda silk shows the openings on that side | Rotation only |
| A4 | ESP32 module rotated so the **antenna points out the left edge**, antenna end 0.5 mm from the edge, ≈ 4 mm clear of the display edge, under nothing. Board keepout (no copper, tracks or vias): 5.5 mm deep at the antenna end, 3 mm either side of the module, out to the edge | Keeps the display's metal back off the antenna. The stock 15 mm side keepout doesn't fit a 72 mm board | If the AP is to the right, flip the module and display left/right |
| A5 | Indicator LEDs (6, 12 mm pitch) in a column on the **right** edge beside the display (the room side, D-033). The light pipe runs from the board to the bezel | D-031/D-033 | Mirror the column if the room side is the left |
| A6 | All test pads on **B.Cu**, including the recovery pairs (D-041). The front is under the display, so the back has to be reachable with the rear lid off | Pads need no assembly on B | If the lid is on the front, move them to the top band |
| A7 | SEN65 connector J5 (side-entry GH) on the bottom edge, bottom right, cable straight down into the sensor bay through the divider grommet | Interfaces §5 | Moving it along the bottom edge is free |
| A8 | Recovery pairs: pad edge to edge 0.2 mm, pairs 12 mm apart. Each pad has its own mask opening; a shared opening reads as a mask bridge in DRC, and a 0.2 mm web won't stop a screwdriver tip | D-041 asked for one opening per pair | Add a shared opening by hand if you prefer it |

## 4. Barrier (pcb/SAFETY.md)
- Domains are netclasses (`FAN`, `OCC`, `DCI`; everything else with a net is node) set in `exhaust.kicad_pro`. Rules live in `exhaust.kicad_dru`: clearance **and** creepage ≥ 3.0 mm node↔field, ≥ 1.5 mm field↔field.
- Keepout rule areas (no tracks, vias or pour) make the barrier physical for any router: a 5 mm band under the optos (y 21.5–26.5 mm), a 3 mm vertical band between the USB/buck corner and the field islands, and 1.5 mm strips between the OCC, DC and fan islands. Freerouting gets them through the DSN. Quilter should honour them; DRC is the check either way.
- **Rules verified by mutation** on the placed board: raising the 3.0 mm rules to 8.0 mm gives 41 clearance and 35 creepage violations, all from the three barrier rules. The smallest node↔field distance is **6.16 mm** (U4's own row gap). Raising field↔field to 6.0 mm reports a minimum of **2.18 mm** (D2 to R14). At the real limits: 0 violations. Routing can only reduce these, so DRC has to be rerun on each candidate.
- Mounting holes H1–H4 are NPTH with no net. The closest, H2, is ≈ 10 mm below the barrier band, so no hole sits at a barrier.

## 5. Known warnings, not errors
- Silkscreen: values and refs overlapping or clipped at the edge (`silk_*`, 96). Leave until the routed candidate is picked, then clean up in the GUI.
- `lib_footprint_mismatch` on TP2 and TP8: their courtyard is removed so each recovery pair can sit at the copper minimum.
- Schematic parity isn't checked: `kicad-cli pcb drc --schematic-parity` refuses with "requires a fully annotated schematic". `check.py` covers the netlist, and footprints carry schematic UUIDs, so GUI "Update PCB from Schematic" matches them.

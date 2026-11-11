# Mechanical concept: Waveshare 3.5 + carrier + SEN65 (D-056, D-057, D-058)

**Status:** concept, 2026-11-10. Model: `mech/concept.py`. Outputs: `mech/out/`. Geometry checks: `mech/tests/`, 13 passing, with the output in `mech/out/test-results.txt`. Waveshare geometry is read from its STEP (`mech/fetch_vendor.sh`) and never retyped. Terminal, LED and keep-flat positions come from the placed carrier board (`pcb/carrier/carrier-placed.kicad_pcb`).

## Frame and stack-up (frame E: +x right, +y up, +z out of the front; origin at the lens centre)

| Item | z (mm) | Source |
|------|--------|--------|
| Bezel front | +3.6 | lens +1.1, 1.0 gasket, 1.5 lip |
| Waveshare PCB back | −6.4 | STEP |
| J8 face (low-profile SMD female, 5.1 mm) | −11.5 | STEP |
| SMT standoffs end | −10.4 | STEP |
| Carrier top / back | −16.4 / −18.0 | M2 × 6 nylon spacer, 1.6 mm PCB |
| Male header: body top, pin tip | −13.9, −7.9 | 3.6 mm insertion, 1.5 mm short of the socket floor |
| SEN65 front / back | −22.0 / −47.6 | 4.0 mm gap (≤ 1/4", holds the 1/8" foam) |
| Rear wall outside | −50.1 | 0.5 clearance + 2.0 wall |

**Outside:** 97.4 × 66.0 × 53.7 mm, about 345 cm³. The cleat adds a few mm.

## Layout (seen from the front)
- **Orientation:** landscape. The board is mounted rotated so its USB-C is on the left. J8 runs along the top. The PWR, RESET and BOOT side buttons are on the bottom edge and are not reachable from outside, which isn't needed: flashing uses native USB, and power-on is the AXP2101 plus the DNP one-shot.
- **Left wall:**
  - The USB-C pocket steps in to the receptacle mouth. A standard plug (12 × 6.5 mm overmold) clears the display solids (slab-probed in the tests).
  - Three strain-relief slots for the fan, OCC and DC cables, centred on the placed terminals, at terminal height behind the carrier.
- **Right wall, front to back:**
  - **LED diffuser slot** (51 × 6 mm) at the board-to-board gap. The 6 LEDs are on the carrier's display side and shine through the gap.
  - **SEN65:** stands on end with its port face (55.2 × 25.6) against the wall through a 1 mm gasket.
    - Inlets at the bottom, slot 9 × 20 mm (≥ 56 mm²). The outlet is above, a Ø 20.5 mm circle (≥ 148 mm²).
    - A 21 mm gasket rib separates them.
    - This is lateral placement, allowed by the mech guide (Fig. 5).
    - The diffuser slot ends 3.6 mm in front of the SEN65 zone.
- **SEN65 behind the carrier, right side.**
  - The 1/8" closed-cell foam strip goes on its carrier-facing face. Notch the foam around the two right-hand M2 nylon screw heads.
  - Its connector is on an L × H face. I put it on the rear face because a GH plug won't fit in the 4 mm gap. The cable loops round the module's left face to J5 on the carrier's back, which sits left of the keep-flat zone with its entry facing +x.

## Departures from Andrew's direction, and why
- **SEN65 depth is 25.6 mm, not 21.3.** The SEN6x has its inlets and outlet on the same 55.2 × 25.6 face (mech guide Fig. 1). Facing that face into the room through the right wall means the 25.6 dimension runs front to back.
- **Smaller alternative, not taken:** put the SEN65 beside the Waveshare board instead of behind it. That's about 121 × 66 × 33 mm (≈ 265 cm³, 25 % less volume, 20 mm thinner, 24 mm wider). It moves the module next to the LED edge.
- **Gap is 4.0 mm, not 6.35.** That's inside Andrew's "at most 1/4"" and still holds the 1/8" foam.
- **Foam caveat:** Sensirion's mech guide says not to thermally insulate the module (§3). A strip on one face is a radiant shield, not insulation, but don't wrap the module.

## Defaults used tonight (D-058, change any of them)
1. **Opening:** front bezel and rear shell split at z = −8.0, screwed from the back. To service the module, lift the unit off the cleat (one locking screw) and remove the rear shell.
2. **Cables:** clamp-and-foam strain reliefs on the left wall. Straight USB-C plug into the stepped pocket.
3. **Indicator:** 6 LEDs at 9 mm pitch along the right edge only, no corner wrap.
4. **Carrier mounting:** nylon M2 × 6 spacers and nylon M2 screws into the Waveshare SMT standoffs, at all four holes. The two left holes sit in field zones (SAFETY note). The carrier outline is 91.4 × 57.0 mm.

## Open items
- **Cleat and lock-screw geometry.** Not modelled yet.
- **Sealing:**
  - Bezel/rear-shell seam gasket.
  - Lens gasket compression.
  - Gaskets for the cable reliefs and the USB pocket.
- **SEN65 retention:** a cradle that holds the module against the port gasket. The model has the box only.
- **Thermal check:** measure the module's over-temperature against the guide's < 5 K target with the LEDs at their 150 mA cap. Bench item.
- **Diffuser:** material and part, either a printed light pipe or a separate diffusing insert.

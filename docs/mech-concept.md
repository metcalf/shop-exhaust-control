# Mechanical concept: Waveshare 3.5 + carrier + SEN65 (D-056, D-057, D-058, D-059)

**Status:** concept rev 2, 2026-11-10, after Andrew's review: no bezel, 1.6 mm walls with ribs, thinner stack. Model: `mech/concept.py`. Outputs: `mech/out/`. Geometry checks: `mech/tests/`, results in `mech/out/test-results.txt`. Waveshare geometry is read from its STEP (`mech/fetch_vendor.sh`) and never retyped. Terminal, LED, keep-flat and part positions come from the placed carrier board (`pcb/carrier/carrier-placed.kicad_pcb`, `pcb/carrier/reports/placed-parts.json`).

## Frame and stack-up (frame E: +x right, +y up, +z out of the front; origin at the glass centre)

| Item | z (mm) | Source |
|------|--------|--------|
| Cover glass front (enclosure front face) | +1.1 | STEP |
| Glass back at the rim / wall rim | 0.0 / −0.8 | STEP probe; 0.8 mm foam rim gasket |
| Waveshare PCB back | −6.4 | STEP |
| J8 socket face (low-profile SMD female, 5.1 mm) | −11.5 | STEP |
| Lowest Waveshare part (camera) | −12.3 | STEP |
| Male header body | −14.0 to −11.5 | fitted normally, seated on the socket face |
| Carrier top / back | −14.0 / −15.6 | 1.7 mm below the camera, 1.6 mm PCB, 3.6 mm spacer |
| J8 male posts: tip, engagement | −8.5, 3.0 mm | short-post header (ASSUME, Q-47); tips 2.1 mm short of the PCB |
| Tabs and screw heads | −15.6 to −18.9 | 2.0 mm tab + 1.3 mm nylon pan head |
| SEN65 front / back | −19.6 / −45.2 | 4.0 mm gap (≤ 1/4"), holds the 1/8" foam |
| Back panel inner / outer | −45.6 / −47.2 | 0.4 mm clearance, 1.6 mm panel |

**Outside:** 92.44 × 61.0 × 48.3 mm, about 272 cm³, which is the glass outline. Andrew's estimate was 47.7 mm; the 0.6 mm difference is the header body (2.5 mm) seated on the socket face. With a standard 11.5 mm header on longer spacers instead, it's 50.7 mm. The cleat adds a few mm.

## Layout (seen from the front)
- **No bezel.** The cover glass is the front face, and its edges are exposed at the sides.
  - **Shell:** four 1.6 mm walls. The glass's black border (9.5 mm wide) sits on the wall rim through a 0.8 mm closed-cell foam gasket.
  - **Fit:** the LCD module clears the inner walls by 0.7 mm on the left, its tightest side.
- **Retention:** four tabs off the top and bottom walls, behind the carrier at the Waveshare holes. One nylon M2 screw per hole goes in from the back, through the tab, the carrier and a 2.4 mm spacer, into the SMT standoff. Tightening pulls the glass onto the rim gasket.
- **Service:**
  1. Remove the back panel to reach the SEN65.
  2. Remove the module, then the four screws.
  3. The display and carrier come out through the front.
- **Left wall:**
  - **USB-C:** a stepped pocket runs in to the receptacle mouth, 6.2 mm inside the outline. A standard plug clears the display solids (slab-probed in the tests).
  - **Cable entry:** strain-relief slots for the fan, OCC and DC cables, centred on the placed terminals.
- **Right wall, front to back:**
  - **LED diffuser slot** (51 × 6 mm) in the board-to-board gap. It ends 3.6 mm in front of the SEN65.
  - **SEN65 ports:** the module stands on end, port face to the wall through a 1 mm gasket. Inlet slot at the bottom, outlet circle above, with a 21 mm gasket rib between them.
- **SEN65 connector:** it sits on the face opposite the ports (mech guide Fig. 1 "Rear View"; datasheet: "adjacent to the air outlet"). It faces −x into a 12 mm bay kept clear beside the module, and a short GH cable runs to J5 on the carrier back. The previous concept had this wrong: it put the connector on the rear face and looped the cable round the module.
- **Ribs:** 1.2 × 4 mm on the back panel's inside, at a 15 mm pitch plus one along x. They stop short of the SEN65 bay, because the module is 0.4 mm off the panel.
  - **Walls:** the walls get no ribs yet. With the glass in front and the back panel screwed on, the box is closed on both faces.
  - **Back panel exterior:** this is the place to add more if the print flexes. The cleat interface can double as the ribs.

## Departures and caveats
- **SEN65 depth is 25.6 mm, not 21.3.** The SEN6x has its inlets and outlet on the same face. Facing that face into the room through the right wall puts the 25.6 mm dimension front to back.
- **Camera clearance.** The camera is 1.7 mm above the carrier top, so only low parts can go under it. The mech test checks heights.
- **Header.** J8's male header is fitted normally and needs short posts (about 3 mm); see Q-47. Body-on-back would be 1.2 mm thinner, but Andrew rejected it because front-side solder fillets would block full insertion.
- **Foam caveat.** Sensirion's mech guide says not to thermally insulate the module (§3). A strip on one face is fine. It's notched round the two right-hand tabs and screw heads.

## Defaults still in force (D-058)
- **Cables:** clamp-and-foam strain reliefs, and a straight USB-C plug.
- **LEDs:** 6 at 9 mm pitch on the right edge.
- **Hardware:** nylon M2 at all four holes. The left holes are in field zones (`pcb/SAFETY.md`).

## Open items
- **Back panel fastening:** screw bosses and the cleat and lock-screw geometry.
- **Sealing:** rim gasket compression, gaskets for the cable reliefs and USB pocket, and the back panel seam.
- **SEN65 cradle:** holds the module against the port gasket.
- **Thermal check:** module over-temperature against the < 5 K target, with the LEDs at their 150 mA cap. Bench item.
- **Diffuser:** material and part.

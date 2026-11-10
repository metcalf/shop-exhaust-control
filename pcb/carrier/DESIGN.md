# Carrier PCB design notes (D-054, D-055, D-056)

Carrier for the Waveshare ESP32-S3-Touch-LCD-3.5. It plugs into the board's 2×16 female header J8 and sits on the board's M2 pattern (72.00 × 48.50 mm).

- **Source:** `pcb/carrier/gen/build.py` until layout starts.
- **Checks:** `pcb/carrier/gen/run.sh` runs the footprint build, ERC, netlist assertions, SVG and raw BOM, writing to `pcb/carrier/reports/`.
- **Related docs:** signals and pins in `docs/interfaces.md` §2–§3; isolation in `pcb/SAFETY.md`. Circuit values carried over from the main board are argued in `pcb/design.md` §2–§4. Only what changed is recorded here.

## Status (2026-11-10)
- **ERC:** 0 violations.
- **Netlist assertions:** pass. 68 parts, 56 nets, barrier U1–U5.
- **Mutation check:** each of these makes the checks fail:
  - renaming the gate net
  - breaking the presence LED feed
  - merging the DC domain into GND
  - renaming PWRON
  - shorting the one-shot's resistor chain
  - populating the one-shot FET
- **JLC:** all SMT is Basic except D4–D9 (SK6812SIDE-A, one Extended line). Resistor and capacitor LCSC numbers are assigned per value at BOM time, as on the main board.
- **DNP:** Andrew hand-solders J1, J2–J4, J7 and J5. The one-shot (Q2, C1, R1, R2, D1) and the I²C pull-ups (R14, R15) are not fitted.

## Blocks
- **J1, Waveshare J8 (Rev 2.0 numbering).**
  - 1 `+5V` (VBUS)
  - 3/4/29/30 GND
  - 6 GPIO21 (indicator)
  - 8 GPIO38 `FAN_PWM`
  - 10 GPIO39 `FAN_TACH`
  - 12 GPIO40 `FAN_PRESENT`
  - 14 GPIO41 `OCC_IN`
  - 16 GPIO42 `DC_IN`
  - 23 PWRON
  - 25/27 SCL/SDA (GPIO7/8)
  - 31/32 `+3V3`
  - Everything else is unconnected, including the strapping pins GPIO0/45/46 and the spares GPIO17/18/47/48/43/44. `check.py` asserts this.
  - **Numbering:** V1 boards number the rows the other way round, with the same physical positions.
  - **Orientation:** the male header on the carrier faces the board's female J8. Check the orientation against the STEP before layout.
- **Fan side (SR-08), same as the 2.8B carrier.**
  - U1 (LTV-817): LED driven from GPIO38 through 390 Ω, with a 10 kΩ pull-down. Collector on Q1's gate, emitter on GND_F.
  - R5 (2.2 kΩ) pulls Q1's gate to +10V_F.
  - Q1 (AO3400A) holds the yellow speed line low unless U1 is lit.
  - Tach: U2. Presence: U3 is restored from the main board, with 10 kΩ from +10V_F and 22 kΩ to `+3V3`.
  - Fan-side draw is ≈ 6.3 mA max, against ≈ 9 mA available (Q-26).
- **OCC (U4) and DC (U5).** Same circuit as `pcb/design.md` §3: J3 and J4, each 10 kΩ 1206 → MB10S → LTV-817, with a 47 kΩ / 1 µF output filter.
- **SEN65.**
  - J5 is a GH-6 wired per SEN6x Table 17, on `+3V3` with 10 µF + 100 nF.
  - It shares the Waveshare I²C bus, which also carries FT6336 (0x38), ES8311 (0x18), PCF85063 (0x51), AXP2101 (0x34), TCA9554 (0x20/0x21) and QMI8658 (0x6A, SA0 tied to GND). The SEN65's 0x6B is free.
  - R14/R15 are DNP pull-up pads.
- **Indicator (D-055).**
  - Drive: GPIO21 → Q3 (2N7002). R16 (10 kΩ) pulls the gate up, so DIN idles low through reset. It's no longer a strapping pin, so this is only about idle state.
  - Data path: R17 (1 kΩ) pulls the drain up to `+5V`, then R18 (470 Ω) feeds the first DIN.
  - Data is inverted, so RMT uses `invert_out`.
  - Chain of 6 (`N_LED`, final count set by mech), 100 nF each, plus 1 µF bulk.
- **PWRON one-shot (D-056, DNP).**
  - Q2 (2N7002) pulls PWRON to GND. Its gate is fed from `+5V` through C1 (2.2 µF, C23630, 16 V X5R), with R1 + R2 (2 × 1 MΩ) from gate to GND.
  - D1 (1N4148WS) runs from GND to the gate, so the RC resets when VBUS falls.
  - Pulse length is ≈ 2.1–6.4 s, depending on the 2N7002's V_th and the X5R's DC-bias derating. Analysis is in `docs/interfaces.md` §3.
  - Fit it only if the bench shows the AXP2101 doesn't power on from VBUS. Trim the values on the bench when it's fitted.
- **Footprint.** `carrier:LED_SK6812SIDE-A_4.0x1.6mm` comes from easyeda2kicad (C5378721), with pads renumbered to `LED:SK6812`. Per the datasheet: 1 DIN, 2 VDD, 3 DOUT, 4 GND.

## Open for layout
- **Outline:** J8 runs along the Waveshare board's bottom edge between the lower M2 holes, so the carrier covers that region. The LED edge has to reach the enclosure wall; a corner wrap needs LEDs on a second edge (mech).
- **Barrier:**
  - Copy the netclasses and `.kicad_dru` rules from the main board (≥ 3.0 mm node↔field).
  - Keepouts under U1–U5.
- **Placement:** the side-emitting LEDs and the USB-C step in the enclosure wall must not collide. The USB-C is on the left edge of the Waveshare board.

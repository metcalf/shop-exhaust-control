# Carrier PCB design notes (D-054, D-055)

Carrier for the Waveshare ESP32-S3-Touch-LCD-2.8B, on its 2×12 header J7 and M2 pattern (40.9 × 59.7 mm). Source: `pcb/carrier/gen/build.py` until layout starts. Checks: `pcb/carrier/gen/run.sh` (footprints, ERC, netlist assertions, SVG, raw BOM into `pcb/carrier/reports/`). Signals and pins: `docs/interfaces.md` §2. Isolation: `pcb/SAFETY.md`. Circuit values carried over from the main board are argued in `pcb/design.md`; only what changed is here.

## Status (2026-11-10)
- ERC: 0 violations. Netlist assertions pass (51 parts, 39 nets, barrier U1–U3). Mutation-checked: renaming the gate net, GPIO0, FAN_PWM or a chain link, or merging GND_F into GND, each makes the checks fail.
- JLC: SMT is all Basic except D2–D7 (SK6812SIDE-A, one Extended line). Resistor/capacitor LCSC numbers are assigned per value at BOM time, as on the main board. J1, J2, J3, J7, J5 are DNP (Andrew hand-solders them).

## Blocks
- **J1, Waveshare header.** Waveshare J7 numbering: 1–2 `+5V` (USB_5V), 5/6/23/24 GND, 11 GPIO0, 13 GPIO4, 17 SCL, 18 GPIO43, 19 SDA, 20 GPIO44, 21–22 `+3V3`; the rest unconnected (asserted). Socket vs. pins and the row mirroring when stacked: check against the Waveshare STEP at layout.
- **Fan (SR-08).** U1 LTV-817: LED from GPIO44 via 390 Ω (≈ 5.4 mA), 10 kΩ pull-down; collector on Q1's gate, emitter GND_F. R3 2.2 kΩ pulls the gate to +10V_F (45 mW in 0603, rated 100 mW). Q1 AO3400A holds yellow low unless U1 is lit. Fan-side draw ≈ 5.4 mA max against the ≈ 9 mA available (Q-26). Tach U2 and its 10 k / 22 k are unchanged from the main board.
- **OCC.** Unchanged from `pcb/design.md` §3, output to GPIO4 (R24 lifted on the Waveshare board).
- **SEN65.** J5 GH-6 per SEN6x Table 17, on `+3V3` with 10 µF + 100 nF. The bus is the Waveshare's shared I²C (GT911 0x5D, TCA9554 0x20, PCF85063 0x51; U6 0x6B removed), whose pull-ups are on that board; R8/R9 are DNP pads in case the bench shows slow edges with the cable.
- **Indicator (D-055).** GPIO0 → Q2 2N7002 gate, R10 10 kΩ gate pull-up to `+3V3` (with Waveshare's own 10 k: GPIO0 reads high at reset, normal boot; DIN idles low). R11 1 kΩ drain pull-up to `+5V`; R12 470 Ω series into the first DIN (datasheet §14 asks for ≈ 500 Ω). Data is inverted: RMT `invert_out`. Rise time ≈ 1 kΩ × (≈ 15 pF) ≈ 15 ns against the 300 ns T0H. Chain of 6 (set by mech, `N_LED`), 100 nF each, 1 µF bulk. `+5V` capacitance kept ≈ 1.6 µF because the Waveshare board already sits on VBUS (USB sink 10 µF limit; its own capacitance unknown).
- **Footprint.** `carrier:LED_SK6812SIDE-A_4.0x1.6mm` from easyeda2kicad (C5378721), pads renumbered to `LED:SK6812` (datasheet: 1 DIN, 2 VDD, 3 DOUT, 4 GND). Which side emits relative to the pads: confirm from the datasheet drawing before placing at the board edge.

## Open for layout
- Board outline (≈ 50 × 70 mm) with the LED edge reaching the enclosure wall; a corner wrap needs LEDs on a second edge (mech).
- Barrier: copy the netclasses and `.kicad_dru` rules from the main board (≥ 3.0 mm node↔field), keepouts under U1–U3.
- GPIO43's ROM boot log drives U2's collector through the Waveshare 499 Ω: ≤ 6.6 mA, harmless; noted, not mitigated.

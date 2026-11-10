# Schematic design notes (v1)

Source: `pcb/gen/build.py` → `pcb/exhaust.kicad_sch` (D-035). Checks: `pcb/gen/run.sh` (ERC, netlist assertions, SVG, raw BOM into `pcb/reports/`). Parts: `pcb/gen/parts.py`, sourced in `sourcing/*.md` (2026-10-28). Isolation: `pcb/SAFETY.md`.

Datasheet figures below come from the sourcing notes. Where a value is assumed rather than read, it says so.

## 1. Power (D-030, D-037)
- J1 USB-C (HRO TYPE-C-31-M-12) VBUS goes straight to `+5V`, with no series fuse: overcurrent protection is the source's job (listed LPS adapter or the PC port; D-040). Rd 5.1 kΩ on CC1 and CC2 (sink). D1 SMAJ5.0A on `+5V`. U2 USBLC6-2SC6 on D±. Shield goes straight to GND: the enclosure is plastic and there's no chassis.
- **`+5V` capacitance is limited to 1–10 µF** (non-PD USB sink; asserted in `check.py`). The only cap on the rail is the buck's 10 µF input. Don't add bulk.
- **3.3 V: AP63203WU-7 sync buck** (D-040; datasheet DS41326 Rev. 2-2): fixed 3.3 V, 2 A, TSOT-26, 3.8–32 V in, 35 V abs max VIN and EN, 1.1 MHz, PFM at light load, ~100 % duty in dropout, UVLO 3.7 V max rising and ≈ 3.1 V falling. EN to VIN, FB straight to `+3V3`, 100 nF BST to SW, 10 µF in, 2 × 22 µF out (Fig. 21, Table 2). Layout: 10 µF tight to VIN/GND, GND plane under the part (datasheet Fig. 25).
- **Inductor stays 2.2 µH** (C135262; 3.4 A Isat, above the 3.1 A max peak limit; 46 mΩ), not Table 2's 3.9 µH. Eq. 7 ties that value to about 12 V in (ΔI ≈ 0.56 A). At 5 V in, 2.2 µH gives ΔI ≈ 0.46 A and 3.9 µH only ≈ 0.26 A, against the 0.6–1 A guidance. It's inside the datasheet's 2.2–10 µH range.
- Why not an LDO: at 0.35 A typical, an LDO dissipates ≈ 0.6 W, too much for SOT-23-5 in a sealed box (sourcing/power.md). Peak load ≈ 0.8 A at 3.3 V (module TX 360 mA + display 100 mA + SEN65 350 mA for 2 ms), within the 2 A rating.
- No `+5V` sense (D-039). The indicator keeps its fixed 300 mA firmware cap. GPIO2, 10 and 38–40 are unconnected spares (D-039, D-047, D-048).
- **Hot-plug (O-4, closed by D-040):** a live VBUS into a ceramic-only input (A-to-C cable, or a supply that doesn't switch VBUS) rings. *Estimated, not measured:* 6.6 V peak on 3 m of 24 AWG, ≈ 8 V on a short heavy cable before SMAJ5.0A starts conducting. The buck's 35 V rating covers that. Bulk capacitance isn't an option under the USB limit above. If the display ends up on `+5V` (Q-35), check that its on-board regulator tolerates this.

## 2. Fan interface, fan domain (SR-08, SR-09, D-023; G2 review S-2)
Circuit as in `docs/interfaces.md` §2.1, with these parts: U4 H11L1S-TA1-L, VCC straight from `+10V_F` (3–15 V operating, 16 V abs max), no fan-side regulator (D-044); Q1 AO3400A (gate at 10 V against ±12 V max; same part as the indicator switches, one fewer unique part), U5 (tach) and U6 (presence) LTV-817S-TA1-C (D-045). No TVS on the fan lines (D-042) and no series diode on tach (D-043).

**Fan-side current from red +10 V, datasheet maxima (S-2):**

| Load | Max |
|------|-----|
| H11L1 ICC (on or off), specified at 5 V. Andrew: the datasheet curve shows no significant rise at 10 V | 1.3 mA |
| Q1 gate pull-up 10 k to `+10V_F` (flows to GND_F via U4 when lit) | 1.0 mA |
| Tach LED, white low: (10 − 1.0) / 10 k (Vf min) | 0.9 mA |
| Presence LED: (10 − 1.0) / 10 k | 0.9 mA |
| **Total** | **≈ 4.1 mA**, against the ≤ 9 mA budget (Q-26: the port supplies ≈ 9.3 mA) |

- PWM LED drive: (3.3 − 1.5) / 390 Ω ≥ 4.6 mA against H11L1 IF(on) max 1.6 mA: 2.9× margin. GPIO4 has a 10 k pull-down, so the LED stays dark through reset and boot, and the fan stays off (SR-08).
- Tach and presence outputs: LTV-817 C rank, CTR 200–400 % at 5 mA. Typical CTR at IF = 1 mA is 80 % (Andrew, from the Lite-On curve; a typical value, not a minimum). At ≈ 0.9 mA that gives IC ≈ 0.7 mA against the 0.15 mA the 22 k pull-up needs: ≈ 4.7×, still ≈ 2.4× after 50 % aging. Switching time with a 22 k load is ~100 µs order (not characterized), against a ≥ 3.3 ms tach half-period.
- H11L1 propagation is ≤ 0.5 µs (Lite-On), < 0.3 % of the 200 µs PWM period.

## 3. 24 VAC occupancy and wired DC inputs (FR-07, IR-01, D-025, D-036; G2 review S-5)
J-OCC and J-DC use one identical circuit, with no input TVS (D-046): terminals → 2 × 2.7 kΩ 1206 in series (5.4 k) → MB10S bridge → LTV-817S-TA1-C LED. The output has a 47 k pull-up to 3.3 V and 1 µF to GND. A bridge, not an antiparallel diode (D-036): half-wave conduction leaves ≥ 8 ms gaps per cycle, which the RC would have to bridge.

Path drop, worst case: LED 1.4 V + two bridge diodes ≈ 1.8 V, so ≈ 3.2 V. The pull-up needs 3.3 V / 47 k = 70 µA.

| Case | Result |
|------|--------|
| 12 VDC − 10 % (10.8 V) | IF ≥ (10.8 − 3.2) / 5.4 k = 1.4 mA. With CTR 80 % (typical at 1 mA, as §2), IC ≈ 1.1 mA, ≈ 16× the 70 µA needed |
| 12 VAC − 10 % (15.3 V pk) | Conducts usefully (IF ≥ 0.3 mA) above 4.8 V, i.e. above 18° of each half-cycle. Gap ≈ 1.7 ms per half-cycle; RC τ = 47 ms, so the output rises ≈ 3.3 × 1.7 / 47 = 0.12 V, well below VIL (0.83 V). No chatter |
| 24 VAC + 10 % (26.4 V, 37.3 V pk) | IF pk 6.5 mA (LTV-817 max 50 mA). P ≈ 26.4² / 5.4 k ≈ 0.13 W total, 65 mW per 1206 (rated 0.25 W) |
| Lightly loaded Class 2 secondary, 29 VAC / 41 V pk | IF pk 7.1 mA, 0.155 W total |
| 26.4 VDC either polarity | 4.4 mA, 0.105 W. The bridge makes polarity irrelevant |
| Assert / release | Assert: the opto discharges 1 µF at ≥ 1.4 mA, ≈ 2 ms. Release: rises to VIH (2.48 V) in −τ ln 0.25 ≈ 65 ms. Both are well inside the 0.5 s debounce (C-20 / C-31) |
| Open input | LED dark, pulled high: reads not asserted |

## 4. SEN65 rail (D-031, S-13)
- Runs directly from `+3V3`, with no power switch (D-047). 10 µF + 100 nF at J5; I²C pull-ups (10 k) to `+3V3`. A locked-up module needs a USB replug; firmware retries bus recovery and the module reset command first.
- J5 pinout per the SEN6x datasheet §3, Table 17: 1 VDD, 2 GND, 3 SDA, 4 SCL, 5 GND, 6 VDD (`sourcing/off-board.md`). Supply 3.15–3.6 V.

## 5. MCU, boot and recovery (G2 review S-14)
- EN: 10 k to 3V3 and 1 µF to GND (Espressif HW design guide RC). GPIO0: 10 k pull-up. No switches (D-041). Test pads for 3V3, 5V, GND, TXD0, RXD0, EN and BOOT (UART0 rescue), and SEN_SDA and SEN_SCL for probing I²C.
- **Recovery pads (layout):** two separate pairs, TP6 (EN) + TP2 (GND) and TP7 (BOOT) + TP8 (GND). Within a pair, set the gap to the board's minimum copper clearance (the DRC rule set at layout; check the fab's limit, about 0.13 mm at JLC from memory), so a screwdriver tip bridges it easily. Use one solder-mask opening per pair and no paste. Keep the pairs far enough apart (≥ 10 mm, center to center) to hold a screwdriver on each at once, and away from the other test pads, `+3V3`, `+5V` and fan-domain copper. Label them on silkscreen. To enter the bootloader: short BOOT, tap EN, then release BOOT.
- Strapping: GPIO3, 45 and 46 are not connected, so the internal defaults apply. With GPIO45 low, VDD_SPI is 3.3 V, which is right for the N16R8's 3.3 V flash and PSRAM. GPIO35–37 (octal PSRAM) are not connected. check.py asserts all of these.
- Reset states: FAN_PWM has a 10 k pull-down (LED dark, fan off). IND_R/G/B have 100 k gate pull-downs (dark). So only the display backlight comes on before firmware runs (the module's pull-up holds it on; harmless).
- Firmware backlog (not hardware): TWDT panic, RTC WDT, LEDC duty 0 before routing the pin.
- **Open (O-6):** confirm that GPIO47/48 run at 3.3 V on the N16R8 (VDD_SPI domain question).

## 6. Indicator (D-031, FR-15)
Six C601699 3528 common-anode RGB LEDs on `+5V`, one resistor per colour per LED, and three AO3400A low-side switches (a 2N7002 isn't specified at a 3.3 V gate; AO3400A is). Red 200 Ω: (5 − 2.0) / 200 = 15 mA. Green and blue 120 Ω: (5 − 3.0) / 120 = 16.7 mA, or 13 mA at Vf 3.4 V. All six full white ≈ 290 mA, so the 300 mA firmware cap is barely binding. Green is ~3× brighter, so colour balance happens in PWM. The count of 6 is provisional: mech sets it (D-031).

## 7. Display and touch (D-048)
- J6: 1×14, 8.5 mm socket (C2897377) for the Elecrow DLS29028B / LCDwiki MSP2834. 1 VCC (`+5V`), 2 GND, 3 CS, 4 RST, 5 D/C, 6 MOSI, 7 SCK, 8 LED, 9 MISO (NC), 10 CTP_SCL, 11 CTP_RST, 12 CTP_SDA, 13 CTP_INT, 14 SD_CS (NC; pulled up on the module). No local bulk cap: `+5V` is at its 10 µF limit (§1).
- Backlight: GPIO47 drives the LED pin directly, which is the gate of the module's BSS138 with a 10 k pull-up to its 3.3 V rail. Floating or high is on, low is off, and PWM works. Firmware drives it open-drain (LEDC with `GPIO_MODE_OUTPUT_OD`): the module's pull-up supplies the high, so the pin never fights a 3.3 V pull-up, whatever O-6 turns out to be. The former AO3401A is gone.
- Touch: on the module, CTP_SCL and CTP_SDA have 10 k to VCC on the header side and a BSS138 to the 3.3 V FT6336G (module schematic, 2022-12-02), so with VCC at 5 V those header pins idle at 5 V. The S3 isn't 5 V tolerant, so each line has a 2N7002 (gate `+3V3`, source to the GPIO with 10 k to `+3V3`, drain to J6). CTP_RST goes through the module's 74LVC245 and CTP_INT is 3.3 V; both have 10 k to `+3V3`.
- **Why 2N7002, not the AO3400A already on the board:** the AO3400A's 630 pF Ciss gives ≈ 5 µs rise at 10 k. The 2N7002 (50 pF, Basic) plus trace is ≈ 0.6 µs, inside I²C's 1 µs at 100 kHz but not 400 kHz, so **run the touch bus at 100 kHz**. When the touch side pulls low, the body diode takes the GPIO to ≈ 0.6–0.7 V, under the S3's V_IL (0.25 × VDD, from memory; verify), then the channel conducts.
- The physical-controls design this replaced is in `docs/physical-controls-record.md`.

## 8. Open items before layout
| ID | Item |
|----|------|
| O-1 | ~~SEN6x connector pinout~~: closed, datasheet Table 17 matches the schematic |
| O-2 | ~~Display module choice~~: closed, DLS29028B / MSP2834 (D-048, Q-35) |
| O-3 | Footprints against the LCSC drawings. Stock KiCad footprints are placeholders: H11L1S lead span (SMDIP W9.53), LTV-817S lead span (10.16 ± 0.3 mm tip to tip, 1.0 mm feet, so ≈ 9.2 mm foot centers against the W9.53 footprint), MB10S (MBS vs the MBLS footprint used), 3528 RGB pin map against the LED_ARGB symbol numbering, KF128L and XY350V terminals (the Phoenix PT footprint used differs), GH header, HRO USB-C pin map. Use `easyeda2kicad` footprints where they exist |
| O-4 | ~~VBUS hot-plug overshoot against the buck's abs max~~: closed by D-040, wide-input buck (§1) |
| O-5 | Opto package creepage. Pad-to-pad across the 9.53 mm gull-wing span is ≈ 7 mm, which comfortably exceeds the 3 mm basic barrier (D-028). Confirm from the drawings |
| O-6 | GPIO47/48 voltage on the N16R8. GPIO47 now drives the module's backlight FET gate directly, so 1.8 V would leave it near threshold |

# Evaluation: Waveshare ESP32-S3-Touch-LCD-2.8B instead of the custom PCB

**Date:** 2026-11-10 · **Status:** proposed, needs Andrew (D-053, Q-40…Q-43)
**Sources:** Waveshare wiki page, vendor schematic (`docs/vendor/waveshare-2.8b/schematic.pdf`, which has a GPIO allocation table), ESP-IDF demo source (`ESP32-S3-Touch-LCD-2.8B-Demo.zip`), and the dimension drawing (`docs/vendor/waveshare-2.8b/dimensions.pdf`). STEP from the same zip, not committed (21 MB): `https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-2.8B/ESP32-S3-Touch-LCD-2.8B-20241031.zip`.

## Verdict
It works. With two small reworks we get every required signal except `FAN_PRESENT` and the wired `DC_IN`, and those two can come back over I²C if we want them. Fail-off (SR-08) can't be met by PC817 modules alone. It needs a normally closed relay contact. Recommend switching.

## What the board gives us
- ESP32-S3R8 (8 MB octal PSRAM), 16 MB flash, native USB-C for flashing, logging and 5 V power. Board size 47.9 × 66.7 mm, glass 52.9 × 71.3 mm, 11.1 mm deep including the header. Four M2 threaded holes on a 40.9 × 59.7 mm pattern.
- 2.8" 480 × 640 IPS with an ST7701S over 16-bit RGB parallel; GT911 capacitive touch. Still touch-only, as in D-048.
- TCA9554 expander at 0x20: LCD_RST, TP_RST, LCD_CS, SD_CS, IMU_INT1/2, RTC_INT, buzzer. All eight pins are used and none is broken out.
- QMI8658 IMU, PCF85063 RTC, buzzer, TF slot, Li-ion charger (unused).

## Free GPIOs: the docs are wrong, the schematic is authoritative
| GPIO | Docs say | Schematic / demo | Usable for |
|------|----------|------------------|-----------|
| 16 | "Spare" | **GT911 TP_INT** (demo `I2C_Touch_INT_IO 16`) | Nothing: the touch controller drives it |
| 43 | UART TX | U0TXD through a 499 Ω series resistor, header only | Input (ROM boot log drives it briefly, current limited by the 499 Ω) |
| 44 | UART RX | U0RXD, header only | Output or input; it's an input through boot |
| 4 | Battery ADC | BAT_ADC through **R24 (0 Ω)** | Free once R24 is lifted (no battery fitted) |
| 0 | BOOT | 10 kΩ pull-up plus the BOOT key; strapping pin | **Output only** (an input pulled low at reset puts the chip in download mode) |
| 19/20 | USB | Native USB | Keep: flashing and logs |
| 33–37 | PSRAM | Octal PSRAM | Never |
| 7/15 | I²C | Shared bus: GT911 0x5D, QMI8658 **0x6B**, PCF85063 0x51, TCA9554 0x20 | SEN65, after fixing the address clash (below) |

That's four usable pins (43, 44, 4, 0), one of them output only. The console moves to USB-Serial-JTAG, so UART0 is free.

## Proposed allocation
| Signal | GPIO | Hardware | Notes |
|--------|------|----------|-------|
| `FAN_PWM` | 44 | PC817 module, node side driven; output transistor across fan yellow–GND_F | **Inverted:** LED on pulls the speed line low (fan slower). A pull-up from 3V3 to the module input keeps the LED on through reset and boot, so the fan is held off (see Fail-off). |
| `FAN_TACH` | 43 | PC817 module, LED fed from +10V_F into white (as in the current U2); output pulled up to 3V3 | 30–150 Hz, so PC817 speed is fine. Read with PCNT or an ISR once the app is running |
| `OCC_IN` | 4 (R24 lifted) | **AC-input** opto module (bridge or PC814) for 24 VAC | A plain PC817 DC module would see −34 V peak across a 6 V LED. Needs AC rating |
| Indicator | 0 | Addressable LED strip, 5 V from the header's 5V pin, RMT | Strapping is safe: the LED's DIN is high-Z. 3.3 V data into 5 V WS2812B is marginal (V_IH 0.7·VDD = 3.5 V), so check it on the bench; fallback is an AHCT125 breakout, or one diode drop on the strip's supply |
| SEN65 | I²C 7/15, external I²C header | 3V3 from the header | 0x6B clashes with the QMI8658 (see Q-42) |
| `FAN_PRESENT` | — | dropped | FR-18's fan-port fault goes. The tach fault stays and still catches "commanded on, not spinning" |
| `DC_IN` | — | dropped | Back to BLE only (D-016), which reverts D-025 / AC-06 |

## Fail-off (SR-08): PC817 modules alone can't do it
An opto can only pull the speed line low while its LED is lit. With the node unpowered the LED is dark, the fan's 2.2 kΩ pull-up wins, and the fan runs at **full** speed. The custom board solved this with a stage powered from the fan side (D-023). No off-the-shelf module does that. The same is true of the non-isolated level-shifter route: a BSS138 shifter releases the line when the node is unpowered.

**Proposal:** a 1-channel 5 V relay module, its coil energized whenever the board has power (input tied active, no GPIO), with its **NC contact across yellow–GND_F**.
- Node unpowered: NC closed, line low, fan off. This is passive, so there's no burst when fan mains returns, which is better than D-028's accepted exception.
- Node booting: relay energized, but the pull-up keeps the PWM opto's LED on, so the line stays low and the fan off.
- Node running: firmware drives the inverted PWM. 0 % LED gives full speed.
- Hung firmware: same exposure as the custom board (GPIO state frozen until the task watchdog reboots).
Cost: about 70 mA of continuous coil current from USB, one module and one resistor. SR-08's wording ("powered from the fan side") needs a small amendment: the hold-off becomes a passive NC contact. The intent is unchanged.

## Risks to check on the bench before G4
1. **PC817 at 5 kHz.** The turn-off time into the fan's 2.2 kΩ pull-up distorts duty, and `sourcing/fan-pwm-thread.md` already flagged it. A 3.3 V module with a ~1 kΩ input resistor gives only about 2 mA of LED current, about 2 mA of sink at CTR ≈ 100 %. Pulling a 2.2 kΩ pull-up to 10 V low takes about 4.5 mA. **Choose a module with ≤ 470 Ω on the input** (or swap its resistor) and scope the yellow line at 10/50/90 %. Fallback: a lower PWM frequency if the fan accepts it, or an H11L1 module.
2. **RGB panel and Wi-Fi.** RGB panels on the S3 drift or tear under PSRAM and flash contention (Wi-Fi, OTA writes). Plan on esp_lcd RGB bounce buffers from the start.
3. **Module wiring.** Four or five modules plus Dupont or screw-terminal interconnect, in a dusty shop. Use the screw-terminal versions and ferrules, and strain-relieve everything to the enclosure.
4. **Barrier quality.** Hobby opto modules don't control creepage. That's acceptable because the fan port is SELV (D-028) and the barrier is functional, for ground-loop and touch noise (process note 2026-11-09), not for safety.

## What changes
- **Dropped:** `pcb/` custom board (schematic and placement stay in git as the reference design), JLC PCBA, Q-38/Q-39 (moot), FR-18's fan-port fault, D-025 wired DC input, the FT6336G/Elecrow display (D-048 hardware).
- **Mech:** the enclosure is redone around the Waveshare board (its STEP, M2 holes) plus a module tray. The USB-C is on the board edge, so we need a panel-mount USB-C extension or an edge cutout, which reopens D-030's external gasketed receptacle.
- **Firmware:** ST7701S RGB + GT911 + TCA9554 drivers (Espressif component registry), 480 × 640 LVGL layout, inverted PWM, RMT LED, USB-Serial-JTAG console. The pure-C++ control logic is unaffected apart from removing `fan_port` and `dc_wired`.
- **Cost:** board price, unverified, roughly $25–35, plus about $10–15 in modules, against about $151 for two PCBA boards plus the display. G4 confirms.
- **Reverts / amends:** D-008 (custom PCB), D-022, D-030 (USB-C path), D-031 (indicator), D-048 (display hardware), D-025, D-050 (barrier now off-the-shelf modules), SR-08 wording, FR-18, IR-01.

---

# Option B (Andrew, 2026-11-10): Waveshare board + minimal custom carrier PCB

The Waveshare board keeps the ESP32-S3, display, touch, USB-C and 3.3 V supply. Our PCB is a backpack plugged onto its 2×12 header (2.54 mm, M2 standoffs on the same 40.9 × 59.7 mm hole pattern). It holds only what modules do badly: the isolated **fail-off** fan interface (D-023, unchanged), the occupancy and DC optos, the SEN65 connector and the LED-strip driver. Nothing on it needs the ESP32 module, USB, regulator, display socket or touch shifters.

## Pin plan: every signal kept, no relay, no Waveshare rework
| Signal | Where | Carrier circuit |
|--------|-------|-----------------|
| `FAN_PWM` | GPIO44 (input through boot) | H11L1 + Q1 powered from +10V_F, exactly as now. 10 kΩ pull-down keeps the LED dark → **fan held off unpowered, in reset and booting** (SR-08 as written) |
| `FAN_TACH` | GPIO43 | LTV-817, 22 kΩ pull-up. The ROM boot log drives TX through Waveshare's 499 Ω; harmless against an opto collector |
| Indicator | GPIO0 | 2N7002 inverter, 1 kΩ pull-up to 5 V, 10 kΩ gate pull-up to 3V3 (keeps GPIO0 high for a normal boot and the strip's DIN low/idle). RMT with `invert_out`. Strip off-board on a 3-pin terminal |
| `FAN_PRESENT`, `OCC_IN`, `DC_IN` | **PCA9536** 4-bit I²C expander, fixed 0x41 (no clash), polled at 10 Hz | LTV-817 (+ MB10S on the AC inputs), as now. One input spare |
| SEN65 | **TCA9543A** I²C switch, 0x70, channel 0 | Fixes the 0x6B clash with the board's QMI8658 without rework, and keeps the SEN65 cable's capacitance and noise off the touch bus |
| GPIO4 | spare (R24 stays) | — |

Power comes from the header: 3V3 (Waveshare MP1605, 2 A) for the logic and SEN65, 5V (direct VBUS) for the strip, with the 300 mA firmware cap kept.

## Cost: what moves parts toward Basic and fees toward zero
Live JLC data, 2026-11-10 (parts API and part pages). JLC exposes no "preferred" or "promotional" flag on these parts, so check that at BOM upload. **Fees:** the sources disagree on the Extended-part fee: $3.07 (our notes) or $1.50 (a third-party note dated 2025-12). Both are shown.

| Lever | Effect |
|-------|--------|
| **JLC Economic, not Standard.** Possible now because no ESP32 module is on our board. All the S3 modules are "Standard Only"; every carrier part checked is Economic-eligible | Setup + stencil $9.71 instead of $33.77. Basic parts carry no fee (Standard charged $1.53 each, for all 28) |
| **You hand-solder all THT and connectors:** 2×12 socket, KF128 terminals, GH-6 | No hand-solder fee, and three fewer Extended lines |
| Basic only, wherever there's a choice: LTV-817, MB10S, AO3400A, 2N7002, 0603 passives | Placed for free on Economic. Consolidating values no longer saves anything |
| LED strip off-board (it can also wrap the room-side corner, D-033); the carrier sits behind the display anyway | No LED parts on board (the 2812-class parts that can wrap a corner are mostly "Standard Only") |
| Remaining Extended placed: **H11L1, PCA9536, TCA9543A** | 3 × $1.50–3.07 |
| Board ≈ 50 × 70 mm, under 100 × 100 | Cheapest 2-layer tier |

**Estimate for 2 carriers (unquoted):** fees $14–19, joints <$1, parts ≈ $5 (≈ $2.50/board), PCBs ≈ $2–5, shipping ≈ $10–20 → **≈ $32–50**. Hand-soldered connectors ≈ $3–5. LED strip ≈ $5–10. Waveshare board ≈ $25–35 (its non-touch listing is $22.99–29.99; touch price unverified).
**One complete unit, electronics ≈ $65–100**, against $144 for the current plan (2 custom boards plus display).

## More cuts, with what each costs
| Cut | Saves (2 boards) | Price |
|-----|------------------|-------|
| H11L1 → LTV-817 (Basic) for PWM; drop the Q1 gate pull-up to 2.2 kΩ to speed turn-off | $2.40–4 | Duty distortion at 5 kHz (storage time, roughly tens of µs out of 200). Bench check needed; firmware can map duty to tach. **Not recommended**: the one place speed matters |
| Remove the QMI8658 from the Waveshare board instead of using the TCA9543A | $2.90–4.50 | Hot-air an LGA-14 next to the RGB FPC, and the SEN65 shares the touch bus |
| Lift R24, OCC on GPIO4, drop the PCA9536 (and with it FAN_PRESENT and DC_IN) | $3.20–4.70 | The signals Option A had to drop anyway |
| DIY assembly (bare PCB + $7 stencil + LCSC parts) | ≈ $5–15 | LCSC shipping eats most of it; ~1 h per board |

## Honest comparison
A lean **all-custom** board (S3 module hand-soldered so Economic applies, AMS1117 (Basic) instead of the buck, connectors hand-soldered) works out to ≈ $50–75 for 2 boards plus a $10.90 display, about the same as Option B. B's case isn't price. It's that the riskiest custom work (module, USB, power, display) becomes a proven board, the custom board shrinks to ~40 parts with no RF or USB, and we get a 480 × 640 IPS panel. B costs us: the RGB display firmware (bounce buffers, Wi-Fi drift), a stack-up enclosure, and dependence on one Waveshare SKU.

---

# Chosen (Andrew, 2026-11-10): route B, stripped down
Andrew chose route B with three cuts: LTV-817 for PWM, desolder the QMI8658 (U6) on the Waveshare board, and lift R24. Taking the R24 cut means no expander, so `FAN_PRESENT` and `DC_IN` are dropped (Q-43).

| Signal | Pin | Carrier circuit |
|--------|-----|-----------------|
| `FAN_PWM` | GPIO44 | Node side: 390 Ω to the LTV-817 LED, 10 kΩ pull-down (dark through reset and boot). Fan side: LTV-817 output pulls Q1's (AO3400A) gate low against **2.2 kΩ** to +10V_F (was 10 kΩ, to speed turn-off). LED lit → Q1 off → line released → fan runs. Unlit or unpowered → Q1 on → **fan off** (SR-08 unchanged) |
| `FAN_TACH` | GPIO43 | LTV-817, LED from +10V_F through 10 kΩ into white; 22 kΩ pull-up to 3V3 |
| `OCC_IN` | GPIO4 (R24 lifted) | 10 kΩ 1206 → MB10S → LTV-817; 47 kΩ / 1 µF; firmware debounce C-20 |
| Indicator | GPIO0 | 2N7002 inverter, 1 kΩ to 5V, 10 kΩ gate pull-up to 3V3; on-board SK6812SIDE-A row on the carrier's room-side edge, 100 nF each (D-055) |
| SEN65 | I²C 7/15 directly (U6 removed) | 6-pin GH, hand-soldered |

- **Fan-side budget:** gate pull-up (10 − 0.2) / 2.2 k ≈ 4.5 mA (only while the LED is lit) plus the tach LED at 0.9 mA, about 5.4 mA, within the ≤ 9 mA the port supplies (Q-26). The H11L1 (1.3 mA) and the presence opto are gone.
- **PWM drive margin:** I_F ≈ (3.3 − 1.2) / 390 ≈ 5.4 mA. C-rank CTR ≥ 200 % gives ≥ 10.8 mA against the 4.5 mA needed, a 2.4× margin, or 1.2× after 50 % aging. If the bench shows marginal saturation, drop to 270 Ω.
- **Bench check (before G4):** scope the yellow line at a commanded 10/50/90 % at 5 kHz. Expect the high time to stretch by the LTV-817 storage time plus the gate RC. Firmware can map commanded duty to tach. If the error is too large, try a lower PWM frequency on the fan.
- **Carrier BOM:** one Extended part, SK6812SIDE-A (D-055); everything else Basic. LTV-817 ×3, MB10S, AO3400A, 2N7002, and 0603/1206 resistors and capacitors are all Basic and Economic-eligible (live check, 2026-11-10). JLC Economic fees ≈ $9.71 per order, plus one Extended fee ($1.50–3.07) for the LEDs.
- **Cost (unquoted):** 2 carriers ≈ $28–42 (fees ≈ $11–13, parts ≈ $3, PCBs $2–5, shipping $10–20). One unit's electronics ≈ $58–87 with the Waveshare board, and hand-soldered connectors (no strip).
- **Rework on each Waveshare board:** lift R24 (0 Ω, BAT_ADC → GPIO4), and hot-air U6 (QMI8658, LGA-14). Then check that I²C 0x6B answers only once the SEN65 is plugged in.

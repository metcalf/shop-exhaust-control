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

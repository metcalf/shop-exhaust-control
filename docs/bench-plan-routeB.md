# Bench plan: Waveshare ESP32-S3-Touch-LCD-3.5 and fan-stage check (route B, D-054, D-056)

For Andrew. Do steps 1–3 before the carrier layout is frozen, and step 4 before G4. Record each result in this file: nothing below counts as tested until its result is written here.

## 1. Stock board, no battery fitted
- **Revision:** note the revision on the back label (V1 or Rev 2.0).
- **Demo:** flash the Waveshare ESP-IDF demo (GitHub `waveshareteam/ESP32-S3-Touch-LCD-3.5`). Confirm the display, touch, and USB-Serial-JTAG logging work.
- **I²C scan on GPIO7/8.** Expect:
  - 0x18 (ES8311)
  - 0x20 or 0x21 (TCA9554)
  - 0x34 (AXP2101)
  - 0x38 (FT6336)
  - 0x51 (PCF85063)
  - 0x6A (QMI8658)
  - Nothing at 0x6B.
- **Result:**

## 2. AXP2101 power-on (decides whether the carrier's PWRON one-shot gets fitted, D-056)
- **Cold start:** with no battery, plug in USB-C from a wall adapter. Without touching PWR, does the board boot? Repeat 5 times, unplugged for ≥ 10 s each time.
- **Power-on source:** in firmware, read REG20 (PWRON status) and log it. Expect bit 2 = 1 ("VBUS insert and good").
- **Off state with USB present:** hold PWR 6 s until the board turns off. Then unplug USB, wait 10 s and replug. Does it boot without a click?
- **Short power cut:** cut USB for ~0.5 s (switch the adapter at the wall) and record whether the board comes back.
- **Decision:**
  - If every case boots unaided, the one-shot stays DNP.
  - If any case doesn't, hand-fit Q2/C1/R1/R2/D1 on the carrier. Then measure the PWRON low time on a scope and trim R1/R2 into 2.5–5 s.
- **Result:**

## 3. Fan-side stage on a breadboard (5 parts, mirrors the carrier's U1/Q1)
- **Wiring:**
  - Node side: LTV-817 LED from GPIO38 through 390 Ω, with 10 kΩ to GND.
  - Fan side: LTV-817 collector to the AO3400A gate, emitter to fan GND, and 2.2 kΩ from the gate to fan red (+10 V).
  - AO3400A drain on fan yellow.
- **Node unpowered:** plug in the fan. Expect it to stay **off**, with yellow held low.
- **Duty sweep:** command 10 / 50 / 90 % at 5 kHz from LEDC. Scope yellow on the fan side and record high-time duty against the command. Expect the high time to be stretched by the LTV-817's turn-off time.
- **If the ends misbehave or the duty error is > ~5 points:** try 270 Ω, then a lower LEDC frequency.
- **Tach map:** record the tach frequency at each command. Firmware uses this as its duty → tach map.
- **Result:**

## 4. With a carrier fitted (after PCBA)
- **Header:** J8 orientation is correct, and 3V3 and 5V read correctly at TP2 and TP3.
- **Indicator:** LEDs stay dark until firmware runs. The chain lights with RMT `invert_out`, in GRB order, and the edge emission reaches the diffuser.
- **Presence:** with the fan cable plugged in, `FAN_PRESENT` reads low. Unplugged, it reads high.
- **Inputs:** `OCC_IN` and `DC_IN` follow 24 VAC applied at J3 and J4.
- **Repeat:** run step 3 on the carrier, then the AC-18 boot hold-off check.
- **Result:**

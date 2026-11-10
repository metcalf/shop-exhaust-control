# Bench plan: Waveshare rework and fan-stage check (route B, D-054)

For Andrew, before carrier layout is frozen (steps 1–3) and before G4 (step 4). Record results in this file. Nothing below counts as tested until its result is written here.

## 1. Stock board first (before any rework)
- Flash the Waveshare ESP-IDF demo (`ESP32-S3-Touch-LCD-2.8B-Demo.zip`, ESP-IDF folder). Confirm display, touch and USB-Serial-JTAG logging.
- Run an I²C scan on GPIO7/15. Expect 0x20 (TCA9554), 0x51 (PCF85063), 0x5D (GT911), 0x6B (QMI8658).
- **Result:**

## 2. Rework
- **R24** (0 Ω, BAT_ADC → GPIO4): lift or remove it. Check: GPIO4 reads high with the internal pull-up and low when you ground it at J7 pin 13.
- **U6** (QMI8658, LGA-14): hot-air it off. Keep the RGB FPC shielded (Kapton plus foil). Check: the demo still runs, and the I²C scan shows no 0x6B.
- Plug in the SEN65 at J7 (3V3 pin 21, GND pin 23, SCL pin 17, SDA pin 19). Check: 0x6B appears, and a measurement frame reads back.
- **Result:**

## 3. Fan-side stage on a breadboard (5 parts, mirrors the carrier U1/Q1)
Wiring: LTV-817 LED from a GPIO44 test pin through 390 Ω, with 10 kΩ to GND. On the fan side, the LTV-817 collector goes to the AO3400A gate, the emitter to fan GND, 2.2 kΩ from gate to fan red (+10 V), and the drain on fan yellow.
- With the node unpowered, plug in the fan. Expect the fan to stay **off**, with yellow held low.
- Command 10 / 50 / 90 % at 5 kHz from LEDC. Scope yellow (fan side) and record the high-time duty against the command. Expect the high time to be stretched by the LTV-817 turn-off time.
- If the 90 % → 100 % or 10 % ends misbehave, try 270 Ω. If the duty error is more than about 5 points, try a lower LEDC frequency and record whether the fan follows it.
- Record the tach frequency at each command. That gives the duty → tach map firmware will use.
- **Result:**

## 4. With a carrier fitted (after PCBA)
- GPIO0 at reset is ≥ 2.5 V, the board boots normally, and the LEDs are dark until firmware drives them.
- The LED chain lights through the 2N7002 with RMT `invert_out`. Check the colors are in GRB order, and that the edge emission reaches the diffuser.
- Repeat step 3 on the carrier. Also check the AC-18 boot-hold-off on the carrier.
- **Result:**

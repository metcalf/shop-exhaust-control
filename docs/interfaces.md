# Interface Control Document

**Status:** complete for G2 (drafted 2026-10-25, nightly). §2, §3 and §5 rewritten 2026-11-10 for route B (D-054, D-055). Andrew approves at G2. The **DC coupling** section (§1) is shared with the future dust collector project; changes to it need a decision entry, because both systems depend on it.

Companion docs: `docs/architecture.md` (block diagram, power, cost), `docs/control-logic.md` (state machine). Pin numbers and part names here are architecture-level: phase 3 confirms them against datasheets (list in `docs/architecture.md` §9).

## 1. DC coupling (shared with the DC controller project)

| Field | Value |
|-------|-------|
| Signal name | `DC_RUNNING` |
| Direction | DC controller → exhaust controller |
| Meaning | Asserted while the DC motor is **commanded on**, including the DC's own run-on. Whether the motor is confirmed running (current sensing) is a separate flag (bit 3) that the exhaust side ignores in v1. |
| Transport | BLE 4.x **legacy, non-connectable advertising** (`ADV_NONCONN_IND`) from the DC node (D-016). No wired backup (D-025 reverted by D-054: no spare pin). No MQTT path. |
| Advertising interval (DC side) | 100 ms for 5 s after any payload change, then 500 ms. The fast burst makes assertion latency independent of the scanner's duty (AC-22: ≤ 3 s). |
| Scanning (exhaust side) | Passive scan, window 30 ms every 100 ms (30 %), duplicate filtering off, coexisting with Wi-Fi (D-016, D-021). |
| Failure behavior | No valid advertisement for P-24 (10 s) is treated as "DC not running". FR-09 then holds the boost floor for P-11 more, so a short reception gap is invisible to the fan. Exhaust Auto still works on PM/VOC alone. |
| Authentication | None in v1: a spoofed `DC_RUNNING` only boosts the exhaust. Any future command *to* the DC (message type 0x02) must carry the MAC field (bytes 13–20) from a shared key plus the sequence counter as a replay guard. Stopping the DC stays hardwired at the DC. |
| Sender filter | Optional compile-time allow-list of DC node BLE addresses (empty = accept any valid frame). Set once the DC node exists. |
| Interim source (before the DC controller exists) | None (Q-12). A bench test sender (any ESP32 running the same encoder) is used for AC-06 and AC-22. |
| Wired backup (DC side) | *Dropped (D-054).* If BLE proves unreliable, the fallback is a v2 carrier or an MQTT path, decided then. |

### 1.1 Payload: manufacturer-specific data (AD type 0xFF)

Byte offsets within the AD data, after the AD length/type bytes. Multi-byte fields little-endian. Total 21 bytes, fits a legacy advertisement next to the 3-byte Flags AD.

| Offset | Size | Field | v1 value / meaning |
|--------|------|-------|--------------------|
| 0 | 2 | Company ID | `0xFFFF` (Bluetooth SIG value reserved for internal/test use; no registered ID needed for a private two-node link) |
| 2 | 2 | Magic | `0x4D 0x53` ("MS"): distinguishes our frames from other `0xFFFF` users |
| 4 | 1 | Version | high nibble = major (1), low nibble = minor (0). Receivers reject a different major; accept any minor and ignore trailing bytes they don't know |
| 5 | 1 | Message type | `0x01` DC status (DC → others). `0x02` reserved: command to DC (needs MAC). `0x03` reserved: exhaust status (exhaust → shared panel) |
| 6 | 1 | Sender ID | `0x01` DC controller, `0x02` exhaust controller, `0x10–0x1F` test senders |
| 7 | 2 | Sequence | uint16, increments on every payload change and at least once per 10 s; wraps |
| 9 | 1 | Flags | bit 0 `DC_RUNNING` (commanded on, incl. run-on); bit 1 DC fault; bit 2 manual force-on active; bit 3 motor current confirmed; bit 4 current sensing present; bits 5–7 reserved = 0 |
| 10 | 1 | Run-on remaining | minutes, 0–254; 255 = unknown/not in run-on. Informational |
| 11 | 2 | DC status word | reserved for the DC project (open-gate count, filter ΔP band, etc.); 0 in v1 |
| 13 | 8 | MAC | reserved for authenticated message types; 0 for type 0x01 |

Exhaust-side handling: a frame is valid if company ID, magic, major version and type 0x01 match and the length is ≥ 10 bytes. The link layer reports `dc_running` (bit 0 of the last valid frame, or false after P-24 of no valid frames), last RSSI, and frame age. The parser and link timeout are pure C++ and host-tested (AC-22 sim part).

Boost behavior (how long, what level, what happens after the DC stops) belongs to the **exhaust** side (FR-09), not here.

## 2. Electrical I/O (exhaust node)

Route B (D-054): a **Waveshare ESP32-S3-Touch-LCD-2.8B** (ESP32-S3R8, 16 MB flash, 480×640 ST7701S RGB panel, GT911 touch, USB-C) with our **carrier PCB** plugged onto its 2×12 2.54 mm header J7 and fixed on the same M2 pattern (40.9 × 59.7 mm). Sources: `docs/vendor/waveshare-2.8b/schematic.pdf`, `docs/eval-offtheshelf-board.md` ("Chosen"). Every other S3 pin is taken by the panel, PSRAM, flash or USB.

**Rework on each Waveshare board (Andrew):** lift R24 (0 Ω, BAT_ADC → GPIO4); remove U6 (QMI8658 IMU, I²C 0x6B, clashes with the SEN65). Both are on the bench plan.

**J7 pins the carrier uses** (Waveshare numbering): 1, 2 `USB_5V`; 5, 6, 23, 24 GND; 11 GPIO0; 13 GPIO4; 17 SCL (GPIO7); 18 GPIO43 (U0TXD, 499 Ω series on the Waveshare board); 19 SDA (GPIO15); 20 GPIO44 (U0RXD); 21, 22 3V3. Not connected: 3 VCC, 4 BAT, 7/9 USB D−/D+, 8/10/12/14/16 PSRAM (GPIO33–37), 15 GPIO16 (touch INT). The console is USB-Serial-JTAG, so UART0 is free.

| Signal | Dir | Type | Level | Connector | GPIO (J7 pin) | Notes |
|--------|-----|------|-------|-----------|---------------|-------|
| `FAN_PWM` | Out | Opto LED drive (§2.1) | 3.3 V, ≈ 5.4 mA | J-FAN (two 2-pos 3.5 mm screw terminals, fan side of the barrier; D-049) | 44 (20) | LEDC 5 kHz, ≥ 10-bit. LED on = speed line released. 10 kΩ pull-down keeps the LED dark through reset and boot (GPIO44 is an input then) |
| `FAN_TACH` | In | Opto phototransistor, 22 kΩ pull-up | 3.3 V | J-FAN | 43 (18) | 30–150 Hz, PCNT or ISR. The ROM boot log drives GPIO43 through the Waveshare 499 Ω; into the opto collector that's ≤ 6.6 mA, harmless |
| `OCC_IN` | In | AC-input opto, RC-filtered (§2.2) | 3.3 V, low = 24 VAC present | J-OCC (2-pos 3.5 mm screw terminal) | 4 (13), R24 lifted | Debounce C-20 |
| Indicator data | Out | 2N7002 inverter → SK6812SIDE-A chain (D-055) | 3.3 V gate, 5 V data | on carrier | 0 (11) | RMT, `invert_out`. 10 kΩ gate pull-up to 3V3 holds GPIO0 high at reset (normal boot) and the chain's DIN low (idle). 1 kΩ drain pull-up to 5 V. 100 nF per LED. Firmware caps total LED current at 300 mA |
| SEN65 I²C SDA / SCL | Bidir | I²C 100 kHz, shared with GT911 0x5D, TCA9554 0x20, PCF85063 0x51 | 3.3 V | J-SEN (SEN65's 6-pin GH 1.25 mm, hand-soldered) | 15 / 7 (19 / 17) | Pull-ups are on the Waveshare board (value to read from its schematic in the carrier step); DNP pads for extra pull-ups on the carrier. SEN65 0x6B is unique once U6 is removed. Cable < 10 cm |
| Display, touch, RTC, expander | — | On the Waveshare board | — | — | — | ST7701S 16-bit RGB (bounce buffers, D-054), GT911, TCA9554 resets/CS. Not our hardware |
| USB: power in + flash/log | Bidir | Native USB on the Waveshare board | 5 V | Waveshare USB-C on its board edge | 19 / 20 | D-030 path, now on the Waveshare board; reached through a gasketed wall opening (§5, NFR-04) |

Dropped by D-054: `FAN_PRESENT` (FR-18 fan-port fault) and the wired `DC_IN` (D-025).

**S6 control port (UIS), measured by Andrew 2026-10-25 (Q-15):** black = GND, red = +10 V from the fan (low current), yellow = speed (fan pulls up via 2.2 kΩ; the controller pulls it low; 5 kHz PWM, high-time duty = speed; 20/46/100 % at levels 1/4/10), white = tach (50 % square, ~30/75/144 Hz at levels 1/4/10; stock controller pulls it up 10 kΩ to its 5 V). Unplugged = full speed. Andrew hard-wires the four conductors into J-FAN by color (Q-25, D-026): J2 `GND (BLK) / +10V (RED)`, J7 `SPD (YEL) / TACH (WHT)` (carrier refdes reassigned in the carrier schematic). Fan GND vs. mains (Q-22, Q-30, Q-31): ≈ 60 µA capacitive coupling, SELV in practice (SR-09, D-028).

### 2.1 Fan interface: isolated, fail-off (SR-08, SR-09, FR-10, FR-18)

Everything left of the barrier is powered by the fan's own +10 V and referenced to fan GND; nothing on it connects to node ground, the panel or USB. D-023 topology with the H11L1 replaced by an LTV-817 (Q-44).

```
 FAN SIDE (GND_F, powered from fan red +10 V)          ║ barrier ║  NODE SIDE (GND, 3V3)
                                                        ║  ≥3 mm  ║
 yellow ──── D  Q1 AO3400A                              ║         ║
             S ── GND_F                                 ║         ║
             G ──┬──[2.2k]── +10V_F (Q1 ON by default   ║         ║
                 │                 → yellow low → OFF)  ║         ║
                 └── U1 C (LTV-817), E ── GND_F         ║ U1 LED ─╫──[390Ω]── GPIO44 FAN_PWM
                                                        ║         ║           └[10k]─ GND
 white ───── U2 LED cathode;                            ║ U2 C ───╫── GPIO43 FAN_TACH (22k → 3V3)
              anode ──[10k]── +10V_F                    ║ U2 E ── GND
```

- **Node unpowered, in reset or booting:** U1 dark → Q1 gate pulled to +10V_F → yellow held low → **fan off** (SR-08). Needs only fan power.
- **Running:** U1 lit → gate low → Q1 off → the fan's 2.2 kΩ takes yellow high. Fan duty = LED-on fraction; no inversion in firmware.
- **Tach:** white low → U2 lit → `FAN_TACH` low.
- **Fan-side current from red:** gate pull-up ≈ 4.5 mA (only while U1 is lit) + tach LED ≈ 0.9 mA ≈ 5.4 mA, inside the ≈ 9 mA the port supplies (Q-26).
- **PWM drive margin:** I_F ≈ (3.3 − 1.2) / 390 ≈ 5.4 mA; CTR ≥ 200 % (C rank) → ≥ 10.8 mA sink against 4.5 mA needed (2.4×, 1.2× after 50 % aging). 270 Ω if the bench shows marginal saturation.
- **Timing:** LTV-817 turn-off (storage) is tens of µs against a 200 µs period, so the high time stretches. Bench check: scope yellow at 10/50/90 % commanded; firmware maps commanded duty to tach, or the fan PWM frequency drops if the fan accepts it.
- **Barrier:** LTV-817 UL 1577 5 kV rms. PCB creepage and clearance ≥ 3.0 mm across the barrier (D-050, `pcb/SAFETY.md`). Functional (ground loop, ~65 VAC float on fan GND), since the port is SELV in practice (D-028).

J-FAN sits on the fan side of the barrier, with ≥ 3 mm to any node-side copper.

### 2.2 Occupancy input (FR-07)
24 VAC from the lighting transformer's secondary (Q-16) → J-OCC (2-pos KF128L) → 10 kΩ 1206 (D-049) → MB10S → LTV-817 LED (D-036, D-045). Output: 47 kΩ pull-up to 3.3 V and 1 µF to GND → GPIO4. No input TVS (D-046). Same ≥ 3 mm barrier. Worst cases in `pcb/design.md` §3. Firmware debounce C-20 (0.5 s).

### 2.3 Wired `DC_RUNNING` input
*Dropped (D-054).* IR-01 is BLE only.

## 3. Power (D-018, D-030, D-054)

- **Mains:** none in the enclosure or on any of our boards (SR-01). The fan and the node's adapter both plug into the always-on receptacle in the fan cabinet (IR-05, D-013). SR-01a is not triggered.
- **Adapter (D-030):** UL-listed 5 V USB-C wall adapter, ≥ 2 A, LPS, into the Waveshare board's USB-C. Cable ≤ 3 m, USB 2.0 data, 24 AWG or heavier power conductors. Flashing and wired logs: swap the adapter for a PC on the same cable.
- **Waveshare board:** USB_5V → its own 3.3 V regulator (MP1605 per the schematic; verify rating at bring-up) for the ESP32, panel logic and the I²C devices. Battery charger unused (no cell fitted). Protection on USB_5V is whatever Waveshare fitted; ours adds none.
- **Carrier:** takes `USB_5V` (J7 1–2) for the LEDs and `3V3` (J7 21–22) for the opto pull-ups and the SEN65 (10 µF + 100 nF at J-SEN). No regulator on the carrier.
- **Budget** (estimates; measure at bring-up):

| Load | Rail | Typical | Peak | Source |
|------|------|---------|------|--------|
| Waveshare board: ESP32-S3 Wi-Fi + BLE scan, panel + backlight | 5 V | ≈ 250 mA | ≈ 500 mA (TX) | Estimate; Waveshare doesn't publish it |
| Carrier optos, pull-ups | 3.3 V | 6 mA | 12 mA | §2 |
| SEN65 measuring | 3.3 V | 90 mA | 350 mA for 2 ms | SEN6x DS Table 12 |
| Indicator (SK6812SIDE-A, ≈ 4–8) | 5 V | 60 mA | 300 mA (firmware cap) | One band color; quiescent ≈ 0.6 mA per LED |
| **Total at 5 V** | 5 V | **≈ 0.4 A (2 W)** | **≈ 1.1 A**, ms-scale | |

A ≥ 2 A adapter keeps ~2× margin. About 2 W dissipates in the sealed compartment, a few kelvin of rise; the SEN65 offset is tuned at commissioning (FR-20).
- **Fan side:** powered by the fan's +10 V (§2.1), not by the node.

## 4. Home Assistant (FR-12, FR-13, IR-03)

MQTT with discovery, following the `HassMessages` (pure, host-tested topic/discovery builder) plus `Mqtt*HomeClient` (`BaseMqttClient`) split from hvac_control. One HA device, "Shop Exhaust". State goes out as one JSON document on `shop_exhaust/state`, and each entity's discovery config picks its field with a `value_template`. Availability is `shop_exhaust/availability` with an MQTT last will (`0`), so HA marks every entity unavailable when the node drops (FR-13, AC-09).

**Publish policy:** the state document goes out every 1 s while the SEN65 is measuring and any field has changed by more than its resolution, at least every 60 s otherwise, and immediately on any mode, fault or occupancy change. At 1 Hz this is ~86 k states per entity per day in the HA recorder. That's intended (FR-12 replay), but exclude the raw channels from long-term statistics if the database grows.

**Read-only:** no command topics in v1 (FR-16 dropped).

| Entity | Type | Unit / class | Category | Requirement |
|--------|------|--------------|----------|-------------|
| `sensor.shop_exhaust_pm1_0` / `_pm2_5` / `_pm4_0` / `_pm10` | sensor | µg/m³; `pm1` / `pm25` / — / `pm10` | — | FR-12 |
| `sensor.shop_exhaust_nc_pm0_5` … `_nc_pm10` (5) | sensor | #/cm³ | diagnostic | FR-12 |
| `sensor.shop_exhaust_voc_index` | sensor | index (node algorithm, D-017) | — | FR-12, FR-14 |
| `sensor.shop_exhaust_nox_index` | sensor | index (module) | — | FR-12 |
| `sensor.shop_exhaust_voc_raw` / `_nox_raw` | sensor | ticks | diagnostic | FR-12 (replay) |
| `sensor.shop_exhaust_voc_index_module` | sensor | index (module's own algorithm, for comparison) | diagnostic | FR-14 (D-017 check) |
| `sensor.shop_exhaust_temperature` / `_humidity` | sensor | °C `temperature` / % `humidity` | diagnostic | FR-20 |
| `sensor.shop_exhaust_fan_speed` | sensor | % (commanded duty) | — | FR-12 |
| `sensor.shop_exhaust_fan_tach` | sensor | Hz (pulses/rev unknown; RPM once known) | diagnostic | FR-12, FR-18 |
| `sensor.shop_exhaust_state` | sensor | text: `Auto`, `Hold 60%`, `Quiet`, `Boost`, `Spray`, `Spray clearing` | — | FR-12 |
| `sensor.shop_exhaust_state_remaining` | sensor | min (`duration`) | — | FR-12 |
| `sensor.shop_exhaust_demand_source` | sensor | text: `floor`, `pm`, `voc`, `dc`, `vacant_cap`, `off` | diagnostic | FR-12 (tuning) |
| `binary_sensor.shop_exhaust_occupied` | binary_sensor | `occupancy` | — | FR-07, FR-12 |
| `binary_sensor.shop_exhaust_dc_running` | binary_sensor | `running` (BLE) | — | FR-09, FR-12 |
| `sensor.shop_exhaust_dc_link_rssi` | sensor | dBm | diagnostic | AC-22 |
| `binary_sensor.shop_exhaust_fan_running` | binary_sensor | `running` (commanded > 0) | — | FR-12 |
| `sensor.shop_exhaust_run_hours` | sensor | h, `total_increasing` | — | FR-12 |
| `sensor.shop_exhaust_sensor_hours` | sensor | h measuring, `total_increasing` | diagnostic | NFR-02, AC-13 |
| `sensor.shop_exhaust_sensor_duty` | sensor | % measuring, last 24 h | diagnostic | FR-12 |
| `sensor.shop_exhaust_decay_rate` | sensor | 1/h (last fitted clear-down rate) | diagnostic | FR-05 |
| `sensor.shop_exhaust_airflow_est` | sensor | CFM (decay rate × 3,050 ft³ ÷ 60) | diagnostic | FR-05 |
| `binary_sensor.shop_exhaust_fault` | binary_sensor | `problem` (any fault) | — | FR-13 |
| `sensor.shop_exhaust_fault_reason` | sensor | text: `none`, `sensor_no_data`, `sensor_status`, `sensor_range`, `fan_tach` | — | FR-13 |
| `binary_sensor.shop_exhaust_cleardown_incomplete` | binary_sensor | `problem` | — | FR-19 |
| `binary_sensor.shop_exhaust_filter_clean_due` | binary_sensor | `problem` | — | FR-13 |
| `sensor.shop_exhaust_filter_exposure` | sensor | % of P-14 | diagnostic | FR-13 |
| `binary_sensor.shop_exhaust_sensor_measuring` | binary_sensor | — | diagnostic | FR-04 |

Precedence: the panel is the only command source in v1, so no rule is needed. If HA control returns, decide precedence then.

## 5. Mechanical interfaces

- **Location (D-033, replaces D-015's spot):** wall-mounted on the refrigerator side panel beside the hood (`docs/site/mounting location option - next to intake.jpg`). The panel face is ~18" laterally from the hood's edge and ~24" deep; the controller sits a few inches back from the panel's front edge, center ~60" above the floor (hood intake ~66"). The display faces across the kids' workbench toward the hood side; the indicator light runs along the front's room-side edge (toward the panel's front edge, south down the shop) and, if mech can reach it, wraps that corner; the sensor inlet is on the bay's corner-side end (north, toward the back wall ~1 ft away, sheltered), never facing down, with the outlet separated (NFR-09). ≤ 10 ft of cable to the fan cabinet (IR-04).
- **Enclosure form (D-019):** one enclosure in two compartments. Upper: sealed electronics compartment, Waveshare board behind the front bezel with the carrier stacked behind it, gasketed lid, no vents (NFR-04). Lower: sensor bay, open through a grille on its corner-side (north) end, with the SEN65 inlet behind it: open air in front, not facing down, outlet separated (NFR-09). The bay is below the electronics, as Sensirion recommends (sensor below heat sources).
- **Sensor bay:** the SEN65 sits in a cradle behind a tool-less cover (thumb screw or snap). Its cable plugs in at the module end and passes into the electronics compartment through a sealed grommet in the dividing wall (no air path, NFR-04). Removal: open the cover, unplug, lift out, < 5 min (NFR-03). Module orientation per Sensirion's mechanical guidelines (inlets/outlet not blocked, inlet and outlet separated, no airflow > 1 m/s across it).
- **Indicator (D-055, D-033):** SK6812SIDE-A LEDs on the carrier's room-side edge emit sideways into a diffuser in the enclosure wall beside the display, readable down the shop (FR-15). The carrier edge reaches past the Waveshare outline to the wall; a corner wrap needs LEDs on a second edge. Count (≈ 4–8) follows diffuser length and depth (pitch ≈ LED-to-diffuser gap).
- **Cable entry:** top or back (panel-side) face, routed up the panel edge to the fan cabinet: J-FAN (4-conductor fan cable, hard-wired), J-OCC (2-conductor thermostat wire to the 24 VAC terminals), and the USB-C cable to the Waveshare board (power and flash/log, D-030). The terminal cables pass through gasketed glands, are stripped inside and land on fixed screw terminals (D-032), each with a printed strain-relief clamp; wired once at install. The Waveshare USB-C sits on that board's edge behind a wall opening with a compressed foam gasket around the receptacle shell; the receptacle mouth itself is open (NFR-04 exception), facing the cabinet rather than the room.
- **Mounting:** a printed cleat screws to the panel (wood screws, fastener length checked against the panel thickness) and the enclosure hooks onto it and locks with one screw.
- **Positions:** Waveshare outline, glass, holes and USB-C position come from its STEP and `docs/vendor/waveshare-2.8b/dimensions.pdf`; carrier LED and connector positions from the carrier `.kicad_pcb`. Never retyped (D-011).
- **Display module (D-054):** Waveshare board 47.9 × 66.7 mm, glass 52.9 × 71.3 mm, 11.1 mm deep including the header; 4 × M2 threaded holes on 40.9 × 59.7 mm. Glass exposed at the face with a gasket around it. Model from the STEP, not this summary. (The D-048 MSP2834 module is superseded.)

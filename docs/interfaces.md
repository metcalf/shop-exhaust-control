# Interface Control Document

**Status:** complete for G2 (drafted 2026-10-25, nightly). Andrew approves at G2. The **DC coupling** section (§1) is shared with the future dust collector project; changes to it need a decision entry, because both systems depend on it.

Companion docs: `docs/architecture.md` (block diagram, power, cost), `docs/control-logic.md` (state machine). Pin numbers and part names here are architecture-level: phase 3 confirms them against datasheets (list in `docs/architecture.md` §9).

## 1. DC coupling (shared with the DC controller project)

| Field | Value |
|-------|-------|
| Signal name | `DC_RUNNING` |
| Direction | DC controller → exhaust controller |
| Meaning | Asserted while the DC motor is **commanded on**, including the DC's own run-on. Whether the motor is confirmed running (current sensing) is a separate flag (bit 3) that the exhaust side ignores in v1. |
| Transport | BLE 4.x **legacy, non-connectable advertising** (`ADV_NONCONN_IND`) from the DC node (D-016). Backup: an opto-isolated wired input on the exhaust node (§2.3, D-025); either path asserts. No MQTT path. |
| Advertising interval (DC side) | 100 ms for 5 s after any payload change, then 500 ms. The fast burst makes assertion latency independent of the scanner's duty (AC-22: ≤ 3 s). |
| Scanning (exhaust side) | Passive scan, window 30 ms every 100 ms (30 %), duplicate filtering off, coexisting with Wi-Fi (D-016, D-021). |
| Failure behavior | No valid advertisement for P-24 (10 s) is treated as "DC not running". FR-09 then holds the boost floor for P-11 more, so a short reception gap is invisible to the fan. Exhaust Auto still works on PM/VOC alone. |
| Authentication | None in v1: a spoofed `DC_RUNNING` only boosts the exhaust. Any future command *to* the DC (message type 0x02) must carry the MAC field (bytes 13–20) from a shared key plus the sequence counter as a replay guard. Stopping the DC stays hardwired at the DC. |
| Sender filter | Optional compile-time allow-list of DC node BLE addresses (empty = accept any valid frame). Set once the DC node exists. |
| Interim source (before the DC controller exists) | None (Q-12). A bench test sender (any ESP32 running the same encoder) is used for AC-22; AC-06 uses the wired input. |
| Wired backup (DC side) | If BLE proves unsatisfactory, the DC controller closes a contact (or drives an output) that energizes the exhaust node's `DC_IN` with 12–24 V AC or DC, either polarity, while `DC_RUNNING` is asserted (§2.3). Same meaning as bit 0. |

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

GPIOs assume an ESP32-S3-WROOM-1-N16R8 (D-022): GPIO 0/3/45/46 (strapping), 19/20 (USB), 26–32 (flash), 35–37 (octal PSRAM) are not used; 43/44 stay as UART0 for logs. Assignments are provisional until the phase 3 schematic.

| Signal | Dir | Type | Level | Connector | GPIO | Notes |
|--------|-----|------|-------|-----------|------|-------|
| `FAN_PWM` | Out | Opto LED drive (§2.1) | 3.3 V, ~5 mA | J-FAN (4-pos fixed screw terminal, 3.5 mm, fan side of the barrier) | 4 | LEDC 5 kHz, ≥ 10-bit. LED on = speed line released (high). 10 kΩ external pull-down keeps the LED off through reset/boot |
| `FAN_TACH` | In | Opto phototransistor, 10 kΩ pull-up | 3.3 V | J-FAN | 5 | Edge timing via GPIO ISR (30–150 Hz); frequency only (pulses/rev unknown) |
| `FAN_PRESENT` | In | Opto phototransistor, 10 kΩ pull-up | 3.3 V, low = fan side powered | J-FAN | 6 | Fan-side +10 V present. Lost when the fan cable is unplugged **or** the fan loses mains (§2.1) |
| `OCC_IN` | In | AC-input opto, RC-filtered | 3.3 V, low = 24 VAC present | J-OCC (2-pos fixed screw terminal, 3.5 mm) | 7 | Rectifier-less bidirectional-LED opto; MOV/TVS across the input. Firmware debounce C-20 |
| `DC_IN` | In | AC-input opto, RC-filtered (§2.3) | 3.3 V, low = asserted | J-DC (2-pos fixed screw terminal, 3.5 mm) | 1 | Wired `DC_RUNNING` backup (D-025). Firmware debounce C-31 |
| SEN65 I²C SDA / SCL | Bidir | I²C 100 kHz, 10 kΩ pull-ups | 3.3 V (sensor rail) | J-SEN (module's 6-pin cable; connector verified in phase 3) | 8 / 9 | Run < 10 cm (sensor bay directly below the board). Pull-ups go to the **switched** rail only, so nothing back-powers the module when it's off (G2 review S-13) |
| `SEN_PWR_EN` | Out | Load-switch gate, active low (AO3401-class P-FET, high side) | 3.3 V | — | 10 | Recovery only: power-cycles a hung module (SR-04, C-12); sleep uses the module's Idle command. 100 kΩ gate pull-up to 3.3 V keeps the rail off through reset and boot until firmware drives it low. Power-cycle sequence: SDA/SCL to hi-Z with internal pull-ups off, rail off ≥ 1 s, a bleed resistor takes the rail below 0.3 V (bench-verify), rail on, wait P-06 |
| Display SPI SCLK / MOSI / CS / DC / RST | Out | SPI 40 MHz | 3.3 V | J-DISP (8-pin 0.1" header, module) | 12 / 11 / 13 / 14 / 21 | 2.8" 240×320 IPS, ST7789/ILI9341-class module, no touch (D-022) |
| Display backlight | Out | PWM to N-FET | 3.3 V | J-DISP | 47 | Dim when vacant; off after C-21 vacant |
| Encoder A / B / push | In | Quadrature + push, RC debounce 10 kΩ/10 nF | 3.3 V | on board (EC11-class) | 15 / 16 / 17 | PCNT for quadrature |
| Buttons 1–4 | In | Momentary tact, RC debounce | 3.3 V | on board | 18 / 38 / 39 / 40 | Assignments are config (initially Auto, Quiet, Boost, spare) (D-009) |
| Indicator R / G / B | Out | LEDC PWM to three low-side N-FETs (2N7002-class) | 5 V LED supply, 3.3 V gate | on board (plain RGB LEDs, one resistor per color per LED; count set in mech, ~4–8) | 48 / 41 / 42 | D-031. Shares the fan PWM's LEDC timer or its own, ~5 kHz. 100 kΩ gate pull-downs keep it dark through boot. Firmware caps total LED current at 300 mA |
| USB: power in + flash/log | Bidir | ESP32-S3 native USB (USB-Serial-JTAG), 5 V VBUS | 5 V nominal, ≥ 4.4 V at the board under peak load | J-USB (USB-C receptacle, 16-pin, **external**, gasketed opening) | 19 / 20 | D-030. The only power input. 5.1 kΩ Rd on CC1/CC2; ESD array on D± and CC; polyfuse and TVS on VBUS |
| Spare | — | — | — | test pad | 2 | Reserved |

**S6 control port (UIS), measured by Andrew 2026-10-25 (Q-15):** black = GND, red = +10 V from the fan (low current), yellow = speed (fan pulls up via 2.2 kΩ; the controller pulls it low; 5 kHz PWM, high-time duty = speed; 20/46/100 % at levels 1/4/10), white = tach (50 % square, ~30/75/144 Hz at levels 1/4/10; stock controller pulls it up 10 kΩ to its 5 V). Unplugged = full speed. The fan end of the cable is USB-C (stock controller J1 is a USB-C receptacle, `docs/site/ac infinity controller pcb.jpg`), but the node doesn't use USB-C: Andrew hard-wires the four conductors into J-FAN by color (Q-25, D-026), so the USB-C contact map isn't needed. J-FAN is labelled `GND (BLK) / +10V (RED) / SPD (YEL) / TACH (WHT)`. Fan GND vs. mains (Q-22, Q-30): unplugged, open to L, N and earth on resistance and diode checks; plugged in, ~65 VAC open-circuit to N/earth, which looks like Y-capacitor coupling from an isolated supply. Q-31 confirmed it: ≈ 60 µA into 10 kΩ (SR-09, D-028).

### 2.1 Fan interface: isolated, fail-off (SR-08, SR-09, FR-10, FR-18)

Everything left of the barrier is powered by the fan's own +10 V and referenced to fan GND; nothing on it connects to node ground, the panel or USB.

```
 FAN SIDE (GND_F, powered from fan red +10 V)          ║ barrier ║  NODE SIDE (GND, 3V3)
                                                        ║  ≥3 mm  ║
 red +10V ──[LDO 5V, low Iq]── +5F                      ║         ║
                                                        ║         ║
 yellow ──┬── D  Q1 N-MOSFET (2N7002-class)             ║         ║
          │   S ── GND_F                                ║         ║
          │   G ──┬──[10k]── +5F   (Q1 ON by default    ║         ║
          │       │                 → yellow low → OFF) ║         ║
          │       └── U1 out (Schmitt opto, open-coll., ║ U1 LED ─╫──[R≈420Ω]── GPIO4 FAN_PWM
          │            H11L1-class, VCC = +5F)          ║         ║            └[10k]─ GND
          │                                             ║         ║
 white ───┼──[10k]── +5F (pull-up, as stock)            ║         ║
          └── U2 LED cathode (via series diode);        ║ U2 CE ──╫── GPIO5 FAN_TACH (10k → 3V3)
              anode ──[1.5k]── +5F                      ║         ║
 +5F ──[R]── U3 LED ── GND_F                            ║ U3 CE ──╫── GPIO6 FAN_PRESENT (10k → 3V3)
 TVS on yellow/white/red to GND_F                       ║         ║
```

Behavior:
- **Node unpowered, in reset or booting:** U1's LED is off → U1 output open → Q1 gate pulled to +5F → Q1 on → yellow held low → **fan off** (SR-08). This needs only fan power.
- **Running:** LED on → U1 output low → Q1 off → the fan's own pull-up takes yellow high. Fan duty = LED-on fraction, so LEDC duty is the fan duty directly, with no inversion in firmware.
- **100 %:** LED on continuously. **0 %:** LED off continuously.
- **Tach:** white low (fan sinking) → U2 LED on → `FAN_TACH` low. Works for an open-drain or a ≤ 10 V push-pull tach output; the series diode blocks reverse bias on U2's LED if the fan drives white above +5F.
- **Presence:** U3 is lit whenever the fan side has power. `FAN_PRESENT` high means the fan cable is unplugged (fan then runs **full speed** on its own) or the fan has lost mains; both raise a fault (FR-18 extension, `docs/control-logic.md` §6).
- **Fan-side current from red +10 V:** ≈ 4–5 mA typical, ≤ 8 mA worst case (U1 supply ~1–2 mA, Q1 gate pull-up 0.5 mA, tach LED ~1 mA average, presence LED 1 mA, LDO Iq µA). Measured (Q-26): the stock controller draws ≈ 9.3 mA from red (13.7 mA in GND with the fan off includes the ≈ 4.5 mA through the fan's 2.2 kΩ speed pull-up, which our Q1 also sinks to GND_F rather than drawing from red). So the port demonstrably supplies ≈ 9 mA; keep the datasheet-maximum fan-side budget ≤ 9 mA in the schematic (G2 review S-2).
- **Timing:** H11L1-class propagation is ~1–4 µs against a 200 µs PWM period (≤ 2 % of period); rise on yellow is set by the fan's 2.2 kΩ against cable capacitance (< 1 µs for 3 m). AC-18 measures duty at the fan, and any fixed offset is calibrated in firmware.
- **Barrier:** opto parts UL 1577 ≥ 3.75 kV rms, with IEC 60747-5-5 (VDE 0884) versions where JLC stocks them. PCB creepage and clearance ≥ 3.0 mm across the barrier, which is above basic insulation for 150 V working voltage under IEC 62368-1 (pollution degree 2). The phase 3 DRC rule encodes it (D-010). The barrier stays although the evidence says the port is SELV (Q-22, Q-30, D-028), because it also breaks the ground loop through the fan cable and keeps the ~65 VAC capacitive float on fan GND off node ground.

J-FAN sits on the fan side of the barrier, with ≥ 3 mm to any node-side copper. Its conductors carry nothing the fan's own cable doesn't already expose.

### 2.2 Occupancy input (FR-07)
24 VAC from the lighting transformer's secondary (the same terminals that drive the old fan relay coil, Q-16) → 2-pos terminal → bidirectional TVS (48 V standoff, SMBJ48CA-class: lightly loaded Class 2 secondaries read 26–29 VAC, up to ~41 V peak at high line) → 2 × 2.2 kΩ (1206, series) → AC-input opto (LTV-814/PC814-class) → phototransistor with 10 kΩ pull-up and 1 µF to GND (τ ≈ 10 ms bridges the zero crossings) → GPIO7. Input draw ≈ 5–6 mA rms. Same ≥ 3 mm barrier as §2.1. Firmware debounce C-20 (0.5 s), well inside AC-04's 2 s.

### 2.3 Wired `DC_RUNNING` input (IR-01 backup, D-025)
The same circuit as §2.2, with the series resistance sized so 12 V DC still lights the LED (≥ 2 mA) and 24 VAC (+10 %, ≈ 37 V peak) stays within its rating: TVS (48 V standoff, as §2.2) → 2 × 2.7 kΩ (1206) → AC-input opto (bidirectional LED, so either polarity or AC) → 10 kΩ pull-up and 1 µF → GPIO1. Same ≥ 3 mm barrier. Unconnected reads not asserted. J-DC and J-OCC accept the same inputs, so swapping their wires at install is harmless (wrong function only). Phase 3 checks the resistor values against the opto's CTR and LED ratings.

## 3. Power (D-018)

- **Mains:** none in the custom enclosure or on the PCB (SR-01, Q-18 (a)). The fan and the node's adapter both plug into the always-on receptacle in the fan cabinet (IR-05, D-013). SR-01a is not triggered.
- **Adapter (D-030):** UL-listed 5 V USB-C wall adapter, ≥ 2 A, LPS. USB-C cable ≤ 3 m (IR-04's ≤ 10 ft), with USB 2.0 data and 24 AWG or heavier power conductors (≈ 0.5 V round-trip drop at the 1.1 A worst-case peak on 24 AWG). For flashing or wired logs, swap the adapter for a PC on the same cable; remote logging over Wi-Fi is the normal path.
- **On board:** J-USB → polyfuse (1.5 A) → TVS (5 V standoff) → 5 V input rail. (a) 5 V → 3.3 V regulator, ≥ 1 A, for the ESP32, display, logic and sensor: a small sync buck or a low-dropout LDO (≤ 0.4 V dropout at 1 A; not AMS1117), chosen in the schematic from JLC stock. (b) AO3401-class P-FET load switch plus an LC/bulk filter from 3.3 V to the SEN65, so its 350 mA / 2 ms peaks stay off the MCU's supply pins and firmware can power-cycle it. (c) The indicator runs from the 5 V input. No 12 V and no separate 5 V rail; no reverse-polarity FET (USB-C is keyed).
- **Budget** (typical / peak):

| Load | Rail | Typical | Peak | Source |
|------|------|---------|------|--------|
| ESP32-S3 module, Wi-Fi + BLE scan | 3.3 V main | 110 mA | 360 mA (TX) | ESP32-S3 datasheet (verify) |
| Display logic + backlight | 3.3 V main | 80 mA | 100 mA | typical 2.8" module (verify) |
| Node-side opto drive, pull-ups | 3.3 V main | 5 mA | 12 mA | §2 |
| SEN65 measuring | 3.3 V (switched) | 90 mA | 350 mA for 2 ms (110 mA max sustained) | SEN6x DS Table 12 |
| Indicator | 5 V input | 60 mA | 300 mA (firmware cap) | One band color at a time, ~10–20 mA per LED |
| **Total at 5 V input** (LDO case; a buck is ~25 % lower) | 5 V | **≈ 0.35 A (1.7 W)** | **≈ 1.1 A (5.5 W), ms-scale** | |

A ≥ 2 A adapter has ~2× peak margin. On a PC USB 2.0 port (500 mA) the typical load fits; firmware caps the indicator lower when it can't tell which source it's on (reading the CC advertisement via ADC is a phase 3 option). About 1.7 W dissipates in the sealed electronics compartment (a few kelvin of rise); the sensor bay is thermally separated (`docs/architecture.md` §5) and the SEN65 temperature offset is tuned at commissioning (FR-20).
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
| `binary_sensor.shop_exhaust_dc_running` | binary_sensor | `running` (BLE or wired) | — | FR-09, FR-12 |
| `binary_sensor.shop_exhaust_dc_wired` | binary_sensor | `running` (wired input alone) | diagnostic | IR-01, AC-06 |
| `sensor.shop_exhaust_dc_link_rssi` | sensor | dBm | diagnostic | AC-22 |
| `binary_sensor.shop_exhaust_fan_running` | binary_sensor | `running` (commanded > 0) | — | FR-12 |
| `sensor.shop_exhaust_run_hours` | sensor | h, `total_increasing` | — | FR-12 |
| `sensor.shop_exhaust_sensor_hours` | sensor | h measuring, `total_increasing` | diagnostic | NFR-02, AC-13 |
| `sensor.shop_exhaust_sensor_duty` | sensor | % measuring, last 24 h | diagnostic | FR-12 |
| `sensor.shop_exhaust_decay_rate` | sensor | 1/h (last fitted clear-down rate) | diagnostic | FR-05 |
| `sensor.shop_exhaust_airflow_est` | sensor | CFM (decay rate × 3,050 ft³ ÷ 60) | diagnostic | FR-05 |
| `binary_sensor.shop_exhaust_fault` | binary_sensor | `problem` (any fault) | — | FR-13 |
| `sensor.shop_exhaust_fault_reason` | sensor | text: `none`, `sensor_no_data`, `sensor_status`, `sensor_range`, `fan_tach`, `fan_port` | — | FR-13 |
| `binary_sensor.shop_exhaust_cleardown_incomplete` | binary_sensor | `problem` | — | FR-19 |
| `binary_sensor.shop_exhaust_filter_clean_due` | binary_sensor | `problem` | — | FR-13 |
| `sensor.shop_exhaust_filter_exposure` | sensor | % of P-14 | diagnostic | FR-13 |
| `binary_sensor.shop_exhaust_sensor_measuring` | binary_sensor | — | diagnostic | FR-04 |

Precedence: the panel is the only command source in v1, so no rule is needed. If HA control returns, decide precedence then.

## 5. Mechanical interfaces

- **Location (D-015):** hung from the underside of the north-wall upper cabinets, ≥ 3 ft from the hood's edge (NFR-09), front face toward the room (south, down the shop), ≤ 10 ft of cable to the fan cabinet (IR-04). Exact cabinet dimensions: Q-27.
- **Enclosure form (D-019):** one enclosure in two compartments. Upper: sealed electronics compartment, PCB vertical behind the front bezel (display, encoder, 4 buttons), gasketed lid, no vents (NFR-04). Lower: sensor bay, open to the room through a front grille, with the SEN65 inlet facing into the room, not toward the hood (NFR-09). The bay is below the electronics, as Sensirion recommends (sensor below heat sources).
- **Sensor bay:** the SEN65 sits in a cradle behind a tool-less cover (thumb screw or snap). Its cable plugs in at the module end and passes into the electronics compartment through a sealed grommet in the dividing wall (no air path, NFR-04). Removal: open the cover, unplug, lift out, < 5 min (NFR-03). Module orientation per Sensirion's mechanical guidelines (inlets/outlet not blocked, inlet and outlet separated, no airflow > 1 m/s across it).
- **Indicator (D-031):** a short diffused light strip aligned with one edge of the display (horizontal or vertical; picked in mech), lit by plain RGB LEDs through a light pipe, visible down the shop's length (FR-15). LED count follows strip length and diffuser depth (pitch ≈ LED-to-diffuser gap).
- **Cable entry:** rear or top face, toward the cabinet: J-FAN (4-conductor fan cable, hard-wired), J-OCC (2-conductor thermostat wire to the 24 VAC terminals), J-DC (2-conductor, only if the wired DC backup is used), J-USB (USB-C power and flash/log, D-030). The terminal cables pass through gasketed glands, are stripped inside and land on fixed screw terminals (D-032), each with a printed strain-relief clamp; wired once at install. J-USB is board-mounted behind a wall opening with a compressed foam gasket around the receptacle shell; the receptacle mouth itself is open (NFR-04 exception), facing the cabinet rather than the room.
- **Mounting:** a printed bracket screws to the cabinet bottom (4 wood screws) and the enclosure slides onto it and locks with one screw, so the unit comes down without unscrewing from the cabinet.
- **Positions:** display, encoder, button, LED and connector positions come from the `.kicad_pcb` in phase 3, never retyped (D-011).

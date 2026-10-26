# Interface Control Document

**Status:** skeleton. Claude completes this in phase 2 (architecture), and Andrew approves it at G2. The **DC coupling** section is shared with the future dust collector project. Changes to it need a decision entry, because both systems depend on it.

## 1. DC coupling (shared with the DC controller project)

| Field | Value |
|-------|-------|
| Signal name | `DC_RUNNING` |
| Direction | DC controller → exhaust controller |
| Meaning | Asserted while the DC motor is commanded on, including run-on. ‹TBD: commanded vs. confirmed by current› |
| Transport | BLE legacy advertising from the DC node (D-016), interval ~0.5–1 s; the exhaust node scans at partial duty alongside Wi-Fi. No wired or MQTT path. |
| Payload (manufacturer-specific data) | ‹G2: company ID (or test ID), message version, sender ID, sequence counter, flags bit 0 = `DC_RUNNING`; remaining bytes reserved for DC status (shared-panel option)› |
| Failure behavior | No valid advertisement for P-24 (10 s) is treated as "DC not running." Exhaust Auto still works on PM/VOC alone. |
| Authentication | Not needed for v1: a spoofed `DC_RUNNING` only boosts the exhaust. Any future command *to* the DC (e.g. force-on from a shared panel) must carry a MAC from a shared key plus a replay counter. Stopping the DC stays hardwired at the DC. |
| Interim source (before the DC controller exists) | None (Q-12) |

Boost behavior (how long the DC must run first, the boost level, and what happens after the DC stops) belongs to the **exhaust** side and is defined in FR-09, not here.

## 2. Electrical I/O (exhaust node)

| Signal | Dir | Type | Level | Connector | GPIO | Notes |
|--------|-----|------|-------|-----------|------|-------|
| Fan speed | Out | Open-drain pull-down, 5 kHz PWM, on the fan's speed line (yellow) | Fan pulls up to +10 V via ~2.2 kΩ; high-time duty = speed | Fan's UIS port (USB-C-style cable) | | Held low = off; open/high = full (Q-15). Isolated from node (SR-09). Stock levels 1/4/10 = 20/46/100 % |
| Fan tach | In | Square wave on white; 50 % duty; ~30 / 75 / 144 Hz at levels 1 / 4 / 10 | Stock controller pulls it up 10 kΩ to its 5 V; fan output type (open-drain vs push-pull) unconfirmed, so design for either | Fan's UIS port | | Fan fault detection (FR-18). Isolated (SR-09). Pulses/rev unknown; only frequency vs command is needed |
| Occupancy | In | Isolated AC input | 24 VAC from the lighting transformer in the fan cabinet (Q-16) | | | Rectifier plus optocoupler |
| `DC_RUNNING` | In | BLE (on-module radio) | | | | No wired input (D-016) |
| PM sensor | Bidir | SPS30, I²C or UART (G2) | 5 V supply | | | Sleep/wake and fan-clean by command (D-012) |
| Coarse dust sensor | In | Analog + pulsed LED drive | 5 V | | | v2 candidate (FR-17) |
| VOC sensor | Bidir | I²C | 3.3 V | | | SGP41 (D-012) |
| Panel: encoder | In | Quadrature + push | 3.3 V | | | |
| Panel: buttons | In | Momentary, unlit | 3.3 V | | | About 4; assignments are config (initially Auto, Quiet, Boost, spare) (D-009) |
| Panel: display | Out | SPI | 3.3 V | | | ~2" IPS (ST7789-class) |
| Ambient indicator | Out | Addressable LED data | 5 V | | | Level-shifted; with the panel at the north end (D-015) |

**S6 control port (UIS), measured by Andrew 2026-10-25 (Q-15):** black = GND, red = +10 V from the fan (don't draw meaningful current), yellow = speed, white = tach. Fan's GND relation to mains unknown (SR-09). The stock controller pulls yellow low through a transistor against the fan's 2.2 kΩ pull-up.

## 3. Power
- Mains in: always-on 120 V receptacle in the fan cabinet (D-013, IR-05)
- Low-voltage supply: listed external supply (SR-01, Q-18 (a))
- Logic: 5 V / 3.3 V derived from it

## 4. Home Assistant entities
Naming prefix: `shop_exhaust_` (confirmed, survey §4). Alerts go to the HA mobile app.

Illustrative only. Finalize at G2 to match the design, including VOC, the optional coarse sensor, holds and scenes.

| Entity | Type | Notes |
|--------|------|-------|
| `sensor.shop_exhaust_pm2_5` | sensor | µg/m³, relative |
| `sensor.shop_exhaust_pm10` | sensor | |
| `binary_sensor.shop_exhaust_fan_running` | binary_sensor | |
| `sensor.shop_exhaust_fan_speed` | sensor | % or step |
| `sensor.shop_exhaust_state` | sensor | Auto, or the active scene/hold, with time remaining (FR-12). Read-only in v1 (FR-16 dropped) |
| `binary_sensor.shop_exhaust_occupied` | binary_sensor | Occupancy input (FR-07) |
| `binary_sensor.shop_exhaust_dc_running` | binary_sensor | From the BLE link; plus `sensor.shop_exhaust_dc_link_rssi` (diagnostic) |
| `sensor.shop_exhaust_run_hours` | sensor | |
| `binary_sensor.shop_exhaust_fault` | binary_sensor | Plus a fault-reason text sensor |
| `binary_sensor.shop_exhaust_cleardown_incomplete` | binary_sensor | Vacant limit (FR-19) hit with PM/VOC still high |
| `sensor.shop_exhaust_sensor_duty` | sensor | Diagnostic |

**Control from Home Assistant:** none in v1 (FR-16 dropped 2026-10-24); the panel is the only command source, so no precedence rule is needed. If HA control returns, decide precedence then.

## 5. Mechanical interfaces
- Sensor mount relative to the plenum and mesh: ‹TBD, see context: Mounting›
- Enclosure location and mounting: ‹TBD›
- Cable routing and strain relief: ‹TBD›

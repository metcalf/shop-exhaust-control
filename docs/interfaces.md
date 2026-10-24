# Interface Control Document

**Status:** skeleton. Claude completes this in phase 2 (architecture), and Andrew approves it at G2. The **DC coupling** section is shared with the future dust collector project. Changes to it need a decision entry, because both systems depend on it.

## 1. DC coupling (shared with the DC controller project)

| Field | Value |
|-------|-------|
| Signal name | `DC_RUNNING` |
| Direction | DC controller → exhaust controller |
| Meaning | Asserted while the DC motor is commanded on, including run-on. ‹TBD: commanded vs. confirmed by current› |
| Primary transport | ‹TBD. Preferred: isolated dry contact (DC side) into an optocoupled input (exhaust side)› |
| Fallback transport | Home Assistant binary sensor relayed to the exhaust node, or a direct node-to-node MQTT topic (no Home Assistant automation in the path) |
| Failure behavior | Loss of the signal is treated as "DC not running." Exhaust Auto mode still works on PM alone. |
| Interim source (before the DC controller exists) | ‹TBD: contactor aux contact / CT clamp on the DC circuit / none› |

Boost behavior (how long the DC must run first, the boost level, and what happens after the DC stops) belongs to the **exhaust** side and is defined in FR-09, not here.

## 2. Electrical I/O (exhaust node)

| Signal | Dir | Type | Level | Connector | GPIO | Notes |
|--------|-----|------|-------|-----------|------|-------|
| Fan speed | Out | PWM to the fan's EC control port | ~10 V PWM (community reports) ‹verify› | Fan's UIS port ‹TBD› | | Includes off if the port supports it (Q-15) |
| Fan tach | In | ‹TBD: if the port exposes one› | | | | Fan-running confirmation, fault detection |
| Fan mains switch | Out | Relay/contactor | | | | **Only if** Q-15 shows the port can't reach true off or a safe fail state |
| Occupancy | In | Isolated AC input | 24 VAC (lighting circuit) | | | Rectifier plus optocoupler; confirm source (Q-16) |
| `DC_RUNNING` | In | Opto | | | | |
| PM sensor | Bidir | UART + SET | 3.3 V/5 V | | | Sleep through SET or serial command |
| Coarse dust sensor | In | Analog + pulsed LED drive | 5 V | | | Optional (Q-08), e.g. Sharp GP2Y1014 |
| VOC sensor | Bidir | I²C | 3.3 V | | | SGP41-class |
| Panel: encoder | In | Quadrature + push | 3.3 V | | | |
| Panel: scene buttons | In/Out | Momentary + LED backlight | 3.3 V | | | 3–4 plus Auto/cancel |
| Panel: display | Out | SPI | 3.3 V | | | ~2" IPS (ST7789-class) |
| Ambient indicator | Out | Addressable LED data | 5 V | | | Level-shifted; may be remote from the panel (Q-10) |

## 3. Power
- Mains in: ‹TBD›
- Low-voltage supply: ‹TBD: listed external supply, or an on-board recognized AC-DC module›
- Logic: 5 V / 3.3 V derived from it

## 4. Home Assistant entities
Naming prefix: `shop_exhaust_` ‹confirm against Andrew's conventions, survey §4›

Illustrative only. Finalize at G2 to match the design, including VOC, the optional coarse sensor, holds and scenes.

| Entity | Type | Notes |
|--------|------|-------|
| `sensor.shop_exhaust_pm2_5` | sensor | µg/m³, relative |
| `sensor.shop_exhaust_pm10` | sensor | |
| `binary_sensor.shop_exhaust_fan_running` | binary_sensor | |
| `sensor.shop_exhaust_fan_speed` | sensor | % or step |
| `select.shop_exhaust_scene` | select | Auto or an active scene/hold; can start one (FR-16) |
| `binary_sensor.shop_exhaust_dc_running` | binary_sensor | |
| `sensor.shop_exhaust_run_hours` | sensor | |
| `binary_sensor.shop_exhaust_fault` | binary_sensor | Plus a fault-reason text sensor |
| `sensor.shop_exhaust_sensor_duty` | sensor | Diagnostic |

**Precedence rule (proposed):** last command wins, from the panel or Home Assistant; the panel is always available and can cancel anything. Decide at G2.

## 5. Mechanical interfaces
- Sensor mount relative to the plenum and mesh: ‹TBD, see context: Mounting›
- Enclosure location and mounting: ‹TBD›
- Cable routing and strain relief: ‹TBD›

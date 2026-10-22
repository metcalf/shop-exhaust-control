# Interface Control Document

**Status:** skeleton. Claude completes this in phase 2 (architecture), and Andrew approves it at G2. The **DC coupling** section is shared with the future dust collector project. Changes to it need a decision entry, because both systems depend on it.

## 1. DC coupling (shared with the DC controller project)

| Field | Value |
|-------|-------|
| Signal name | `DC_RUNNING` |
| Direction | DC controller → exhaust controller |
| Meaning | Asserted while the DC motor is commanded on, including run-on. ‹TBD: commanded vs. confirmed by current› |
| Primary transport | ‹TBD. Preferred: isolated dry contact (DC side) into an optocoupled input (exhaust side)› |
| Fallback transport | Home Assistant binary sensor relayed to the exhaust node, or a direct ESPHome-to-ESPHome link |
| Failure behavior | Loss of the signal is treated as "DC not running." Exhaust Auto mode still works on PM alone. |
| Interim source (before the DC controller exists) | ‹TBD: contactor aux contact / CT clamp on the DC circuit / none› |

Boost behavior (how long the DC must run first, the boost level, and what happens after the DC stops) belongs to the **exhaust** side and is defined in FR-09, not here.

## 2. Electrical I/O (exhaust node)

| Signal | Dir | Type | Level | Connector | GPIO | Notes |
|--------|-----|------|-------|-----------|------|-------|
| Mode selector | In | ‹TBD› | | | | Off / Auto / On / Spray |
| Spray-mode hard path | — | ‹TBD› | | | | Must work without firmware (SR-03) |
| `DC_RUNNING` | In | Opto | | | | |
| Fan run | Out | Relay/contactor | | | | Rated for motor inrush |
| Fan speed | Out | ‹TBD by motor type› | | | | 0–10 V / PWM / relay taps / VFD |
| PM sensor | Bidir | UART + SET | 3.3 V/5 V | | | Sleep through SET or serial command |
| Occupancy | In | ‹TBD› | | | | Lights / motion / Home Assistant |
| Indicators | Out | LED | | | | Mode, fan, fault |

## 3. Power
- Mains in: ‹TBD›
- Low-voltage supply: ‹TBD, e.g. 24 VDC DIN-rail, listed›
- Logic: 5 V / 3.3 V derived from it

## 4. Home Assistant entities
Naming prefix: `shop_exhaust_` ‹confirm against Andrew's conventions, survey §4›

| Entity | Type | Notes |
|--------|------|-------|
| `sensor.shop_exhaust_pm2_5` | sensor | µg/m³, relative |
| `sensor.shop_exhaust_pm10` | sensor | |
| `binary_sensor.shop_exhaust_fan_running` | binary_sensor | |
| `sensor.shop_exhaust_fan_speed` | sensor | % or step |
| `select.shop_exhaust_mode` | select | Mirrors the physical selector. Physical controls win (see below). |
| `binary_sensor.shop_exhaust_dc_running` | binary_sensor | |
| `sensor.shop_exhaust_run_hours` | sensor | |
| `binary_sensor.shop_exhaust_fault` | binary_sensor | Plus a fault-reason text sensor |
| `sensor.shop_exhaust_sensor_duty` | sensor | Diagnostic |

**Precedence rule (proposed):** the physical mode selector is authoritative. Home Assistant can request changes only when the selector is in Auto, or it reports state only. Decide at G2.

## 5. Mechanical interfaces
- Sensor mount relative to the plenum and mesh: ‹TBD, see context: Mounting›
- Enclosure location and mounting: ‹TBD›
- Cable routing and strain relief: ‹TBD›

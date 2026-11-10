# Architecture

**Status:** drafted for G2 (2026-10-25, nightly). Approved requirements: `docs/requirements.md`. Detail lives in `docs/interfaces.md` (signals, pins, power, HA entities, mechanical interfaces) and `docs/control-logic.md` (state machine). New decisions: D-017…D-026. **Revised 2026-11-10 for route B (D-054, D-055, D-056):** Waveshare ESP32-S3-Touch-LCD-3.5 plus a carrier PCB replaces the custom main board.

**Not a life-safety device.** Air-quality sensing here is a convenience control. It is not respiratory protection and doesn't on its own protect health (SR-05).

## 1. Block diagram

```mermaid
flowchart LR
  subgraph CAB["Fan cabinet (north wall)"]
    REC["Always-on 120 V receptacle (IR-05)"]
    S6["AC Infinity S6 fan<br/>UIS port: +10 V, GND, speed, tach"]
    XFMR["24 VAC lighting transformer<br/>(switches with Lutron lights)"]
    PSU["Listed 5 V USB-C adapter, ≥2 A (D-030)"]
    REC --- S6
    REC --- PSU
  end

  subgraph ENC["Controller enclosure, under north cabinets (D-015, D-019)"]
    subgraph EC["Sealed electronics compartment"]
      subgraph FS["Fan side: powered by fan +10 V, GND_F"]
        FAN_IF["Fail-off pull-down + tach + presence<br/>(interfaces §2.1)"]
      end
      BAR1{{"≥3 mm barrier, optos"}}
      subgraph WS["Waveshare ESP32-S3-Touch-LCD-3.5 (D-056)"]
        MCU["ESP32-S3R8, 16 MB flash<br/>Wi-Fi + BLE"]
        PWR["AXP2101 PMIC<br/>DCDC1 → 3.3 V"]
        PANEL["3.5&quot; 320×480 IPS, ST7796 SPI<br/>FT6336 touch"]
        USB["USB-C: power in + flash/log (D-030)"]
      end
      subgraph CAR["Carrier PCB on the 2×16 header, node side (GND, 5 V, 3.3 V)"]
        LEDS["SK6812SIDE-A row on the edge,<br/>2N7002 shifter (D-055)"]
        POK["PWRON one-shot (DNP)"]
      end
      OCC_IF["24 VAC input: R, bridge, opto"]
      DC_IF["Wired DC_RUNNING backup: R, bridge, opto"]
    end
    subgraph BAY["Sensor bay, open to room, below electronics"]
      SEN["Sensirion SEN65<br/>PM, VOC/NOx, RH/T (D-012)"]
    end
  end

  DC["DC controller (future)<br/>BLE advertiser"]
  HA["Home Assistant (MQTT)"]

  S6 <== "4-wire fan cable, hard-wired to terminals, ≤10 ft" ==> FAN_IF
  FAN_IF -.- BAR1 -.- MCU
  XFMR -- "2-wire 24 VAC" --> OCC_IF -.-> MCU
  PSU -- "USB-C cable ≤3 m" --> USB --> PWR --> MCU
  SEN -- "I²C <10 cm, sealed grommet" --- MCU
  MCU --- PANEL
  MCU --> LEDS
  DC -. "BLE adv: DC_RUNNING (interfaces §1)" .-> MCU
  DC -. "optional 2-wire backup (interfaces §2.3)" .-> DC_IF -.-> MCU
  MCU <-. "Wi-Fi MQTT, read-only (FR-12)" .-> HA
```

## 2. Partitioning

| Concern | Where it lives | Why |
|---------|----------------|-----|
| Mains | Nowhere in our design. The fan and a listed adapter plug into the existing always-on receptacle | 0 % PWM is a true off (Q-15), so there's nothing to switch (D-013). SR-01a isn't triggered; G3 covers only the receptacle and adapter (SR-07) |
| Fan speed and off | Fan's UIS port, through an isolated, fan-powered fail-off interface | SR-08 (off when the node is dead), SR-09 (isolation), FR-10 |
| Control logic | `exhaust_logic`, pure C++ on the node | NFR-01, NFR-06; host-tested |
| Sensing | One SEN65 in a bay open to the room | D-012, NFR-04, NFR-09 |
| User interface | Panel on the enclosure front | D-003, D-009, FR-01, FR-11 |
| DC link | BLE advertising, scanned by the on-board radio; an opto-isolated wired input as backup | D-016, D-025, IR-01/02 |
| History and alerts | HA over MQTT, read-only | FR-12, FR-13, FR-16 dropped |

## 3. Electronics (Waveshare board + carrier PCB, D-054, D-056)

- **MCU and panel:** Waveshare ESP32-S3-Touch-LCD-3.5: ESP32-S3R8 (8 MB octal PSRAM for LVGL and NimBLE headroom), 16 MB flash, 3.5" 320×480 ST7796 over SPI, FT6336 touch, AXP2101 PMIC (3.3 V from DCDC1), USB-C. No rework. Pins: `docs/interfaces.md` §2.
- **Carrier PCB:** 2-layer, on the Waveshare 2×16 header and M2 pattern (72.00 × 48.50 mm). Holds the fail-off fan interface (§2.1: three LTV-817 across a ≥ 3 mm barrier, AO3400A pulled on from the fan's +10 V), the occupancy and wired-DC optos (§2.2, §2.3), the SEN65 connector, the indicator LEDs on its room-side edge (D-055) and a DNP PWRON one-shot (§3). No regulator, no RF, no USB.
- **Power:** 5 V USB-C into the Waveshare board; the carrier takes `VBUS` and `VCC3V3` from the header (`docs/interfaces.md` §3).
- **PCBA (NFR-05):** JLC Economic. All SMT is Basic except SK6812SIDE-A (one Extended fee). Andrew hand-solders the header pins, screw terminals and the GH-6.
- **Off-board wiring:** fan cable hard-wired into J-FAN (D-026, D-049), 2-conductor thermostat wire to the 24 VAC terminals, optional 2-conductor DC backup, USB-C cable for power. WireViz drawing in `electrical/` in phase 3 (D-010).

## 4. Firmware (ESP-IDF, C++)

```
firmware/
  main/                       app wiring, task creation
  components/
    esp-iot-core/             submodule (D-007): Wi-Fi, OTA, remote log, BaseMqttClient, NetworkTaskManager
    exhaust_logic/            pure C++20: Controller, Sampler, AutoDemand, ModeManager, OutputShaper,
                              Faults, Maintenance, UiInput, DcLinkParser, Config.h (P-nn, C-nn, on-screen action map)
    gas_index/                Sensirion gas index algorithm (BSD-3, vendored C), D-017
    hass/                     HassMessages (pure) + MqttExhaustHomeClient (BaseMqttClient)
    drivers/                  Sen6x (I²C), FanPort (LEDC 5 kHz + tach + present), Occupancy,
                              Display (esp_lcd ST7796 SPI + LVGL), Touch (FT6336), Expander (TCA9554: LCD/TP reset), Pmu (AXP2101: input limit, PWRON power-off off), Indicator (RMT SK6812, inverted)
    dc_link/                  NimBLE passive scanner → DcLinkParser
  test/                       host GoogleTest (control-logic.md §10), results committed
```

| Task | Rate | Owns |
|------|------|------|
| `control` | 1 Hz tick + event queue | `Controller`; writes the fan duty; publishes a snapshot (mutex) for UI/indicator/HA |
| `sensor` | 1 Hz while measuring | SEN65 I²C; carries out Measure/Idle/PowerCycle/Clean; posts frames |
| `ui` | 10–20 Hz | LVGL; reads the snapshot; panel events → `UiInput` → `control` queue |
| `ble` | continuous scan | NimBLE observer; `DcLinkParser`; posts `dc_running` and RSSI |
| network | esp-iot-core | Wi-Fi, MQTT, OTA, remote logging; HA state from the snapshot |

- The task watchdog covers `control` and `sensor` and panics on a stall (`CONFIG_ESP_TASK_WDT_PANIC`); a stuck task means a reboot, with no in-place recovery. On any reset the opto LED goes dark, so the fan is off in hardware until `control` decides (SR-08). The active hold or scene survives every reset except power loss, through RTC no-init memory (NFR-07, D-027), so an OTA reboot or a crash during Spray costs a few seconds of fan-off, not the run-on. OTA isn't deferred.
- Nothing in `control` waits on the network (NFR-01). MQTT publishing reads a copy of the snapshot.
- BLE/Wi-Fi coexistence: the ESP-IDF software coexistence is on; the 30 % scan duty is tested alongside OTA (AC-22).
- `P-nn`/`C-nn` and the on-screen action map live in one `Config.h`. Changes go by OTA (NFR-10 dropped, NFR-11).

## 5. Mechanical concept (D-019, details in phase 3)

- One printed enclosure (MJF PA12, D-011) with two compartments: a **sealed electronics compartment** on top (gasketed lid, no vents, gasket around the touch glass; IP5X intent, NFR-04), and an **open sensor bay** below it, its inlet on the corner-side (north) end, sheltered, not facing down, outlet separated (NFR-09).
- Bay below the electronics, with an insulating air gap in the dividing wall: it keeps the SEN65 below and away from the ~1.3 W of electronics heat, as Sensirion recommends, and the RH/T offset is tuned at commissioning (FR-20).
- Tool-less bay cover. The module unplugs at its own end, and its cable crosses into the electronics compartment through a sealed grommet (NFR-03, NFR-04).
- Touch display on the front, which faces across the kids' bench. The carrier's edge LEDs light a diffuser beside the display on the room-side edge, reading down the shop; a corner wrap needs LEDs on a second carrier edge (D-033, D-055).
- Stack-up: lens at the bezel, Waveshare board, J8, carrier behind it; carrier edge reaches the enclosure wall for the LEDs. The wall steps in around the inset USB-C (D-056). Positions from the Waveshare STEP and the carrier `.kicad_pcb`.
- Wall-mounted on a cleat on the refrigerator side panel, one locking screw (`docs/interfaces.md` §5, D-033).
- No part of the controller is in the exhaust airstream (SR-02): it's outside the cabinet, ≥ 3 ft from the hood.

## 6. Failure modes

| Failure | Effect | Handling | Req / AC |
|---------|--------|----------|----------|
| Node unpowered, crashed, resetting, booting | No control | Fan held **off** by the fan-powered pull-down; HA shows offline via LWT. After a crash or OTA reboot, the hold or scene resumes (D-027) | SR-08, NFR-07, FR-13, AC-18, AC-09 |
| Fan mains returns with the node unpowered | Possible brief full-speed burst before the fan-side hold-off rail is up | Accepted (D-028) | SR-08, AC-18 |
| Fan cable unplugged | Fan runs **full** (fan behavior) | `fan_port` fault from loss of `FAN_PRESENT` (displayed; HA) | SR-08, FR-18 |
| Fan has no mains / motor failed | No exhaust | `fan_port` (no +10 V) or `fan_tach` fault | FR-18, AC-07 |
| SEN65 fault (no data, status, range) | No PM/VOC | SR-04: PM/VOC demand dropped, floor and DC boost kept (occupied → P-01, vacant → off unless DC); module reset retries, USB replug if it stays hung (D-047); Spray uses P-09 alone | SR-04, AC-20 |
| SEN65 fouled (reads high) | Fan runs too long | FR-19 vacant caps (P-22, P-21) and the clear-down incomplete notice | FR-19, AC-27 |
| Wi-Fi, broker or HA down | No history or alerts | No control impact | NFR-01, AC-12 |
| DC link lost or DC absent | No boost | Treated as DC off after P-24; boost persists P-11. If BLE proves unreliable, wire the backup input (D-025) | IR-01, AC-22, AC-06 |
| Spoofed BLE frame | False boost only | Accepted risk; allow-list option | `interfaces.md` §1 |
| 24 VAC input lost | Reads vacant | Trusted signal, no handling (Q-17); display shows Vacant | FR-07 |
| Fan-port mains fault (port not SELV) | Hazard on fan-side circuits | ≥ 3 mm barrier, rated optos; nothing fan-side is touchable; flashing USB is on the node side | SR-09, AC-26 |
| Touch panel or controller fails | No local input | Control logic keeps running; holds time out to Auto; Home Assistant can still trigger the same actions (D-009). There is no physical fallback (D-048) | FR-01 |
| Fan wires mis-terminated at J-FAN | Fan won't run, or runs full; fan-side parts stressed | Color-coded terminal labels; AC-18 bench check before install. No USB-C fan cable reaches the node, so it can't meet the USB port (D-026, D-030) | SR-09, AC-18 |
| Adapter fault | Node dead → fan off | Listed LPS adapter | SR-01, SR-08 |
| AXP2101 stays off after power returns | Node dead → fan off (SR-08 holds) | Bench check of VBUS power-on; DNP PWRON one-shot fitted if needed (D-056) | NFR-07, SR-08 |

## 7. Traceability (M and S requirements)

| Req | Design element | Verified by |
|-----|----------------|-------------|
| FR-01 | `UiInput`, on-screen action map in `Config.h`, touch flow (control-logic §8) | AC-08 |
| FR-02 | `AutoDemand` §4, `OutputShaper` §7 | AC-01 |
| FR-04, FR-06 | `Sampler` §5 | AC-02 |
| FR-05 | `Sampler` rest rule and decay fit §5; `decay_rate`/`airflow_est` entities | AC-03 |
| FR-07 | Occupancy input §2.2; control-logic §3; Sampler Off | AC-04 |
| FR-08, SR-03 | Spray/SprayRunOn §2; Protect state §5 | AC-05 |
| FR-09 | `DcBoostActive` §4; BLE link §1; wired input §2.3 | AC-06, AC-22 |
| FR-10 | Fan interface §2.1; LEDC 5 kHz; C-06 | AC-07, AC-18 |
| FR-11 | Display model §8 | AC-08 |
| FR-12, FR-13, IR-03 | HA entities (interfaces §4); `HassMessages` | AC-09 |
| FR-14 | Host-side gas index, paused across Idle (D-017); VocValid gating | AC-10, AC-28 |
| FR-15 | Indicator §8; carrier edge LEDs (§3, §5) | AC-11 |
| FR-18 | Tach and presence optos; `fan_tach`/`fan_port` faults | AC-07 |
| FR-08 (override) | Auto tap and new holds/scenes end Spray/SprayRunOn (control-logic §2, D-024) | AC-05 |
| FR-19 | Vacant cap/limit §4; SprayRunOn vacant exit §2 | AC-27 |
| NFR-01 | No network dependence in `control` (§4) | AC-12 |
| NFR-02 | Sampler duty; weekly clean; sensor-hours entity | AC-13 |
| NFR-03, NFR-04 | Sensor bay, tool-less cover, sealed compartment (§5) | AC-14, AC-15 |
| NFR-05 | Carrier: one-sided SMT, JLC Economic (§3) | AC-24 |
| NFR-06 | `exhaust_logic` + host tests | AC-16 |
| NFR-07, SR-08 | Fan-powered fail-off; boot to Auto | AC-18 |
| NFR-08 | Cost estimate (§8) | AC-24 |
| NFR-09 | Location, inlet orientation (interfaces §5) | AC-17 |
| NFR-11 | esp-iot-core OTA; Waveshare USB-C flash/log port (D-030) | AC-19 |
| SR-01, SR-01a, SR-07 | No mains in the design; listed adapter (D-018) | AC-21 |
| SR-02 | Enclosure outside the cabinet and airstream | AC-15 |
| SR-04 | Fault table and fallback (control-logic §6, §4) | AC-20 |
| SR-05, SR-06 | Statements here, in the README and on the panel's About page | AC-25 |
| SR-09 | Carrier barrier, LTV-817s; USB on the node side only | AC-26 |
| IR-01, IR-02 | BLE payload v1.0 (interfaces §1.1); wired backup input (§2.3, D-025) | AC-22, AC-06 |
| IR-04, IR-05 | Three short LV cables; always-on receptacle | AC-23 |

Design elements without a requirement: none.

## 8. Cost estimate (NFR-08, AC-24)

Estimates, **not quoted** (route B, 2026-11-10; detail in `docs/eval-offtheshelf-board.md`). G4 replaces them.

| Item | Est. USD |
|------|---------:|
| SEN65 (SEN66 is $62; SEN65 assumed lower) | 45 |
| Waveshare ESP32-S3-Touch-LCD-3.5 (Waveshare store $25.99–32.99, 2026-11-10) | 30 |
| Carrier PCBA, 2 boards (Economic fees + one Extended fee, parts, PCBs) | 20 |
| Hand-soldered connectors (2×16 pin header, terminals, GH-6) | 5 |
| Enclosure, MJF PA12, two parts + bracket | 40 |
| Gasket, inserts, screws, diffuser | 10 |
| 5 V USB-C listed adapter (≥ 2 A) + 3 m USB-C data cable | 15 |
| Fan-cable extension if needed, thermostat wire for occupancy | 15 |
| Shipping and duties (PCBA and print in one JLC order) | 35 |
| **Total** | **≈ 215** (range ≈ 180–250) |

The second carrier is a spare; a second Waveshare board (≈ $30) makes a full spare unit.

## 9. To verify in phase 3

- J8 physical orientation: V1 and Rev 2.0 number the rows oppositely (`docs/interfaces.md` §2); check against the STEP and the delivered board's label.
- AXP2101: does VBUS alone power it on with no cell (REG20 after boot)? Default input current limit (REG16) and DCDC1 capability with the SEN65 added.
- I²C pull-up values on IO7/8 (Waveshare schematic) and edge quality with the SEN65 cable.
- LTV-817 PWM at 5 kHz: scope yellow at 10/50/90 % (`docs/interfaces.md` §2.1).
- SK6812SIDE-A emission side vs. pads, and data timing through the 2N7002, 1 kΩ and 470 Ω.
- Boot config: task watchdog panic, RTC watchdog, LEDC at duty 0 before GPIO38 is routed (G2 review S-14).

# Decision Log

ADR-lite format. Status is one of: **Proposed**, **Accepted**, **Superseded by D-nnn**, or **Rejected**. Gate approvals are logged here too.

Keep this log to live decisions. When one is superseded, delete it if the new entry's alternatives already record why; keep a rejected entry only if the idea is likely to be re-proposed. Working assumptions live in `docs/context.md` until they're decided. IDs are never reused.

Template:
```
## D-nnn: Title
- Date:
- Status:
- Context:
- Decision:
- Alternatives considered:
- Consequences:
```

---

## D-001: Exhaust fan controller is the pilot project
- Date: 2026-10-22
- Status: Accepted (Andrew)
- Context: Two related projects, exhaust fan control and DC control, plus a new Claude-led design process to try out.
- Decision: Build the exhaust controller first.
- Alternatives considered: DC first (higher value, but more I/O, distributed wiring and a 3 HP motor contactor).
- Consequences: The exhaust project defines the `DC_RUNNING` interface. The DC project reuses this repo's structure and its process notes.

## D-002: Separate controllers, coupled by one signal
- Date: 2026-10-22
- Status: Accepted (Andrew)
- Context: The two systems share only "DC running," plus an optional shared UI.
- Decision: Independent ESP32 nodes. Shared UI and history go in Home Assistant.
- Alternatives considered: One combined controller.
- Consequences: Each node must work on its own (NFR-01). The interface lives in `docs/interfaces.md` §1.

## D-003: Local physical controls; Home Assistant for history and alerts
- Date: 2026-10-22 (revised 2026-10-23)
- Status: Accepted (Andrew)
- Context: Andrew doesn't want to pull out a phone at the bench.
- Decision: Physical controls and indicators in the shop. Need not be analog: a small display is fine, resistive touch possible but physical controls preferred. Not presumed to be a fixed mode list; the interaction model is in `docs/requirements.md` §2. Home Assistant handles logging, notifications and remote viewing, and may trigger the same actions as the panel.
- Consequences: Precedence between panel and Home Assistant is decided at G2 (`docs/interfaces.md` §4). *Update 2026-10-24:* HA control dropped for v1 (FR-16); HA is read-only, so no precedence rule is needed yet.

## D-007: Bare ESP-IDF firmware, reusing the hvac_control network stack
- Date: 2026-10-23
- Status: Accepted (Andrew, 2026-10-23, including extraction)
- Context: Andrew writes ESP32 firmware in bare ESP-IDF. `~/code/hvac_control` already has a working Wi-Fi/OTA/remote-log/MQTT base (`components/wifi`) and two Home Assistant MQTT-discovery clients built on it. The DC controller will need the same stack.
- Decision: ESP-IDF in C++, not ESPHome. Control logic is a pure C++ component, host-tested. Reuse `components/wifi`, extracted with history into `metcalf/esp-iot-core` and consumed as a git submodule at `components/esp-iot-core`, matching how hvac_control already pulls in its other shared libs. HA integration follows the `MqttHomeClient`/`MqttZCHomeClient` pattern.
- Alternatives considered:
  - ESPHome: less code for HA entities, but not Andrew's workflow, and complex logic ends up in C++ external components anyway.
  - Copy `components/wifi` into this repo: fastest, but forks it three ways once the DC project starts.
- Consequences: hvac_control switches to the submodule on branch `extract-esp-iot-core`, mounted at `components/esp-iot-core` (consumers `REQUIRES esp-iot-core`); both firmware builds and host tests pass. `release.sh` takes `OTA_DIR_PREFIX` (default `hvac_control_`); each project sets its own OTA URL template, MQTT user and `remote_spec.cfg` in gitignored per-checkout files. The Python reference model is dropped (Andrew, 2026-10-23); the logic has one implementation, tested on the host in C++.

## D-008: Custom PCB with third-party assembly
- Date: 2026-10-23
- Status: Accepted (Andrew, direction; mains and DIN-rail constraints lifted 2026-10-23); details confirmed at G2/G3
- Context: Andrew wants to try a custom PCB for this project. He has designed mains PCBs before. He can hotplate-reflow SMD and is open to third-party PCBA.
- Decision: v1 uses a custom PCB: ESP32-S3 module, power, PM sensor connector, optocoupled `DC_RUNNING` input, control-panel and indicator I/O, and outputs. Mains on the board is allowed; whether the supply, relay or contactor are on or off board is decided at G2. Mains sections follow IEC 62368-1 creepage/clearance with reinforced insulation to accessible low voltage, documented in `pcb/SAFETY.md` (SR-01a). Enclosure is custom; no DIN-rail constraint. KiCad design, assembled by JLCPCB by default using parts it stocks; leftovers hand-soldered or reflowed by Andrew.
- Alternatives considered:
  - Dev board plus modules: no layout risk, but more wiring and a bigger enclosure. Kept as the fallback on the same pinout.
  - Low-voltage-only board (initial draft): simpler review, but rules out an on-board supply or relay that may make the build smaller. Remains an option at G2.
- Consequences: Phase 3 adds a KiCad project with ERC/DRC and fab/PCBA outputs; G3 review covers the board. The PCB order is a purchase, approved at G4. Claude's layout needs Andrew's review in KiCad. Mains layout is the highest-risk part of Claude's weakest area, so Andrew reviews it at G3 against `pcb/SAFETY.md`.

## D-009: Occupancy-based Auto; encoder plus configurable buttons
- Date: 2026-10-24
- Status: Accepted (Andrew, direction); floor level and thresholds set at commissioning
- Context: Requirements review. Spraying is infrequent and doesn't justify a dedicated button. Andrew expects the sensors to do most of the work, with manual overrides rare.
- Decision: In Auto, an occupied shop always gets a low ventilation floor; the fan turns off only when the shop is vacant and the air is clear. Panel: encoder with push (multi-step hold entry, defaulting to the last values) plus about 4 unlit buttons whose assignments are configuration (initially Auto, Quiet, Boost, spare). Scenes stay as an extensible concept; Spray is a scene, not a button. No backlit buttons; state is shown on the display and the ambient indicator.
- Alternatives considered:
  - Sensor-only on/off (previous FR-02): no baseline ventilation while working.
  - Dedicated Spray button, or one press per action with no menus: optimizes for rare actions.
- Consequences: The occupancy input moves from S to M (FR-07); it's trusted as correct, with no failure handling (Q-17), and the display shows occupancy. PCB routes about 4 button inputs with no LED drivers. Button mapping lives in config, not in the state machine.

## D-010: PCB/electrical toolchain built around Claude's weak spots
- Date: 2026-10-24
- Status: Proposed — needs Andrew (reversible; confirm before phase 3)
- Context: Claude is reasonable at schematic topology but error-prone at symbol/footprint pin mapping and readable sheet placement, and weak at layout (D-008). The toolchain should turn those into scripted, checkable steps.
- Decision:
  - **Schematic:** native KiCad 9, generated with `kiutils` (Python) rather than hand-written S-expressions. Symbols, footprints and 3D models from `easyeda2kicad` by LCSC part number; LCSC fields via `kicad-jlcpcb-tools`.
  - **Verification:** render sheets and board with `kicad-cli` (`sch export svg`, `pcb export svg`, `pcb render`) and review the images; scripted netlist assertions against datasheet pin requirements (strapping pins, EN RC, decoupling, opto input); ngspice for the analog bits (`DC_RUNNING` input, snubbers, supply). Results are committed.
  - **Mains spacing:** KiCad 9 custom DRC rules, including `creepage`, encode the IEC 62368-1 spacings; `pcb/SAFETY.md` cites the rule file. Third-party layout tools never stand in for this check.
  - **Layout:** Claude scripts placement (pcbnew/IPC API): board outline, edge connectors, antenna keepout, mains zone with slots, net classes. Mains section is pre-routed and locked. From the same locked placement, generate one candidate with Freerouting and one with Quilter (free tier, KiCad in/out); both must pass our DRC; Andrew picks one and touches it up.
  - **Outputs:** KiBot/KiKit for Gerber/BOM/CPL; InteractiveHtmlBom for hand-placed parts.
  - **Off-board wiring:** WireViz (YAML) in `electrical/`.
  - **Mechanical fit:** `kicad-cli pcb export step` into the CadQuery enclosure assembly for interference checks.
- Alternatives considered:
  - Hand-written `.kicad_sch`: works but unreadable placement, no structure for checks.
  - SKiDL/atopile (circuit-as-code): good netlists, but no schematic sheet for Andrew to review. Reconsider for the DC controller.
  - Flux: browser platform with its own format; conflicts with the repo/KiCad/`kicad-cli` workflow.
  - DeepPCB: overlaps Quilter; try only if Quilter disappoints. JITX: commercial, overkill.
- Consequences: Phase 3 needs KiCad 9 (`kicad-cli`, creepage DRC) on the working machine (Q-14), plus Python deps (`kiutils`, `easyeda2kicad`) and Freerouting (Java). Quilter is a cloud upload and its creepage/slot handling is unverified, hence our DRC as the gate. The Freerouting-vs-Quilter comparison is recorded in `docs/process-notes.md` for the DC project.

---

## Gate approvals
| Gate | Date | Approved by | Notes |
|------|------|-------------|-------|
| G1 Requirements | | | |
| G2 Architecture | | | |
| G3 Mains/safety | | | |
| G4 BOM | | | |
| G5 First power-up | | | |

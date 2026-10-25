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
  - **Mechanical fit:** `kicad-cli pcb export step` into the build123d enclosure assembly (D-011) for interference checks.
- Alternatives considered:
  - Hand-written `.kicad_sch`: works but unreadable placement, no structure for checks.
  - SKiDL/atopile (circuit-as-code): good netlists, but no schematic sheet for Andrew to review. Reconsider for the DC controller.
  - Flux: browser platform with its own format; conflicts with the repo/KiCad/`kicad-cli` workflow.
  - DeepPCB: overlaps Quilter; try only if Quilter disappoints. JITX: commercial, overkill.
- Consequences: Phase 3 needs KiCad 9 (`kicad-cli`, creepage DRC) on the working machine (Q-14), plus Python deps (`kiutils`, `easyeda2kicad`) and Freerouting (Java). Quilter is a cloud upload and its creepage/slot handling is unverified, hence our DRC as the gate. The Freerouting-vs-Quilter comparison is recorded in `docs/process-notes.md` for the DC project.

## D-011: Mechanical toolchain: build123d, checked by renders and geometry tests; outsourced PA12 enclosure
- Date: 2026-10-24
- Status: Proposed — needs Andrew (build123d choice accepted in principle by Andrew 2026-10-24; enclosure material tied to Q-18)
- Context: Claude's mechanical errors are mostly orientation/selector mistakes, assembly fit, and manufacturability, not the parametric geometry itself. Andrew expects to outsource SLS printing of the enclosure.
- Decision:
  - **CAD:** build123d (FOSS, OCCT kernel, STEP export) instead of CadQuery. Explicit objects, `Location`s and named faces replace chained string selectors (`>Z`), the main source of silent orientation errors. No mechanical code existed yet, so switching is free.
  - **Single source of truth:** connector, mounting-hole, display and encoder positions are read from the `.kicad_pcb` file via pcbnew Python, never retyped. The KiCad STEP export goes into the assembly.
  - **Checks:** headless renders (iso, six orthographic views, section cuts) via PyVista/trimesh for Claude to review; pytest assertions for bounding boxes, minimum wall thickness, boss/insert clearances, and zero pairwise interference volume across the assembly (PCB included); trimesh watertight/manifold checks on exported meshes.
  - **Fabrication outputs:** STEP for Fusion; dimensioned drawings via FreeCAD headless (TechDraw) for anything Andrew cuts or welds (mounts, brackets); 1:1 PDF templates for cutouts and hole patterns, checked on the real parts before cutting.
  - **Enclosure process:** outsourced PA12 powder-bed nylon. Default MJF PA12 at JLC3DP, ordered with the PCB; SLS if the vendor or finish demands it. Design rules: ≥2 mm walls, brass heat-set inserts in bosses, ~0.3 mm clearance on mating fits, powder-escape holes for closed voids, gasketed lid if needed for dust.
- Alternatives considered:
  - CadQuery: same kernel and fine, but its selector API produces wrong-face errors that build without complaint.
  - Zoo (KCL/text-to-CAD): commercial; duplicates code-CAD with more lock-in.
  - SLA resin: brittle for a shop enclosure. FDM: fine if Andrew prints, but slower to dial in remotely. Off-the-shelf listed enclosure with machined cutouts plus a printed bezel: the fallback if mains ends up inside (Q-18).
- Consequences: Phase 3 mech needs Python deps (`build123d`, `pyvista` or `trimesh`, `pytest`) and FreeCAD for drawings. Standard PA12 is not flame-rated (typically UL94 HB), so it can't be the fire enclosure around mains; Q-18 resolves this at G2. CLAUDE.md updated from CadQuery to build123d.

## D-012: SPS30 for PM and SGP41 for VOC, both in v1
- Date: 2026-10-25
- Status: Accepted (Andrew, Q-08 and Q-09)
- Context: PMS5003 was the kickoff working assumption. The SPS30 costs more but has a fan self-clean and better contamination resistance; VOC was a v2 candidate.
- Decision: SPS30 (I²C or UART, chosen at G2) for PM; SGP41 for VOC, both in v1. The coarse dust sensor (FR-17) stays a v2 candidate.
- Alternatives considered: PMS5003 (cheaper, shorter life, no self-clean); VOC deferred to v2.
- Consequences: FR-14 becomes M and also drives Auto (solvents, soldering), not just Spray run-on. Settling time P-06 follows the SPS30 datasheet. Adds roughly $25–30 over a PMS5003 to the BOM (NFR-08).

## D-013: Fan and node on always-on 120 V; lighting relay no longer switches the fan
- Date: 2026-10-25
- Status: Proposed — needs Andrew (site mains change; reviewed at G3)
- Context: Survey §2: the fan's receptacle is switched by a relay driven from the 24 VAC lighting transformer, so the fan loses power when the lights go off. Auto (D-009) turns the fan off only when the shop is vacant *and* the air is clear, which needs the fan to run after the lights go off.
- Decision: Give the fan and the node's listed supply always-on 120 V in the cabinet: either an unswitched receptacle, or remove the relay from the fan receptacle's feed. The 24 VAC transformer stays and becomes the occupancy input only (FR-07). Andrew does the wiring (survey §3); G3 flags anything an electrician should check.
- Alternatives considered:
  - Keep the relay: the fan stops when the lights go off, so no vacant clear-down and Spray run-on dies with the lights. Contradicts FR-02/FR-08.
  - Controller switches mains itself: unnecessary, since 0 % PWM is true off (Q-15), and it would put mains in the enclosure (Q-18).
- Consequences: IR-05. The fan's off state now depends entirely on the control port, so its behavior with the node dead (Q-15, SR-08) matters more: if it runs at full speed with no control signal, a dead node means the fan runs until noticed (HA offline alert, FR-13).

## D-014: Panel, sensors and indicator above the miter station
- Date: 2026-10-25
- Status: Accepted (Andrew, Q-10, location); sensor/panel split decided at G2
- Context: The fan and 24 VAC are at the north end; work and dust are mid-shop; the DC wiring will reach the miter station's blast gate anyway.
- Decision: The panel and ambient indicator go above the miter station, on the cabinet/wall beside the miter hood rather than on the hood itself (vibration, direct ejecta). The sensor bay goes with them by default. Low-voltage cable runs along the ceiling to the fan cabinet (IR-04).
- Alternatives considered: by the rear door or at the fan (survey §8): less wiring, but farther from the work, and from the fan the indicator isn't visible down the shop.
- Consequences: Where the node lives (panel end or fan end) and what crosses the ceiling cable is a G2 decision.

---

## Gate approvals
| Gate | Date | Approved by | Notes |
|------|------|-------------|-------|
| Phase 0 survey | 2026-10-25 | Claude (sufficient for requirements); Andrew to confirm with G1 | Survey and photos committed d9833fd |
| G1 Requirements | | | |
| G2 Architecture | | | |
| G3 Mains/safety | | | |
| G4 BOM | | | |
| G5 First power-up | | | |

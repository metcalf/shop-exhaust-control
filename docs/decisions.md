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
- Consequences: Each node must work on its own (NFR-01). The interface lives in `docs/interfaces.md` §1; transport is BLE (D-016).

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

## D-012: One Sensirion SEN65 module for PM, VOC/NOx and RH/T
- Date: 2026-10-24, revised 2026-10-25
- Status: Accepted (Andrew, 2026-10-25, Q-24)
- Context: Sensors went through PMS5003 → SPS30 + SGP41 (Q-08, Q-09) → plus a coarse sensor and an SHT4x for VOC humidity compensation. The SHT4x needs enclosure self-heating compensation; the SEN55 combines everything but is NRND at Sensirion (`sourcing/pm-sensor.md`).
- Decision: A single SEN65 (SEN6x family, active): PM mass and number concentrations, VOC and NOx indices, RH/T. No coarse dust sensor (FR-17 dropped) and no separate RH/T sensor, so the sensor bay has one airflow path.
- Alternatives considered:
  - SEN55: cheaper and has a gas-only mode, but NRND.
  - SPS30 + SGP41 (+ SHT4x): independent failure of PM and VOC, but two airflow paths and the compensation problem.
  - Adding a coarse sensor: dropped for one airflow path; v2 candidate.
- Consequences:
  - No gas-only mode: VOC is measured only while the module measures PM. Acceptable (Andrew): when dust is high and PM sampling is sparse, the fan is already high.
  - The VOC baseline must survive module sleep (FR-14); check the SEN6x for algorithm-state backup/restore at G2, else keep a host-side baseline on the raw signal.
  - SEN6x runs on 3.3 V with peaks of ~350 mA for 2 ms; the supply and decoupling are sized at G2.
  - Fan auto-clean behavior isn't documented for SEN6x; plan a manual clean command on a schedule (NFR-02).
  - A module fault takes out PM and VOC together (SR-04).
  - Price unchecked; the SEN66 is ~$62 at DigiKey and the SEN65 should be lower. Checked at G4.

## D-013: Fan and node on always-on 120 V; lighting relay no longer switches the fan
- Date: 2026-10-25
- Status: Accepted (Andrew, 2026-10-25, Q-19: use the existing unswitched receptacle)
- Context: Survey §2: the fan's receptacle is switched by a relay driven from the 24 VAC lighting transformer, so the fan loses power when the lights go off. Auto (D-009) turns the fan off only when the shop is vacant *and* the air is clear, which needs the fan to run after the lights go off.
- Decision: Plug the fan and the node's listed supply into the existing unswitched receptacle in the cabinet. No rewiring. The 24 VAC transformer stays and becomes the occupancy input only (FR-07).
- Alternatives considered:
  - Keep the relay: the fan stops when the lights go off, so no vacant clear-down and Spray run-on dies with the lights. Contradicts FR-02/FR-08.
  - Controller switches mains itself: unnecessary, since 0 % PWM is true off (Q-15), and it would put mains in the enclosure (Q-18).
- Consequences: IR-05. No mains work, so G3 for this is a check that the receptacle's circuit is suitable. The fan's off state now depends entirely on the control port. The fan runs at full speed with the cable unplugged (Q-15), but SR-08 holds it off whenever the node is unpowered or booting, so a dead node means no exhaust until noticed (HA offline alert, FR-13).

## D-015: Controller at the north (exhaust) end
- Date: 2026-10-25
- Status: Accepted (Andrew, 2026-10-25), replaces D-014 (panel above the miter station). Spot: under the north-wall upper cabinets, < 10 ft of cable to the fan cabinet (Q-23)
- Context: Makeup air enters at the south end and the hood exhausts at the north, so air flows the length of the shop. A sensor at the miter station (D-014) would be blind to everything downstream of it: the lathe, the north bench (soldering) and spraying north of it.
- Decision: Panel, ambient indicator and sensors go together at the north end, out of the hood's capture zone. Spot: hung under the north-wall upper cabinets (Q-23), at least 3 ft from the hood's edge, facing south down the shop. The enclosure hangs from the cabinet bottom with the display and controls angled toward the user, and the sensor inlet faces into the room. All site wiring (fan port, 24 VAC, supply) is local to the fan cabinet. Whether the DC gets its own panel or shares this one is deferred to the DC project.
- Alternatives considered:
  - Above the miter station (D-014, accepted earlier on Q-10): close to the work and the DC wiring, but blind downstream and needed a 35 ft ceiling cable. Splitting the sensors from the panel was also possible, but separating them buys nothing once the sensors are at the north end.
  - Directly beside the fan, under the cabinet (survey option 3): least wiring, but inside the hood's draw and poorly visible.
- Consequences: Sensing integrates the whole shop and clears last, so the off decision is conservative; upstream sources are detected later, which DC boost largely covers. Manual controls are at the north end, by the interior door you enter through. The DC wired link is no longer nearly free, which led to D-016. IR-04 shrinks to a short local cable.

## D-016: BLE advertising for the DC link, with no wired or MQTT path
- Date: 2026-10-25
- Status: Accepted (Andrew, 2026-10-25)
- Context: With the controller at the north end (D-015), a wire from the DC would be a separate ~30 ft run. ESP-NOW was considered, but it shares the Wi-Fi channel, so AP outages and channel changes would need a channel-sweep scheme and an `esp-iot-core` change.
- Decision: The DC node broadcasts `DC_RUNNING` in BLE advertisements; the exhaust node scans and treats P-24 of silence as "not running". No wired input, and no MQTT fallback, for simplicity (Andrew). Message format in `docs/interfaces.md` §1, versioned and with room for DC status and a reverse direction.
- Alternatives considered:
  - Dry contact into an optocoupler: robust and simple, but a dedicated wire run.
  - ESP-NOW: better range and lower latency, but tied to the Wi-Fi channel.
  - MQTT node-to-node fallback: dropped; it adds a second path to test for a non-critical function.
  - BLE GATT connection: more state than a few bytes at a low rate needs.
- Consequences: BLE and Wi-Fi time-share the radio; the scan duty and coexistence get tested with OTA (AC-22). Adds the NimBLE stack to RAM and flash; checked at G2, with a PSRAM module as the fallback. Supersedes the transport text in D-002's consequences; D-002 itself (separate nodes, coupled by one signal) still stands. Loss of the link costs only boost. Commands to the DC, if ever added, need authentication.

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

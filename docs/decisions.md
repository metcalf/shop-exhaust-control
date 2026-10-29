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
- Status: Accepted (Andrew, 2026-10-25), replaces D-014 (panel above the miter station). Spot: under the north-wall upper cabinets, < 10 ft of cable to the fan cabinet (Q-23). **Spot amended by D-033** (refrigerator side panel); the north-end choice stands
- Context: Makeup air enters at the south end and the hood exhausts at the north, so air flows the length of the shop. A sensor at the miter station (D-014) would be blind to everything downstream of it: the lathe, the north bench (soldering) and spraying north of it.
- Decision: Panel, ambient indicator and sensors go together at the north end, out of the hood's capture zone. Spot: hung under the north-wall upper cabinets (Q-23), at least 3 ft from the hood's edge, facing south down the shop. The enclosure hangs from the cabinet bottom with the display and controls angled toward the user, and the sensor inlet faces into the room. All site wiring (fan port, 24 VAC, supply) is local to the fan cabinet. Whether the DC gets its own panel or shares this one is deferred to the DC project.
- Alternatives considered:
  - Above the miter station (D-014, accepted earlier on Q-10): close to the work and the DC wiring, but blind downstream and needed a 35 ft ceiling cable. Splitting the sensors from the panel was also possible, but separating them buys nothing once the sensors are at the north end.
  - Directly beside the fan, under the cabinet (survey option 3): least wiring, but inside the hood's draw and poorly visible.
- Consequences: Sensing integrates the whole shop and clears last, so the off decision is conservative; upstream sources are detected later, which DC boost largely covers. Manual controls are at the north end, by the interior door you enter through. The DC wired link is no longer nearly free, which led to D-016. IR-04 shrinks to a short local cable.

## D-016: BLE advertising for the DC link, with no wired or MQTT path
- Date: 2026-10-25
- Status: Accepted (Andrew, 2026-10-25). **Amended by D-025** (wired backup input added)
- Context: With the controller at the north end (D-015), a wire from the DC would be a separate ~30 ft run. ESP-NOW was considered, but it shares the Wi-Fi channel, so AP outages and channel changes would need a channel-sweep scheme and an `esp-iot-core` change.
- Decision: The DC node broadcasts `DC_RUNNING` in BLE advertisements; the exhaust node scans and treats P-24 of silence as "not running". No wired input, and no MQTT fallback, for simplicity (Andrew). Message format in `docs/interfaces.md` §1, versioned and with room for DC status and a reverse direction.
- Alternatives considered:
  - Dry contact into an optocoupler: robust and simple, but a dedicated wire run.
  - ESP-NOW: better range and lower latency, but tied to the Wi-Fi channel.
  - MQTT node-to-node fallback: dropped; it adds a second path to test for a non-critical function.
  - BLE GATT connection: more state than a few bytes at a low rate needs.
- Consequences: BLE and Wi-Fi time-share the radio; the scan duty and coexistence get tested with OTA (AC-22). Adds the NimBLE stack to RAM and flash; checked at G2, with a PSRAM module as the fallback. Supersedes the transport text in D-002's consequences; D-002 itself (separate nodes, coupled by one signal) still stands. Loss of the link costs only boost. Commands to the DC, if ever added, need authentication.

## D-017: VOC index computed on the node from the SEN65 raw signal
- Date: 2026-10-25
- Status: Proposed (G2). Reversible in firmware
- Context: FR-14 needs the VOC baseline to survive module Idle. The module's index algorithm resets whenever a measurement starts. D-012 left two options: the module's algorithm-state backup/restore, or a host-side baseline on the raw signal.
- Decision: Run Sensirion's open-source gas index algorithm (BSD-3, plain C) on the node, fed one step per valid 1 s raw VOC reading. Pause it (keep its state) while the module isn't measuring and for C-07 after each start. Save the state to NVS hourly and restore it at boot. Publish the module's own index too, as a check.
- Alternatives considered: Module state backup/restore (fewer lines of code, but behaviour across long Idle is undocumented, and recorded traces can't be replayed through the module). It stays as the fallback if the raw signal proves unusable on the bench.
- Consequences: Deterministic, so host tests and HA replay run exactly the same algorithm (FR-12, AC-28). Phase 3 confirms that the SEN6x raw VOC command exists and is humidity-compensated inside the module. Restoring a stale state after a long node outage is accepted; the algorithm re-adapts over hours.

## D-018: No mains in the design; listed 12 V adapter
- Date: 2026-10-25
- Status: Proposed (G2). **Adapter and on-board supply amended by D-030** (5 V USB-C); "no mains" stands
- Context: CLAUDE.md leaves on- or off-board mains to architecture. The fan is switched off through its control port (Q-15, D-013), so there's no relay or contactor to host. Q-18 (a) prefers no mains in the printed enclosure.
- Decision: No mains on the PCB or in the enclosure. A UL-listed 12 V / ≥ 1 A Class 2 adapter plugs into the always-on cabinet receptacle and feeds a barrel jack. On board: fuse, reverse-polarity FET, TVS, 12→5 V buck, 5→3.3 V buck, plus a switched 5→3.3 V LDO for the SEN65.
- Alternatives considered: 5 V USB-C adapter (cheaper by one buck, but ~0.3 V drop over 10 ft at peak, and a second external USB-C next to the fan's USB-C port invites mis-plugging; see D-020). On-board mains supply (saves the adapter, but brings SR-01a, `pcb/SAFETY.md` and a flame-rated enclosure for no functional gain).
- Consequences: SR-01a isn't triggered. G3 covers only the receptacle circuit, the adapter listing and the 24 VAC hookup (SR-07). PA12 is fine as the enclosure material.

## D-019: One enclosure: sealed electronics above an open sensor bay
- Date: 2026-10-25
- Status: Proposed — needs Andrew (sets the enclosure's shape and cutouts). Mounting amended by D-033: wall cleat on the fridge side panel, not a cabinet bracket
- Context: NFR-03/04/09, D-015 (under the north cabinets), Sensirion's guidance to keep the module below heat sources.
- Decision: One PA12 enclosure hung from a cabinet bracket. The sealed electronics compartment is on top, with the panel on the front face and the light bar along its bottom edge. The open sensor bay is below, with a front grille and a tool-less cover; the module cable crosses through a sealed grommet. Cables enter at the back or top with strain reliefs.
- Alternatives considered: A separate sensor pod on a short cable (better thermal separation, but I²C over a longer run and two enclosures). Sensor bay beside the electronics (shorter enclosure, but at the same height as the heat).
- Consequences: Phase 3 mech models two compartments and a grommet pass-through. The SEN65 RH/T offset is tuned at commissioning.

## D-020: Flashing USB is internal; the fan port is the only external USB-C
- Date: 2026-10-25
- Status: **Superseded by D-030** (USB-C is now external, as the power input and flash/log port). Earlier amended by D-026
- Context: The S6 control cable is USB-C (stock controller J1). If the fan cable went into a node USB port, the fan's +10 V and GND would land on non-isolated node pins, bypassing SR-09.
- Decision: The ESP32-S3 native USB-C is inside the electronics compartment, reachable only with the lid off. OTA is the normal update path (NFR-11). Power comes in on a barrel jack (D-018).
- Alternatives considered: External flashing port with a label (relies on the label). A non-USB connector for the fan (needs a custom or cut fan cable).
- Consequences: First flash and recovery need the lid off. The fan-port receptacle is labelled "FAN".

## D-021: BLE DC link: payload v1.0, fast-burst advertising, 30 % scan
- Date: 2026-10-25
- Status: Proposed (G2). Shared with the DC project, so changes after G2 need a decision entry
- Context: D-016 chose BLE advertising. AC-22 needs assertion within 3 s and no false assertions, with Wi-Fi running.
- Decision: Manufacturer-specific data with company ID 0xFFFF, magic "MS", version, type, sender, sequence, flags (bit 0 `DC_RUNNING`) and reserved status and MAC fields (`docs/interfaces.md` §1.1). The DC side advertises every 100 ms for 5 s after a change, then every 500 ms. The exhaust side scans passively, 30 ms every 100 ms.
- Alternatives considered: A constant 500 ms interval with a higher scan duty (more radio time taken from Wi-Fi). Extended advertising (BLE 5; not needed for 21 bytes).
- Consequences: The DC project implements the encoder from this table. The exhaust side tests the parser and timeout on the host.

## D-022: ESP32-S3-WROOM-1-N16R8, 2.8" IPS display module, LVGL
- Date: 2026-10-25
- Status: Proposed (G2)
- Context: D-008 named the ESP32-S3. D-016 flagged NimBLE RAM, with a PSRAM module as the fallback. Andrew's hvac_control already uses LVGL.
- Decision: The N16R8 module (octal PSRAM, so GPIO 35–37 are unavailable). A 2.8" 240×320 **IPS** SPI display module (ST7789 or ILI9341-IPS class) on a header, **no touch** (Andrew, 2026-10-28; was 2.0"). LVGL via `esp_lcd`.
- Alternatives considered: N8 without PSRAM (cheaper by ~$1; RAM is tight with NimBLE, TLS OTA and LVGL). A bare FPC panel (cheaper, but a fine-pitch connector and backlight circuit on our board). 2.0" IPS (smaller enclosure; same 240×320, so text is ~30 % smaller at the user's distance under the cabinet). 2.8" TN (common and cheap, but washes out viewed from below). Resistive touch (dulls the image; the encoder and buttons cover input, D-009).
- Consequences: GPIO plan in `docs/interfaces.md` §2. The display module's outline feeds the enclosure in phase 3; the bezel and board grow to about 50 × 86 mm for the module. Backlight ~2× the 2.0" draw (power budget updated, ≈ 1.5 W typical). Sourcing must confirm IPS from the panel datasheet. Cost ≈ +$3 per board.

## D-023: Fan-powered, fail-off isolated fan interface
- Date: 2026-10-25
- Status: Proposed — needs Andrew. Q-26 answered: the stock controller draws ≈ 9.3 mA from the port, so the ≤ 9 mA budget is within demonstrated capacity
- Context: SR-08 requires the fan to be off with the node unpowered, with the hold-off powered from the fan side. SR-09 requires isolation. FR-18 needs the tach.
- Decision: A fan-side N-MOSFET holds the speed line low by default (gate pulled up from a 5 V LDO on the fan's +10 V). A Schmitt-output opto driven by the node's PWM releases it, so the LED-on fraction is the fan duty. Two more optos carry the tach and a fan-present signal back. ≥ 3 mm barrier (`docs/interfaces.md` §2.1).
- Alternatives considered: An isolated DC-DC powering the fan side from the node (fails on, since the hold-off dies with node power). A relay on the speed line (slow; can't PWM at 5 kHz). A digital isolator (needs a few mA on both sides, no better than the opto here).
- Consequences: A brief full-speed burst is possible when fan mains returns before the node's hold-off rail is up; accepted (D-028, G2 review S-1). If the port can't supply the current (Q-26), the fallback is a smaller budget: drop the presence LED and raise the pull-up values. Phase 3 verifies the opto polarity and timing (architecture §9). AC-18 scopes it.

## D-024: Q-28 control-logic calls: user overrides always win; sensor faults drop only sensed demand
- Date: 2026-10-26
- Status: Accepted (Andrew, Q-28). Amends approved FR-08, FR-18, SR-04 and AC-05, AC-07, AC-20; drops P-19 and C-10
- Context: The G2 draft made five interpretations the approved requirements didn't spell out (Q-28 (a)–(e)).
- Decision:
  - (a, d) An Auto press returns to Auto from any mode, including Spray and SprayRunOn, with no run-on. Any new hold or scene replaces Spray or its run-on. The 3 s long-press and the "refused during Spray" rule are gone.
  - (b) Confirmed: the SEN65 idles from Spray start until C-07 before the P-09 minimum run-on ends. FR-08 now says so.
  - (c) A sensor fault removes only PM/VOC demand; the occupancy floor (P-01) and DC boost stay, within the FR-19 vacant limits. P-19 (fault fallback speed) is dropped, since the floor already gives the "low speed" Q-07 asked for.
  - (e) The `fan_port` fault (fan side unpowered: cable unplugged → fan full, or no mains) is accepted and written into FR-18.
- Alternatives considered: as drafted (long-press, refusal, literal SR-04). Andrew chose simpler, override-first behavior.
- Consequences: SR-03 still holds: only explicit user input ends Spray early, never a sensor or network path. Leaving Spray by Auto press means the SEN65 starts from Idle, so for ~1 min (P-06, C-07) Auto runs only floor and DC demand. That's an accepted cost of the override. If an accidental Auto press while spraying turns out to bite, the fix is a firmware change (e.g. a run-on on Spray exit by Auto).

## D-025: Keep a wired, opto-isolated `DC_RUNNING` input as a BLE backup
- Date: 2026-10-26
- Status: Accepted (Andrew, Q-28 (f)). Amends D-016 and approved IR-01, AC-06
- Context: D-016 dropped the wired input for simplicity. Andrew wants it kept on the board as a backup in case BLE disappoints, and as the simpler AC-06 bench test.
- Decision: A second AC-input opto channel (`DC_IN`, GPIO1, J-DC 2-pos 3.5 mm screw terminal, D-032), the same circuit as occupancy but accepting 12–24 V AC or DC of either polarity (`docs/interfaces.md` §2.3). `dc_running = dc_ble OR dc_wired`; an unconnected input reads false, so no configuration. The BLE payload (D-021) is unchanged.
- Alternatives considered: dry-contact input with an isolated local source (needs an isolated supply on the node); no wired input (D-016 as was).
- Consequences: About $1 per board, one more cable entry and GPIO (spare 1 used). The DC project can drive it with a relay contact switching its own 12–24 V, or straight from the 24 VAC if it has one. AC-06 runs on the wired input; AC-22 still covers BLE once a test sender or the DC node exists. A spoofed BLE frame or a wired assert both only boost.

## D-026: Fan cable hard-wired into a 4-position terminal, no USB-C on the node
- Date: 2026-10-26
- Status: Accepted (Andrew, Q-25)
- Context: J-FAN was a USB-C receptacle, which needed the fan cable's USB-C contact map (Q-25) and created the mis-plug hazard D-020 addressed.
- Decision: J-FAN is a 4-pos 3.5 mm terminal (fixed screw, D-032) on the fan side of the barrier, labelled GND (BLK) / +10V (RED) / SPD (YEL) / TACH (WHT). Andrew hard-wires the four conductors (from the S6's Q-15 color map).
- Alternatives considered: USB-C receptacle wired to the measured contact map (needs Q-25 and a symmetry check).
- Consequences: Q-25 is closed with no measurement needed. No USB-C fan cable reaches the node. Mis-termination is the new risk: color labels, fan-side TVS, and the AC-18 bench check.

## D-027: Holds and scenes survive non-power resets (RTC memory)
- Date: 2026-10-28
- Status: Accepted (Andrew, Q-29). Amends approved NFR-07 and AC-18. Resolves G2 review B-1
- Context: Any reset ended Spray, so an OTA reboot, a stack panic or a watchdog trip could turn the fan off while vapor was present (SR-03).
- Decision: The current mode and its remaining time (any hold or scene, including Spray and SprayRunOn) live in RTC no-init memory with a CRC and are restored after every reset except power-on and brown-out. OTA isn't deferred, and a stuck task still just reboots (Andrew: no extra recovery machinery).
- Alternatives considered: Defer OTA during Spray and recover a stuck sensor task in place (proposed; more code paths for the same result).
- Consequences: A crash or OTA reboot costs a few seconds of fan-off (hardware hold-off during boot). A crash loop during a scene keeps resuming that scene, which is the safe direction for Spray. Power loss still returns to Auto. The Controller stays pure: snapshot/restore is host-tested; the RTC storage is platform code.

## D-028: Fan port treated as SELV on measured evidence; basic barrier kept; power-up burst accepted
- Date: 2026-10-28
- Status: Accepted (Andrew, Q-22/Q-30 measurements, S-1), confirmed by Q-31 (≈ 60 µA into 10 kΩ, under the 0.5 mA ES1 limit). Resolves G2 review B-2; closes S-1
- Context: B-2: the barrier is basic insulation while the port's SELV status was unknown, and lid-off flashing and AC-18's scope touch the fan side. S-1: when fan mains returns with the node off, the speed line can read high before the LDO-fed hold-off is up.
- Decision: Unplugged, port GND is open to L, N and earth (resistance and diode). Plugged in, ~65 VAC open-circuit to N/earth, which is consistent with Y-capacitor coupling from an isolated supply into a 10 MΩ meter. On that evidence the port is treated as SELV. The ≥ 3 mm basic barrier is kept for the ground loop and the capacitive float, with no fan-side cover or "unplug before service" rule. S-1's fan power-up burst is accepted (Andrew), so the LDO-fed hold-off stays.
- Alternatives considered: Reinforced barrier and fan-side cover regardless (unnecessary if Q-31 confirms). Feed Q1/U1 from +10 V to close S-1 (stays an option if Q-26 shows the port current is tight, since it also cuts the draw).
- Consequences: If Q-31 reads above the ES1 touch-current limit (0.5 mA), B-2's reinforced fix applies before layout. AC-18 records fan power-up behavior instead of requiring it to be off.

## D-029: Phase 3 starts with the schematic and a priced parts list
- Date: 2026-10-28
- Status: Accepted (Andrew)
- Context: The part choices (ESP32 module, H11L1-class opto, regulators, display) drive cost, JLC extended-part fees, board size and enclosure dimensions. Pricing was planned for phase 4, after the mech and firmware work that depends on those parts.
- Decision: After G2, phase 3 runs in this order: (1) PCBA vendor check (JLC Economic rules, Q-14); (2) KiCad schematic, ERC clean; (3) priced parts list from the schematic: LCSC basic/preferred/extended status, stock, price, fees, plus off-board parts; Andrew reviews it as a checkpoint; (4) only then PCB layout, mech and firmware. G4 still approves the final BOM.
- Alternatives considered: phase order as in CLAUDE.md (design everything, then source).
- Consequences: Part swaps to cut extended-part fees (e.g. LTV-814 → PC817 + diode, 5→3.3 V buck → AMS1117, enabled LDO → AMS1117 + AO3401) are made in the schematic, not after layout. The firmware host-test work also waits; it doesn't depend on hardware, but Andrew wants the cost picture first.

## D-030: Single external USB-C for power and flash/log; 3.3 V only
- Date: 2026-10-28
- Status: Accepted (Andrew). Amends D-018 (adapter, on-board supply) and NFR-04; supersedes D-020
- Context: Nothing on the node needs 5 V except the indicator LEDs, which can run from a 5 V input directly. D-018's two reasons for 12 V were the mis-plug risk next to a USB-C fan cable (gone with D-026) and cable drop into a 5 V rail (moot once everything regulates to 3.3 V).
- Decision: Power comes from a listed 5 V USB-C adapter (≥ 2 A) through the node's only external USB-C, which is also the native-USB flash/log port. On board: polyfuse, TVS, one 5→3.3 V regulator (buck or low-dropout LDO, picked in the schematic), and a P-FET load-switched 3.3 V sensor rail. The receptacle sits behind a compressed foam gasket in the wall, facing the cabinet; its mouth is an accepted NFR-04 exception (Andrew: reduced IP5X intent is OK if sealing adds complexity).
- Alternatives considered: 12 V barrel with an internal USB (D-018/D-020 as was: two regulators, lid-off flashing). A gasketed panel-mount USB-C pigtail (better seal, more parts and a cable inside).
- Consequences: Fewer parts (no 12→5 V buck, no reverse-polarity FET, no barrel jack, no VBUS OR-ing), and flashing/logs without opening the lid. The input cable needs 24 AWG or heavier power conductors and ≤ 3 m. Running from a PC port during flashing means a lower indicator cap. No 12 V headroom for future loads.

## D-031: Indicator: plain RGB, short strip by the display; sensor load switch kept for recovery
- Date: 2026-10-28
- Status: Accepted (Andrew)
- Context: FR-15 needs one band color (or a red fault flash) readable down the shop; nothing needs per-LED effects. The 12-LED bar along the enclosure's bottom edge had no derivation behind its count. Separately: does the SEN65 need a power switch when sleep uses the module's Idle command?
- Decision: Plain RGB LEDs driven by three LEDC PWM channels through low-side N-FETs from the 5 V input; no WS2812B or level shifter. A short diffused strip aligned with one edge of the display; length, diffuser depth and LED count are set in mech (~4–8 LEDs). No illuminated encoder (Andrew: only worth it as a simpler or cheaper replacement for the strip, and a lit shaft isn't readable down the shop, FR-15). The SEN65 load switch stays, for unattended recovery of a hung module only (a node reboot doesn't reset it); S-13's back-powering fixes are applied.
- Alternatives considered: WS2812B bar (extended part plus shifter; effects not wanted). Illuminated RGB encoder as the indicator (too small and dim for FR-15 at ~30 ft; costs more than a plain EC11 plus a few LEDs). No sensor switch (two fewer parts; a hung sensor then needs a USB replug).
- Consequences: GPIO 48/41/42 for R/G/B; one spare (GPIO 2) left. The LEDs and FETs are probably JLC basic parts, but each LED needs a resistor per color. `SEN_PWR_EN` is active low with a gate pull-up (the earlier "pull-down" was wrong for a P-FET).

## D-032: Fixed screw terminals for all field wiring
- Date: 2026-10-28
- Status: Accepted (Andrew)
- Context: J-FAN, J-OCC and J-DC were pluggable. Andrew plans to wire it once, and a plug can't pass back out through a gland sized for its cable, so pluggable saved nothing on removal.
- Decision: Fixed 3.5 mm screw terminals (one part, 2- and 4-position) for J-FAN, J-OCC and J-DC, inside the sealed compartment behind the cable glands.
- Alternatives considered: Pluggable terminals (a bench swap without re-terminating; ~$1–2 more and a mis-plug question). Pluggable headers through the rear wall (lid-closed removal, but another sealing gap).
- Consequences: Taking the unit down means lid off and unscrewing the conductors. The J-OCC/J-DC mis-plug question and the pitch-keying go away. One terminal part family for the BOM.

## D-033: Controller on the refrigerator side panel next to the hood
- Date: 2026-10-29
- Status: Accepted (Andrew, Q-27/Q-32, 2026-10-29). Amends D-015's spot and approved NFR-09, IR-04
- Context: Andrew proposes the side of the refrigerator panel beside the hood (`docs/site/mounting location option - next to intake.jpg`): within reach, near the airflow, still visible from most of the shop. NFR-09 wants the sensor inlet ≥ 3 ft from the hood's edge; the panel looks closer.
- Decision: Wall-mount a few inches back from the panel's front edge, center ~60" up (hood intake ~66"); the panel face is ~18" laterally from the hood's edge, so the inlet is ≈ 2 ft from the hood. Display faces across the kids' workbench; the sensor inlet and indicator are on the room-facing end. NFR-09's distance becomes "as far from the hood as the mount allows" (≈ 2 ft), validated by AC-17.
- Alternatives considered: Under the north cabinets ≥ 3 ft from the hood (D-015 as written; harder to reach).
- Consequences: The enclosure becomes a flat wall mount, not a cabinet-hung unit (D-019's compartments stay; the slide-off bracket becomes a wall cleat). The kids' workbench below (glue, markers, hot glue) will show as local VOC/PM and can raise the fan; accepted unless AC-17 or commissioning shows it misleads clear-down. At ~60" over a kids' bench, the panel is in children's reach: holds expire and the logic returns to Auto, and a panel lock is on the firmware backlog. Cable route from the fan cabinet down the panel edge, < 10 ft.

---

## Gate approvals
| Gate | Date | Approved by | Notes |
|------|------|-------------|-------|
| Phase 0 survey | 2026-10-25 | Andrew (with G1) | Survey and photos committed d9833fd |
| G1 Requirements | 2026-10-25 | Andrew | `docs/requirements.md` as of this commit, including the SEN65 consequences (FR-14 baseline survival, FR-08 sensor sleep during Spray minimum run-on) |
| G2 Architecture | | | |
| G3 Mains/safety | | | |
| G4 BOM | | | |
| G5 First power-up | | | |

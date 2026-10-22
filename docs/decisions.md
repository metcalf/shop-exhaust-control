# Decision Log

ADR-lite format. Status is one of: **Proposed**, **Accepted**, **Superseded by D-nnn**, or **Rejected**. Gate approvals are logged here too.

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

## D-003: Local analog controls; Home Assistant for history and alerts
- Date: 2026-10-22
- Status: Accepted (Andrew)
- Context: Andrew doesn't want to pull out a phone at the bench.
- Decision: Physical mode selector and indicators at the fan. Home Assistant handles logging, notifications and remote viewing.
- Consequences: Physical controls take precedence (see `docs/interfaces.md` §4). The exact precedence rule is decided at G2.

## D-004: A single PM sensor with adaptive duty cycling
- Date: 2026-10-22
- Status: Proposed (working assumption; confirm at G2)
- Context: PM sensors foul in dusty air. A Sharp GP2Y1014 as the coarse trigger and smoke-detector internals were both considered.
- Decision: One PMS5003-class sensor. Run it continuously at low dust and sample sparsely at high dust (Andrew's scheme, see context). No Sharp sensor.
- Alternatives considered:
  - Sharp plus SPS30 split (more parts, and the Sharp's resolution is too coarse for turning the fan off).
  - Running the sensor only at high dust (backwards: it concentrates fouling exactly where readings add the least).
  - SPS30 instead of the PMS5003. Still open: better contamination resistance and life, at a higher cost.
- Consequences: The sampling-schedule logic is the most complex part of the firmware, so it gets simulation tests first.

## D-005: v1 is built from off-the-shelf modules and listed components
- Date: 2026-10-22
- Status: Proposed
- Context: Claude is weak at PCB layout. Mains parts must be listed.
- Decision: ESP32 dev board, DIN-rail relays and contactors and supplies, sensor breakouts. No custom PCB in v1.
- Consequences: The enclosure needs room for modules. A custom PCB can be reconsidered for v2.

## D-006: Capacitor run-on for contactor coils rejected (DC project, recorded for reference)
- Date: 2026-10-21
- Status: Rejected
- Context: A run-on delay for the DC after the blast gates close.
- Decision: Don't hold a contactor coil up with a capacitor. Use an off-delay timer relay, or have the controller drive the coil.
- Consequences: A decaying coil voltage causes chatter and contact pitting, and the timing drifts.

---

## Gate approvals
| Gate | Date | Approved by | Notes |
|------|------|-------------|-------|
| G1 Requirements | | | |
| G2 Architecture | | | |
| G3 Mains/safety | | | |
| G4 BOM | | | |
| G5 First power-up | | | |

# Fan PWM: findings from the rollitup Cloudline/ESP32 thread

Source: https://www.rollitup.org/t/idiots-guide-to-getting-an-esp32-to-control-ac-infinity-cloudline-ec-fans-esphome-ha.1053910/ (all 10 pages, 190 posts, read 2026-10-28). Forum reports, not measurements we made.

- **PC817 at 1 kHz is not validated.** The original build switched the speed line with a MOSFET module; the PC817 was optional, ahead of it. 1 kHz "seemed to work well enough". No one reported duty accuracy or low-end behavior with a bare PC817 on the fan side.
- **Frequencies reported working:** 1 kHz, 4,156 Hz (scoped on an S4 stock controller), 5 kHz, 10–14 kHz. 40 kHz reported not working. Our S6's stock controller is 5 kHz (Q-15).
- **Low end:** one builder at 1 kHz saw no rotation below 30 % duty; another at 5 kHz found a narrow responsive range. Possibly wiring/inversion confusion; our stock level 1 is 20 %.
- **Port current:** A6 Lite stock controller labelled 10 V, 0.5 W (~50 mA). One overload report (three channels on one fan's +10 V; fan stopped supplying 10 V until mains was cycled), later partly withdrawn. Our fan-side budget is ~9 mA (Q-26 still to measure).
- **Tach:** open-collector, sinks to ground per pulse. Matches `docs/interfaces.md` §2.1.
- **Fail state:** one builder saw the fan stay still through OTA and reboot with his fail-off design.
- **Damage:** one builder lost two fans, cause unknown. Scope the speed line before connecting a new design.
- **JLC Economic PCBA:** one board designer says its reflow is too hot for ESP32 modules and used Standard. Unverified; check in the vendor research.

**Decision (Andrew, 2026-10-28):** keep the H11L1 at 5 kHz. Revisit PC817 at ~1 kHz (with tach-trimmed duty) only if the priced parts list shows a significant cost difference; that would need a bench test on the S6 first (tach vs duty against stock levels 1/4/10 = 30/75/144 Hz).

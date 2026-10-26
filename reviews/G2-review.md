# G2 Review: Architecture sign-off

**Reviewer:** independent reviewer subagent, 2026-10-26
**In scope:** `docs/requirements.md`, `docs/interfaces.md`, `docs/architecture.md`, `docs/control-logic.md`, `docs/decisions.md` (D-016 to D-026)
**Not read (per brief):** STATE.md, context.md, open-questions.md, process-notes.md, scripts/
**Method:** desk review only. Nothing was built, simulated or measured. Datasheet figures below come from memory and need checking in phase 3 where marked "(verify)".

Overall: the architecture is coherent and traceability is close to complete. The fan-powered fail-off interface (D-023) is a good answer to SR-08. Three issues block G2. Two are safety holes (an SR-03 hole through resets, and an unverified fan-port SELV assumption combined with lid-off servicing). The third is a logic contradiction that turns heavy dust into a sensor fault.

---

## Blocking

### B-1. Any reset ends Spray, so a network or sensor path can cancel SR-03
- **Location:** `control-logic.md` §2 ("Reset or power loss: always Auto"); `architecture.md` §4 (task watchdog covers `control` **and** `sensor`; esp-iot-core OTA); NFR-07; SR-03.
- **Problem:** NFR-07 says every reset goes to Auto. The firmware has several ways to reset that come from a sensor or the network:
  - a `sensor` task stall (I²C hang, driver bug) trips the task watchdog and reboots the node;
  - a Wi-Fi, MQTT or NimBLE stack panic reboots it;
  - an OTA update reboots it after the image lands.

  Each one ends Spray or SprayRunOn. If the shop is vacant (or the vacant limit has passed), Auto then turns the fan **off** while vapor is still present.
- **Why it matters:** SR-03 (M, safety) requires full exhaust "regardless of any sensor, sensor fault, or network state". The architecture's claim that only explicit user input ends Spray (D-024 consequences) doesn't hold.
- **Suggested fix (needs Andrew, because it amends NFR-07):**
  1. Keep the Spray/SprayRunOn state (mode, `t_end`, remaining D) in RTC memory (`RTC_NOINIT_ATTR`). It survives software, panic and watchdog resets on the S3, but not power-on or brown-out.
  2. On any non-power-on reset, resume Spray/SprayRunOn. Write this into NFR-07 as an exception.
  3. Defer OTA reboots while in Spray or SprayRunOn (and ideally during any hold).
  4. Don't reboot the system for a `sensor` task stall. Recover by power-cycling the module or restarting the task.
  5. Add an AC-05/AC-18 case: forced panic and OTA during Spray, then check the fan is still at 100 %.

### B-2. SR-09 rests on an unverified SELV assumption, and servicing exposes the fan side
- **Location:** SR-09; `interfaces.md` §2 (Q-22 open) and §2.1 "Barrier"; D-020 (flashing needs the lid off); AC-18 (scope the speed line on the fan side); `architecture.md` §6 ("nothing fan-side is touchable").
- **Problem:**
  - The design reaches **basic** insulation (3.0 mm, 3.75 kV optos). If the port were not SELV, basic insulation alone between a hazardous circuit and an unearthed, touchable SELV node (panel, USB to a PC) wouldn't be enough under IEC 62368-1. That needs reinforced or double insulation. The CLAUDE.md safety rule also asks for reinforced.
  - 3.0 mm also falls short of reinforced creepage at 150 V working voltage for FR-4 (material group IIIb, PD2). Basic is about 1.6 mm, so reinforced is about 3.2 mm (Table 17, verify).
  - The bigger gap is operational. First flash and recovery need the lid off (D-020). AC-18 has Andrew clip a scope ground onto GND_F. Both put hands and grounded test gear directly on the fan side, with no insulation at all, while its status is "unknown".
- **Why it matters:** this is the one place a hazardous voltage could reach a person. The cheapest fix is a measurement, not a redesign.
- **Suggested fix:** close Q-22 before G2 is recorded, or record G2 as conditional on it before any phase-3 layout.
  - **Measurement:** with the S6 plugged in, measure AC and DC volts from port GND and +10 V to receptacle earth and neutral. With the S6 unplugged, measure resistance from port GND to each plug prong. Also check the S6 documentation or listing for a Class 2 / SELV port statement.
  - **If it's SELV:** say so in SR-09 and keep the barrier as functional isolation (ground loop).
  - **If it's not, or it can't be shown:**
    - make the barrier reinforced: ≥ 4 mm with a routed slot where it's tight, and optos with reinforced IEC 60747-5-5 ratings at the working voltage;
    - require unplugging the J-FAN pluggable terminal before lid-off service;
    - add an insulating cover over the fan-side section;
    - have AC-18 use a differential or isolated probe.

### B-3. Heavy dust can be classed as a sensor fault, so PM demand drops at the worst moment
- **Location:** `control-logic.md` §6 `sensor_range` ("PM above the module's output range … for P-18"); §4 ("A saturated reading (≥ 1,000 µg/m³) counts as 1,000 and marks the sample saturated"); FR-06; SR-04.
- **Problem:** FR-06 (M) says a reading at or above the range limit is "high". SR-04's "out-of-range readings" are meant as invalid data. As written, though, `sensor_range` fires on PM above the output range for 60 s. The SEN6x reports mass concentration as a scaled uint16. It can report valid values above 1,000 µg/m³, and it uses a distinct code (0xFFFF) for "unavailable" (verify).
  - An uncollected planer or band saw run at the north end can hold PM above 1,000 for more than 60 s while the Sampler is still Continuous, before the first sparse window.
  - That raises a fault, which forces PmActive clear. The fan drops to the P-01 floor (or off if vacant) in the heaviest dust.
- **Why it matters:** this is a direct contradiction between FR-06 and SR-04 in the design. The result is the opposite of the intended behavior, and AC-02/AC-20 as written wouldn't catch it.
- **Suggested fix:**
  - Define `sensor_range` as invalid codes only (0xFFFF/"not available"), physically impossible combinations (e.g. PM1.0 > PM2.5 > PM10 ordering violated, number concentrations at zero while mass is high), or stuck raw values.
  - Never let any value ≥ range limit raise `sensor_range`. Clamp it to saturated.
  - Add a sim test: PM pinned at 1,000 (and at 1,500, if the module can report it) for 30 min. Expect no fault and full or sparse handling.

---

## Should fix (before G3)

### S-1. Fan-side power-up: the hold-off waits for an LDO while the fan's pull-up doesn't
- **Location:** `interfaces.md` §2.1 (Q1 gate pulled to +5F from an LDO on +10 V); SR-08; AC-18.
- **Problem:** the case is node unpowered (or still booting) when fan mains returns, e.g. after a mains blip that resets both.
  - Yellow is pulled up by the fan's 2.2 kΩ straight from +10 V. Q1's gate only rises once the LDO is in regulation (dropout, soft-start, and Vgs(th) up to ~2.5 V for 2N7002).
  - During that window the fan sees "high = full speed". Whether the fan's MCU latches a speed in that window is unknown. AC-18 doesn't test this ordering: it scopes "through reset" and "node unpowered", but not "fan mains applied with node off".
- **Why it matters:** SR-08's "held off with node unpowered" has to hold at fan power-up too, which is when it's most likely to be exercised.
- **Suggested fix:**
  - Drop the LDO from the hold-off path. 2N7002 Vgs max is ±20 V and H11L1 VCC is 3–15 V (verify), so pull Q1's gate (100 kΩ is enough) and U1's VCC straight from +10 V. The hold-off then rises with the same rail as the fan's own pull-up.
  - Keep a small 5 V rail, or a divider, only for the tach pull-up and LED.
  - Add an AC-18 step: node unpowered, cycle the fan's mains 5×, scope yellow and watch the impeller. Repeat with node first, then fan.
  - This also cuts fan-side current (helps S-2).

### S-2. The SR-08 mechanism depends on Q-26 (port current), and the worst case is understated
- **Location:** `interfaces.md` §2.1 current budget; D-023 status and fallback.
- **Problem:**
  - The budget says ≤ 8 mA worst case with U1 at 1–2 mA. The H11L1 datasheet ICC maximum is about 5 mA (verify at 5 V). Worst case is then about 5 + 0.5 (gate) + 2.6 (tach LED plus 10 k when white is low) + 1 (presence) ≈ 9 mA.
  - The D-023 fallback ("drop the presence LED") removes FR-18's `fan_port` detection. D-023 doesn't say so.
  - Q-26 is a bench measurement: load red with 1.2 kΩ and watch the voltage and fan behavior.
- **Why it matters:** if the port can't supply this current, the whole fail-off architecture (SR-08, M) changes.
- **Suggested fix:**
  - Measure Q-26 before the schematic starts.
  - Restate the worst-case budget from datasheet maxima.
  - List the FR-18 cost of the fallback in D-023.
  - S-1's change lowers the draw.

### S-3. No fault for a fan running when it shouldn't (open yellow, Q1 open, fan side unpowered)
- **Location:** FR-18; `control-logic.md` §6 `fan_tach` (only "tach < C-14 × expected"); `architecture.md` §6.
- **Problem:** several faults make the fan run at **full** with no alarm, because FAN_PRESENT stays good and the tach is higher than expected, not lower:
  - a loose or broken yellow conductor at J-FAN;
  - Q1 failed open;
  - a U1 output stuck low.

  The commanded-0 % case isn't checked either (`fan_tach` needs duty ≥ C-06).
- **Why it matters:** while vacant this defeats FR-19's limits (noise and heat loss all night) and NFR-07/SR-08's "off". It's the mirror image of the fault FR-18 already covers.
- **Suggested fix:**
  - Add `fan_overspeed`: tach > (1/C-14) × f_expected(duty) for P-16, or tach above a few Hz while commanded 0 % (after a spin-down allowance).
  - This needs an FR-18 amendment (S) and an AC-07 bench case with yellow disconnected.
  - Use the same tach reading to tell the two `fan_port` causes apart: no +10 V with tach present means a wiring fault; no +10 V with no tach means no mains.

### S-4. Isolation domains and every barrier crossing aren't defined
- **Location:** `interfaces.md` §2.1–§2.3 ("Same ≥ 3 mm barrier as §2.1"); `architecture.md` §1 (OCC_IF and DC_IF drawn outside both domains).
- **Problem:** the board has at least four galvanic domains: fan (GND_F), occupancy (24 VAC), DC_IN (DC controller's supply) and node. The docs give spacing only to the node side. They don't define:
  - fan↔OCC and fan↔DC spacing (these matter if B-2 finds the port isn't SELV, since the 24 VAC field wiring is accessible);
  - OCC↔DC spacing;
  - the 3.5 mm-pitch terminal blocks sitting next to each other.

  Other crossing paths aren't excluded either: copper pours, stitching vias, mounting holes and heat-set inserts, any Y cap, the shared cable gland. TVS parts are "across the input" in §2.2 but not stated for §2.3.
- **Why it matters:** SR-09 and AC-26 ("no galvanic connection") have to be checked per domain pair, and the phase-3 DRC rule (D-010) needs the list.
- **Suggested fix:** add a short isolation-domain table to `interfaces.md`. List each domain, the required insulation grade to each other domain, the spacing, and the parts that cross. State "no Y caps, no pours, no metal fasteners across any barrier". Put the TVS across the pair (not to any ground) on both field inputs.

### S-5. The wired DC_IN input is marginal at 12 V and probably fails at 12 VAC
- **Location:** `interfaces.md` §2.3 (2 × 2.7 kΩ, LTV-814-class, 10 kΩ pull-up, 1 µF).
- **Problem:**
  - **12 V DC:** IF = (12 − 1.2)/5.4 k ≈ 2.0 mA, or 1.8 mA at 10.8 V. LTV-814 CTR is 20 % minimum (verify), so IC is about 0.36–0.40 mA against the 0.33 mA the 10 kΩ pull-up needs. That's no margin for temperature or aging.
  - **12 VAC** (17 V peak): the LED only pulls the node low above about 10 V. The off-gap is about 72° per half-cycle, roughly 3.3 ms, and the 10 ms RC rises about 0.9 V in that time, which is at or above VIL. At minimum CTR the GPIO chatters at 120 Hz, so the 0.5 s debounce may never see a stable assertion.
  - **For comparison, the occupancy input (§2.2) checks out:** 24 VAC peak 34 V, threshold about 8.5 V, gap about 1.3 ms, ripple about 0.4 V.
- **Why it matters:** IR-01 and D-025 promise 12–24 V AC/DC from the DC project, and AC-06 relies on this input.
- **Suggested fix:** use a CTR-ranked part (LTV-814A, 50–150 %), raise the node-side pull-up to 33–47 kΩ with a matching cap, and/or use a bidirectional current limiter in place of the resistors. Recheck with worst-case CTR at 12 VAC, 12 V DC and 26.4 VAC. The 26.4 VAC check covers LED current and resistor dissipation.

### S-6. A crashed DC node can advertise a stale DC_RUNNING forever
- **Location:** `interfaces.md` §1 (failure behavior), §1.1 (sequence "increments … at least once per 10 s"; exhaust handling ignores it).
- **Problem:** on ESP32 the BLE controller keeps advertising the last payload when the host task hangs. P-24 only catches silence, not frozen frames.
- **Why it matters:** if the DC node hangs while DC_RUNNING is set, boost stays on indefinitely while occupied (60 %, noise and heat loss). It's not a safety issue, but the protocol field built to detect this goes unused.
- **Suggested fix:** in `DcLinkParser`, treat a frame whose sequence hasn't changed for > P-24 (e.g. 15 s) as invalid. Add it to the AC-22 sim part. Because this is shared-interface behavior, record it in D-021.

### S-7. SprayRunOn has no upper bound while occupied
- **Location:** `control-logic.md` §2 SprayRunOn exit; FR-08.
- **Problem:** while occupied, the only exits after P-09 are "PM < P-04 **and** VOC < off" or a user press. These cases each hold the fan at 100 % indefinitely:
  - background PM2.5 above 12 (smoke season, a dusty day in the shop);
  - a lingering VOC source such as a freshly finished piece off-gassing;
  - a fouled sensor reading high.

  Auto would handle the same air at P-13 or the PM ramp.
- **Why it matters:** it's loud, wastes conditioned air, and only ends by user action. It's the occupied counterpart of the case FR-19 was written for.
- **Suggested fix (needs Andrew, FR-08 amendment):** after P-09, exit to Auto once the VOC index is below P-12 off and PM is below P-03 (rather than P-04), letting Auto's own PM/VOC demand finish the job. Alternatively, cap SprayRunOn at a C-xx maximum and then hand to Auto with a notice. Add both to AC-05/AC-27.

### S-8. A sensor unplugged while Resting or Off isn't detected within AC-20's time
- **Location:** `control-logic.md` §6 `sensor_no_data` ("Sampler wants Measure, past warm-up"); AC-20 ("Fault shown within P-18 + 5 s").
- **Problem:**
  - If the module is unplugged during a sparse rest (up to 10 min) or while Off, the fault appears only after the next window: rest + P-06 + P-18.
  - During Protect it appears only after the wake.
  - The Sampler's behavior while faulted (keep Measuring? only the C-12 cycles?) isn't specified.
- **Why it matters:** AC-20 as written fails depending on Sampler state. Late detection also delays the HA alert (FR-13).
- **Suggested fix:** I²C works with the SEN6x in Idle, so probe it (status or serial read) every 10–30 s in every Sampler state except unpowered, and raise `sensor_no_data` from failed probes. Specify the Sampler state while faulted. Make AC-20 cover unplugging in Continuous, Resting and Off.

### S-9. The tach-fault timer can be reset forever by duty changes
- **Location:** `control-logic.md` §6 `fan_tach` ("ignoring C-15 after any duty change"); §7 down-ramp at 2 %/s and up-steps on noise.
- **Problem:** in Auto, duty changes every second during ramps and on each up-step. If each change restarts the C-15 (10 s) ignore window and the P-16 (30 s) count, a dead fan in a busy Auto period never faults.
- **Suggested fix:** apply C-15 only after a change larger than about 10 % or a 0 → on transition. Keep accumulating P-16 across small changes. Treat tach = 0 at duty ≥ C-06 as a fault after C-15 from the last 0 → on transition, regardless of later changes. Add a sim test with a noisy Auto trace and the tach at 0.

### S-10. PM, VOC and filter state across Idle, Protect and fault exit is unspecified
- **Location:** `control-logic.md` §2 (Auto press leaving Spray), §4 (EMA, PmActive), §5.
- **Problem:**
  - Entering Protect or Resting leaves the "last filtered PM2.5" and PmActive stale. After an Auto press out of Spray, it's unclear whether the stale pre-Spray PmActive keeps driving demand. §2 says PM "needs P-06 before it counts", while §4 holds sparse values between windows.
  - The EMA initial value after any Idle or fault exit isn't defined. Starting from a stale low value biases the SprayRunOn exit toward "clean". It's safe with the current C-01/C-02 ratio, but fragile if they're tuned.
- **Suggested fix:**
  - Define the behavior: on entering Protect, clear PmActive and VocActive. On any measurement start, seed the EMA with the first valid reading. On fault exit, reset the filters and require P-06 again.
  - Add sim cases for an Auto press mid-Spray with high pre-Spray PM, and for a SprayRunOn wake where the pre-Spray PM was low but the post-spray PM is high.

### S-11. P-07 is a range, and the low end of it fails AC-02
- **Location:** P-07 ("30 s sample every 5–10 min"); `control-logic.md` §5 (window = P-06 + C-23 = 40 s, not 30 s); AC-02 (≤ 10 % at saturation).
- **Problem:** at a 5 min rest, on-time is 40/340 ≈ 11.8 %, which fails AC-02. Tests need a single value, and the window length disagrees with P-07's 30 s.
- **Suggested fix:** set P-07 to a single rest (10 min, as §5 assumes), define the window as P-06 + C-23, and state the resulting duty. Or relax AC-02.

### S-12. SEN65 status bits: warnings are treated as errors, and a gas error drops PM too
- **Location:** `control-logic.md` §6 `sensor_status` ("fan, laser, gas, RH/T").
- **Problem:** the SEN6x status register distinguishes warnings (e.g. fan-speed warning, also set during cleaning) from errors (verify). Treating every bit as a fault drops PM demand on a benign warning. A gas-only error drops PM demand too, even though PM is fine. SR-04 says a module fault drops both, but a partial error isn't really a module fault.
- **Suggested fix:**
  - Fault only on error bits, debounced by P-18, and ignore them during `Clean`.
  - Consider mapping gas or RH/T errors to "VOC invalid" only, and laser or fan errors to PM fault. This keeps SR-04's intent and may need a small SR-04 wording change.

### S-13. The SEN65 can be back-powered through I²C when its rail is off
- **Location:** `interfaces.md` §2 (pull-ups on the sensor rail; `SEN_PWR_EN` power-cycle for recovery, SR-04).
- **Problem:** if firmware leaves SDA/SCL with ESP internal pull-ups enabled, or drives them high, while the rail is off, the module is powered through its ESD diodes. The power-cycle then doesn't reset it, which is the recovery path for SR-04 faults.
- **Suggested fix:** pull-ups to the switched rail only (already stated). Firmware switches SDA/SCL to output-low or hi-Z with no pull-ups before disabling the rail. Use an LDO with active output discharge. Bench-verify that the rail falls below about 0.3 V during a power-cycle.

### S-14. The reset-to-safe claim depends on watchdog and boot configuration
- **Location:** `architecture.md` §4 ("On any reset the opto LED goes dark…"); `control-logic.md` §7.5.
- **Problem:**
  - ESP-IDF's task watchdog only logs by default. `CONFIG_ESP_TASK_WDT_PANIC` must be enabled, or a stalled `control` task leaves the LEDC running at the last duty indefinitely.
  - LEDC must be configured with duty 0 before the pin is routed, or boot can produce a glitch.
  - There are no BOOT (GPIO0) or EN buttons for recovery if the app breaks USB-Serial-JTAG.
- **Suggested fix:** list these as phase-3 requirements in architecture §9: TWDT panic on; RTC watchdog on; LEDC duty 0 before GPIO matrix routing; internal BOOT and EN tact switches or pads; EN RC per the Espressif hardware design guide.

### S-15. Missing ACs and tests: FR-13 maintenance logic and FR-20
- **Location:** requirements §9 (every requirement has an AC, by convention); `control-logic.md` §10.
- **Problem:**
  - FR-13's filter-exposure accumulation, P-14 threshold, panel clear and NVS persistence have no sim test. AC-09 only checks that the entities exist.
  - FR-20 (C) has no AC at all.
  - NFR-02's clean scheduling (C-19) isn't tested in sim.
- **Suggested fix:** add sim tests for exposure accumulation, threshold, clear, persistence across reset and C-19 scheduling. Add an AC for FR-20 (bench: temperature and RH within a stated offset of a reference after the offset is set), or mark FR-20 as exempt.

### S-16. AC-09's 60 s LWT needs a short MQTT keepalive
- **Location:** AC-09; `interfaces.md` §4.
- **Problem:** esp-mqtt's default keepalive is 120 s, and the broker fires the LWT after about 1.5 × keepalive, so about 180 s. That fails AC-09.
- **Suggested fix:** state keepalive ≤ 30 s in `interfaces.md` §4, and check that esp-iot-core `BaseMqttClient` exposes the setting. If it doesn't, fix it upstream.

### S-17. The 24 VAC TVS has little margin over a lightly loaded transformer
- **Location:** `interfaces.md` §2.2 (SMBJ40CA, "above the 37 V peak of 24 VAC + 10 %").
- **Problem:** Class 2 24 VAC transformers commonly read 26–29 VAC lightly loaded (39–41 V peak). Add a high-line mains and the peak reaches the 40 V standoff, so leakage and heating rise.
- **Suggested fix:** use SMBJ48CA (or a MOV with ≥ 30 VAC continuous rating). The extra clamp voltage is harmless with 4.4 kΩ in series and a bidirectional LED. Bench-measure the actual secondary voltage with the lights on.

---

## Notes

- **N-1 Power budget** (`interfaces.md` §3). Peak at 12 V comes to about 0.46 A once the sensor LDO's 5 V input power (5 V × 350 mA) and the second-stage buck are counted, not 0.40 A. It's still well within 1 A. "TVS (15 V)" should say standoff vs. breakdown. If it's a 15 V standoff, the clamp (~24 V) sets the buck's minimum VIN rating.
- **N-2 Fan-side TVS standoffs** (§2.1). Yellow and red sit at +10 V, and white may too if the tach is push-pull. Specify ≥ 12 V standoff on all three. With a push-pull 10 V tach, the 10 k pull-up on white back-feeds +5F at 0.5 mA, which is fine as long as the +5F load stays above that.
- **N-3 Fan-end USB-C orientation.** The node end is now hard-wired (D-026), but the fan-end plug can still be inserted either way. Add "both orientations at the fan end" to AC-18.
- **N-4 `t_vacant` at boot** (`control-logic.md` §3). Restarting the vacant limit on reboot makes the fan run longer, the opposite of conservative for FR-19. A reboot loop while vacant could run the fan at P-22 all night. Keep the elapsed vacant time in RTC memory across non-power-on resets. This goes with B-1.
- **N-5 `fault_reason`** is a single text value. Simultaneous faults (sensor plus fan) need a list or a priority order.
- **N-6 Effective minimum Spray run-on** is P-09 + C-02 (≈ 21 min), because VOC first becomes valid at `t_min` and then needs C-02 of data below off. That's fine; document it so commissioning isn't surprised.
- **N-7 FR-01 example** is "max for 20 min", but the encoder offers 15 min steps. Either change the example or allow 5 min steps below 1 h.
- **N-8 AC-18** says "duty ±2 % across 5–100 %", but OutputShaper raises anything below C-06 (10 %) to C-06. State that AC-18 drives LEDC directly (test firmware) or start the range at C-06.
- **N-9 AC-22** "no false assertion from other BLE devices" needs a duration and an environment (e.g. 24 h in the shop with phones present).
- **N-10 Accidental override.** Any one-press button (Quiet, Boost, Auto) ends Spray at once. Quiet drops the fan to 30 % mid-spray. This is accepted in D-024; it's recorded here so the G3 safety summary lists it.
- **N-11 A sensor power-cycle during Protect** is pointless (the fault can't clear without Measure). The SEN6x powers up idle, so it's harmless, but skip it.
- **N-12 IR-02 future auth.** A 16-bit wrapping sequence that resets on reboot is a weak replay guard for type 0x02. Note that a persistent or wider counter will be needed. This doesn't block v1.
- **N-13 HA recorder volume** (§4). 1 Hz × ~30 entities is about 2.6 M rows a day. Consider putting raw and diagnostic channels on a separate topic that is only published while a "capture" mode is on, or rely on remote logging for traces.
- **N-14 Antenna** at the board's top edge, directly under the cabinet bottom, with the DC about 30 ft south. Check the cabinet material, and log RSSI in AC-22 as planned.
- **N-15 Cost estimate** omits the SEN65 cable (not bundled with the module, verify) and a spare or sacrificial S6 cable if Andrew cuts one for D-026.
- **N-16 Grommet pass-through** (`interfaces.md` §5). A pre-terminated SEN65 cable has to pass the dividing wall, so use a split grommet or pass the board-end connector through. Plan it in mech.
- **N-17 G3 scope** (SR-07). Include confirmation that the lighting transformer is Class 2, so CL2 thermostat wire is permitted on its secondary.
- **N-18 Traceability nits.** SR-02 is traced to AC-15, which checks dust ingress, not "outside the airstream". Add an explicit location check (inspection at install). Backlight dimming (C-21) and info pages have no requirement. They're harmless, but the "none" claim in `architecture.md` §7 is slightly overstated.
- **N-19 GPIO choices.** I found no strapping, flash, PSRAM or USB conflicts on the N16R8. Three points:
  - GPIO 39 and 40 are the pad-JTAG pins, which is fine with USB-JTAG.
  - GPIO 15 and 16 are the 32 kHz crystal pins, which is fine since no crystal is fitted.
  - A brief high glitch on GPIO4 at power-up would only release yellow for tens of µs. Still confirm it against the S3 power-up glitch table, as §9 already plans.

## Checked and found consistent (no action)
- **SR-08 node side:** GPIO4 has a 10 k pull-down. LED current is about 4–5 mA against H11L1 IF(on) ≤ 1.6 mA (verify). H11L1 inverting polarity matches "LED on = released". Timing is about 1–4 µs against a 200 µs period.
- **Occupancy input:** CTR, ripple and turn-off (~14 ms) all fit AC-04.
- **BLE:** payload fits a legacy advertisement (26 of 31 bytes). Burst plus 30 % scan supports ≤ 3 s. P-24 together with P-11 masks the expected reception gaps.
- **SR-04 fallback logic:** matches the amended requirement (floor and DC kept, within FR-19).
- **FR-19 with DC boost and Spray:** matches AC-27, including the vacant SprayRunOn exit and the latch reset on occupancy.
- **Sampler rest bound:** the derivation is sound under its stated assumption (true k ≤ k_hi). With the initial values R_max always binds (e.g. p = 35 gives a 12 min raw rest, clamped to 2 min), as the spec itself notes.
- **Traceability:** every M and S requirement maps to a design element and an AC, apart from S-15.

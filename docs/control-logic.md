# Control Logic Specification

**Status:** drafted for G2 (2026-10-25, nightly). Implements FR-01…FR-20, SR-03, SR-04, SR-08, NFR-01, NFR-07. Thresholds `P-nn` are in `docs/requirements.md` §8. This spec adds **design constants `C-nn`** (§9). They're design choices, not requirements, so they don't change the approved requirements; they're compiled into the same config header (NFR-10 note).

This is the contract for the pure C++ component `exhaust_logic` (no ESP-IDF headers, NFR-06). Everything here is host-testable against simulated and recorded traces (§10).

## 1. Shape of the component

```
           ┌───────────────────────── exhaust_logic::Controller ─────────────────────────┐
 Inputs ──►│ Occupancy ─┐                                                                 │
 (1 Hz +   │ DcBoost ───┤                                                                 │
  events)  │ PmTrack ───┼─► AutoDemand ─► ModeManager ─► OutputShaper ─► fan duty         │──► Outputs
           │ VocTrack ──┤        ▲            ▲  (Auto/Hold/Scene/Spray)                    │
           │ Faults ────┘        │            └── Commands (from UiInput)                   │
           │ Sampler ◄───────────┴── decides SEN65 Measure / Idle / PowerCycle / Clean       │
           │ Maintenance (run hours, filter exposure, clean schedule)   Indicator/Display    │
           └──────────────────────────────────────────────────────────────────────────────┘
```

- **Time:** monotonic milliseconds, injected (`now`). No wall clock is needed; nothing depends on time of day.
- **Calls:** `tick(inputs, now)` once per second; `command(cmd, now)` on each user action, which also recomputes outputs immediately, so panel actions reach the fan within one PWM update (AC-05/AC-06: ≤ 2 s).
- **Inputs:** occupied (debounced by the I/O layer, C-20), `dc_ble` (from the BLE link layer, already including the P-24 timeout), `dc_wired` (the backup input, debounced by the I/O layer, C-31), the latest SEN65 frame plus the module's state (measuring since *t*, idle, unpowered) and device-status bits, tach frequency, fan-present.
- **Outputs:** fan duty 0–100 %, sensor request (`Measure`, `Idle`, `PowerCycle`, `Clean`), display model, indicator model, notices and faults, and the telemetry snapshot for HA.
- **Separate pure units**, each tested on its own: `UiInput` (button/encoder events → commands, with the configurable button map), `DcLinkParser` (BLE frame → `dc_running`, `docs/interfaces.md` §1.1), `HassMessages` (topics/discovery/state JSON).

## 2. Modes (ModeManager)

| Mode | Fan duty | Ends | Next |
|------|----------|------|------|
| **Auto** (boot default, NFR-07) | `AutoDemand` (§4) | — | — |
| **Hold(L, D)** | L (0–100 %), ignores sensors, DC boost and vacant limits | D elapses, Auto button, or a new hold/scene | Auto, or the new mode |
| **Quiet(D)** | min(`AutoDemand`, C-11) | as Hold | Auto |
| **Boost(D)** | 100 % | as Hold | Auto |
| **Spray(D)** | 100 % | D elapses; or Auto button or a new hold/scene | **SprayRunOn**; or Auto / the new mode |
| **SprayRunOn** | 100 % | exit rule below; or Auto button or a new hold/scene | Auto; or the new mode |

- Starting any hold or scene replaces the current mode, including Spray and SprayRunOn: user overrides are always respected (Q-28 (d), D-024). Starting Spray again restarts Spray with the new D.
- **SprayRunOn exit** (FR-08, FR-19, SR-04). Let `t_end` be when Spray ended and `t_min = t_end + P-09`. Exit when `now ≥ t_min` and either:
  - the sensor is faulted (P-09 alone governs, SR-04), or
  - PM2.5 (filtered) < P-04 and VOC index < P-12 (off), both holding for C-02, with valid data, or
  - the shop is vacant and `now − t_vacant ≥ P-21` (the extension counts against the vacant limit). If PM or VOC is still above its off-threshold, raise **clear-down incomplete**.
- **Spray protects the sensor:** the Sampler holds the SEN65 in Idle from Spray start until `t_min − C-07`, so a warmed-up, valid PM and VOC reading is ready at `t_min` (FR-08, confirmed Q-28 (b)).
- **Auto press** returns to Auto from any mode, including Spray and SprayRunOn, with no run-on (FR-08, D-024). It's an explicit user override, not a sensor or network path, so SR-03 still holds. Leaving Spray this way means the SEN65 starts from Idle: PM demand needs P-06 and VOC demand C-07 before they count, so Auto runs on floor and DC demand for the first minute.
- **Reset (NFR-07, D-027):** after a power-on or brown-out reset, Auto. After any other reset (software, panic, watchdog, OTA reboot), the current mode resumes with its remaining time. The Controller exposes `ModeSnapshot` (mode, hold level, remaining D, and for SprayRunOn the time since `t_end`) and `restore(snapshot, now)`. The platform layer keeps the snapshot in RTC no-init memory with a magic and CRC, refreshes it every tick, and restores it only when the reset reason isn't power-on/brown-out and the CRC is valid. Boot time (fan held off in hardware, a few seconds) isn't counted against D. Everything else (occupancy edges, PM/VOC state) restarts as at power-up.
- Spray, holds, Quiet and Boost run whether occupied or vacant. Holds aren't vacant-limited (FR-19). Quiet's Auto part is.

## 3. Occupancy and vacancy (FR-07, FR-19)
- `occupied` follows the debounced 24 VAC input. The controller adds no vacancy delay; the Lutron's 15 min timeout already applies.
- `t_vacant` is set on the occupied→vacant edge and cleared on vacant→occupied. At boot, if vacant, `t_vacant = now`. This is conservative: the vacant run limit restarts after a reboot.
- On vacant→occupied: clear the **clear-down incomplete** notice and the vacant cut-off latch.

## 4. AutoDemand (FR-02, FR-09, FR-14, FR-19, SR-04)

```
floor   = occupied ? P-01 : 0
pm      = PmActive  ? lerp(P-01 → 100 %, over PM2.5 from P-04 → P-05), clamped : 0
voc     = VocActive and VocValid ? P-13 : 0
dc      = DcBoostActive ? P-10 : 0
demand  = max(floor, pm, voc, dc)

if sensor fault:  demand = max(floor, dc)                                (SR-04: drop module demand only)
if vacant:        demand = min(demand, P-22)                              (FR-19)
                  if now − t_vacant ≥ P-21: demand = 0, latch cut-off;     (FR-19)
                     raise clear-down incomplete if PmActive or VocActive
```

- **PmActive** (hysteresis): set when filtered PM2.5 ≥ P-03; cleared when filtered PM2.5 < P-04 for C-02 of continuous valid data. It can't clear during sparse sampling; the Sampler forces continuous sampling below P-03 anyway (§5).
- The `pm` ramp starts at P-01 at P-04, so a vacant clear-down runs no slower than the occupied floor, and an occupied shop sees no step down when PmActive clears. On entry at P-03 the speed steps up to ≈ 33 % (initial values).
- **Filtered PM2.5:** in continuous sampling, an EMA with time constant C-01 over valid 1 s readings. In sparse sampling, the mean of each sample window (C-23), held until the next window. A saturated reading (≥ 1,000 µg/m³, the specified range; FR-06) counts as 1,000 and marks the sample saturated.
- **VocActive:** set when the VOC index > P-12 (on); cleared when < P-12 (off) for C-02. **VocValid** = module measuring for ≥ C-07 and not faulted. When not valid, VOC demand is 0 (AC-28). VocActive keeps the Sampler continuous (§5), so VOC isn't left unmeasured during a VOC event.
- **DcBoostActive** (FR-09, IR-01): `dc_running = dc_ble OR dc_wired`; true while `dc_running`, and for P-11 after it falls. A BLE link timeout looks like a fall (the link layer applies P-24). An unconnected wired input reads false, so the OR needs no configuration (D-025).
- On a sensor fault, PmActive and VocActive are forced clear, so a fault can't leave a stale PM/VOC demand or raise **clear-down incomplete**; the fault itself is the notice.
- DC boost is a floor in Auto only. Holds and scenes override it, and Quiet caps it.

## 5. Sampler (FR-04, FR-05, FR-06, FR-07, FR-08, NFR-02)

States: **Off** (module Idle; vacant and fan off), **Protect** (Idle during Spray, §2), **Warming** (measuring, < P-06 since start: readings not used for PM; VOC needs C-07), **Continuous**, **Window** (a sparse sample: warming plus C-23 of averaging), **Resting** (Idle between windows).

- **Needed** = occupied, or fan duty > 0, or a SprayRunOn wake is due. Not needed → **Off**. Protect overrides everything except a sensor fault's power-cycle.
- **Continuous** when the last filtered PM2.5 < P-03, or VocActive, or in SprayRunOn after `t_min − C-07`. AC-02 checks it.
- **Sparse** otherwise (PM ≥ P-03, VOC inactive). After each window with value `p`, rest for

  ```
  rest = clamp( t_e + P-23 − (P-06 + C-23),  C-24,  R_max(p) )
  t_e  = ln(p / P-04) / k_hi          (earliest plausible crossing of P-04)
  k_hi = C-25 × k_fit   if a decay fit is valid, else C-26 (fastest assumed decay)
  R_max(p) = lerp(C-27 at P-03 → P-07 rest at P-05), clamped; P-07 rest when saturated
  ```

  If PM truly decays no faster than `k_hi`, the reading after the rest is ready by the P-04 crossing + P-23, so **worst-case overrun ≤ P-23** (plus C-02 confirmation). A larger P-23 means longer rests and less sensor on-time; AC-03 sweeps it. `R_max(p)` is a separate bound for responsiveness: in the mid range a rising source still has to be seen within minutes. With the initial values `R_max` binds in most of the range, so expect the AC-03 curve to be flat in P-23 until C-27 and the P-07 rest are raised. AC-03 therefore sweeps C-27 as well. A window that reads < P-03 switches to Continuous.
- **Decay fit (FR-05):** least squares on ln(PM2.5) against time over the last ≥ 3 valid points (window means while sparse, 60 s means while continuous) with PM between P-04 and 1,000, no PM rise between points, and fan duty within ±10 % across them. Valid if R² ≥ C-28. Gives `k_fit` (1/h). The last valid fit is published (`decay_rate`, `airflow_est`). The fit resets on a rise (new source) or a duty change > 10 %. Over-estimating k only makes wakes earlier, so `k_hi` is deliberately high.
- **Saturation (FR-06):** rest = P-07 maximum. On-time per window = P-06 + C-23 = 40 s; at the 10 min P-07 rest that's ≈ 6 % duty, inside AC-02's ≤ 10 %.
- **Weekly fan clean (NFR-02):** after C-19 of accumulated module measuring time, issue `Clean` at the next point where the module is measuring in Continuous, not in SprayRunOn and not within C-02 of a threshold decision. Hold the last readings through the clean (10 s) plus P-06.
- **Module power-cycle:** only on a sensor fault (§6).

**VOC index (D-017):** computed on the node by Sensirion's open-source gas index algorithm from the SEN65's raw VOC signal, one step per valid 1 s reading. The algorithm is **paused, not reset**, whenever the module isn't measuring, or is within C-07 of a start. This keeps the learned baseline across Idle (FR-14). The state is saved to NVS every C-29 and restored at boot. The module's own VOC index is published alongside for comparison. If the bench shows the raw signal isn't usable, fall back to the module's algorithm-state backup/restore (D-017).

## 6. Faults and notices (FR-13, FR-18, SR-04, FR-19)

| Fault / notice | Raised when | Effect | Cleared when |
|----------------|-------------|--------|--------------|
| `sensor_no_data` | Sampler wants Measure, past warm-up, and no valid frame (I²C error, CRC, timeout) for P-18 | SR-04 (§4): PM and VOC demand off, floor and DC boost unchanged; SprayRunOn uses P-09 only. Power-cycle the module (`SEN_PWR_EN`) every C-12 while faulted | C-13 of valid frames |
| `sensor_status` | Device-status error bits (fan, laser, gas, RH/T) set for P-18 | as above | bits clear for C-13 |
| `sensor_range` | Invalid data only, for P-18: the module's "not available" code, physically impossible readings (PM1.0 > PM2.5 > PM10 ordering violated; mass high with number concentrations at zero), or a raw signal stuck at one code. A high PM value is **never** a fault: at or above the range limit it's saturated (FR-06, §4) | as above | C-13 of valid data |
| `fan_tach` (FR-18) | Duty ≥ C-06 and tach < C-14 × `f_expected(duty)` for P-16, ignoring C-15 after any duty change | Display, indicator, HA. Command unchanged | Tach OK for C-15 |
| `fan_port` | `FAN_PRESENT` lost for C-16 | As `fan_tach`. Message says the cable may be unplugged (fan then runs full) or the fan has lost mains | Present for C-16 |
| clear-down incomplete (notice) | FR-19 vacant cut-off (§4) or vacant SprayRunOn exit with PM/VOC still above off-threshold | Display, HA | Next occupancy |
| filter clean due (notice) | Filter exposure ≥ P-14 | Display, HA | Cleared from the panel menu |

`f_expected(duty)`: piecewise linear through (20 %, 30 Hz), (46 %, 75 Hz), (100 %, 144 Hz) from Q-15, extrapolated linearly below 20 %. Re-measured at commissioning.

Faults are shown on the display and in HA at any time. The indicator flashes red only while occupied (FR-15).

## 7. Output shaping (FR-02 chatter, FR-10)

Applied to the arbitrated duty `T` (Auto or mode) to produce the command `O`:
1. **Mode changes** (any transition in §2, including Auto entry) and transitions **to 0** take effect immediately. A transition to 0 in Auto is already confirmed upstream (PmActive/VocActive hysteresis, occupancy).
2. **Up:** if `T > O`, `O = T` at once (floor within 2 s of occupancy, AC-01; full within 2 s of Spray, AC-05).
3. **Down:** `O` only drops if `T ≤ O − C-03` has held for C-04, then it ramps toward `T` at C-05. Noise then ratchets `O` up to a peak and holds it, which gives ≤ 1 reversal per 2 min on a flat noisy trace (AC-01).
4. **Minimum run:** a command in (0, C-06) becomes C-06; the S6's lowest steady speed is measured on the bench.
5. **Boot:** `O = 0` until the first `tick` with valid occupancy. The hardware already holds the fan off before firmware runs (SR-08, `docs/interfaces.md` §2.1).

## 8. UI, display, indicator, maintenance (FR-01, FR-11, FR-13, FR-15)

**Button map** (config, D-009): Auto (Auto from any mode, including Spray and its run-on), Quiet (Quiet for its last duration), Boost (Boost for its last duration), spare (unassigned). One press each (AC-08).

**Encoder** (hold entry, three presses for a repeat, FR-01):
- *Idle* → press → **Level** (list: Off, 20, 40, 60, 80, 100 %, then scenes Spray, Quiet, Boost; starts at the last used) → press → **Duration** (15 min steps from 15 min to 4 h; starts at the last used for that level or scene) → press → command issued.
- C-30 without input cancels. Turning in Idle scrolls the info pages.
- A long press in Idle opens **Menu**: clear filter reminder, sensor clean now, info/about (with the SR-05 non-life-safety statement and SR-06 limitations, AC-25), firmware version.

**Display** (FR-11): mode and time remaining; Occupied/Vacant; fan duty (and tach); PM2.5 with band, VOC index; "DC" when boost is active; active faults and notices (top priority line); an Idle-sensor marker ("PM sampled 3 min ago") while sparse or in Protect. Backlight dims while vacant and turns off after C-21 vacant.

**Indicator** (FR-15): band from filtered PM2.5 per P-15 (green < P-03 ≤ amber < P-05 ≤ red). Shows the last valid band while the module rests. Any fault while occupied → red flash at 1 Hz. Vacant → dark. Brightness capped (≤ 300 mA total).

**Maintenance:** run hours (duty > 0), sensor measuring hours, and filter exposure `E += PM10 × airflow(duty) × dt`. `airflow(duty)` = C-17 × duty until FR-05 data replaces it. PM10 is the last valid value, held between samples. All three are saved to NVS every C-18 and on clear. C-19's counter is persisted too.

## 9. Design constants

Initial values for host tests; tuned at commissioning (phase 6) like `P-nn`.

| ID | Constant | Initial | Reason |
|----|----------|---------|--------|
| C-01 | PM2.5 EMA time constant (continuous) | 30 s | Smooths 1 s noise; small against minutes-long events |
| C-02 | Off-threshold confirmation (PM and VOC) | 60 s | "Several consecutive low readings" (context) |
| C-03 | Down deadband | 5 % duty | Anti-chatter, AC-01 |
| C-04 | Down hold | 60 s | Anti-chatter, AC-01 |
| C-05 | Down ramp rate | 2 %/s | Audible smoothness |
| C-06 | Minimum running duty | 10 % | Placeholder; bench-measure the S6's lowest steady speed |
| C-07 | VOC warm-up after measurement start | 60 s | ≥ P-06; MOX settling. Bench-check with AC-28 |
| C-11 | Quiet cap | 30 % | Placeholder |
| C-12 | Sensor power-cycle retry while faulted | 5 min | Recovery without hammering |
| C-13 | Sensor fault clear | 60 s valid data | Symmetric with P-18 |
| C-14 | Tach fault ratio | 0.5 | "Far below expected" (FR-18) |
| C-15 | Tach settle after duty change | 10 s | EC fan spin-up |
| C-16 | Fan-present debounce | 5 s | |
| C-17 | Airflow per % duty (filter exposure) | 4 CFM/% | 400 CFM free air at 100 %; replaced by FR-05 data |
| C-18 | NVS save interval (counters) | 1 h | Flash wear |
| C-19 | Module fan-clean interval | 168 h measuring | SEN6x has a manual clean command; weekly per sourcing notes |
| C-20 | Occupancy debounce | 0.5 s | AC-04: ≤ 2 s |
| C-21 | Backlight off after vacant | 5 min | |
| C-23 | Sparse window averaging | 10 s | After P-06 settling |
| C-24 | Minimum rest | 60 s | Below this, stay Continuous |
| C-25 | Decay-fit safety factor | 1.5 | Conservative k (earlier wakes) |
| C-26 | Assumed fastest decay (no fit) | 8 /h | 400 CFM × 60 / 3,050 ft³ ≈ 7.9 ACH |
| C-27 | Max rest at P-03 | 2 min | Mid-range PM still steers speed |
| C-28 | Decay fit R² minimum | 0.9 | |
| C-29 | VOC algorithm state save interval | 1 h | Flash wear |
| C-30 | Encoder entry timeout | 10 s | |
| C-31 | Wired `DC_RUNNING` input debounce | 0.5 s | As C-20; AC-06: ≤ 2 s |

C-08, C-09 and C-22 are unused; C-10 (Auto long-press) was dropped 2026-10-26 (Q-28 (a)). IDs are never reused.

## 10. Host tests (AC-16)

Layout, matching hvac_control: `firmware/components/exhaust_logic/` (pure C++20) and `firmware/test/` (CMake + GoogleTest via FetchContent, `run_tests.sh`). Test output is committed (`firmware/test/results/`), because nothing counts as tested otherwise.

- **Room model** (test helper): well-mixed shop, `dC/dt = G(t)/V − k(duty)·C + C_bg`, with V = 3,050 ft³, `k(duty)` from an assumed 200–400 CFM at 100 %, sources `G(t)` from scripts. This closes the loop for clear-down tests, since decay depends on the commanded speed.
- **Sensor model:** PM noise (±(5 µg/m³ + 5 %)), saturation at 1,000, P-06 warm-up, Idle gaps; VOC raw-signal steps; fault injection (no data, status bits, stuck values).
- **Recorded traces:** CSV exported from HA history (FR-12), replayed open-loop.

| AC | Test |
|----|------|
| AC-01 | Occupancy step → floor within 2 s; PM step/ramp follows P-03…P-05; noisy flat trace ≤ 1 reversal per 2 min; off only when vacant and PM < P-04 |
| AC-02 | Constant low/high/saturated PM: continuous below P-03; ≤ 10 % duty at saturation; no PM used before P-06; PM pinned at and above the range limit for 30 min raises no fault and keeps full-speed demand (G2 review B-3) |
| AC-03 | Closed-loop exponential clear-down at two airflows, sweeping P-23: report on-time vs overrun (the trade-off curve); mean overrun ≤ P-23 at the initial value; fitted k within 20 % |
| AC-04 | Occupancy follows input; module Idle when vacant and fan off |
| AC-05 | Spray from every mode; sensors faulted, absent or offline; full within 2 s; run-on ≥ P-09 and until criteria; module Idle until `t_min − C-07`; Auto press or a new hold/scene during Spray and SprayRunOn takes effect at once |
| AC-06 | DC assert/de-assert/link timeout on each of `dc_ble` and `dc_wired`, and both; floor P-10 for P-11 after; PM above P-10 wins; holds override |
| AC-10 | VOC raw step → index > P-12 → ≥ P-13; release below off-level |
| AC-18 (logic part) | Boot output 0; `restore` mid-hold, mid-Spray and mid-SprayRunOn resumes with the remaining time and keeps `t_min`; no snapshot or a bad CRC → Auto |
| AC-20 | Sensor fault with PM and VOC high: occupied → P-01 floor; vacant → off; DC boost still applied (≤ P-22 vacant); within P-18 + 5 s; no clear-down incomplete notice |
| AC-22 (sim part) | `DcLinkParser`: valid/invalid frames, other `0xFFFF` users, version handling, timeout |
| AC-27 | Vacant PM pinned high → ≤ P-22, off at P-21, notice; vacant Spray with VOC high → full through P-09, off at P-21; vacant hold runs its duration; reset on occupancy |
| AC-28 (sim part) | VOC elevated → Idle → measure: index stays elevated (paused baseline); VOC demand 0 while not valid |
| AC-08 (logic part) | `UiInput`: one-press buttons; repeat-last hold in 3 presses; remapped buttons, no logic change |

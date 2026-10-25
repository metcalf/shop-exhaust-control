# Kickoff Context

A summary of design discussions with Andrew in October 2026, before this repo existed. These are the starting points and reasoning. Anything marked *working assumption* is open to revision in phases 1–2.

## The shop
- A small, one-person wood and metal shop. Major woodworking tools include a table saw, miter saw, jointer, planer, band saw and various hand tools. Metalworking tools include a band saw, metal lathe, drill press and possible future benchtop mill. Occasional aerosol-can finishing; no spray guns.
- Dust collector: an older **Lobo 3 HP single-phase** unit with an aftermarket pleated filter. It recirculates filtered air into the shop. A separate controller project for it follows this one.
- An **exhaust fan** (AC Infinity CLOUDLINE PRO S6) sits behind a **coarse metal mesh filter**.
- Andrew runs a Home Assistant instance and builds ESP32 nodes, usually in bare ESP-IDF (C++).

## Goal
Automatically set exhaust fan speed based on shop air quality. Keep day-to-day control local and physical, and tie it to the DC so exhaust boosts when the DC has been running. Ideally provide some ambient visualization of air quality (e.g. a reasonably visible color change when air quality goes beyond a certain point)

## Control-system philosophy
- **Physical controls in the shop.** Buttons, knobs and a small display are fine; physical controls preferred over touch; no phone needed. Home Assistant handles history, alerts and texts.
- **Local autonomy.** All control logic runs on the ESP32 node and works with Wi-Fi or Home Assistant down.
- **Separate from the DC controller.** The two systems are coupled by one signal ("DC running"). Shared UI, if any, lives in Home Assistant. Boosting exhaust is non-critical, so routing that signal through Home Assistant is acceptable; a dry contact or a direct node-to-node link is sturdier.

## Sensing: particulate
*Decided 2026-10-25 (D-012): SPS30 plus SGP41, both v1. The text below is the original reasoning.* **Former working assumption:** a PMS5003-class laser particle sensor with **adaptive duty cycling**. Consider a separate coarse dust sensor that can run continuously (e.g. **Sharp GP2Y1014AU0F**). It's rugged and cleanable, but its resolution is only about 20–50 µg/m³ with heavy averaging, roughly 0.1 mg/m³ to trigger reliably. It can't see the lingering fines that matter for deciding when to turn the fan off.

Alternative to evaluate: the **Sensirion SPS30** (about $50). It has a fan-boost self-clean and is more contamination-resistant, with a roughly 10-year rated life under normal conditions. It may be worth the cost over a PMS5003.

### Duty-cycling scheme (Andrew's design)
- **Low dust:** run continuously to catch the initial spike quickly. Fouling is minimal at low concentrations.
- **High dust:** very low duty cycle. The fan is already on and clearing takes a while, so nothing is lost by sampling rarely. Example: a 30 s sample every 5–10 minutes, about 5–10% duty.
- **Each wake costs about 30 s** of fan settling before readings are valid.
- **Saturation:** the PMS5003 tops out around 1000 µg/m³. A pegged reading just means use the slowest sample rate.
- **Clear-down:** shorten the sample interval as readings fall, so the fan doesn't run a whole extra interval. Better: clearance is roughly exponential, so fit the decay rate from recent samples, predict when the reading will cross the off threshold, and wake just before.
- **Hysteresis** on fan on/off, and several consecutive low readings before turning off.
- **Unoccupied sleep:** the laser has a finite life (a few years continuous), so sleep the sensor when the shop is empty. Possible occupancy signals: lights, motion sensor, DC circuit. I believe we have a 24VAC signal somewhere near the fan that switches on with the shop lights.
- **Calibration caveat:** consumer PM sensors are calibrated for smoke, not wood dust. Treat readings as relative; absolute numbers are approximate. For context, ACGIH's hardwood dust guideline is about 1 mg/m³ inhalable, and clean indoor air is about 5–20 µg/m³.

### Layout
The shop is long and narrow (~11' x 33') with an air inlet at one end (near the dust collector) and exhaust at the other end. The heaviest dust is produced by a table saw and miter saw roughly in the middle of the space. You'll need to consider:
* How location of the unit affects sensing.
* How Andrew accesses the controls and views indications of air quality change
* How we wire to the exhaust fan and lighting signal. Exposed low voltage wiring on the walls is OK.
* Whether and how we wire to the dust collector controller.

## Sensing: VOCs
- MOX sensors (SGP41, BME680) report an index, not a concentration. They auto-baseline, so a slow sustained exposure gets treated as normal, but a sudden rise when spraying starts is clear.
- Silicone vapors can poison MOX sensors.
- **Spraying:** occasional aerosol cans only. A manual **spray mode** gives full exhaust immediately; sensors only keep the fan running afterward until levels settle. Aerosol volumes don't warrant a vapor-rated fan; revisit if spray-gun finishing is ever added.

## Coupling with the dust collector
- **Signal:** "DC running" goes from the DC controller to the exhaust controller.
- **Behavior Andrew described:** raise exhaust fan speed once the DC has been engaged for some amount of time. Exact semantics are an open question.

## Dust collector project (later; noted here so interfaces fit)
Andrew's feature list for the DC controller:
- Blast-gate switches start the DC, with a delayed turn-off.
  - Switch choice: alarm-style reed contacts for aluminum or plastic gates, maybe inductive proximity sensors for steel gates.
  - Run-on comes from the ESP32.
- Filter differential-pressure clog alert, and multi-open-gate warnings.
- Exhaust boost when the DC is engaged.
- manual force on/off
- Possible additions:
  - bin fill level
  - motor current through a CT clamp (current drops when airflow is restricted)
  - duct static pressure at the blower inlet
  - run hours and start counts
  - a limit on starts per hour
  - a filter cleaning prompt
  - an optional bin heat sensor
- UI: a manual on/off at the DC, a small status display there, and warning LEDs at each gate that prompt a look at the display. Texts and history go through Home Assistant.
- Motor cycling matters for a 3 HP motor: extend run-on rather than restarting.

## Process decisions
- The exhaust fan project goes first as the pilot: one node, few sensors, low stakes, and it defines the DC interface.
- Claude Code acts as supervisor, with few subagents. The main subagent use is **independent review**; sourcing research is the other.
- Agents communicate through repo files, with explicit human gates. See `CLAUDE.md`.

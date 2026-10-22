# Kickoff Context

A summary of design discussions with Andrew in October 2026, before this repo existed. These are the starting points and reasoning. Anything marked *working assumption* is open to revision in phases 1–2.

## The shop
- A small, one-person woodshop. Tools include a table saw, miter saw and Festool 125 random orbital sander. Andrew also does HVLP spray finishing.
- Dust collector: an older **Lobo 3 HP single-phase** unit with an aftermarket pleated filter. It probably recirculates filtered air into the shop; confirm in the site survey. A separate controller project for it follows this one.
- An **exhaust fan** sits behind a **coarse metal mesh filter** in a plenum. Its make, model and speed-control method are unknown; see the site survey.
- Andrew runs a Home Assistant instance and builds ESP32 and ESPHome nodes.

## Goal
Automatically run the exhaust fan, and later set its speed, based on shop air quality. Keep day-to-day control local and physical, and tie it to the DC so exhaust boosts when the DC has been running.

## Control-system philosophy
- **Analog first in the shop.** Physical controls and indicators; no phone needed. Home Assistant handles history, alerts and texts.
- **Local autonomy.** All control logic runs on the ESP32 node and works with Wi-Fi or Home Assistant down.
- **Separate from the DC controller.** The two systems are coupled by one signal ("DC running"). Shared UI, if any, lives in Home Assistant. Boosting exhaust is non-critical, so routing that signal through Home Assistant is acceptable; a dry contact or a direct ESPHome link is sturdier.

## Sensing: particulate
**Working assumption:** a PMS5003-class laser particle sensor with **adaptive duty cycling**, and no separate coarse sensor.

Considered and rejected:
- **Sharp GP2Y1014AU0F**, an analog dust sensor with no fan. It's rugged and cleanable, but its resolution is only about 20–50 µg/m³ with heavy averaging, roughly 0.1 mg/m³ to trigger reliably. It can't see the lingering fines that matter for deciding when to turn the fan off. Dropped in favor of duty cycling a single PM sensor.
- **Smoke detector internals.** Sensitive only at alarm levels, the chip outputs only alarm/no-alarm, and dust fouls the labyrinth.

Alternative to evaluate: the **Sensirion SPS30** (about $50). It has a fan-boost self-clean and is more contamination-resistant, with a roughly 10-year rated life under normal conditions. It may be worth the cost over a PMS5003.

### Duty-cycling scheme (Andrew's design)
- **Low dust:** run continuously to catch the initial spike quickly. Fouling is minimal at low concentrations.
- **High dust:** very low duty cycle. The fan is already on and clearing takes a while, so nothing is lost by sampling rarely. Example: a 30 s sample every 5–10 minutes, about 5–10% duty.
- **Each wake costs about 30 s** of fan settling before readings are valid.
- **Saturation:** the PMS5003 tops out around 1000 µg/m³. A pegged reading just means use the slowest sample rate.
- **Clear-down:** shorten the sample interval as readings fall, so the fan doesn't run a whole extra interval. Better: clearance is roughly exponential, so fit the decay rate from recent samples, predict when the reading will cross the off threshold, and wake just before.
- **Hysteresis** on fan on/off, and several consecutive low readings before turning off.
- **Unoccupied sleep:** the laser has a finite life (a few years continuous), so sleep the sensor when the shop is empty. Possible occupancy signals: lights, motion sensor, DC circuit.
- **Calibration caveat:** consumer PM sensors are calibrated for smoke, not wood dust. Treat readings as relative; absolute numbers are approximate. For context, ACGIH's hardwood dust guideline is about 1 mg/m³ inhalable, and clean indoor air is about 5–20 µg/m³.

### Mounting
Andrew is considering putting the sensor in the exhaust plenum behind the mesh. Issues identified:
- **Fan off:** the plenum is a dead pocket, so the initial spike arrives late and muted. The sensor's intake should draw from the room side of the mesh, for example a tube through the mesh or the sensor mounted just in front of it.
- **Fan on:** static pressure doesn't matter much, since the whole sensor sits at the same pressure. Crossflow does: the PMS5003's inlet and outlet sit side by side, and fast air moving past them can push or suppress flow through the sensor. Point the ports downstream, or use a shroud with a single opening facing away from the flow. Undersampling of large particles in fast flow is minor for the fine fraction.
- **Plenum dust:** dust built up on the mesh and walls can shed when the fan starts or vibrates, causing false spikes. Hysteresis and consecutive-reading logic mostly cover this.
- **Validation test:** with the shop at a steady dust level, compare readings just before and after the fan starts, and at each fan speed. A jump means the mounting is biasing readings.
- **Prefiltering:** a very coarse screen or foam is fine. Anything finer loads up, reduces the sensor fan's flow and makes readings drift low. A passive settling box or downward-facing inlet often beats a filter. Some dust drifts in even while the sensor sleeps, so a cover or downward inlet helps.

## Sensing: VOCs (optional, possibly v2)
- MOX sensors (SGP41, BME680) report an index, not a concentration. They auto-baseline, so a slow sustained exposure gets treated as normal, but a sudden rise when spraying starts is clear.
- Silicone vapors can poison MOX sensors.
- **Spraying:** a manual **spray mode** that guarantees full exhaust is the primary control. Sensors only keep the fan running afterward until levels settle. If solvent-based finishes are sprayed, the fan must be suitable for flammable vapors (motor outside the airstream, or explosion-proof).

## Coupling with the dust collector
- **Signal:** "DC running" goes from the DC controller to the exhaust controller.
- **Behavior Andrew described:** raise exhaust fan speed once the DC has been engaged for some amount of time. Exact semantics are an open question.
- **If the DC vents outdoors** rather than recirculating, running it alongside the exhaust fan depressurizes the shop, with backdraft risk for any gas appliance flue and a need for makeup air. If it recirculates, the boost makes sense to catch fines that get past the filter.

## Dust collector project (later; noted here so interfaces fit)
Andrew's feature list for the DC controller:
- Blast-gate switches start the DC, with a delayed turn-off.
  - Switch choice: alarm-style reed contacts for aluminum or plastic gates, inductive proximity sensors for steel gates.
  - Run-on comes from an off-delay timer relay or the ESP32. A capacitor holding the contactor coil was rejected: it chatters on dropout and its timing drifts.
- Filter differential-pressure clog alert, and multi-open-gate warnings.
- Exhaust boost after the DC has run for a while.
- Suggested additions:
  - bin fill level
  - motor current through a CT clamp (current drops when airflow is restricted)
  - duct static pressure at the blower inlet
  - run hours and start counts
  - a limit on starts per hour
  - staggered start against the exhaust fan
  - a filter cleaning prompt
  - manual force on/off
  - an optional bin heat sensor
- UI: a manual on/off at the DC, a small status display there, and warning LEDs at each gate that prompt a look at the display. Texts and history go through Home Assistant.
- Motor cycling matters for a 3 HP motor: extend run-on rather than restarting.

## Process decisions
- The exhaust fan project goes first as the pilot: one node, few sensors, low stakes, and it defines the DC interface.
- Claude Code acts as supervisor, with few subagents. The main subagent use is **independent review**; sourcing research is the other.
- Agents communicate through repo files, with explicit human gates. See `CLAUDE.md`.

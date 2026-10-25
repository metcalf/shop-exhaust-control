# Site Survey — Shop Exhaust Fan Controller

**For Andrew to fill in (phase 0).** Answer inline. "Unknown" and "don't care" are valid answers. Put photos in `docs/site/` and reference them by filename. Items marked ★ block requirements; the rest can follow.

Already known, so not asked here: fan model and motor (Q-01), DC recirculates (Q-02), aerosol-only finishing (Q-04), occupancy from the 24 VAC lighting signal (Q-06), panel hardware and Auto behavior (D-009), tool list (`docs/context.md`). Questions with a default live in `docs/open-questions.md` and aren't repeated here: fuel-burning appliances (Q-05, ★), DC boost semantics (Q-03), panel and indicator location (Q-10), budget (Q-11), interim `DC_RUNNING` source (Q-12), the 24 VAC signal (Q-16).

---

## 1. The shop space
- ★ Ceiling height (plan is ~11' × 31'): 8' 10.5"
- Doors and windows: how many, and are they usually open while working? 2 doors, 1 window, usually closed.
- ★ Makeup air path when the exhaust runs: what is the inlet at the DC end (louver, door undercut, open window)? Any others? There is a 6" duct from the adjacent garage with a spring loaded backdraft damper. Garage is vented to the exterior.
- Heating or cooling in the shop? (Exhaust running in winter costs heat. Is that a concern?) Heating only (radiant in-floor), relatively minor concern given mild San Francisco weather.
- Typical occupancy pattern (days and hours): Lumpy, most of the time is spent weekdays during 9-5 hours, frequently walk in to do something quickly/grab something since it's also where tools live for house projects.

## 2. Exhaust fan
- ★ What's plugged into the S6's control port today (stock AC Infinity controller, nothing), and where is it? Stock low-end (0-10 levels, single button) controller near the fan.
- How is it switched today, and where is that switch? 120V power is switched via a relay which is in turn powered by a 24VAC transformer on the lighting circuit.
- Ducting to outside: length, diameter, bends. Backdraft damper (gravity or motorized)? Gravity backdraft, 6" diameter, 2 90 degree swept turns, ~10' total from inlet.
- ★ Plenum: dimensions and photos, mesh opening size and material, distance from mesh to fan. Intake is through a Broan PM300SS range hood with its own fan removed and the CLOUDLINE added inline above it.
- How dirty does the mesh or plenum get, and how often do you clean it? Gets dusty, don't clean it on a schedule, though given what this system knows about dust in the space it could provide smart nudges for when to clean it.
- Noise: acceptable at full speed for long periods, or should normal running be low speed? (Informs the occupied ventilation floor.) Ideally run at lower speeds when possible and only run higher when needed.

## 3. Electrical
- ★ Circuit feeding the fan: breaker size, other loads on it, receptacle or hardwired? It's on the 20A circuit from the range hood but it's a pretty low powered fan so should be minimal issues with circuit sizing here.
- Distance from the fan to the main work area (table saw / miter saw), for panel and indicator wiring: About 18' horizontally. Wire would run up to ceiling (~3') and down to operating height (~4').
- Is there an existing 24 VDC or 12 VDC supply nearby? Not that I can think of and I think having a dedicated supply makes more sense anyway.
- Room on the wall near the fan for an enclosure (dimensions)? Fan is inside a cabinet with room for an enclosure.
- Do you want the mains wiring changes done by you or an electrician? By me.

## 4. Network and Home Assistant
- Wi-Fi signal strength at the fan location (RSSI from a phone or an existing ESP node): Will not be a problem, AP on the other side of the wall.
- ESP32 nodes already in the shop? No
- Notification channel you want for alerts (HA mobile app, SMS, other): HA mobile app
- Any existing HA naming conventions for entities, areas or devices (proposed prefix `shop_exhaust_`): That works.

## 5. Dust sources and activities
- Which machines are dust-collected, and which aren't? Table saw, miter saw, router table, jointer, planer, band saw (poor collection). Use a vacuum with orbital sander.
- Hand sanding and power sanding: how often, and for how long? Both, varies by project--minutes to hours.
- Aerosol finishing: how often, how long per session, and where in the shop relative to the fan? Infrequent, variable location, highly variable amount of time though usually not covering a lot of area.
- Any metal grinding or cutting in this space (sparks near the plenum)? Some metal grinding and cutting but sparks wouldn't be near the intake.
- Other fumes or odors (glue, epoxy, soldering, welding)? Soldering, burning oil from lathe, solvents (e.g. acetone, alcohol), limited epoxy/glues

## 6. Preferences and constraints
- Enclosure material and look (3D-printed, wood, sheet metal, don't care): Bias is 3d printed for easy of fabrication but open to trying something new (e.g. sheet metal bent by a vendor).
- 3D printer available? (Welding, woodworking and SMD reflow are already assumed.) No, but have had good experience outsourcing SLS.
- Hard no's:

## 7. Photos and measurements checklist
- [ ] Fan, plenum and mesh, from the room side
- [ ] Inside the plenum, if accessible -- skipping since we're not going to put sensors in the plenum space
- [ ] Current fan switch, control port connection and wiring
- [ ] Wall area where the control panel would go
- [ ] Exterior duct termination
- [ ] DC location, with nameplate
- [X] Rough floor-plan sketch (fan, DC, saws, spray area, doors, makeup air, 24 VAC signal location)

# Site Survey — Shop Exhaust Fan Controller

**For Andrew to fill in (phase 0).** Answer inline. "Unknown" and "don't care" are valid answers. Put photos in `docs/site/` and reference them by filename. Items marked ★ block requirements; the rest can follow.

Already known, so not asked here: fan model and motor (Q-01), DC recirculates (Q-02), aerosol-only finishing (Q-04), occupancy from the 24 VAC lighting signal (Q-06), panel hardware and Auto behavior (D-009), tool list (`docs/context.md`). Questions with a default live in `docs/open-questions.md` and aren't repeated here: fuel-burning appliances (Q-05, ★), DC boost semantics (Q-03), panel and indicator location (Q-10), budget (Q-11), interim `DC_RUNNING` source (Q-12), the 24 VAC signal (Q-16).

---

## 1. The shop space
- ★ Ceiling height (plan is ~11' × 33'; correct it if that's off):
- Doors and windows: how many, and are they usually open while working?
- ★ Makeup air path when the exhaust runs: what is the inlet at the DC end (louver, door undercut, open window)? Any others?
- Heating or cooling in the shop? (Exhaust running in winter costs heat. Is that a concern?)
- Typical occupancy pattern (days and hours):

## 2. Exhaust fan
- ★ What's plugged into the S6's control port today (stock AC Infinity controller, nothing), and where is it?
- How is it switched today, and where is that switch?
- Ducting to outside: length, diameter, bends. Backdraft damper (gravity or motorized)?
- ★ Plenum: dimensions and photos, mesh opening size and material, distance from mesh to fan.
- How dirty does the mesh or plenum get, and how often do you clean it?
- Noise: acceptable at full speed for long periods, or should normal running be low speed? (Informs the occupied ventilation floor.)

## 3. Electrical
- ★ Circuit feeding the fan: breaker size, other loads on it, receptacle or hardwired?
- Distance from the fan to the main work area (table saw / miter saw), for panel and indicator wiring:
- Is there an existing 24 VDC or 12 VDC supply nearby?
- Room on the wall near the fan for an enclosure (dimensions)?
- Do you want the mains wiring changes done by you or an electrician?

## 4. Network and Home Assistant
- Wi-Fi signal strength at the fan location (RSSI from a phone or an existing ESP node):
- ESP32 nodes already in the shop?
- Notification channel you want for alerts (HA mobile app, SMS, other):
- Any existing HA naming conventions for entities, areas or devices (proposed prefix `shop_exhaust_`):

## 5. Dust sources and activities
- Which machines are dust-collected, and which aren't?
- Hand sanding and power sanding: how often, and for how long?
- Aerosol finishing: how often, how long per session, and where in the shop relative to the fan?
- Any metal grinding or cutting in this space (sparks near the plenum)?
- Other fumes or odors (glue, epoxy, soldering, welding)?

## 6. Preferences and constraints
- Enclosure material and look (3D-printed, wood, sheet metal, don't care):
- 3D printer available? (Welding, woodworking and SMD reflow are already assumed.)
- Hard no's:

## 7. Photos and measurements checklist
- [ ] Fan, plenum and mesh, from the room side
- [ ] Inside the plenum, if accessible
- [ ] Current fan switch, control port connection and wiring
- [ ] Wall area where the control panel would go
- [ ] Exterior duct termination
- [ ] DC location, with nameplate
- [ ] Rough floor-plan sketch (fan, DC, saws, spray area, doors, makeup air, 24 VAC signal location)

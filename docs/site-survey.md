# Site Survey — Shop Exhaust Fan Controller

**For Andrew to fill in (phase 0).** Answer inline. "Unknown" and "don't care" are valid answers. Put photos in `docs/site/` and reference them by filename. Items marked ★ block requirements; the rest can follow.

---

## 1. The shop space
- ★ Interior dimensions (L × W × ceiling height):
- Rough air volume, if you know it:
- Doors and windows: how many, and are they usually open while working?
- ★ Makeup air path when the exhaust runs (door undercut, louver, open window, none):
- ★ Any fuel-burning appliances in or connected to the shop's air (water heater, furnace, gas dryer)? Location and type:
- Heating or cooling in the shop? (Exhaust running in winter costs heat. Is that a concern?)
- Typical occupancy pattern (days and hours):
- What's a reliable occupancy signal? (Shop lights on a switch? Existing motion sensor in Home Assistant? Anything else?)

## 2. Exhaust fan
- ★ Make and model, and photo of the nameplate:
- ★ Motor type (shaded-pole, PSC, EC/ECM, three-phase with VFD, unknown):
- ★ Voltage, rated current or wattage:
- ★ How is speed controlled today? (single speed, multi-tap switch, wall dimmer or triac, 0–10 V input, PWM input, VFD, none)
- How is it switched today, and where is that switch?
- Is the motor in the airstream?
- Rated airflow (CFM), if known:
- Ducting to outside: length, diameter, bends. Backdraft damper (gravity or motorized)?
- ★ Plenum: dimensions and photos, mesh opening size and material, distance from mesh to fan.
- How dirty does the mesh or plenum get, and how often do you clean it?
- Noise: acceptable at full speed for long periods, or should normal running be low speed?

## 3. Electrical
- ★ Circuit feeding the fan: breaker size, other loads on it, receptacle or hardwired?
- Distance from the fan to where you'd want the control panel or indicators:
- Is there an existing 24 VDC or 12 VDC supply nearby?
- Room on the wall near the fan for an enclosure (dimensions)?
- Do you want the mains wiring changes done by you or an electrician?

## 4. Network and Home Assistant
- Wi-Fi signal strength at the fan location (RSSI from a phone or an existing ESP node):
- ESPHome nodes already in the shop?
- Notification channel you want for alerts (HA mobile app, SMS, other):
- Any existing HA naming conventions for entities, areas or devices:

## 5. Dust sources and activities
- Machines in regular use, and which are dust-collected (table saw, miter saw, sander, router table, bandsaw, other):
- Hand sanding and power sanding: how often, and for how long?
- ★ Spray finishing:
  - Which products? Waterborne, solvent lacquer, shellac, oil-based?
  - How often, and for how long per session?
  - Where in the shop do you spray, relative to the fan?
- Any metal grinding or cutting in this space (sparks near the plenum)?
- Other fumes or odors (glue, epoxy, soldering, welding)?

## 6. Dust collector (for the interface)
- ★ Does the Lobo vent outdoors, or recirculate filtered air into the shop?
- Location relative to the exhaust fan:
- Is a "DC running" signal easy to get today (contactor auxiliary contact, current clamp, smart plug)? Or will it come from the future DC controller?
- What should "boost" mean? (Full speed whenever the DC runs? Only after it has run N minutes? Stay on after the DC stops, and for how long?)

## 7. Preferences and constraints
- ★ Physical controls you want at the fan or entry: e.g. an Off / Auto / On / Spray switch, a speed knob, an indicator LED, a small display:
- Where should those controls live?
- Should the system ever run the fan when you're not in the shop (e.g. overnight clear-down after finishing)?
- Budget range for v1:
- Enclosure and aesthetics (DIN-rail box, wood panel you build, 3D-printed, don't care):
- Fabrication you're happy doing (metal brackets, 3D printing, PCB soldering):
- Hard no's:

## 8. Photos and measurements checklist
- [ ] Fan nameplate
- [ ] Fan, plenum and mesh, from the room side
- [ ] Inside the plenum, if accessible
- [ ] Current fan switch and wiring
- [ ] Wall area where the control panel would go
- [ ] Exterior duct termination
- [ ] DC location, with nameplate
- [ ] Rough floor-plan sketch (fan, DC, spray area, door, makeup air)

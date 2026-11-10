# Physical controls: the design we didn't build

**Status:** not used in v1. Replaced by the touch panel in D-048 (2026-11-09). This is a record so the design can be picked up again here or on the dust collector. Nothing below was built or tested.

The schematic as it stood with these controls is commit `f061a2e` (`pcb/gen/build.py`, `controls` block).

## Why it was dropped
Andrew chose to avoid the mechanical work (bezel openings, rods, overlay, sealing). Removing the controls saves only about $13 on the 2-board order, so **cost was not the reason**. What touch gives up:
- Operation by feel, and with gloves (capacitive touch doesn't work through most work gloves).
- Local control if the panel or touch controller fails. With physical controls, a dead LCD still leaves Auto, Quiet and Boost.

Reconsider physical controls if glove use or a bare glass front turns out to be a problem in the shop.

## Interaction model (D-009)
- **Encoder with push:** press → turn to set level (Off, 20–100 %, then scenes) → press → turn to set duration (15 min steps, 15 min to 4 h) → press to issue. Each step defaults to the last value, so repeating a hold is three presses. 10 s without input cancels (C-30). Turning in Idle scrolls info pages. Long press opens the menu.
- **Four unlit buttons,** assignments in config: Auto, Quiet, Boost, spare. One press each.
- Button-to-action mapping stayed out of the state machine, so `UiInput` is the only unit that changes between physical and touch input.

## Electrical

| Item | Part | LCSC | JLC class | Unit price (2026-10-28) |
|---|---|---|---|---:|
| Encoder, 18 pulse / 36 detent, push, 20 mm flatted shaft | Alps EC11E18244A5 | C255515 | Extended | $2.10 |
| 4 × tact, 6×6 mm, 9.5 mm tall, THT, round actuator | HCTL TC-6610-9.5-260G | C2845262 | Extended | $0.024 |
| 10 k pull-up + 100 nF at each of 7 pins (τ = 1 ms) | existing values | — | Basic | — |

- **GPIOs:** encoder A / B / push on 15 / 16 / 17 (PCNT for quadrature); buttons on 18 / 38 / 39 / 40.
- Debounce with the RC plus firmware and the PCNT filter. Fast-spin quadrature edges are ≥ 2 ms apart, so 1 ms is fine. If counts drop on the bench, fit 10 nF on A and B.
- Taller tacts in stock at the time are listed in `sourcing/ui-connectors.md` §2.

**Cost of keeping them, 2 boards (estimates):** encoders $4.20, knob ≈ $3, JLC per-part fees $3.06, THT labor ≈ $2, switches and passives under $1: **≈ $13**.

## Mechanical design we landed on: sleeves, floating T-rods, vinyl overlay
Tact switches stay on the main PCB. Each is pressed by a loose printed rod that slides in a sleeve molded into the front panel, under an adhesive overlay.

**Why a rod is needed.** Switch tops are 9.5 mm above the main board; the panel's outer face is about 15 mm above it (8.5 mm socket + 4.4 mm non-touch module + 2–2.5 mm wall; layout-dependent estimate). So each button bridges about 6 mm.

**Geometry (starting values, none tested)**
- **Rod:** T-shaped. Head about 8–9 mm across, sitting in a shallow pocket in the face, about flush to 0.2 mm proud so the film barely flexes. Stem about 4–5 mm diameter.
- **Sleeve:** about 5 mm long in total (the wall plus about 2.5 mm behind it). About 3.5 mm is available between the bezel's inner face and the switch top. Bore clearance about 0.3 mm; MJF bores may need drilling to size. A short sleeve under a wide head can bind on off-center presses, hence the thick stem.
- **Assembly:** rods drop in from the front. The head stops them falling inward with the board out, and the overlay stops them coming out forward.
- **Overlay:** adhesive film over the whole key area. Bond to a smooth surface, sanded and sealed or a thin faceplate, because bare MJF is rough and porous. Prefer cast vinyl or polyester over calendered craft vinyl, which tends to fatigue and shrink. A Cricut can cut it. Put legends beside the keys so they don't wear.

**Why this works**
- MJF tolerance (about ±0.3 mm) is more than the tact's travel (about 0.25 mm). A fixed plunger could hold a switch closed or leave dead travel. A free-floating rod rests on the switch, so length error only changes how proud it sits. A bad rod can be sanded or reprinted.
- The wide head gives a real key while keeping the cheap 6×6 tacts.
- No silicone, which can poison the SEN65's MOX element if it off-gases. Avoid RTV especially.

**What still needed care**
- Each press loads the main board, so standoffs go next to the switch row.
- The overlay is the only dust seal for these openings (NFR-04). If it lifts, the sleeve clearance is a path into the compartment. Inspect the edges at the AC-15 one-month check.
- The EC11 isn't sealed. It needs a shaft O-ring or a skirted knob.
- **Test first:** one sleeve, one rod and the actual film on a printed coupon, pressed a few hundred times with and without gloves.

## Alternatives considered

| Option | Result |
|---|---|
| **Sleeves + floating T-rods + overlay** | Chosen, then dropped for touch |
| 2nd PCB of switches screwed to the front panel, vinyl overlay pressed directly (Andrew) | Good tolerance and no press load on the main board. Needed a cable, a small extra PCB (≈ $5–10) and a schematic change, and 12×12 mm tacts for a usable key. Rods got the same result with no second board |
| One-piece printed TPU keypad with stubs to each tact | Workable; sealed by clamping the web. Needed tuning for feel, and FDM TPU at thin webs needs a dust check |
| Thinned PA12 diaphragm, no hole | Too stiff: about 0.03 mm deflection at 2.5 N (0.8 mm wall, 15 mm span, estimated) against about 0.25 mm of travel |
| Panel-mount sealed pushbuttons on a harness | Most robust. Roughly $15–30 for four (unquoted), plus a harness and schematic change. The fallback if a printed part can't be made to feel right |
| Stock rubber keypad | Not searched. Mostly 2×2 or 4×4 hobby pads for carbon contacts, with no clamping flange (from memory). Could work if one exists with a flange |
| Snap-on caps for tacts | Don't seal the opening |
| IP67 tact switches | Seal the switch, not the hole in the enclosure |

## For the dust collector or a later revision
- `UiInput` isolates the input method, so a physical panel is a hardware and `UiInput` change.
- The freed GPIOs in this design are now touch (15–18) and spare (38–40). Any physical controls would need to reassign those.

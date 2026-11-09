# Priced parts list (D-029 checkpoint)

**Andrew: review this before layout starts (Q-33…Q-36).** Prices and stock are from the sourcing notes (`sourcing/*.md`), checked 2026-10-28, except the AP63203 (2026-11-09, LCSC API; D-040). Several came from summarised page fetches, so spot-check the live pages before G4. This is a checkpoint, not the G4 BOM. `bom.csv` gets written at G4, from the final schematic.

## Summary

| Block | 2 assembled boards | Basis |
|-------|-------------------:|-------|
| PCBA: JLC Standard (D-034) fees, joints, parts (+5 %), 5 bare PCBs, shipping | **≈ $149** | Generated table below (`pcb/gen/price.py`). Fees ≈ $91 of it: setup $25.56, stencil $8.21, THT labour $3.58, and 35 unique parts × $1.53. The per-part fee on Basic parts is unverified; if Basic is fee-free, take off ≈ $30 |
| SEN65-SIN-T + Sensirion jumper cable | $35.64 | DigiKey price $29.55 + $6.09; buy at Mouser, which Andrew found in stock (Q-34) |
| Display, 2.8" 240×320 IPS SPI, no touch | ≈ $11–15 | Proposed: LCDwiki MSP2833 (IPS stated in its spec, ILI9341V), or its touch twin MSP2834 (Elecrow DLS29028B, $10.90) with touch unused; see `off-board.md` §2a and Q-35. Newhaven $28.95 is the fallback |
| Encoder knob | ≈ $3 | est. |
| USB-C supply and cable | $0 | Andrew supplies both from stock (Q-36). It needs to be listed and deliver ≥ 5 V at 1.5 A (D-030). Confirm the model at G3 |
| Cable glands PG7 ×3 + locknuts | ≈ $5.50 | Essentra CG-PG7-2-BK, DigiKey |
| Lid gasket strip | ≈ $5–15 | est. A printed TPU gasket is ≈ $0 |
| Enclosure, MJF PA12 (two parts + cleat) | ≈ $40 | est. (architecture §8), not quoted; quote with the JLC order |
| Inserts, screws, diffuser | ≈ $10 | est. |
| Thermostat wire 18/2, fan-cable extension if needed | ≈ $0–15 | est.; may be on hand |
| **Total** | **≈ $259–289** | With Standard PCBA. Low end: TPU gasket, wire on hand. The table below gives the other assembly routes |

Against NFR-08 ($300 ceiling, "well below" preferred), the whole range now fits, since Q-36 removed the supply and cable. It isn't "well below" yet. What drives it:
1. **PCBA fixed fees (≈ $91) dominate the board cost.** Parts are only $12.28 per board. Confirm the Basic-part fee on the live JLC quote; consolidating another few values (e.g. 120/200 Ω → one value, at some loss of colour balance) saves $1.53 each.
2. **Enclosure ($40, est.).** FDM in PETG/ASA on a printer Andrew has access to would cut most of it (needs a D-011 amendment).
3. **Assembly route** (below): up to ≈ $80.
4. Five assembled boards instead of two cost ≈ $192 total ($38 per board). Only worth it if spares or the DC project could use them; they can't directly, since the DC board is different.

## Assembly routes (Q-33 follow-up, 2026-10-29)

These are estimates for 2 boards, from the fee schedule in `pcba-vendor.md` §1 and the part classes above. None is a live quote. Unique parts: 35, or 34 without the module. Of those 34, 17 are Extended, and the 6 "Basic?" parts are assumed Basic.

| Route | JLC fees | Other cost vs. the current plan | ≈ Board total (2) | Saves vs. Standard |
|---|---:|---|---:|---:|
| **A. Standard, everything placed** (current plan) | $90.90 if Basic parts carry the $1.53 fee; $64.89 if they're free | — | $149, or $123 | — |
| **B. Economic, you solder the module** | $65.48 ($8.18 setup + $1.53 stencil + $3.58 hand-solder + 17 Extended × $3.07). Basic and "preferred extended" parts are fee-free | Module ×2 from Mouser with the SEN65 order (≈ $15, vs. $10 inside A's parts cost) | ≈ $131 | **≈ $18** if Standard charges Basic; **≈ −$8** (B costs more) if it doesn't. Each Extended part that turns out to be "preferred" takes $3.07 off B |
| **C. Bare PCB + stencil, you assemble everything** | $0 (5 PCBs ≈ $5–10 + frameless stencil ≈ $7 + shipping ≈ $10–15) | Parts for 2 boards: LCSC ≈ $30–35 plus ≈ $15–20 shipping, or Mouser ≈ $55–70 shipped free with the SEN65 order | ≈ $70–95 | **≈ $60–85**, or **≈ $30–55** if Standard's Basic parts are free |

Labour and risk:
- **B.** The WROOM-1's castellated edges are easy with an iron. The bottom EPAD (pin 41, GND) isn't. Electrically the edge GND pins carry this load, and the thermal duty is low, but an unsoldered EPAD also leaves the module mechanically weaker. Options: hot air, or a footprint with 3–4 ≥ 0.6 mm vias under the EPAD so you can solder from the back. **Don't hotplate it**: the board would already carry JLC's THT plastics (encoder, sockets, terminal blocks) on the same side. That via change is the only way B touches the layout.
- **C.** About 100 SMT placements per board. The smallest are 0603, and the only fine pitch is the USB-C receptacle (HRO TYPE-C-31-M-12). Every part is single-sided, so: stencil, place, hotplate (module included), inspect, then hand-solder the about 36 THT joints. Rough guess: 2–3 h per board plus bring-up rework risk. JLC's 70 mm minimum board size for Standard stops mattering.
- **Unpriced on every route:** US import duty on China-origin goods. It scales with declared value, so it's largest on A, smaller on B and smallest on C if the parts come from Mouser.
- **Layout is the same on all three routes**, apart from B's optional EPAD vias. The route can be chosen at G4 from a live JLC quote on the real Gerber, BOM and CPL. That quote also answers the Basic-fee question.

## On-board parts (generated, per board)

| LCSC | Value | Class | Qty/board | Unit $ | $/board | Stock (LCSC) | Refs |
|---|---|---|---|---|---|---|---|
| C2913202 | ESP32-S3-WROOM-1-N16R8 | Extended | 1 | 4.7466 | 4.75 | 31,339 | U1 |
| C255515 | EC11E18244A5 | Extended | 1 | 2.1026 | 2.10 | 262 | SW1 |
| C780769 | AP63203WU-7 | Extended | 1 | 1.2115 | 1.21 | 1,337 | U3 |
| C601699 | RGB CA 3528 | Extended | 6 | 0.1061 | 0.64 | 14,300 | D6-D11 |
| C7435535 | H11L1S-TA1-L | Extended | 1 | 0.4051 | 0.41 | 1,541 | U5 |
| C133065 | SM06B-GHS-TB | Extended | 1 | 0.3599 | 0.36 | 25,620 | J5 |
| C20917 | AO3400A | Basic | 4 | 0.0897 | 0.36 | 615,350 | Q1,Q4-Q6 |
| C474930 | KF128L-3.5-2P | Extended | 2 | 0.1571 | 0.31 | 3,000 | J3,J4 |
| C557656 | J-FAN | Extended | 1 | 0.3015 | 0.30 | 3,495 | J2 |
| C12891 | 22u | Basic? | 2 | 0.1171 | 0.23 | 138,620 | C3,C4 |
| C15127 | AO3401A | Basic | 2 | 0.0968 | 0.19 | 475,090 | Q2,Q3 |
| C165948 | TYPE-C-31-M-12 | Extended | 1 | 0.1886 | 0.19 | 281,585 | J1 |
| C15850 | 10u | Basic? | 4 | 0.0441 | 0.18 | 1,708,660 | C1,C5,C14,C16 |
| C2897371 | display 1x8 | Extended | 1 | 0.1547 | 0.15 | 10,272 | J6 |
| C3008369 | PC817C-S | Extended | 4 | 0.0366 | 0.15 | 343,540 | U6-U9 |
| C693510 | SMBJ48CA | Extended | 2 | 0.0518 | 0.10 | 4,410 | D2,D4 |
| C14663 | 100n | Basic | 12 | 0.0082 | 0.10 | 42,950 | C2,C6,C10,C13,C15,C17-C23 |
| C2845262 | B1 | Extended | 4 | 0.0240 | 0.10 | 1,120 | SW2,SW3,SW4,SW5 |
| C15849 | 1u | Basic | 5 | 0.0141 | 0.07 | 391,100 | C7-C9,C11,C12 |
| C2488 | MB10S | Basic? | 2 | 0.0272 | 0.05 | 461,500 | D3,D5 |
| C135262 | 2.2u | Extended | 1 | 0.0537 | 0.05 | 130,370 | L1 |
| C41355185 | HT7550-1 | Extended | 1 | 0.0502 | 0.05 | 69,710 | U4 |
| C2827654 | USBLC6-2SC6 | Extended | 1 | 0.0452 | 0.05 | 103,720 | U2 |
| C113952 | SMAJ5.0A | Extended | 1 | 0.0413 | 0.04 | 487,120 | D1 |
| C25804 | 10k | Basic | 16 | 0.0022 | 0.04 | 0 | R3-R5,R7,R8,R20-R23,R25-R31 |
| C8218 | 200 | Basic? | 6 | 0.0039 | 0.02 | 799,600 | R32,R35,R38,R41,R44,R47 |
| C22787 | 120 | Basic | 12 | 0.0019 | 0.02 | 669,200 | R33,R34,R36,R37,R39,R40,R42,R43,R45,R... |
| C17950 | 2.7k | Extended | 4 | 0.0044 | 0.02 | 38,600 | R13,R14,R16,R17 |
| C25803 | 100k | Basic | 5 | 0.0030 | 0.01 | 9,309,700 | R19,R24,R50-R52 |
| C31850 | 22k | Basic | 2 | 0.0042 | 0.01 | 1,837,200 | R10,R12 |
| C25819 | 47k | Basic | 2 | 0.0020 | 0.00 | 584,000 | R15,R18 |
| C23186 | 5.1k | Basic? | 2 | 0.0016 | 0.00 | 16,428,100 | R1,R2 |
| C23162 | 4.7k | Basic | 1 | 0.0028 | 0.00 | 3,636,100 | R11 |
| C22978 | 3.3k | Basic | 1 | 0.0022 | 0.00 | 2,987,300 | R9 |
| C23151 | 390 | Basic? | 1 | 0.0017 | 0.00 | 1,845,000 | R6 |

Unique LCSC parts: 35. Components per board: $12.28. Joints/board ≈ 464 SMT, 36 THT.

2 assembled boards: fees $90.90 + joints $2.71 + parts $25.79 (+5 % attrition) + PCBs $10.00 + shipping $20.00 ≈ **$149** ($75/board)

5 assembled boards: fees $90.90 + joints $6.77 + parts $64.47 (+5 % attrition) + PCBs $10.00 + shipping $20.00 ≈ **$192** ($38/board)

"Basic?" means the JLC page was ambiguous; confirm at BOM upload. C25804 (10 k Basic) showed 0 LCSC stock on 2026-10-28; JLC keeps its own stock, and the Extended fallback is C98220. The encoder (262 in stock) and H11L1 (1,541) have the thinnest stock: re-check before ordering.

Footprints are KiCad stock placeholders; checking them against the LCSC drawings is a layout task (`pcb/design.md` O-3).

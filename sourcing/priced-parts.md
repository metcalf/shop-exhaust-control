# Priced parts list (D-029 checkpoint)

**Andrew: review this before layout starts (Q-33…Q-36).** Prices and stock are from the sourcing notes (`sourcing/*.md`), checked 2026-10-28, except the AP63203 (2026-11-09, LCSC API; D-040). Several came from summarised page fetches, so spot-check the live pages before G4. This is a checkpoint, not the G4 BOM. `bom.csv` gets written at G4, from the final schematic.

## Summary

| Block | 2 assembled boards | Basis |
|-------|-------------------:|-------|
| PCBA: JLC Standard (D-034) fees, joints, parts (+5 %), 5 bare PCBs, shipping | **≈ $135** | Generated table below (`pcb/gen/price.py`). Fees ≈ $82 of it: setup $25.56, stencil $8.21, THT labour $3.58, and 29 unique parts × $1.53. The per-part fee on Basic parts is unverified; if Basic is fee-free, take off ≈ $30 |
| SEN65-SIN-T + Sensirion jumper cable | $35.64 | DigiKey price $29.55 + $6.09; buy at Mouser, which Andrew found in stock (Q-34) |
| Display, 2.8" 240×320 IPS SPI, capacitive touch | $10.90 | Elecrow DLS29028B (LCDwiki MSP2834), in stock 2026-11-09; see `off-board.md` §2a and D-048. Elecrow shipping not included |
| USB-C supply and cable | $0 | Andrew supplies both from stock (Q-36). It needs to be listed and deliver ≥ 5 V at 1.5 A (D-030). Confirm the model at G3 |
| Cable glands PG7 ×3 + locknuts | ≈ $5.50 | Essentra CG-PG7-2-BK, DigiKey |
| Lid gasket strip | ≈ $5–15 | est. A printed TPU gasket is ≈ $0 |
| Enclosure, MJF PA12 (two parts + cleat) | ≈ $40 | est. (architecture §8), not quoted; quote with the JLC order |
| Inserts, screws, diffuser | ≈ $10 | est. |
| Thermostat wire 18/2, fan-cable extension if needed | ≈ $0–15 | est.; may be on hand |
| **Total** | **≈ $242–267** | With Standard PCBA. Low end: TPU gasket, wire on hand. The table below gives the other assembly routes |

Against NFR-08 ($300 ceiling, "well below" preferred), the whole range now fits, since Q-36 removed the supply and cable. It isn't "well below" yet. What drives it:
1. **PCBA fixed fees (≈ $82) dominate the board cost.** Parts are only $9.90 per board. Confirm the Basic-part fee on the live JLC quote; consolidating another few values (e.g. 120/200 Ω → one value, at some loss of colour balance) saves $1.53 each.
2. **Enclosure ($40, est.).** FDM in PETG/ASA on a printer Andrew has access to would cut most of it (needs a D-011 amendment).
3. **Assembly route** (below): up to ≈ $70.
4. Five assembled boards instead of two cost ≈ $169 total ($34 per board). Only worth it if spares or the DC project could use them; they can't directly, since the DC board is different.

## Assembly routes (Q-33 follow-up, 2026-10-29)

These are estimates for 2 boards, from the fee schedule in `pcba-vendor.md` §1 and the part classes above. None is a live quote. Unique parts: 29, or 28 without the module. Of those 28, 12 are Extended, and the 6 "Basic?" parts are assumed Basic.

| Route | JLC fees | Other cost vs. the current plan | ≈ Board total (2) | Saves vs. Standard |
|---|---:|---|---:|---:|
| **A. Standard, everything placed** (current plan) | $81.72 if Basic parts carry the $1.53 fee; $57.24 if they're free | — | $135, or $111 | — |
| **B. Economic, you solder the module** | $50.13 ($8.18 setup + $1.53 stencil + $3.58 hand-solder + 12 Extended × $3.07). Basic and "preferred extended" parts are fee-free | Module ×2 from Mouser with the SEN65 order (≈ $15, vs. $10 inside A's parts cost) | ≈ $111 | **≈ $24** if Standard charges Basic; **≈ $0** if it doesn't. Each Extended part that turns out to be "preferred" takes $3.07 off B |
| **C. Bare PCB + stencil, you assemble everything** | $0 (5 PCBs ≈ $5–10 + frameless stencil ≈ $7 + shipping ≈ $10–15) | Parts for 2 boards: LCSC ≈ $25–30 plus ≈ $15–20 shipping, or Mouser ≈ $50–65 shipped free with the SEN65 order | ≈ $65–90 | **≈ $45–70**, or **≈ $20–45** if Standard's Basic parts are free |

Labour and risk:
- **B.** The WROOM-1's castellated edges are easy with an iron. The bottom EPAD (pin 41, GND) isn't. Electrically the edge GND pins carry this load, and the thermal duty is low, but an unsoldered EPAD also leaves the module mechanically weaker. Options: hot air, or a footprint with 3–4 ≥ 0.6 mm vias under the EPAD so you can solder from the back. **Don't hotplate it**: the board would already carry JLC's THT plastics (encoder, sockets, terminal blocks) on the same side. That via change is the only way B touches the layout.
- **C.** About 100 SMT placements per board. The smallest are 0603, and the only fine pitch is the USB-C receptacle (HRO TYPE-C-31-M-12). Every part is single-sided, so: stencil, place, hotplate (module included), inspect, then hand-solder the about 26 THT joints. Rough guess: 2–3 h per board plus bring-up rework risk. JLC's 70 mm minimum board size for Standard stops mattering.
- **Unpriced on every route:** US import duty on China-origin goods. It scales with declared value, so it's largest on A, smaller on B and smallest on C if the parts come from Mouser.
- **Layout is the same on all three routes**, apart from B's optional EPAD vias. The route can be chosen at G4 from a live JLC quote on the real Gerber, BOM and CPL. That quote also answers the Basic-fee question.

## On-board parts (generated, per board)

| LCSC | Value | Class | Qty/board | Unit $ | $/board | Stock (LCSC) | Refs |
|---|---|---|---|---|---|---|---|
| C2913202 | ESP32-S3-WROOM-1-N16R8 | Extended | 1 | 4.7466 | 4.75 | 31,339 | U1 |
| C780769 | AP63203WU-7 | Extended | 1 | 1.2115 | 1.21 | 1,337 | U3 |
| C601699 | RGB CA 3528 | Extended | 6 | 0.1061 | 0.64 | 14,300 | D4-D9 |
| C7435535 | H11L1S-TA1-L | Extended | 1 | 0.4051 | 0.41 | 1,541 | U4 |
| C133065 | SM06B-GHS-TB | Extended | 1 | 0.3599 | 0.36 | 25,620 | J5 |
| C20917 | AO3400A | Basic | 4 | 0.0897 | 0.36 | 615,350 | Q1,Q4-Q6 |
| C109227 | LTV-817S-TA1-C | Basic | 4 | 0.0818 | 0.33 | 282,150 | U5-U8 |
| C474930 | KF128L-3.5-2P | Extended | 2 | 0.1571 | 0.31 | 3,000 | J3,J4 |
| C557656 | J-FAN | Extended | 1 | 0.3015 | 0.30 | 3,495 | J2 |
| C2897377 | display 1x14 | Extended | 1 | 0.2469 | 0.25 | 15,786 | J6 |
| C12891 | 22u | Basic? | 2 | 0.1171 | 0.23 | 138,620 | C3,C4 |
| C165948 | TYPE-C-31-M-12 | Extended | 1 | 0.1886 | 0.19 | 281,585 | J1 |
| C15850 | 10u | Basic? | 3 | 0.0441 | 0.13 | 1,708,660 | C1,C5,C12 |
| C15849 | 1u | Basic | 4 | 0.0141 | 0.06 | 391,100 | C7,C8,C10,C11 |
| C2488 | MB10S | Basic? | 2 | 0.0272 | 0.05 | 461,500 | D2,D3 |
| C135262 | 2.2u | Extended | 1 | 0.0537 | 0.05 | 130,370 | L1 |
| C2827654 | USBLC6-2SC6 | Extended | 1 | 0.0452 | 0.05 | 103,720 | U2 |
| C113952 | SMAJ5.0A | Extended | 1 | 0.0413 | 0.04 | 487,120 | D1 |
| C8545 | 2N7002 | Basic | 2 | 0.0169 | 0.03 | 5,325,150 | Q2,Q3 |
| C14663 | 100n | Basic | 4 | 0.0082 | 0.03 | 42,950 | C2,C6,C9,C13 |
| C25804 | 10k | Basic | 12 | 0.0022 | 0.03 | 6,238,700 | R3-R5,R7,R8,R10,R18-R23 |
| C8218 | 200 | Basic? | 6 | 0.0039 | 0.02 | 799,600 | R24,R27,R30,R33,R36,R39 |
| C22787 | 120 | Basic | 12 | 0.0019 | 0.02 | 669,200 | R25,R26,R28,R29,R31,R32,R34,R35,R37,R... |
| C17950 | 2.7k | Extended | 4 | 0.0044 | 0.02 | 38,600 | R12,R13,R15,R16 |
| C25803 | 100k | Basic | 3 | 0.0030 | 0.01 | 9,309,700 | R42-R44 |
| C31850 | 22k | Basic | 2 | 0.0042 | 0.01 | 1,837,200 | R9,R11 |
| C25819 | 47k | Basic | 2 | 0.0020 | 0.00 | 584,000 | R14,R17 |
| C23186 | 5.1k | Basic? | 2 | 0.0016 | 0.00 | 16,428,100 | R1,R2 |
| C23151 | 390 | Basic? | 1 | 0.0017 | 0.00 | 1,845,000 | R6 |

Unique LCSC parts: 29. Components per board: $9.90. Joints/board ≈ 380 SMT, 26 THT.

2 assembled boards: fees $81.72 + joints $2.10 + parts $20.78 (+5 % attrition) + PCBs $10.00 + shipping $20.00 ≈ **$135** ($67/board)

5 assembled boards: fees $81.72 + joints $5.25 + parts $51.96 (+5 % attrition) + PCBs $10.00 + shipping $20.00 ≈ **$169** ($34/board)

"Basic?" means the JLC page was ambiguous; confirm at BOM upload. The H11L1 (1,541) and AP63203 (1,337) have the thinnest stock: re-check before ordering.

Footprints are KiCad stock placeholders; checking them against the LCSC drawings is a layout task (`pcb/design.md` O-3).

# Priced parts list (D-029 checkpoint)

**Andrew: review this before layout starts (Q-33…Q-36).** Prices and stock are from the sourcing notes (`sourcing/*.md`), checked 2026-10-28. Several came from summarised page fetches, so spot-check the live pages before G4. This is a checkpoint, not the G4 BOM. `bom.csv` gets written at G4, from the final schematic.

## Summary

| Block | 2 assembled boards | Basis |
|-------|-------------------:|-------|
| PCBA: JLC Standard (D-034) fees, joints, parts (+5 %), 5 bare PCBs, shipping | **≈ $156** | Generated table below (`pcb/gen/price.py`). Fees ≈ $99 of it: setup $25.56, stencil $8.21, THT labour $3.58, and 40 unique parts × $1.53. The per-part fee on Basic parts is unverified; if Basic is fee-free, take off ≈ $30 |
| SEN65-SIN-T + Sensirion jumper cable | $35.64 | DigiKey $29.55 + $6.09. **DigiKey: 0 in stock, 60 due 2027-01-20.** Mouser not checked live (Q-34) |
| Display, 2.8" 240×320 IPS SPI, no touch | $10–29 | Generic ST7789 IPS module ≈ $10 (est., IPS unverified) or Newhaven NHD-2.8-CSXP-BREAKOUT $28.95 (verified IPS, but doesn't fit, see Q-35) |
| Encoder knob | ≈ $3 | est. |
| Raspberry Pi 15 W USB-C supply SC0445 | $11.12 | Newark. Captive 1.5 m 18 AWG cable. UL file number not yet found. Rated 0–40 °C (SF shop, heated: fine) |
| USB-C cable 2 m (StarTech USB2C5C2M) | $0–27 | Only needed if the supply has a port rather than a captive cable (Q-36) |
| Cable glands PG7 ×3 + locknuts | ≈ $5.50 | Essentra CG-PG7-2-BK, DigiKey |
| Lid gasket strip | ≈ $5–15 | est. A printed TPU gasket is ≈ $0 |
| Enclosure, MJF PA12 (two parts + cleat) | ≈ $40 | est. (architecture §8), not quoted; quote with the JLC order |
| Inserts, screws, diffuser | ≈ $10 | est. |
| Thermostat wire 18/2, fan-cable extension if needed | ≈ $0–15 | est.; may be on hand |
| **Total** | **≈ $276–352** | Low end: generic display, captive cable, TPU gasket, wire on hand |

Against NFR-08 ($300 ceiling, "well below" preferred), the low end fits and the high end doesn't. What drives it:
1. **PCBA fixed fees (≈ $99) dominate the board cost.** Parts are only $11.55 per board. Confirm the Basic-part fee on the live JLC quote; consolidating another few values (e.g. 120/200 Ω → one value, at some loss of colour balance) saves $1.53 each.
2. **Enclosure ($40, est.).** FDM in PETG/ASA on a printer Andrew has access to would cut most of it (needs a D-011 amendment).
3. **Display and cable choice** (Q-35, Q-36): up to $46 between options.
4. Five assembled boards instead of two cost ≈ $196 total ($39 per board). Only worth it if spares or the DC project could use them; they can't directly, since the DC board is different.

## On-board parts (generated, per board)

| LCSC | Value | Class | Qty/board | Unit $ | $/board | Stock (LCSC) | Refs |
|---|---|---|---|---|---|---|---|
| C2913202 | ESP32-S3-WROOM-1-N16R8 | Extended | 1 | 4.7466 | 4.75 | 31,339 | U1 |
| C255515 | EC11E18244A5 | Extended | 1 | 2.1026 | 2.10 | 262 | SW3 |
| C601699 | RGB CA 3528 | Extended | 6 | 0.1061 | 0.64 | 14,300 | D10-D15 |
| C7435535 | H11L1S-TA1-L | Extended | 1 | 0.4051 | 0.41 | 1,541 | U5 |
| C133065 | SM06B-GHS-TB | Extended | 1 | 0.3599 | 0.36 | 25,620 | J5 |
| C20917 | AO3400A | Basic | 4 | 0.0897 | 0.36 | 615,350 | Q1,Q4-Q6 |
| C474930 | KF128L-3.5-2P | Extended | 2 | 0.1571 | 0.31 | 3,000 | J3,J4 |
| C557656 | J-FAN | Extended | 1 | 0.3015 | 0.30 | 3,495 | J2 |
| C12891 | 22u | Basic? | 2 | 0.1171 | 0.23 | 138,620 | C5,C6 |
| C15850 | 10u | Basic? | 5 | 0.0441 | 0.22 | 1,708,660 | C1,C3,C7,C16,C18 |
| C15127 | AO3401A | Basic | 2 | 0.0968 | 0.19 | 475,090 | Q2,Q3 |
| C165948 | TYPE-C-31-M-12 | Extended | 1 | 0.1886 | 0.19 | 281,585 | J1 |
| C2897371 | display 1x8 | Extended | 1 | 0.1547 | 0.15 | 10,272 | J6 |
| C78988 | SY8089AAAC | Extended | 1 | 0.1518 | 0.15 | 23,195 | U3 |
| C3008369 | PC817C-S | Extended | 4 | 0.0366 | 0.15 | 343,540 | U6-U9 |
| C20802 | SMD1206P150TF | Extended | 1 | 0.1197 | 0.12 | 11,515 | F1 |
| C693510 | SMBJ48CA | Extended | 2 | 0.0518 | 0.10 | 4,410 | D6,D8 |
| C14663 | 100n | Basic | 12 | 0.0082 | 0.10 | 42,950 | C2,C8,C12,C15,C17,C19-C25 |
| C123802 | SMF15A | Extended | 3 | 0.0326 | 0.10 | 6,520 | D2-D4 |
| C2845262 | B1 | Extended | 4 | 0.0240 | 0.10 | 1,120 | SW4,SW5,SW6,SW7 |
| C15849 | 1u | Basic | 5 | 0.0141 | 0.07 | 391,100 | C9-C11,C13,C14 |
| C2488 | MB10S | Basic? | 2 | 0.0272 | 0.05 | 461,500 | D7,D9 |
| C135262 | 2.2u | Extended | 1 | 0.0537 | 0.05 | 130,370 | L1 |
| C41355185 | HT7550-1 | Extended | 1 | 0.0502 | 0.05 | 69,710 | U4 |
| C2827654 | USBLC6-2SC6 | Extended | 1 | 0.0452 | 0.05 | 103,720 | U2 |
| C318884 | EN | Basic? | 2 | 0.0208 | 0.04 | 875,640 | SW1,SW2 |
| C113952 | SMAJ5.0A | Extended | 1 | 0.0413 | 0.04 | 487,120 | D1 |
| C25804 | 10k | Basic | 16 | 0.0022 | 0.04 | 0 | R7-R9,R11,R12,R24-R27,R29-R35 |
| C25803 | 100k | Basic | 8 | 0.0030 | 0.02 | 9,309,700 | R3-R5,R23,R28,R54-R56 |
| C8218 | 200 | Basic? | 6 | 0.0039 | 0.02 | 799,600 | R36,R39,R42,R45,R48,R51 |
| C22787 | 120 | Basic | 12 | 0.0019 | 0.02 | 669,200 | R37,R38,R40,R41,R43,R44,R46,R47,R49,R... |
| C17950 | 2.7k | Extended | 4 | 0.0044 | 0.02 | 38,600 | R17,R18,R20,R21 |
| C31850 | 22k | Basic | 3 | 0.0042 | 0.01 | 1,837,200 | R6,R14,R16 |
| C81598 | 1N4148W | Basic | 1 | 0.0125 | 0.01 | 2,470,700 | D5 |
| C25819 | 47k | Basic | 2 | 0.0020 | 0.00 | 584,000 | R19,R22 |
| C23186 | 5.1k | Basic? | 2 | 0.0016 | 0.00 | 16,428,100 | R1,R2 |
| C23162 | 4.7k | Basic | 1 | 0.0028 | 0.00 | 3,636,100 | R15 |
| C22978 | 3.3k | Basic | 1 | 0.0022 | 0.00 | 2,987,300 | R13 |
| C1653 | 22p | Basic | 1 | 0.0020 | 0.00 | 198,700 | C4 |
| C23151 | 390 | Basic? | 1 | 0.0017 | 0.00 | 1,845,000 | R10 |

Unique LCSC parts: 40. Components per board: $11.55. Joints/board ≈ 516 SMT, 36 THT.

2 assembled boards: fees $98.55 + joints $2.88 + parts $24.26 (+5 % attrition) + PCBs $10.00 + shipping $20.00 ≈ **$156** ($78/board)

5 assembled boards: fees $98.55 + joints $7.19 + parts $60.65 (+5 % attrition) + PCBs $10.00 + shipping $20.00 ≈ **$196** ($39/board)

"Basic?" means the JLC page was ambiguous; confirm at BOM upload. C25804 (10 k Basic) showed 0 LCSC stock on 2026-10-28; JLC keeps its own stock, and the Extended fallback is C98220. The encoder (262 in stock) and H11L1 (1,541) have the thinnest stock: re-check before ordering.

Footprints are KiCad stock placeholders; checking them against the LCSC drawings is a layout task (`pcb/design.md` O-3).

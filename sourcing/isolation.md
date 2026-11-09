# Sourcing: isolation and small-signal parts (JLCPCB Standard PCBA)

Checked 2026-10-28. Stock and price are from the LCSC product API (wmsc.lcsc.com) on that date. JLC class and PCBA type are from the jlcpcb.com part pages. Prices are USD per unit at qty 10; where the tier ladder has no qty-10 break, the lowest tier that covers 10 is shown, with its break noted.

| # | MPN | LCSC | JLC class | LCSC stock | Unit @10 | Package | PCBA type | Datasheet |
|---|-----|------|-----------|-----------|----------|---------|-----------|-----------|
| 1 | H11L1S-TA1-L (Lite-On) | C7435535 | Extended | 1,541 | $0.4051 | SOP-6 (gull-wing, 2.54 mm pitch) | Economic + Standard | https://datasheet.lcsc.com/datasheet/pdf/40e63325a9c292538a6290c5a02b3ff6.pdf |
| 2 | PC817C-S (UMW) | C3008369 | Extended | 343,540 | $0.0366 | SOP-4 2.54 mm | Economic + Standard | https://datasheet.lcsc.com/datasheet/pdf/cb8303ceadec5b75cc1de32c44918f7d.pdf |
| 3 | MB10S-50MIL (MDD) | C2488 | Basic (unconfirmed, see notes) | 461,500 | $0.0272 (min tier is 20 pcs) | MBS (SOIC-4 style) | Economic + Standard | https://datasheet.lcsc.com/datasheet/pdf/d166b641999f7c4a86c69b88af3f89c6.pdf |
| 4 | 2N7002 (JSCJ/JCET) | C8545 | Basic | 2,522,900 | $0.0162 (min tier is 50 pcs) | SOT-23 | Economic + Standard | https://datasheet.lcsc.com/datasheet/pdf/a141b8bd86b14475955ac8c4d3eea0a8.pdf |
| 5 | AO3401A (AOS) | C15127 | Basic | 475,090 | $0.0968 (5+ tier) | SOT-23 | Economic + Standard | https://datasheet.lcsc.com/datasheet/pdf/fee353dd1e9e0bc90b295f14f381aa4c.pdf |

DigiKey/Mouser equivalents. These are built from the distributors' usual part-number conventions and were not looked up. Confirm before ordering.

| # | Equivalent |
|---|-----------|
| 1 | Mouser 859-H11L1S-TA1-L (same part). Alternative: onsemi H11L1SR2M, which is stocked at Farnell/element14 and is the part the "SR2" name refers to. |
| 2 | Mouser 859-LTV-817S-TA1-C (Lite-On LTV-817S-TA1-C, C-rank SMD) |
| 3 | Mouser 833-MB10S-TP (MCC MB10S-TP) |
| 4 | Mouser 512-2N7002 (onsemi 2N7002) |
| 5 | Mouser 781-AO3401A (AOS AO3401A) |

## 1. H11L1 Schmitt-trigger opto: H11L1S-TA1-L (C7435535)

Lite-On H11Lx-L series datasheet (Rev B, 04/2023). A digital-isolator fallback is not needed because an SMD H11L1 is stocked.

| Item | Value |
|------|-------|
| Isolation | UL 1577 recognized, 5000 Vrms for 1 min. Absolute max table Viso = 5000 Vrms. |
| VDE / IEC 60747-5-5 | The datasheet lists "VDE DIN EN60747-5-5, VIORM = 630 Vpeak" as an option (marked "VDE option" on the package drawing). C7435535 is the plain "-TA1-L" ordering code. The VDE-approved variant has a different ordering code, so LCSC/JLC stock of this C-number is not confirmed as VDE-marked. |
| VCC | 3 V to 15 V operating (absolute max table 3 to 16 V) |
| ICC(off) | typ 0.7 mA, **max 1.3 mA** (IF = 0, VCC = 5 V) |
| ICC(on) | typ 0.7 mA, **max 1.3 mA** (IF = 10 mA, VCC = 5 V) |
| IF(on) threshold | H11L1: typ 1.0 mA, **max 1.6 mA** (RL = 270 ohm, VCC = 5 V). IF(off) min 0.3 mA. Hysteresis ratio IF(off)/IF(on) 0.5 to 0.9. |
| LED | VF 1.2 to 1.6 V at 10 mA; VF 0.75 V min at 0.3 mA; VR max 6 V; IF abs max 20 mA |
| Output | Inverting, open-collector (input high gives output low; truth table in datasheet). Needs an external pull-up (270 ohm in the test circuit). IOH max 100 uA at VO = 15 V. VOL max 0.4 V at 16 mA. |
| Propagation delay | tPHL typ 180 ns, max 500 ns. tPLH typ 120 ns, max 500 ns (RL = 270 ohm, VCC = 5 V). |
| CMTI | 10 kV/us min at VCM = 1000 V |

The output goes high when the LED is off or unpowered. That matches a default-high output when the input side is dead.

Creepage and clearance are not stated in the datasheet text. The drawing shows a 7.62 mm lead span and a ~6.5 mm body width. Do not assume reinforced spacing from this package without the manufacturer's figure.

Other stocked H11L1 SMD parts, for reference only:
- JSMSEMI H11L1S-JSM (C22376095): 340 in stock.
- ISOCOM H11L1VSMT&R (C255762): 0 stock.

## 2. PC817 phototransistor opto: PC817C-S (C3008369)

**Superseded 2026-11-09 (D-045):** the design uses Lite-On LTV-817S-TA1-C (C109227), Basic on its JLC page, $0.0818 @10, 282,150 in stock at LCSC. The claim below that no Basic part was found applied only to PC817 and the variants listed.

No JLC Basic PC817 or equivalent was found. All SOP-4 PC817 variants checked on jlcpcb.com were Extended: C3008369, C22447129, C20612450, C490097, C115502, C66405 and C20612592 (the last by search result only). The ranked C variant at LCSC is Extended.

UMW PC817 datasheet (Apr 2025):

| Item | Value |
|------|-------|
| CTR, C rank | 200% min to 400% max at IF = 5 mA, VCE = 5 V, 25 C. Whole family: 50% to 600%. Grades are L 50-100, A 80-160, B 130-260, C 200-400, D 300-600. |
| CTR at IF = 1 mA | **Not in the datasheet.** There is no CTR-vs-IF curve, only relative CTR vs temperature (about 60% of 25 C value at 100 C, about 100% at 0 to 25 C). Characterise on the bench or use a Sharp/Lite-On datasheet with that curve. |
| LED VR | 6 V max. IR max 10 uA at VR = 4 V. |
| Viso | 5000 Vrms (listed "5,000Vrms" in features; the abs-max row says 500 Vrms, which looks like a typo). VIORM 630 V, VIOTM 6000 V. UL 1577, file E547318. |
| Creepage | Not stated in the datasheet. |
| Other | VCEO 35 V, VECO 6 V, VCE(sat) typ 0.1 V and max 0.2 V (IF = 20 mA, IC = 1 mA). tr typ 4 us, tf typ 3 us. |

The LCSC listing reads "CTR 600%; 50%", which is the family range. The C rank is set by the marking on the part. Check that JLC places the C-marked part, because the MPN field is the only thing that selects the grade.

Fallback if the ranked CTR matters: JSMSEMI PC817C (C22447129, Extended, 83,550 in stock, $0.0402 at qty 10).

## 3. Bridge rectifier: MB10S-50MIL (C2488)

MDD MB1S to MB10S datasheet (Rev 2024A2). The scan has a garbled font on page 1, so the table is read from the series header and the LCSC parameters.
- MB10S: 1000 V reverse (series 50 to 1000 V), 1.0 A average, IFSM 35 A, VF 1.1 V at 400 mA, IR 5 uA at 1 kV, package MBS.
- JLC class: the jlcpcb.com page for C2488 does not print a class label, and a web search listed it as Basic. Confirm in the JLC parts library at BOM upload.
- UMB10S (C2994377) has only 2,565 in stock, so it is not proposed.
- The 1N4148W alternative was not researched, because this part meets the request.

## 4. 2N7002 N-MOSFET (C8545)

JCET datasheet (J, Sep 2016):

| Item | Value |
|------|-------|
| VDS / VGS max | 60 V / +-20 V |
| ID | 115 mA continuous (datasheet header; 500 mA pulsed test point) |
| VGS(th) | 1.0 V min, 1.6 typ, **2.5 V max** (ID = 250 uA) |
| RDS(on) at VGS 10 V | typ 0.9 ohm, max 5 ohm (ID = 500 mA) |
| RDS(on) at VGS 5 V | typ 1.1 ohm, **max 7 ohm** (ID = 50 mA). No 4.5 V line; use the 5 V figure. |
| RDS(on) at VGS 2.5 V | **Not specified.** Max VGS(th) is 2.5 V, so the device is not guaranteed on at 2.5 V. The RDS(on)-vs-VGS curve climbs steeply below about 3.5 V. |

At a 3.3 V gate drive the part is marginal: typical devices conduct, but there is no guarantee. Use 5 V gate drive or a logic-level part for 3.3 V.

## 5. AO3401A P-MOSFET (C15127)

AOS datasheet Rev 3.1 (Dec 2023):

| Item | Value |
|------|-------|
| VDS / VGS max | -30 V / +-12 V |
| ID | -4 A at 25 C |
| VGS(th) | **-0.5 V min, -0.9 V typ, -1.3 V max** (ID = -250 uA) |
| RDS(on) at VGS -2.5 V | typ 60 mohm, **max 85 mohm** (ID = -2.5 A) |
| RDS(on) at VGS -4.5 V | typ 47 mohm, max 60 mohm (ID = -3.5 A) |
| RDS(on) at VGS -10 V | typ 41 mohm, max 50 mohm (ID = -4 A) |

## Notes

- The only part with a UL file number from a datasheet is the PC817 (UMW, E547318, for the UMW family). The H11L1 is stated as UL 1577 recognized in the Lite-On datasheet, with no file number printed. Get the file numbers from the UL Product iQ database before relying on them for the G3 safety review.
- Creepage and clearance are not given for either opto. Any reinforced-isolation claim across the barrier needs the manufacturer's figures or the package drawing checked against the IEC 62368-1 table.
- Items needing a recheck before the G4 BOM freeze: the class of C2488, and whether C7435535 carries the VDE option. CTR at 1 mA: 80 % typical on the LTV-817 (D-045).

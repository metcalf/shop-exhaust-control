# Power input and regulation parts (JLCPCB Standard PCBA)

Checked 2026-10-28. Stock and price are from LCSC's product API (`wmsc.lcsc.com/ftps/wm/product/detail`) fetched that day. Library class is from the JLCPCB part page and the API `smtLabel` (`BASE` = Basic, `EXPAND` = Extended). The JLCPCB page doesn't separate Preferred Extended from Extended, so "Extended" below means Basic was ruled out and Preferred status is unknown. "Qty 10" price is the tier covering 10 (the 5+ tier, or the 10+/20+ tier where that is the minimum). Re-check at order time.

**No Basic part was found for any of the eight items.** Each pick below is `smtLabel=EXPAND`. I did not exhaust the Basic list (JLCPCB has no scriptable filter reachable from here), so a Basic alternative may exist for the TVS, ESD and fuse items. With Standard PCBA, each unique Extended part adds about $1.53 feeder-loading fee (see `sourcing/pcba-vendor.md`).

**Amended 2026-11-09 (D-040):** the fuse (item 4) is dropped, and the buck (item 2a) is now the Diodes AP63203WU-7, C780769, TSOT-23-6, Extended on the JLCPCB page. LCSC API on 2026-11-09: 1,337 in stock, lifecycle `normal`, $1.3568 @1, $1.2115 @10, $0.9722 @100. Keep the C135262 inductor. Lifecycle: Andrew confirmed DigiKey and Mouser both show it active and stocked (2026-11-09). That overrides one LCSC listing seen in search that said "not recommended for new designs"; the live LCSC page and API don't say that either. The rows below are left as researched.

## Picks

| # | Function | MPN | LCSC | Class | Stock | $ @10 | Package | Datasheet | DK/Mouser equivalent (ordering codes not verified) |
|---|---|---|---|---|---|---|---|---|---|
| 1 | USB-C receptacle 16P | Korean Hroparts TYPE-C-31-M-12 | C165948 | Extended | 281,585 | 0.1886 (MOQ 5, multiples of 5) | SMD right-angle, 4 shell legs | [PDF](https://datasheet.lcsc.com/datasheet/pdf/9e56b777c022540fcce7c7f67825f55e.pdf?productCode=C165948) | GCT USB4105-GF-A (Mouser/DigiKey; footprint differs) |
| 2a | 5 V to 3.3 V sync buck, 2 A | Silergy SY8089AAAC | C78988 | Extended | 23,195 | 0.1518 | SOT-23-5 | [PDF](https://datasheet.lcsc.com/datasheet/pdf/400ca014d7a690f5be0127468f87fcc6.pdf?productCode=C78988) | TI TLV62569DBVR (Mouser 595-TLV62569DBVR; not a drop-in, different FB/inductor values) |
| 2a-L | Inductor for 2a, 2.2 uH, 3.4 A | Shun Xiang Nuo SMNR4020-2.2UH | C135262 | Extended | 130,370 | 0.0537 | 4x4 mm SMD | [PDF](https://datasheet.lcsc.com/datasheet/pdf/c30b0f031d0070e2292eba9306a4bf8b.pdf?productCode=C135262) | TDK SPM4020T-2R2M-LR |
| 2b | 3.3 V 1 A LDO (alternative kind) | TI TLV75733PDBVR | C485517 | Extended | 32,620 | 0.2181 | SOT-23-5 | [PDF](https://datasheet.lcsc.com/datasheet/pdf/edd4724bddb84d5511fcf6af443cafd0.pdf?productCode=C485517) | Mouser 595-TLV75733PDBVR |
| 3 | 5 V LDO, Vin to 30 V | GOODWORK HT7550-1 | C41355185 | Extended | 69,710 | 0.0502 | SOT-89 | [PDF](https://datasheet.lcsc.com/datasheet/pdf/45815f7057c698990e702d20d716e32b.pdf?productCode=C41355185) | Microchip MCP1703T-5002E/MB (Mouser 579-MCP1703T-5002E/MB, 16 V max) |
| 4 | PTC 1.5 A hold, 6 V | RUILON SMD1206P150TF | C20802 | Extended | 11,515 | 0.1197 | 1206 | [PDF](https://datasheet.lcsc.com/datasheet/pdf/147b01ecd3cb8b8f5a5deee7c25b85b7.pdf?productCode=C20802) | Littelfuse 1206L150THWR (Mouser 576-1206L150THWR, 8 V) |
| 5 | TVS 5 V uni, VBUS | MDD SMAJ5.0A | C113952 | Extended | 487,120 | 0.0413 (MOQ 20) | DO-214AC (SMA) | [PDF](https://datasheet.lcsc.com/datasheet/pdf/57d80c866df506764ddd60be335ccdff.pdf?productCode=C113952) | Littelfuse SMAJ5.0A (Mouser 576-SMAJ5.0A) |
| 6 | TVS 48 V bidir | FTR SMBJ48CA | C693510 | Extended | 4,410 | 0.0518 | DO-214AA (SMB) | [PDF](https://datasheet.lcsc.com/datasheet/pdf/b17168aad1b3654ddd25c40ea1292331.pdf?productCode=C693510) | Littelfuse SMBJ48CA (Mouser 576-SMBJ48CA) |
| 7 | USB D+/D- ESD | TECH PUBLIC USBLC6-2SC6 | C2827654 | Extended | 103,720 | 0.0452 | SOT-23-6 | [PDF](https://datasheet.lcsc.com/datasheet/pdf/fc4eb899b8e4021ee1843f8c3ea5a928.pdf?productCode=C2827654) | ST USBLC6-2SC6 (Mouser 511-USBLC6-2SC6) |
| 8 | TVS 15 V standoff, fan port | MDD SMF15A | C123802 | Extended | 6,520 | 0.0326 (MOQ 20) | SOD-123FL | [PDF](https://datasheet.lcsc.com/datasheet/pdf/82c461b905225ff344e885083d94bbf3.pdf?productCode=C123802) | Littelfuse SMF15A (Mouser 576-SMF15A) |

## Recommendation for item 2

Use **2a: SY8089AAAC (C78988) with SMNR4020-2.2UH (C135262)**. The LDO (2b) is not viable for this load. TLV75733P dropout is fine (0.30 V typ, 0.425 V max at 1 A, 3.3 V out, -40 to 85 C), but dissipation is 1.7 V x 0.35 A = 0.6 W typical and 1.9 W at the 1.1 A peak. The SOT-23-5 has theta-JA of 100.8 C/W (TI EVM) to 231 C/W (JEDEC), so 60 to 140 K rise typical and no chance at peak. Quiescent current is 25 uA typ / 31 uA max (25 C).

SY8089AAAC facts (Silergy application note):
- Vin 2.7 to 5.5 V, 2 A continuous, 3 A peak, 1 MHz, Rds(on) 110/80 mOhm, 100% dropout operation.
- The datasheet charts efficiency only for 1.8 V out from 3.3/4.2/5.0 V in (about 88 to 92% from 0.1 to 1 A at 5 V in). It has no 3.3 V curve, so I'm not quoting a 3.3 V efficiency figure.
- JLCPCB's listing gives Iq of 55 uA.
- Package: SOT-23-5, theta-JA 170 C/W, Pd 0.6 W at 25 C. At 0.35 A the loss is small (low tens of mW), so no thermal issue.
- Adjustable only: Vout = 0.6 x (1 + R1/R2). For 3.3 V use R1 = 453 k, R2 = 100 k (E96), about 3.32 V. The app circuit uses 22 pF across R1, 22 uF at IN, 2 x 22 uF at OUT, and L = 2.2 uH. EN must not float (pull to VIN).
- Inductor SMNR4020-2.2UH: 2.2 uH +/-20%, 3.4 A rated and Isat, 46 mOhm DCR. Isat is above the 3 A peak limit but with little margin.
- **Abs max Vin is 6.0 V.** USB hot-plug ringing on VBUS can exceed that. The VBUS TVS (item 5) clamps at 9.2 V at 43.5 A, so it will not protect this input. The polyfuse plus a bulk cap on VBUS helps, but the layout needs a damping bulk cap, and the electrical review should look at this. The TLV75733P has the same 6.0 V abs max.

## Notes per item

1. **Pin names (drawing, 16P):** A1 GND, A4 VBUS, A5 CC1, A6 DP1, A7 DN1, A8 SBU1, A9 VBUS, A12 GND; B1 GND, B4 VBUS, B5 CC2, B6 DP2, B7 DN2, B8 SBU2, B9 VBUS, B12 GND. The shell has four legs with no signal name (tie to GND or GND via RC). Both DP1/DP2 and DN1/DN2 are on the connector, so tie them together at the board. Dimensions from the drawing: shell width 8.34 mm (8.64 across the legs, 8.94 across the flange in the top view), height 3.26 mm, depth 6.77 mm in the side view (7.35 mm in the top view including the rear flange). Pin pitch 0.5 mm, 0.6 mm locating holes, 4 shell-leg slots. I read the drawing as an image, so the footprint (EasyEDA/JLC symbol) should be compared against the PDF before layout. Rated 5 A, 20 V. UL rating not applicable to this 5 V port. JLCPCB lists it Economic and Standard, MSL 1. Only one datasheet drawing revision was reviewed.
2. See above. No Basic buck or 1 A LDO with at most 0.4 V dropout turned up. AMS1117 (C6186) is the Basic 1 A option but is excluded.
3. **GOODWORK HT7550-1 (C41355185), not the Holtek original (C16106).** I could not retrieve a readable Holtek datasheet, so I picked the clone whose datasheet I read. From it (HT75XX Rev 2.0 2025 JAN, 7550 table): Vin abs max 30 V, Iout >= 100 mA min (150 mA typ), Iss 1.5 uA typ and 3.0 uA max (no load), dropout 55 mV max at 1 mA, 5.0 V +/-2%, theta-JA 200 C/W in SOT-89 (Pd 500 mW). The reference circuit uses 10 uF in and out; it does not state ESR limits, so use 10 uF ceramic or polarized with margin and check on the bench. At 10 V in and 30 mA, dissipation is 0.15 W (about 30 K rise). Meets the "Iq <= 10 uA max" request. The Holtek C16106 (179,705 in stock, $0.1398) is the alternative if you want the original; LCSC lists it with Iq 2.5 uA and Vin 30 V, unverified against a Holtek datasheet.
4. 1206, Ihold 1.5 A, Itrip 3 A, Vmax 6 V, Imax 100 A. PTC hold current derates with temperature (roughly 1.1 A near 85 C), so it sits close to the 1.1 A peak in a warm enclosure. The 1812 option is RUILON SMD1812P150TF/16 (C20810): 16 V, 1.5 A, 6,675 in stock, $0.1106, Extended. Take the 1812 part if you want margin on the voltage rating. Vmax 6 V is sufficient for a 5 V bus.
5. Vrwm 5 V, VBR 7 V (min), Vc 9.2 V at Ipp 43.5 A, 400 W 10/1000 us. MOQ is 20, so the cost is 20 pieces at $0.0413 each even for a qty of 10.
6. Vrwm 48 V, VBR 53.3 V, Vc 77.4 V at 7.8 A, 600 W. The MDD SMBJ48CA (C173522) shows 0 stock today. TECH PUBLIC SMBJ48CA (C53278498, 2,600 in stock, $0.0445) is the backup if C693510 sells out.
7. A USBLC6-2SC6 clone (2 channels, Vrwm 5 V, Vc 12 V, Ipp 6 A, 150 W). It has a VBUS pin and ties D+ and D- to I/O1 and I/O2. CC1 and CC2 (dual-row connector) are not covered; they need a separate array, or accept the exposure. STMicro original is C7519 (38,030 in stock, $0.1814). The TECH PUBLIC part's datasheet capacitance was not read; check it is low enough for USB 2.0 full-speed, which is not an issue at 12 Mbps with 3.5 pF-class parts.
8. SMF15A unidirectional: Vrwm 15 V, VBR 18.5 V, Vc 24.4 V at 8.2 A, 200 W. At a 10 V signal this leaves headroom and low leakage (1 uA). A negative excursion is clamped at one diode drop. If the fan port can see a negative-going reverse hookup that you want blocked to a higher level, use the bidirectional SMF15CA from baocheng (C53327532, 13,640 in stock). I did not check its class or price. The MOQ is 20.

## Proposed bom.csv rows

`bom.csv` does not exist in the repo yet, so the columns here are a proposal: ref, description, MPN, LCSC, class, stock, price@10, date checked, DK/Mouser equivalent.

```
J_USB,USB-C receptacle 16P,TYPE-C-31-M-12,C165948,Extended,281585,0.1886,2026-10-28,GCT USB4105-GF-A
U_BUCK,5V to 3.3V sync buck 2A,SY8089AAAC,C78988,Extended,23195,0.1518,2026-10-28,TI TLV62569DBVR
L_BUCK,2.2uH 3.4A inductor,SMNR4020-2.2UH,C135262,Extended,130370,0.0537,2026-10-28,TDK SPM4020T-2R2M-LR
U_FAN5V,5V LDO Vin<=30V,HT7550-1 (GOODWORK),C41355185,Extended,69710,0.0502,2026-10-28,Microchip MCP1703T-5002E/MB
F_USB,PTC 1.5A hold 6V 1206,SMD1206P150TF,C20802,Extended,11515,0.1197,2026-10-28,Littelfuse 1206L150THWR
D_VBUS,TVS 5V uni SMA,SMAJ5.0A (MDD),C113952,Extended,487120,0.0413,2026-10-28,Littelfuse SMAJ5.0A
D_48V,TVS 48V bidir SMB,SMBJ48CA (FTR),C693510,Extended,4410,0.0518,2026-10-28,Littelfuse SMBJ48CA
U_ESD,USB ESD array SOT-23-6,USBLC6-2SC6 (TECH PUBLIC),C2827654,Extended,103720,0.0452,2026-10-28,ST USBLC6-2SC6
D_FAN,TVS 15V uni SOD-123FL,SMF15A (MDD),C123802,Extended,6520,0.0326,2026-10-28,Littelfuse SMF15A
```

Item 2b (TLV75733PDBVR, C485517) is a fallback, not proposed for the BOM.

## Caveats

- DigiKey and Mouser ordering codes are from the MPN pattern or search results and were not opened. Verify before G4.
- Datasheets for C165948 (image drawing) and C78988 (application note, first three pages) were read; TLV757P pages 4 to 6 and the GOODWORK HT75XX datasheet pages 1 to 8 were read. The other datasheets were not opened; their numbers for items 4 to 8 come from LCSC's parameter table, not the PDFs.
- Stock and prices are live numbers from one day and move.

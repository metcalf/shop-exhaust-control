# Sourcing: passives (JLCPCB Standard PCBA)

Checked 2026-10-28. Stock and price from the LCSC product-detail endpoint (wmsc.lcsc.com/ftps/wm/product/detail?productCode=Cxxxx); price is USD per piece at the qty-100 break (or the lowest break above the MOQ where there is no 100 tier, noted). Class from the jlcpcb.com/partdetail/Cxxxx page. Class column marked "(?)" means the page did not state the library type unambiguously (page returned only a section heading or a 429); verify in the JLCPCB parts search before ordering. Datasheets: `https://www.lcsc.com/product-detail/Cxxxx.html`.

## Resistors, thick film, 1 %

| Value | Pkg | Rating | MPN | LCSC | Class | LCSC stock | $/pc @100 | Date |
|---|---|---|---|---|---|---|---|---|
| 120 Ω | 0603 | 100 mW | 0603WAF1200T5E | C22787 | Basic | 669,200 | 0.0019 | 2026-10-28 |
| 200 Ω | 0603 | 100 mW | 0603WAF2000T5E | C8218 | Basic (?) | 799,600 | 0.0039 | 2026-10-28 |
| 390 Ω | 0603 | 100 mW | 0603WAF3900T5E | C23151 | Basic (?) | 1,845,000 | 0.0017 | 2026-10-28 |
| 1 kΩ | 0603 | 100 mW | 0603WAF1001T5E | C21190 | Basic | 6,877,400 | 0.0017 | 2026-10-28 |
| 3.3 kΩ | 0603 | 100 mW | 0603WAF3301T5E | C22978 | Basic | 2,987,300 | 0.0022 | 2026-10-28 |
| 4.7 kΩ | 0603 | 100 mW | 0603WAF4701T5E | C23162 | Basic | 3,636,100 | 0.0028 | 2026-10-28 |
| 5.1 kΩ | 0603 | 100 mW | 0603WAF5101T5E | C23186 | Basic (?) | 16,428,100 | 0.0016 | 2026-10-28 |
| 10 kΩ | 0603 | 100 mW | 0603WAF1002T5E | C25804 | Basic | **0 (out of stock)** | 0.0022 | 2026-10-28 |
| 22 kΩ | 0603 | 100 mW | 0603WAF2202T5E | C31850 | Basic | 1,837,200 | 0.0042 | 2026-10-28 |
| 47 kΩ | 0603 | 100 mW | 0603WAF4702T5E | C25819 | Basic | 584,000 | 0.0020 | 2026-10-28 |
| 100 kΩ | 0603 | 100 mW | 0603WAF1003T5E | C25803 | Basic | 9,309,700 | 0.0030 | 2026-10-28 |
| 453 kΩ | 0603 | 100 mW | none found in stock | - | - | - | - | 2026-10-28 |
| 2.7 kΩ | 1206 | 250 mW | 1206W4F2701T5E | C17950 | **Extended** | 38,600 | 0.0044 | 2026-10-28 |

Notes
- 10 kΩ: Basic C25804 shows 0 LCSC stock today (may be transient; JLCPCB keeps its own stock, which the page didn't show). In-stock fallback is Yageo RC0603FR-0710KL, C98220, Extended, 3,787,600 pcs, $0.0027 @100.
- 453 kΩ (E96): the only LCSC/JLC 0603 1 % thick-film 453k parts found are out of stock: Multicomp MCWR06X4533FTL C241123 (Extended, sold out, $0.0038) and CAL-CHIP RM06F4533CT C4333887 (Extended, 0 stock, MOQ 5000). No UNI-ROYAL 0603WAF4533T5E or Yageo RC0603FR-07453KL LCSC listing found. Nearest-value alternatives were not searched; suggest the supervisor pick another divider value or re-check later.
- 1206 2.7 kΩ: no Basic 1206 2.7k found; C17950 is Extended (a $3 loading fee applies if no other Extended part makes it worthwhile; consider two 0603 in series/parallel only if the power budget allows, which was not assessed).

## Capacitors, MLCC

| Value | Pkg | Rating | MPN | LCSC | Class | LCSC stock | $/pc | Date |
|---|---|---|---|---|---|---|---|---|
| 22 pF | 0603 | C0G, 50 V, 5 % | CL10C220JB8NNNC | C1653 | Basic | 198,700 | not retrieved (breaks start at 50 pcs) | 2026-10-28 |
| 10 nF | 0603 | X7R, 50 V, 10 % | CL10B103KB8NNNC | C1589 | **Extended** | 1,840,450 | 0.0075 (@50) | 2026-10-28 |
| 100 nF | 0603 | X7R, 50 V, 10 % | CC0603KRX7R9BB104 | C14663 | Basic | 42,950 | 0.0082 (@50) | 2026-10-28 |
| 1 uF | 0603 | X5R, 50 V, 10 % | CL10A105KB8NNNC | C15849 | Basic | 391,100 | 0.0141 (@50) | 2026-10-28 |
| 10 uF | 0805 | X5R, 25 V, 10 % | CL21A106KAYNNNE | C15850 | Basic (?) | 1,708,660 | 0.0441 (@20) | 2026-10-28 |
| 1 uF | 0805 | X7R, 50 V, 10 % | CL21B105KBFNNNE | C28323 | Basic | 599,990 | 0.0347 | 2026-10-28 |
| 22 uF | 1206 | X5R, 25 V, 10 % | CL31A226KAHNNNE | C12891 | Basic (?) | 138,620 | 0.1171 (@20) | 2026-10-28 |

Notes
- 10 nF: Basic candidate Yageo-style 0603B103K500NT C57112 (X7R 50 V) has 0 stock today, so C1589 (Extended, in stock) is the pick. The 0603 1 uF 50 V part covers both 0603 1 uF lines (>= 16 V).
- X5R/X7R DC-bias derating applies to the 22 uF buck output cap (25 V rating on a ~5 V or lower rail is fine) and the 10 uF 0805.

## Confirmations (price at qty 10)

| Part | LCSC | Class | LCSC stock | $/pc @10 | Date |
|---|---|---|---|---|---|
| ESP32-S3-WROOM-1-N16R8 | C2913202 | Extended | 31,339 | 4.7466 | 2026-10-28 |
| AO3400A | C20917 | Basic | 615,350 | 0.0897 (5+ tier) | 2026-10-28 |
| 1N4148W | C81598 | Basic | 2,470,700 | 0.0125 (lowest tier is 50 pcs, no qty-10 price) | 2026-10-28 |

Caveat: stock/price came via an LLM-summarised fetch of the LCSC JSON, and class via summarised JLCPCB pages; spot-check anything critical on the live site.

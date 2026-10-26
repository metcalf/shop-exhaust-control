# PM sensor comparison for Q-24: SEN55 vs SPS30 (SEN66 for reference)

Checked 2026-10-25. This is a comparison for the supervisor, not a part pick, and no `bom.csv` rows are proposed.
"Not found" means I looked in the documents named and the item isn't there. It does not mean the part lacks the feature.

Documents read directly (page images):
- **SEN5x DS**: SEN5x datasheet v2, March 2022. [PDF](https://sensirion.com/media/documents/6791EFA0/62A1F68F/Sensirion_Datasheet_Environmental_Node_SEN5x.pdf). This is the version linked from search results. I could not confirm whether Sensirion has since published a newer one.
- **SPS30 DS**: SPS30 datasheet v2.0, June 2023. [PDF](https://sensirion.com/file/datasheet_sps30). I read pp. 1-8, 16-18 and 23-24 only (spec tables, modes, formats, I2C overview and command table, mechanical).
- **SEN6x DS**: SEN6x datasheet v1.0, October 2026 (61 pp.). [PDF](https://sensirion.com/media/documents/FAFC548D/6AC50BC5/PS_DS_SEN6x.pdf). I read pp. 1-14, 16-17, 36-37, 42 and 56.
- **AN-Reduced-Power**: [Reduced Power Operation for SEN5x](https://sensirion.com:443/media/documents/1B417576/62F0B936/Reduced_Power_Operation_SEN5x.pdf), v1.0, Aug 2022.
- **AN-Temp**: [Temperature Acceleration and Compensation Instructions for SEN5x](https://sensirion.com:443/media/documents/9B9DE2A7/61E957EB/Sensirion_Temperature_Acceleration_and_Compensation_Instructions_SEN.pdf), v1.0, Jan 2022.
- **AN-Mech**: [Mechanical Design and Assembly Guidelines for SEN5x](https://sensirion.com/resource/user_guide/sen5x/mechanical_design_assembly_guidelines), v1.0, June 2021.

Secondary sources, not Sensirion documents:
- The Sensirion embedded driver `sen5x_i2c.c`/`.h` on GitHub, read through a fetch summary. It is used only for command IDs and the number-concentration answer.
- The RIOT-OS driver docs.
- Distributor pages.

## Comparison table

| Item | SEN55-SDN-T | SPS30 | SEN66-SIN-T (reference) |
|---|---|---|---|
| Lifecycle, Sensirion page | **NRND**, successor listed as SEN65 | No notice on page | Active (SEN6x family all listed Active) |
| Lifecycle, DigiKey | Active | Active | Active |
| DigiKey qty 1, 2026-10-25 | $34.13, 972 in stock (page fetch) | $39.32, stock not shown in fetch | $62.03, 2,481 in stock (page fetch); a search snippet showed $58.55 |
| Mouser qty 1 (search-engine snapshot, date unknown, not verified) | EUR 27.37 on the gr.mouser page, **0 in stock**, backorder dates 8/10 and 8/19/2026 (already past, so stale); no USD price found | $35.36, 1,842 in stock | not checked |
| Outputs | PM mass, RH, T, VOC idx, NOx idx (SEN5x DS Table 1) | PM mass + number conc + typical particle size (SPS30 DS Table 1, §4.3) | PM mass, RH, T, VOC, NOx, CO2 (SEN6x DS p.1) |
| Gas-only mode (fan and laser off, RH/T and VOC/NOx running) | **Yes**: cmd 0x0037, 6.8 mA typ / 8 max (SEN5x DS Table 8, §5.1, §6.1.2) | No gas sensors. Sleep mode is 38 µA typ, 50 max (SPS30 DS Table 2) | **No**. Only Idle and Measurement modes (SEN6x DS §4.1, Fig. 3) |
| Number conc. (PM0.5/1/2.5/4/10) | **Yes**, via cmd 0x0413 per driver. Not in the public datasheet (see A4) | Yes, in the Read Measured Values frame (SPS30 DS §4.3) | Yes, cmd 0x0316, PM0.5-PM10 (SEN6x DS §4.8.13, Table 40) |
| Typical particle size | Yes via 0x0413 per driver; not in the datasheet | Yes (SPS30 DS §4.3, fn 8) | Not found in the SEN6x DS pages read (§4.8.13 has number conc only) |
| Mass conc. range | Specified 0-1000 µg/m³ (Table 3) | 0-1000 µg/m³ (Table 1) | Specified 0-1000; output range 0-6000 (Table 2) |
| Mass precision PM1/PM2.5 | ±(5 µg/m³ + 5 % m.v.) for 0-100; ±10 % m.v. for 100-1000 | Same | Same |
| Mass precision PM4/PM10 | ±25 µg/m³ for 0-100; ±25 % m.v. for 100-1000 | Same | Same |
| Number conc. range and precision | Not found in the SEN5x DS | 0-3000 #/cm³. PM0.5/1/2.5: ±100 #/cm³ for 0-1000, ±10 % m.v. for 1000-3000. PM4/10: ±250 #/cm³, ±25 % m.v. | Not found in the SEN6x DS Table 2 |
| Particle size ranges | Mass: PM1 0.3-1, PM2.5 0.3-2.5, PM4 0.3-4, PM10 0.3-10 µm (Table 3) | Same, plus number PM0.5 0.3-0.5 µm (Table 1) | Mass same as SEN5x (Table 2) |
| PM start-up time | 8 s (200-3000 #/cm³), 16 s (100-200), 30 s (50-100) (Table 3) | Same values (Table 1) | 30 s typ (Table 2) |
| Rated lifetime | >10 y at 24 h/day (Table 2, MTTF-based) | >10 y at 24 h/day (Table 1 fn 6) | 10 y min, for an *indoor air quality mission profile* (Table 1 fn 6), HCHO excluded. See A6 |
| Fan auto-clean | Default 604,800 s ±3 %, 10 s at max speed. Interval set via 0x8004, 0 = off. **Volatile**, reverts on reset (SEN5x DS §5.2, §6.1.13) | Same default. Interval set via 0x8004, **stored in non-volatile memory** (SPS30 DS §4.2) | Manual cmd 0x5607 only in the contents list. No interval command in the TOC. Auto-clean behaviour **not found** (SEN6x DS §4.8.23) |
| Interface | I2C only, 0x69, 100 kbit/s, SEL pin to GND, 10 kΩ pull-ups (SEN5x DS §4, §6). 6-pin ACES 51451-0060N-001, mating JST GHR-06V-S | I2C (0x69, SEL to GND) **or UART** (SHDLC 115200 8N1, SEL floating). 5-pin JST ZHR-5 (SPS30 DS §3, §5, §6) | I2C, 3.3 V logic (SEN6x DS §2) |
| Supply | 5 V, 4.5-5.5 (Table 8) | 5 V, 4.5-5.5 (Table 2) | 3.3 V, 3.15-3.6 (Table 12) |
| Current | Idle 2.6 mA typ / 3 max (first 10 s: 3.8 / 4.2). Gas-only 6.8 / 8. Measurement 63 / 80 after 60 s (70 / 100 in the first 60 s). Peak 100 / 110 mA at 16 µs (Table 8) | Sleep 38 µA. Idle 330 µA. Measurement 55 mA typ / 65 max, 80 max in the first 200 ms (Table 2) | Idle 3.3 mA (4.6 in the first 10 s). Measurement 90 typ / 110 max. Peak 300 / 350 mA at 2 ms (Table 12) |
| Dimensions | 52.3 ±0.4 × 43.3 (+0.2/-0.6) × 22.3 ±0.4 mm, 36.4 g (Fig. 7, Table 2) | 40.8 × 40.8 × 12.3 mm with foil, 26.3 g (Fig. 7, Table 1) | 55.2 × 25.6 × 21.3 mm, 20 g (Fig. 8, Table 1) |
| Operating limits | Recommended 10-40 °C and 20-80 %RH. Absolute -10 to 50 °C and 0-90 %RH non-condensing. Gas specs guaranteed only inside the recommended range (Table 6, §2.5.1) | Best performance 10-40 °C and 20-80 %RH. Absolute -10 to 60 °C and 0-95 %RH (§1.2, Table 3) | Recommended 10-40 °C and 20-80 %RH. Absolute -10 to 50 °C and 0-90 %RH (Table 10) |
| RH/T accuracy (typ / max) | T ±0.45 / ±0.7 °C at 15-30 °C, 50 %RH. RH ±4.5 / ±6 %RH at 25 °C, 30-70 %RH (Table 4) | No RH/T | Same values as SEN55 (Table 3) |
| T-compensation parameters | Offset, slope, time constant (single set), plus acceleration mode (0x60F7) and warm start (0x60C6) (§6.1.6, §6.1.7, §6.1.10) | n/a | Same, plus **5 offset slots** for independent switchable heat sources (§4.8.14) |

## Answers

### 1. Lifecycle
- **SEN55: Sensirion's own product page shows "NRND", with SEN65 named as the successor.** I fetched the page twice and got the same result both times. I could not find a dated notice for it. [SEN55 page](https://sensirion.com/products/catalog/SEN55)
- DigiKey lists the SEN55 as Active. I did not get a Mouser lifecycle field.
- SPS30: the Sensirion page carries no discontinuation notice (page lists the datasheet as 07/2023 and a certification update 10/2025). DigiKey lists it as Active. [SPS30 page](https://sensirion.com/products/catalog/SPS30)
- SEN66: Active at DigiKey. The Sensirion SEN6x series page lists all six variants as Active. [SEN6x series](https://sensirion.com/products/catalog/series/sen6x)
- PCN: search-result summaries of Farnell-hosted Sensirion PDFs mention an Information Letter 231801 (2023-05-02, additional fan supplier, firmware 2.1) and a minimum order quantity change to 270 units for SEN5x. I did not open those PDFs, so treat this as unverified. I found no discontinuation notice (a formal end-of-life PCN) for SEN5x.
- Net: the SEN55 is available now but NRND. A design-in today starts life on a part Sensirion has already steered people away from. The nearest successor, SEN65, has no gas-only mode (SEN6x DS §4.1). See also A3.

### 2. Price and stock (qty 1)
- DigiKey, 2026-10-25, fetched from the page:
  - SEN55-SDN-T: $34.13, 972 in stock.
  - SPS30: $39.32 (DigiKey part 1649-1106-ND). Stock was not shown in the fetch.
  - SEN66-SIN-T: $62.03, 2,481 in stock.
- **Confirmed at DigiKey: the SEN55 is cheaper than the SPS30, by about $5 (13 %).**
- Mouser, from search-engine snapshots with unknown dates and not verified against live pages:
  - SPS30: $35.36, 1,842 in stock.
  - SEN55: EUR 27.37 on the gr.mouser page, **0 in stock**, with backorder dates that have already passed. I found no USD price.
- Mouser's SPS30 ($35.36) and DigiKey's SEN55 ($34.13) are nearly equal. Andrew should re-check live prices before ordering.
- I saw no clearance or promo flags on any of the pages. The SEN66 price differs between two reads ($58.55 from a search snippet, $62.03 from the page fetch), so these numbers move.
- DigiKey quotes an 11-week lead time on both parts, but both show stock now.
- Links: [DigiKey SEN55](https://www.digikey.com/en/products/detail/sensirion-ag/SEN55-SDN-T/16342756), [DigiKey SPS30](https://www.digikey.com/en/products/detail/sensirion-ag/SPS30/9598990), [DigiKey SEN66](https://www.digikey.com/short/384rbwtj), [Mouser SPS30](https://www.mouser.com/en/ProductDetail/Sensirion/SPS30?qs=lc2O%2BfHJPVbEPY0RBeZmPA%3D%3D), [Mouser SEN55](https://gr.mouser.com/ProductDetail/Sensirion/SEN55-SDN-T?qs=MyNHzdoqoQLyWUzejWkZfg%3D%3D).

### 3. Gas-only mode (SEN55): yes
- Command "Start Measurement in RHT/Gas-Only Measurement Mode", ID **0x0037**, execution time under 50 ms (SEN5x DS Table 12, §6.1.2). In this mode the fan and laser are off, and RH/T, VOC and NOx update every 1 s. The PM output reads 0xFFFF (§5.1, §6.1.5).
- Current is **6.8 mA typ / 8 mA max** (Table 8). Full measurement mode is 63 mA typ / 80 mA max.
- Switching: the direct jump between Measurement and Gas-Only needs **firmware v2 or newer** (Fig. 5 caption). Idle mode also works as the entry point.
- Does switching modes reset the VOC/NOx algorithm state?
  - **Not documented.** The datasheet says only that the VOC algorithm "resets its state to initial values each time a measurement is started" (§6.1.11).
  - It doesn't say whether a direct Measurement to Gas-Only switch counts as a "start". The Reduced Power app note's cycling scheme (Fig. 2) shows VOC/NOx updating continuously through the alternation but never states state continuity. I'd treat continuity as likely, not guaranteed, and test it on a real unit. I didn't find the "Engineering Guidelines for SEN5x" document, which might say.
  - Only a VOC state backup/restore command exists (0x6181). There is no NOx equivalent in the datasheet. The command only works in idle mode (§6.1.11).
  - Idle mode does not run the gas algorithms. Using Stop Measurement to go to Idle would reset them, so use gas-only, never Idle, as the low-power state.
- PM warm-up when switching back:
  - The Reduced Power app note says to run Measurement mode **at least 30-60 s before using PM output** (AN-Reduced-Power §2.1). The datasheet's typical start-up is 8 / 16 / 30 s depending on number concentration (Table 3). Concentrations of 100 #/cm³ or less need the 30 s end of that range, which is likely in clean shop air.
  - The note suggests 30 s warm-up plus 30 s of averaging, and says never to go below 8 s.
  - The datasheet's current table has a "first 60 seconds" row at 70 mA typ / 100 max.
- RH/T during cycling: the internal compensation handles the self-heating change between modes, but "at too high switching rates the compensation can become unprecise for built-in scenarios" (AN-Reduced-Power §2.1, Fig. 4). The note shows saw-tooth behaviour.
- Auto-clean: the datasheet says auto-clean is triggered "when the module is in Measurement-Mode" (§5.2), and that the timer resets if the sensor is switched off. **Not found:** whether the timer runs during gas-only. If PM is duty-cycled, plan on a manual clean via 0x5607 (Measurement mode only, §6.1.12) at least weekly.
- Winter caveat: gas specs are guaranteed only at 10-40 °C and 20-80 %RH (Table 6). Andrew should check the shop's winter minimum.

### 4. Number concentrations (SEN55)
- **Yes in function, but not in the public SEN5x datasheet.**
- The SEN5x datasheet v2 (March 2022) lists only these commands (Table 12): 0x03C4 Read Measured Values (PM1/2.5/4/10 mass, RH, T, VOC, NOx), plus the others in the table. It has **no** command for number concentration or typical particle size. It does reference "number concentration" in the PM start-up row of Table 3.
- Sensirion's embedded driver `embedded-i2c-sen5x` (`sen5x_i2c.c`/`.h`) has `sen5x_read_measured_pm_values`, command **0x0413**. It returns mass PM1/2.5/4/10, number concentration PM0.5/1/2.5/4/10 (scaled ×10, #/cm³) and typical particle size (scaled ×1000, µm), with 0xFFFF for unknown. I got the ID through a fetch summary of the source, so spot-check it against the repo before writing firmware. The RIOT-OS driver docs agree on the structure fields and scaling, but don't show the ID.
- The driver also has `read_measured_raw_values` at 0x03D2.
- ESPHome's sen5x component is another reference, but I didn't check which fields it exposes.
- Not found: SEN5x number concentration range and precision, and a typical-size range. The SPS30 does specify 0-3000 #/cm³ with the precision shown above.
- Mass (Table 3) and number precision both rest on Sensirion's PM sensing of PM2.5 calibrated to TSI DustTrak DRX 8533 (mass). The SPS30 also specifies number conc calibrated to TSI OPS 3330 (SPS30 DS Table 1). The SEN5x table doesn't state this.

### 5. PM accuracy and range
- All three parts give the same mass precision, since they share the same mass spec table values.
  - PM1/PM2.5, 0-100 µg/m³: ±(5 µg/m³ + 5 % m.v.). 100-1000 µg/m³: ±10 % m.v.
  - PM4/PM10, 0-100 µg/m³: ±25 µg/m³. 100-1000 µg/m³: ±25 % m.v.
  - Long-term drift: ±1.25 µg/m³/yr (0-100) and ±1.25 % m.v./yr (100-1000).
  - Temperature-dependent drift: ±0.5 % m.v./°C away from 25 °C.
  - Source: SEN5x DS Table 3, SPS30 DS Table 1, SEN6x DS Table 2.
- Range: specified 0-1000 µg/m³ for all three. The SEN6x output range goes to 6,000 µg/m³, but that is outside its specified range.
- PM4 and PM10 are "calculated based on distribution profile of all measured particles" (Table 3 fn 5, SPS30 Table 1 fn 4). For sawdust the PM4/PM10 figures carry the ±25 % precision and should be treated as indicative, with PM2.5 and below as the main signal. I didn't find any spec on how that calculation behaves for sawdust.
- Calibration reference: PM2.5 mass is calibrated to TSI DustTrak DRX 8533 on a KCl aerosol. Wood dust is not what it was verified on. The accuracy statements are against that aerosol, not sawdust.
- Number concentration: SPS30 range 0-3000 #/cm³ (see table). SEN5x and SEN66: not found.
- Particle size range (mass bins): 0.3-1.0 / 2.5 / 4.0 / 10 µm. SPS30 adds number PM0.5 at 0.3-0.5 µm. A numeric range for "typical particle size" is not found for any of them. The SPS30 reports it in nm and describes it in a footnote as correlating with the weighted average of number-concentration bins measured with a TSI 3330 sizer.

### 6. Other per-part items
- Lifetime: SEN5x and SPS30 are both ">10 years at 24 h/day", MTTF-based, with a footnote that it may vary with operating conditions. The SEN6x says 10 years "for an indoor air quality mission profile", so a dustier shop is outside that. None of the three datasheets quantify dust loading. I'd treat the lifetime numbers as unproven for a woodshop.
- Auto-clean: see the table and A3. The SPS30 keeps its interval across power cycles. The SEN55 doesn't.
- Interface: SEN55 is I2C only. The SPS30 offers both and recommends UART for cables over 20 cm. Its I2C section recommends under 10 cm (SPS30 DS §3, §6). The SEN5x datasheet also recommends under 10 cm (§6). Andrew's sensor is mounted under the cabinets with the controller. If the PM sensor sits more than about 10 cm from the ESP32, the SPS30's UART is the more robust option.
- Metal shield: on both SEN5x and SPS30, the GND pin is internally connected to the metal shield. Keep the shield floating, or equalise it (SEN5x DS §4, SPS30 DS §3). This matters for the enclosure design.
- Mounting and airflow (AN-Mech, SEN5x; I found nothing equivalent for the SPS30 in the sections I read):
  - Keep the two inlets and one outlet unobstructed, and seal inlet and outlet from each other and from the enclosure interior (§2.1).
  - Vertical placement: inlets and outlet should face **down** (§2.2). Lateral placement: inlets above the outlet. Horizontal placement: both orientations are fine.
  - Isolate the sensor from external airflow above 1 m/s (§2.3).
  - Keep it away from, and below, heat sources like MCUs and Wi-Fi modules. Avoid direct sunlight (§2.4, §2.5).
  - Don't cover the entire surface in an all-around casing (§3).
- Dust and laser safety: laser Class 1, 660 nm for SEN5x and SPS30, 850 nm for SEN6x.

### 7. SEN55 RH/T compensation and self-heating
- **Yes, the compensation scheme applies to enclosure self-heating, within limits.**
  - The datasheet says the default compensation covers the module's own self-heating, and "if the module is designed into a device, the temperature compensation might need to be adapted to incorporate the change in thermal coupling and self-heating of other device components" (SEN5x DS §5.3).
  - The tuning command is "Read/Write Temperature Compensation Parameters" (0x60B2): `T_comp = T + slope·T + offset`, with offset (int16, scale 200), slope (int16, scale 10000) and a time constant in seconds (uint16). The values are smoothed with that constant, and the command is volatile, so write it at every boot (§6.1.6).
  - AN-Temp gives the procedure: place an accurate reference next to the device, wait for steady state, write the difference as offset, then repeat at another temperature for slope. It also covers the acceleration mode and warm start (0x60F7, 0x60C6).
  - Limit: AN-Mech §2.4 says the algorithm "can be adapted to deal with some additional heating", but "a degradation of performance is expected for excessive temperature offsets", and the module should sit away from and below other heat sources.
  - The SEN5x has one offset set. SEN6x gives five slots so switchable heat sources can be tuned independently (SEN6x DS §4.8.14).
- Stated accuracy (SEN5x DS Table 4): T ±0.45 °C typ / ±0.7 max at 15-30 °C, 50 %RH. RH ±4.5 typ / ±6 max at 25 °C, 30-70 %RH. RH repeatability ±1 %RH. Response: T under 60 s, RH under 20 s (τ63). The figures apply to the bare module under default compensation (AN-Temp p.1: "wooden table", no significant airflow, "to prevent additional heat dissipation due to convection"). They are not guaranteed after design-in.
- Whether the VOC/NOx index algorithms use the RH/T reading for their own compensation is **not found** in the SEN5x datasheet. Q-24's premise (SEN55 humidity feeding VOC compensation) therefore rests on that internal behaviour, which Sensirion doesn't document in the documents I read. The datasheet also gives no humidity-dependent VOC accuracy figures, only the 25 °C / 50 %RH conditions in Table 5.
- A separate SHT4x remains an option for host-side humidity, but then Andrew owns the self-heating compensation himself.

## Open items

- Whether a direct Measurement to Gas-Only switch preserves VOC/NOx state: bench-test it. Also read the SEN5x "Engineering Guidelines", which I couldn't locate.
- Live Mouser stock and USD price for the SEN55 before ordering. The one snapshot I saw showed 0 in stock.
- The SEN55 NRND status: Sensirion's product page is the only source. Ask Sensirion or a distributor for the last-time-buy date if SEN55 is chosen.
- SEN66's number concentration range, typical particle size and auto-clean behaviour, which weren't in the pages I read.

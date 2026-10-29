# UI parts and board connectors (JLCPCB Standard PCBA)

Checked 2026-10-28. Stock/price are LCSC product-detail data for that day (USD, price at qty 10 or nearest tier above the MOQ shown). JLC class and assembly type are from the jlcpcb.com part page. Assembly type: "SMT" = JLC places; "Wave" = THT, JLC wave-solders or hand-solders (Standard PCBA lists THT on the same side as SMT). Nothing here needs owner hand-soldering. Re-check stock at order time.

Result up front: no part below is JLC Basic. Everything is Extended (+$1.53 each on Standard). The only Basic candidate is the SMD tact switch (C318884), and the JLC page did not state its class outright. Verify in the JLC order tool.

| # | Function | MPN | LCSC | JLC class / assembly | Stock | Unit @ qty | Package | Key values | Datasheet | DigiKey / Mouser |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Rotary encoder + push | Alps Alpine EC11E18244A5 | C255515 | Extended / Wave | 262 | $2.1026 @10 | THT vertical, 11 mm body, 7-pin (A,B,C + D,E switch + 2 dummies) | 18 pulse, 36 detent, flat shaft 20 mm long (4.5 mm flatted, 6 mm dia), push travel 1.5 mm, 10 mA 5 V, 15k cycles | https://datasheet.lcsc.com/datasheet/pdf/29035d0f86a1bb052c08784da0871b4f.pdf?productCode=C255515 | DK 4809-EC11E18244A5-ND (DK page: 20 wk lead, stock figures conflicting). Mouser PN not verified |
| 2a | Front-panel tact (x4) | HCTL TC-6610-9.5-260G | C2845262 | Extended / Wave (page shows only "Tactile Switches"; Extended assumed from the others, verify) | 1,120 | $0.0240 @20 (MOQ 20) | THT 6x6 mm, 4-pin, round actuator | 9.5 mm height, 2.6 N, 12 V 50 mA, 100k cycles | https://datasheet.lcsc.com/datasheet/pdf/1313a504967a54f7c30bb226a1314b71.pdf?productCode=C2845262 | Same family: C&K PTS645SK952LFS (LCSC C285478, stock 0). DK/Mouser PN not looked up |
| 2b | Internal BOOT/EN tact | XKB TS-1187A-B-A-B | C318884 | Basic? (JLC page ambiguous) / SMT | 875,640 | $0.0208 @20 (MOQ 20) | SMD 5.1x5.1 mm, 4-pin, 1.5 mm tall (actuator) | 1.6 N (160 gf), 12 V 50 mA, 100k cycles | https://datasheet.lcsc.com/datasheet/pdf/56c8799ae5193945a16a1ffbe378246a.pdf?productCode=C318884 | DK/Mouser PN not looked up |
| 3 | RGB LED, common anode | TOGIALED TJ-S3528UG2W9TLCCYRGB-A5 | C601699 | Extended / SMT | 14,300 | $0.1061 @5-49 | SMD3528-4P, 3.16x2.71x1.9 mm | See LED notes | https://datasheet.lcsc.com/datasheet/pdf/af6ad76b36d8d13fad624b46153f1730.pdf?productCode=C601699 | none (generic part) |
| 4a | 2-pos screw terminal | Cixi Kefa KF128L-3.5-2P | C474930 | Extended / Wave | 3,000 | $0.1571 @5-49 | THT 3.5 mm pitch, 8.6 mm tall | 10 A, 300 V, 16-26 AWG (1 mm2), M2 screw, 105 C | https://datasheet.lcsc.com/datasheet/pdf/588ccdb2ca658a71a0feec98221f7497.pdf?productCode=C474930 | Phoenix MKDS 1/2-3.5 is the nominal DK equivalent (PN not looked up) |
| 4b | 4-pos screw terminal | Xinlaiya XY350V-3.5-4P | C557656 | Extended / Wave | 3,495 | $0.3015 @5-49 | THT 3.5 mm pitch, 8.6 mm tall | 7 A, 300 V, 18-24 AWG (listing), M2 screw | https://datasheet.lcsc.com/datasheet/pdf/b7a21dc8f540ff394fd913146d78d84b.pdf?productCode=C557656 | as 4a |
| 5a | SEN65 board-side header | JST SM06B-GHS-TB(LF)(SN) | C133065 | Extended / SMT | 25,620 | $0.3599 @5-49 | SMD right-angle (side entry), 1.25 mm, 6P, 10.75 mm long | 1 A, 50 V, GH series | https://datasheet.lcsc.com/datasheet/pdf/145d85af57fc54ac5a4f36dce2b36dd3.pdf?productCode=C133065 | DK 455-1568-1-ND (cut tape; from regional pages, confirm on digikey.com) |
| 5b | SEN65 cable | Adafruit #5754, JST-GH 6-pin, 100 mm, GHR-06V-S both ends | n/a | off-board | n/a | n/a | n/a | JST-GH compatible, not genuine JST (see note) | https://thepihut.com/collections/adafruit/products/jst-gh-1-25mm-pitch-6-pin-cable-100mm-long | DK PN not looked up. Commodity module vendor, flagged |
| 6a | 1x8 female header | HCTL PM254-1-08-Z-8.5 | C2897371 | Extended / Wave | 10,272 | $0.1547 @6-59 | THT 2.54 mm, 1x8, 8.5 mm tall, square holes | 3 A, copper alloy, 105 C | https://datasheet.lcsc.com/datasheet/pdf/87e2b5b113f4df247d2b8d5758217346.pdf?productCode=C2897371 | Sullins PPPC081LFBN-RC (DK S7006-ND, from memory, unverified) |
| 6b | 1x8 male header | XFCN PZ254V-11-08P | C492407 | Extended / Wave | 228,990 | $0.0515 @10 | THT 2.54 mm, 1x8, 2.5 mm insulator, 6.1 mm mating pin | 3 A, 250 V, gold, brass | https://datasheet.lcsc.com/datasheet/pdf/3b85a1cdf6ed945f2e278f00c1e42442.pdf?productCode=C492407 | Not looked up |

## Notes

**1. Encoder.** Verified against the Alps EC11 catalog table: EC11E18244A5 is vertical, flat shaft, 20 mm shaft length, 18 pulses / 36 detents, with push switch (1.5 mm travel). That is two detents per quadrature cycle, so decode on every second detent. Active-high pull-ups needed (open-contact type, 10 mA at 5 V max, so use 3.3 V with 10k pull-ups plus a small RC). C361165 (EC11E1834403) is the non-detent version, so don't use it. I did not look for a generic EC11 clone. Alps is cheap enough here.

**2. Tact switches.** A 13 mm 6x6 THT is not stocked in volume. XUNPU TS-1002-13026 (C455107) has 10 pcs, and the SMD 13 mm version has 25. Stocked heights, all HCTL 6x6 THT round-button:
- 9 mm: TC-6610-9-260G, C2845257, 9,350 in stock, MOQ 50, $0.0173.
- 9.5 mm: TC-6610-9.5-260G, C2845262, 1,120, MOQ 20, chosen.
- 17 mm: TC-6610-17-100G, C2845265, 820, MOQ 10, $0.0570, 1 N force.

If the cap needs more reach, the 17 mm is the only taller part in stock. The cap stem length is a mechanical decision. The 5.1x5.1 SMD part is only 1.5 mm tall, which is fine for BOOT/EN on the board face. The G-Switch GT-TC096A-H090-L1 (C963357, 9 mm, 250 stock, Extended) is a second source at 9 mm. Contacts rated 12 V 50 mA, which is fine for GPIO.

**3. RGB LED (datasheet read, p.3).** Common anode on pin 4; cathodes pin 1 = R, 2 = G, 3 = B. Per color at IF = 20 mA:

| Color | Vf min/typ/max | Iv (mcd) | Dominant wavelength |
|---|---|---|---|
| R | 1.8 / 2.0 / 2.4 V | 300-600 | 620-630 nm |
| G | 2.8 / 3.0 / 3.4 V | 1200-2000 | 520-530 nm |
| B | 2.8 / 3.0 / 3.4 V | 300-600 | 460-470 nm |

Abs max 30 mA DC per color, 120 deg view. Lens finish (diffused or clear) is not stated. Two design consequences:
- G and B Vf can reach 3.4 V, which is above a 3.3 V rail. Tie the anode to 5 V (with cathode-side switching or PWM from the ESP32 through resistors or low-side FETs) or accept very dim G/B on 3.3 V.
- G is 3 to 7x brighter than R/B at equal current, so size the green resistor much higher.

This is not Basic. I did not find a Basic common-anode RGB. The 5050 hits on LCSC were addressable (WS2812-type) or didn't state their configuration, so I dropped them. A 5050 would only be needed if you want a bigger emitter. The 3528 is adequate for a status indicator behind a light pipe.

**4. Screw terminals.** The user's "one family in 2 and 4 positions" could not be met:
- KF128L-3.5 (16-26 AWG, 10 A) exists at LCSC in 2P (C474930) and 3P (C474931, 1,565 stock), but I found no 4P listing.
- KF350-3.5 has 2P (C474892, 17,060 stock, $0.1203 @5, 18-24 AWG) and 3P (C474893). No 4P found either.
- KF127S-3.5-4P (C2974905, 400 V, 16-26 AWG) exists, but only 79 in stock and $0.54 @10. KF127S-3.5-2P was 35 in stock. Rejected on stock.
- The XY350V-3.5-4P is the in-stock 4P: 7 A, 18-24 AWG (so it misses 16 AWG), same 3.5 mm pitch and 8.6 mm height as the KF128L. Fits 22-18 AWG signal wire. If 16 AWG is a hard need for the 4P, say so and I will look for another source.
- Alternative if one family matters more than the 4P wire range: XY350V-3.5-3P is C557655, 1,260 stock, but no 2P was found there either.

These are not UL-recognized as listed (LCSC pages carry no UL file number). That is fine for SELV signals, relay coil and sensor lines. Do not use them for line voltage. Mains terminals need a UL-recognized part, handled separately under G3.

**5. SEN65 connector.** Findings from ESPHome and the Sensirion cable listing (I could not retrieve the Sensirion SEN6x datasheet text itself):
- The SEN6x module end uses a JST GHR-06V-S (1.25 mm, 6-pin) cable-side housing. The module itself carries a GH header (not stated in the datasheet I could read).
- Pins 1 and 6 are VDD (tied), pins 2 and 5 are GND (tied). **Pins 3 and 4 (SDA/SCL, and where the SEL/I2C-mode pin sits) are not confirmed.** Read the pin table in the Sensirion SEN6x datasheet before routing. Also confirm which end of the cable is pin 1.
- Board side: the SM06B-GHS-TB(LF)(SN) (C133065) is the side-entry GH header. Place the cable to leave the board edge. C189892 (BM06B-GHS-TBT, vertical, $0.7799 @10, 7,029 stock) is the vertical alternative if the cable must leave upward.
- Cable: a GHR-06V-S to GHR-06V-S assembly (Adafruit #5754, 100 mm) mates to both. I assumed it is wired 1:1 (pin 1 to pin 1). Check with a meter on arrival. This is a JST-GH-compatible cable, not genuine JST. Adafruit lists this item for the SEN6x breakout.
- Sensirion's own cable (GHR-06V-S to 6 single jumper jacks, DK 1649-SEN5XJUMPER6-PINJSTGHR-06V-SCABLESET-ND, 572 in stock, ~$5.4) is an alternative if you prefer a 1x6 0.1" male header on the board instead of a GH header. Not chosen: it needs six loose sockets to be placed on pins, which is mechanically weaker and unpolarized.

**6. Headers.** None is Basic. JLC lists even the 1x40 pin header (C2337) as Extended. The selected parts are the highest-stock 1x8 straight parts that I checked. The female header at 8.5 mm tall puts the display module about 8.5 mm off the board.

## Gaps / not verified
- DigiKey/Mouser PNs for items 2, 3, 6, and 4 (apart from the ones stated). Mouser PN for the encoder.
- JLC class for C2845262 and C318884 (JLC page text ambiguous).
- Exact SEN65 SDA/SCL pin numbers (see note 5).

# Off-board parts (PM sensor, display, USB power, cables, glands)

Checked 2026-10-28. Prices are USD qty 1 unless noted. `bom.csv` does not exist yet, so the proposed rows below use a guessed column set (see the end).
"Not found" means I looked and the item isn't in the document named.

## Summary table

| # | Item | Part | Source / SKU | Price | Stock (2026-10-28) | Lead | Flag |
|---|---|---|---|---|---|---|---|
| 1a | PM/RH/T/VOC/NOx sensor | Sensirion **SEN65-SIN-T** | DigiKey 1649-SEN65-SIN-T-ND | $29.55 | **0** (60 expected 2027-01-20) | 17 wk | Out of stock at DigiKey. See notes. |
| 1b | Sensor cable | Sensirion SEN5X JUMPER 6-PIN JST GHR-06V-S cable set | DigiKey 1649-SEN5XJUMPER6-PINJSTGHR-06V-SCABLESET-ND | $6.09 | 572 | 4 wk | Length and 1:1 mapping not on the page |
| 2 | 2.8" 240x320 IPS SPI TFT, capacitive touch | Elecrow **DLS29028B** (LCDwiki MSP2834; ILI9341V, FT6336G) | [Elecrow](https://elecrow.com/2-8-ips-spi-lcd-capacitive-touch-module-ili9341-driver-240-320-resolution.html) | $10.90 | In stock (fetched 2026-11-09) | n/a | D-048. See §2a. The Elecrow page doesn't name MSP2834. |
| 3 | 5 V USB-C wall adapter | Raspberry Pi 15 W USB-C PSU, US, white **SC0445** (model KSA-15E-051300HU) | Newark SC0445 (Newark part 03AH7033) | $11.12 | 1,411 | n/a | **UL file number not found.** Not stocked at DigiKey. |
| 4 | USB-C to USB-C cable, 2 m | StarTech **USB2C5C2M** | DigiKey (digikey.com/.../USB2C5C2M/22160437) | $27.08 | 67 (4,670 factory) | 2 wk | 24 AWG power pair, 26 AWG listed for the other conductors. Data-pair gauge not published. |
| 5a | Cable gland x3 | Essentra **CG-PG7-2-BK**, PG7, 3.0-6.5 mm, IP68, nylon | DigiKey RPC1898-ND | $1.32 (qty 10: $1.12) | 5,344 | 31 wk listed, but stock is on hand | Locknut probably separate (CGLN-PG7-BK). See notes. |
| 5b | Lid gasket strip | Generic closed-cell neoprene/EPDM foam strip, adhesive back, 1/8" thick x 1/2" wide | Retailer (Zoro, Pres-Bond or similar), no part picked | typical $10-18 for a 50-75 ft roll | not checked | n/a | Typical price only, per your note. Unverified. |

## 1. SEN65-SIN-T and cable

Datasheet: [SEN6x v1.0, October 2026](https://sensirion.com/media/documents/FAFC548D/6AC50BC5/PS_DS_SEN6x.pdf) (the version already used in `sourcing/pm-sensor.md`).

**SEN6x connector pin assignment: SEN6x DS section 3 (p. 15), Table 17, with the pin layout in Fig. 1.**

| Pin | Name | Description / comment |
|---|---|---|
| 1 | **VDD** | Supply voltage |
| 2 | **GND** | Ground |
| 3 | **SDA** | Serial data in/out, "TTL 5V compatible" |
| 4 | **SCL** | Serial clock in, "TTL 5V compatible" |
| 5 | GND | Ground or NC. Pins 2 and 5 are connected internally |
| 6 | VDD | Supply or NC. Pins 1 and 6 are connected internally |

Other facts from the datasheet:
- Sensor-side connector: ACES 51468-0064N-001. Cable-side: ACES 51452-006H0H0-001 or compatible (for example JST GHR-06V-S) (Table 16).
- Cable: at least AWG26 (0.128 mm2), length at most 50 cm (Table 16). The I2C text (section 3.1) says to keep it under 10 cm or well shielded.
- Open-drain SDA/SCL need external pull-ups, for example 10 k to VDD (Fig. 2, section 3.1). The sensor has none.
- **The supply is 3.3 V (3.15-3.6 V), absolute max 3.6 V** (Table 12, Table 13). This differs from the SEN55 (5 V). The I/O pins tolerate 5.5 V (Table 13), so the logic level is not a problem on a 3.3 V ESP32 bus. Power it from the 3.3 V rail, not 5 V.
- Current for SEN65: idle 3.3 mA typ (4.6 mA in the first 10 s), measurement 75 mA typ / 100 mA max, peaks of 140 mA typ / 200 mA max for 2 ms (Table 12).
- SEN65 is covered by the Table 10 environmental limits: recommended 10-40 C and 20-80 %RH, absolute -10 to 50 C and 0-90 %RH non-condensing (p. 11). Gas specs hold only inside the recommended range.
- The SEN65 has no CO2 sensor and no gas-only mode (Figure 3 shows Idle and Measurement only). See `sourcing/pm-sensor.md` for the SEN55/SPS30/SEN66 comparison.

**Sensor availability.** DigiKey shows SEN65-SIN-T as Active at $29.55 with 0 in stock and 60 expected 2027-01-20 (17-week standard lead time). I could not get a live Mouser page (fetch timed out). A search aggregator listed Mouser 403-SEN65-SIN-T at roughly $22-28 with no stock figure, so treat that as unverified. Element14 Singapore showed 200 in stock at S$48.12, which doesn't help a US order. Andrew should check Mouser's live stock before ordering. If it is also out, the in-stock sibling is SEN66-SIN-T ($62.03, 2,481 at DigiKey per the 2026-10-25 note), at roughly twice the price and with CO2 added.

**Cable.** The Sensirion-recommended part is the "SEN5X JUMPER 6-PIN JST GHR-06V-S CABLE SET": $6.09, 572 in stock, 4-week lead (DigiKey). A search result from SOS Electronic lists the same cable as compatible with SEN5x and SEN6x, with a length of about 127 mm. DigiKey's page does not give the length or confirm 1:1 pin mapping. Both are open items. 127 mm is under your 15-20 cm target, and it must be checked against the sensor-to-ESP32 distance. Since the SEN6x datasheet wants under 10 cm for I2C, the shorter cable is not a problem for signal quality.
- If the mapping turns out not to be 1:1, or the length is too short: Adafruit 5754 "JST GH 1.25 mm 6-pin cable, 100 mm" is a different fix. I haven't verified its mapping or stock and am not proposing it as a second part.
- The ESP32 end of the cable is a bare-wire or mating-connector question for the PCB, so the PCB connector is a G3 design item.

## 2. Display: Newhaven NHD-2.8-CSXP-BREAKOUT (not chosen; the fallback)

Datasheet: [NHD-2.8-CSXP-BREAKOUT spec, rev 2, 2026-08-26](https://newhavendisplay.com/content/specs/NHD-2.8-CSXP-BREAKOUT.pdf). DigiKey: $28.95, 57 in stock, 16-week standard lead time ("2.8 IPS TFT ARDUINO BREAKOUT MOD.", non-touch).

- IPS is confirmed by the datasheet: the part-number key says "P - IPS, Wide Temperature", and the drawing says "2.8" 240x320 IPS TFT w/Breakout PCB". Viewing angle 80 degrees all sides, contrast 800 typ, luminance 1000 cd/m2 (p. 5).
- Controller ST7789VI. Interface parallel or SPI. No touch pins are used (TP_* pins are "No connect").
- Supply VDD 3.3-5.5 V. Supply current is 200 mA typ / 280 mA max **at 5.0 V** (p. 5). I found no 3.3 V current figure. Power it from 5 V. Whether the SPI inputs are 3.3 V logic when VIN is 5 V is **not stated**; check the schematic or the ST7789VI notes on Newhaven's support page before wiring directly.
- Operating -20 to +70 C.

**Catch: the board ships configured for 8-bit parallel.** Selecting 4-wire SPI means changing all six interface-select resistors R1-R6 (datasheet "Interface Selection" table, p. 4). Default 8080 8-bit has R1 closed, R2 open, R3 open, R4 closed, R5 open, R6 closed. 4-wire SPI has R1 open, R2 closed, R3 closed, R4 open, R5 closed, R6 open. These are SMD zero-ohm links, so this means hotplate or iron rework on a small board. I don't know their footprint size. This is the main weakness of this pick.

**No cheaper verified alternative.** The other 2.8" 240x320 IPS non-touch SPI modules I found are not verifiably IPS or not clearly pin-header: BuyDisplay ER-TFT028A3-4 (ST7789, IPS not confirmed on the listing), BuyDisplay ER-TFT028A2-4 (IPS, ILI9341, FPC not header), and EA TFT028-23AINN (lcd-module.com, IPS, controller not named). Adafruit's and Waveshare's IPS parts are 2.0" and their 2.8" parts have touch. The generic AliExpress/Amazon "2.8 inch IPS" modules are usually 14-pin or 8-pin SPI boards and I did not find one with a panel datasheet, so I am not proposing one (the listing title alone does not establish IPS).

**Header pinout, J2 (1x20, 2.54 mm, datasheet p. 4).** This single header carries everything needed for SPI; J1 (1x20) is only the parallel data bus.

| J2 pin | Symbol | SPI use |
|---|---|---|
| 1 | GND | Ground |
| 2 | VIN | 3.3 V or 5 V supply |
| 3 | TP_SDA/YD | NC |
| 4 | TP_SCL/XL | NC |
| 5 | TP_INT/YU | NC |
| 6 | TP_RST/XR | NC |
| 7 | IM0 | NC |
| 8 | IM1 | NC |
| 9 | IM2 | NC |
| 10 | SDO | MISO (serial data out; may be left open for write-only) |
| 11 | SDA | MOSI (serial data in) |
| 12 | CSX | CS, active low |
| 13 | SCL | SCLK |
| 14 | RST | Reset, active low |
| 15 | BLK | **No connect** |
| 16 | GND | Ground |
| 17 | TE | NC |
| 18 | SD_SDO | SD card data out |
| 19 | SD_CS | SD card chip select |
| 20 | SD_CD | SD card detect |

**D/C line for 4-wire SPI is on J1, not J2.** J1 pin 3 is "WRX / DCX" and carries the D/C select in 4-wire SPI mode (J1 pin 2 DCX/SCL is the 3/4-wire SPI clock alternative in the table). The table lists J1 pin 2 as "DCX (parallel) / SCL (3/4-wire SPI)" and J1 pin 3 as "WRX (parallel) / DCX (4-wire SPI)". J2 pin 13 is also labeled SCL, so which clock pin is live in SPI mode is ambiguous in the datasheet; the Newhaven example code (support.newhavendisplay.com, GitHub newhavendisplay) should be checked before the pin map is frozen. **This means 4-wire SPI needs a header connection on both J1 (pin 3 for D/C, possibly pin 2) and J2, so "a single header" does not hold.** In 3-wire SPI mode no D/C pin is needed, but that mode needs a different resistor set (R1 closed, R2 open, R3 open, R4 closed, R5 closed, R6 open) and 9-bit framing, which the ESP-IDF `spi_master` can do but is slower to drive.

**Backlight circuit.** Not user-driven. The board has an onboard backlight driver ("Key Features: EMI Shielding, Backlight Driver"), and BLK (J2 pin 15) is listed as "No connect". The backlight therefore runs whenever VIN is applied, and there is no PWM dimming pin. The spec lists luminance at I_LED = 160 mA (p. 5), which is inside the 200 mA typ supply figure. I could not find a schematic, so I don't know whether BLK is an enable that is open by default. If dimming is needed, cut VIN with a load switch (about 200 mA).

**Outline and mounting (mechanical drawing, p. 3).** Board 85.20 +/-0.5 mm tall x 69.03 +/-0.5 mm wide, PCB 1.60 mm, overall thickness 6.72 +/-0.5 mm. Four mounting holes dia 3.2 mm PTH (5.5 mm pad), spaced 62.50 +/-0.2 mm horizontally and 78.70 +/-0.2 mm vertically, holes 3.26 mm from the left edge and 3.25 mm from the top/bottom (per the drawing; verify against the STEP/DXF before cutting the front panel). TFT glass 50.00 x 69.20 mm, active area 43.20 x 57.60 mm; the active area sits 6.25 mm from the board's left side on the drawing as oriented (see the drawing for the origin; I could not extract a clean dimension chain). Headers are 2.54 mm pitch, P2.54 x 19 = 48.26 mm span. An onboard microSD socket and a J4 6-pin and J3 40-pin FFC footprint are on the back.

The mechanical drawing is an image that I read, but the glass-to-hole offsets above are the ones I am least sure of. I recommend Andrew pull the datasheet drawing into the enclosure model rather than using my transcription.

## 2a. Display, chosen: Elecrow DLS29028B / LCDwiki MSP2834 (2.8" IPS SPI, capacitive touch; D-048)

The notes below were written for the no-touch MSP2833 and apply to its touch twin, with the differences in the last two bullets.

Checked 2026-10-29 against the LCDwiki EN user manual, the CN spec and the MSP2833 outline drawing ([wiki](https://lcdwiki.com/2.8inch_IPS_SPI_Module_ILI9341), [files](https://www.lcdwiki.com/res/MSP2833_MSP2834)).

- **IPS is stated in the spec and on the drawing** ("Panel Type IPS", "DISPLAY TYPE: 2.8\" IPS TFT"). That's the bar the generic listings failed. The controller is the **ILI9341V, not ST7789**. I found no 2.8" ST7789 generic with an IPS datasheet. ESP-IDF's `esp_lcd_ili9341` and LVGL both cover the ILI9341V, so the firmware cost is nil.
- **Header: 1×14, 2.54 mm.** 1 VCC, 2 GND, 3 LCD_CS, 4 LCD_RST, 5 LCD_RS (D/C), 6 SDI/MOSI, 7 SCK, 8 LED, 9 SDO/MISO, 10–13 CTP_SCL/RST/SDA/INT (NC on the MSP2833), 14 SD_CS. Pins 1–8 match the current J6 order, so J6 becomes a 1×14 socket with 9–14 NC, and the extra pins add mechanical support.
- **Power.** "Working Voltage 5.0 V", 0.4 W, backlight 80 mA (4 white LEDs). The on-board LDO makes 3.3 V. The manual says to feed it 5 V: at 3.3 V the backlight dims. It has an on-board level converter, so 3.3 V logic is fine. **So J6 VCC moves to +5V**, which also takes ≈ 80–100 mA off the buck.
- **Backlight.** The LED pin goes through a BSS138 with a pull-up. Floating or high turns it on and low turns it off, and the manual describes PWM dimming on this pin. The AO3401A high-side backlight switch is gone (D-048), with GPIO47 driving LED directly. O-6 still matters: if GPIO47 turned out to be 1.8 V, a push-pull high would hold the BSS138 gate at 1.8 V against its 3.3 V pull-up, close to the 1.5 V max threshold, so the backlight might come up dim. Driving the pin open-drain avoids this (`pcb/design.md` §7). Floating at boot gives full on.
- **Outline (MSP2833 drawing, ±0.2).** PCB 50.00 × 86.00 × 1.60. Four holes on a 44.00 × 76.08 pattern, 3.00 from the edges (the hole diameter isn't legible in the text layer; take it from the PDF, likely 3.0 mm). LCD outline 50.00 × 69.20, active area 43.20 × 57.60, header 13 × 2.54 = 33.02 span. Total height with pin header 12.78 mm, or 4.40 mm without. Take the panel-to-hole offsets from the PDF drawing for the bezel, not from this transcription.
- **Touch (MSP2834 schematic and drawing, read 2026-11-09).** FT6336G over I²C, CTP pins 10–13. CTP_SCL and CTP_SDA have 10 k to VCC on the header side through a BSS138 stage, so they idle at 5 V with VCC at 5 V; our board shifts them to 3.3 V (`pcb/design.md` §7). 14.28 mm overall with the pin header (12.78 without touch); 5.90 ± 0.2 from PCB back to glass front.
- **Buying it.** Elecrow DLS29028B, $10.90, in stock (fetched 2026-11-09; [Elecrow](https://elecrow.com/2-8-ips-spi-lcd-capacitive-touch-module-ili9341-driver-240-320-resolution.html)). Module spec, header and outline match the LCDwiki MSP2834, but the Elecrow page doesn't name it, so check the received board against the drawing before committing the bezel. Elecrow shipping isn't in the priced total.

## 3. USB-C wall adapter: Raspberry Pi 15 W USB-C Power Supply, US

- Part: **SC0445** (white, US Type A plug, model KSA-15E-051300HU). SC0218 is the black version of the same supply.
- Datasheet: [Raspberry Pi 15W USB-C Power Supply product brief](https://static.chipdip.ru/lib/036/DOC028036998.pdf), published November 2021 (the copy I could read). Spec: 5.1 V DC, 3.0 A, 15 W, 100-240 Vac, 50/60 Hz, 0.5 A input max, short-circuit/overcurrent/overtemperature protection, no-load 0.075 W max, ripple 120 mVp-p, captive 1.5 m 18 AWG USB-C cable. Operating ambient 0-40 C.
- Source: **Newark** SC0445 (part 03AH7033): $11.12, 1,411 in stock, per a search result today. I didn't open the live Newark page. At DigiKey the SC0445 and SC0218 are "not kept in stock" with a 28-30 week lead time. Farnell Ireland (SC0218, EUR 8.29) and Pi Hut have stock but are not US options.
- **UL listing: not found.** I could not retrieve a UL file number. What I did find:
  - Raspberry Pi's product page says the supply "meets a number of regional and international standards" and points to the [Product Information Portal approvals page](https://pip.raspberrypi.com/categories/503-approvals) for certificates. That portal lists an "rpi-15W-PSU Authorisation of UL mark US Variant" letter (document RP-007966-CF-1, updated 2025-10-06), which should contain the UL report/file number. I could not open the PDF (the URL I guessed returned 404).
  - The sister 27 W supply's UL letter cites UL report E215890-A6054 (UL/CUL 62368-1 Ed.3). That belongs to the 27 W unit and **must not be assumed to cover the 15 W**.
  - The Pi Foundation's own marking on the unit and the downloaded letter are the confirmation. **Andrew should open RP-007966-CF-1 from the portal and record the file number before G4, or check the UL mark on the unit and look up the model on UL Product iQ.**
- Class II, fixed blades, no mains wiring on our side. Needs no cord; the captive USB-C cable plugs straight into the controller or the 2-3 m extension in item 4.
- The 0-40 C ambient rating matters for an unheated shop in winter. The adapter sits indoors at an outlet, but check the shop's winter minimum.

## 4. USB-C to USB-C cable: StarTech USB2C5C2M

- DigiKey: $27.08, 67 in stock (4,670 factory stock), 2-week lead. 2.00 m (6.56 ft), USB 2.0 at 480 Mbps, shielded, black.
- Wire gauge from the DigiKey page: 24 AWG and 26 AWG. This is the best-specified cable I found, with the gauge published. Which pair is which isn't on the DigiKey page; other retailers describe it as 24 AWG for the power pair and thinner for data (an inference, not read from the datasheet). The StarTech [datasheet](https://media.startech.com/cms/pdfs/usb2c5c2m_datasheet.pdf) was not opened.
- DigiKey's page doesn't list a current rating. The model name and retailer listings say 5 A, and the cable is USB-IF certified per resellers, but treat that as unconfirmed until the datasheet is read.
- The user asked for a 2-3 m cable. This is 2 m. StarTech's 3 m version is USB2CC3M, whose spec I haven't checked.
- Price is high for the job; the gauge is the reason for the pick.

## 5. Cable glands and gasket

**Gland: Essentra CG-PG7-2-BK** (DigiKey RPC1898-ND), x3.
- PG7 thread (8.00 mm thread length), cable range 3.00-6.50 mm, IP68, black polyamide. Panel hole 12.7 mm (0.500"). $1.32 each, $1.12 each at qty 10; 5,344 in stock. DigiKey's 31-week standard lead time doesn't matter with stock on hand.
- The page lists contents as "Sealing Gland, Sealing Nut". A separate locknut **CGLN-PG7-BK** shows as a related product. Confirm in the Essentra datasheet whether the sealing nut alone retains the gland in a 12.7 mm hole. If not, add 3 locknuts. RoHS status isn't shown on the page.
- It fits both the 4-conductor and the 2-conductor cable, provided the actual cable OD is 3.0-6.5 mm. Measure the real cables; a 2-conductor cable at 3 mm sits at the bottom of the range and may seal poorly.

**Gasket strip.** Not picked. For the lid, a closed-cell neoprene or EPDM foam strip, adhesive-backed, 1/8" x 1/2", is common as a 50-75 ft roll at about $12-18 (Pres-Bond 75 ft listed at $11.95, 50 ft at $17.99 on a search snippet, not verified). Zoro sells 10 ft strips of closed-cell foam at similar sizes. Neither was checked for current price. The enclosure design (compression gap, groove) should set the thickness before ordering.

## Proposed `bom.csv` rows

`bom.csv` was not found, so the columns below are a guess: `ref,description,mfr,mpn,supplier,supplier_pn,qty,unit_price_usd,stock,lead_time,date_checked,notes,reqs`. The requirement IDs are not given, so that column is blank.

```
OB1,"PM/RH/T/VOC/NOx sensor",Sensirion,SEN65-SIN-T,DigiKey,1649-SEN65-SIN-T-ND,1,29.55,0 (60 exp 2027-01-20),17 wk,2026-10-28,"3.3V supply; 0 stock - check Mouser 403-SEN65-SIN-T",
OB2,"Sensor cable JST GHR-06V-S 6-pin",Sensirion,SEN5X JUMPER 6-PIN JST GHR-06V-S CABLE SET,DigiKey,1649-SEN5XJUMPER6-PINJSTGHR-06V-SCABLESET-ND,1,6.09,572,4 wk,2026-10-28,"length and 1:1 mapping unverified",
OB3,"2.8in 240x320 IPS SPI TFT capacitive touch ILI9341V FT6336G",Elecrow,DLS29028B,Elecrow,DLS29028B,1,10.90,In stock,n/a,2026-11-09,"LCDwiki MSP2834; VCC 5 V",
OB4,"5V USB-C wall adapter 15W UL (file no. TBD)",Raspberry Pi,SC0445,Newark,03AH7033,1,11.12,1411,n/a,2026-10-28,"UL file number not found; DigiKey not stocked",
OB5,"USB-C to USB-C cable 2m USB2.0",StarTech,USB2C5C2M,DigiKey,USB2C5C2M (DigiKey SKU not captured),1,27.08,67,2 wk,2026-10-28,"24/26 AWG",
OB6,"Cable gland PG7 3-6.5mm IP68 nylon",Essentra,CG-PG7-2-BK,DigiKey,RPC1898-ND,3,1.32,5344,31 wk listed,2026-10-28,"locknut CGLN-PG7-BK may be needed",
OB7,"Closed-cell foam gasket strip 1/8x1/2in adhesive",generic,,retailer TBD,,1,~12-18,not checked,,2026-10-28,"typical price only",
```

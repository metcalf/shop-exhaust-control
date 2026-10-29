# PCBA vendor check (qty 2-5, 2-layer ~100x70 mm, ESP32-S3-WROOM-1-N16R8)

Checked 2026-10-28. Fees are from JLCPCB's help pages as fetched that day (USD, converted figures like $8.18). Re-quote in the JLCPCB order page before G4.

## 1. JLCPCB Economic vs Standard

| Item | Economic | Standard |
|---|---|---|
| Sides placed | Single side only (SMT/THT) | Single or double |
| THT | Wave-soldered, or hand-soldered if part marked "wave soldering" in library | Same |
| Setup fee | $8.18 | $25.56 one side / $51.12 two |
| Stencil | $1.53 | $8.21 one side / $16.42 two |
| Extended-part fee | $3.07 per Extended item | $1.53 per Basic/Extended item (feeder loading) |
| Preferred-extended | Fee-exempt on Economic (FAQ). Not stated for Standard | Not stated as exempt |
| Hand-solder labor | $3.58 per order (+ ~$0.017/joint) | same |
| SMT | $0.0016/joint | $0.0016/joint, tiered down |
| Qty | 2-50 | 2-80,000 |
| Board size | 10x10 to 470x500 mm | 70x70 to 460x500 mm (ours, 100x70, is OK but near the 70 mm floor) |
| Thickness | 0.8-1.6 mm | No limit listed |
| Layers / stackup | 2/4/6, standard stackup only | 1-32, any |
| Min package / pitch | 0402, 0.4 mm | 01005, 0.35 mm |
| Other | Panels need mouse-bites; 1-3 day build | 4+ day build; SPI inspection |

Caveats: "per unique part" is implied by "per item" but the pages don't say so explicitly. The capabilities page lists reflow as 255 C (Economic) and 240 C (Standard); the extraction was terse, so treat the numbers as unconfirmed. A handling fee applies if Economic vs Standard price differs by under $14.93.

Sources: https://jlcpcb.com/help/article/pcb-assembly-price , https://jlcpcb.com/capabilities/pcb-assembly-capabilities , https://jlcpcb.com/help/article/98-pcb-assembly-faqs

## 2. ESP32 module on Economic

**Our exact module is Standard Only.** JLCPCB's part page for C2913202 (ESP32-S3-WROOM-1-N16R8, Extended) shows PCBA type "Standard Only": https://jlcpcb.com/partdetail/3198300-ESP32_S3_WROOM_1N16R8/C2913202

- Forum claim in `fan-pwm-thread.md`: **confirmed as to outcome, but the mechanism is unconfirmed.** JLCPCB's own pages don't state a reason (reflow profile or otherwise); the help center and capabilities pages never mention modules. What is verifiable is the per-part "Standard Only" flag.
- It is per part, not a blanket module ban: ESP32-C3-WROOM-02-N4 is listed "Economic and Standard" (https://jlcpcb.com/partdetail/C3013923), and third-party reports say ESP32-SOLO-1C is Economic-eligible while many other ESP32 modules are not (https://techoverflow.net/2024/04/10/jlcpcb-pcb-assembly-list-of-known-standard-only-parts/). Reports on S3-MINI-1 conflict, so check each part.
- Third-party hypothesis (unverified): module datasheet reflow peak is 235-250 C vs the chip's 260 C.
- Economic is single-side only, so a Standard order with the module on one side is the same sides count.

## 3. PCBWay comparison

| | JLCPCB | PCBWay |
|---|---|---|
| Parts model | Their library (LCSC) or consigned | Turnkey (they source, quote-based) or consigned |
| Quote | Instant | 1-2 business days, manual |
| Setup | $8-26 (above) | ~$88-150 per a secondary blog; not on an official page |
| Part markup | LCSC price + load fee | 10-30%+ over distributor (forum: up to 300%) |
| Est. cost, this board, qty 5 | ~$100-170 total (below) | Likely $250+ with setup alone near $90-150 |

PCBWay figures are third-party and unverified (no official price list found): https://pamfinds.pages.dev/guides/best-pcb-assembly-services/ , https://anypcba.com/decoding-pcbway-assembly-cost-a-comprehensive-guide/ . A real PCBWay quote is needed for a firm number.

## 4. Recommendation

Use JLCPCB **Standard PCBA, single-side** (all SMT plus module on the top; screw terminals on the same side). Economic is unavailable for this module, and it is not worth switching modules just to save about $17 in setup. Rough cost for 5 boards (estimate, not a quote): setup $25.56 + stencil $8.21 + hand-solder $3.58 + ~10-12 unique parts x $1.53 (~$15-18) = ~$55 of assembly fees; components ~$60-80 for 5 (module is the bulk); bare PCBs ~$8-15; shipping ~$15-30. Total ~$150-180, roughly half of NFR-08's $300 ceiling. Prefer Basic parts to trim the per-part fees. Fallback if cost matters: order Economic without the module and hotplate-reflow the module yourself (saves ~$20 net, adds a manual step and risk). PCBWay offers no apparent advantage at this quantity.

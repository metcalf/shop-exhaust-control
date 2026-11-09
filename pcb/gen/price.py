"""Priced on-board parts list from pcb/reports/bom-raw.csv + sourced prices (sourcing/*.md, 2026-10-28).

Prints a markdown table and totals for N assembled boards. Run:
  .venv/bin/python pcb/gen/price.py 2 5
"""
import csv
import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "..")

# (value, footprint-substring) -> (LCSC, class, stock, unit $, source)
PRICE = {
    ("120", "R_0603"): ("C22787", "Basic", 669200, 0.0019, "passives"),
    ("200", "R_0603"): ("C8218", "Basic?", 799600, 0.0039, "passives"),
    ("390", "R_0603"): ("C23151", "Basic?", 1845000, 0.0017, "passives"),
    ("1k", "R_0603"): ("C21190", "Basic", 6877400, 0.0017, "passives"),
    ("3.3k", "R_0603"): ("C22978", "Basic", 2987300, 0.0022, "passives"),
    ("4.7k", "R_0603"): ("C23162", "Basic", 3636100, 0.0028, "passives"),
    ("5.1k", "R_0603"): ("C23186", "Basic?", 16428100, 0.0016, "passives"),
    ("10k", "R_0603"): ("C25804", "Basic", 0, 0.0022, "passives (0 LCSC stock; fallback C98220 Ext.)"),
    ("22k", "R_0603"): ("C31850", "Basic", 1837200, 0.0042, "passives"),
    ("47k", "R_0603"): ("C25819", "Basic", 584000, 0.0020, "passives"),
    ("100k", "R_0603"): ("C25803", "Basic", 9309700, 0.0030, "passives"),
    ("2.7k", "R_1206"): ("C17950", "Extended", 38600, 0.0044, "passives"),
    ("22p", "C_0603"): ("C1653", "Basic", 198700, 0.002, "passives (price est.)"),
    ("100n", "C_0603"): ("C14663", "Basic", 42950, 0.0082, "passives"),
    ("1u", "C_0603"): ("C15849", "Basic", 391100, 0.0141, "passives"),
    ("10u", "C_0805"): ("C15850", "Basic?", 1708660, 0.0441, "passives"),
    ("22u", "C_1206"): ("C12891", "Basic?", 138620, 0.1171, "passives"),
    ("SMAJ5.0A", ""): ("C113952", "Extended", 487120, 0.0413, "power"),
    ("SMBJ48CA", ""): ("C693510", "Extended", 4410, 0.0518, "power"),
    ("MB10S", ""): ("C2488", "Basic?", 461500, 0.0272, "isolation"),
    ("RGB CA 3528", ""): ("C601699", "Extended", 14300, 0.1061, "ui-connectors"),
    ("TYPE-C-31-M-12", ""): ("C165948", "Extended", 281585, 0.1886, "power"),
    ("J-FAN", ""): ("C557656", "Extended", 3495, 0.3015, "ui-connectors"),
    ("KF128L-3.5-2P", ""): ("C474930", "Extended", 3000, 0.1571, "ui-connectors"),
    ("SM06B-GHS-TB", ""): ("C133065", "Extended", 25620, 0.3599, "ui-connectors"),
    ("display 1x8", ""): ("C2897371", "Extended", 10272, 0.1547, "ui-connectors"),
    ("2.2u", ""): ("C135262", "Extended", 130370, 0.0537, "power"),
    ("AO3401A", ""): ("C15127", "Basic", 475090, 0.0968, "isolation"),
    ("AO3400A", ""): ("C20917", "Basic", 615350, 0.0897, "passives"),
    ("EC11E18244A5", ""): ("C255515", "Extended", 262, 2.1026, "ui-connectors"),
    ("B1", ""): ("C2845262", "Extended", 1120, 0.0240, "ui-connectors"),
    ("B2", ""): ("C2845262", "Extended", 1120, 0.0240, "ui-connectors"),
    ("B3", ""): ("C2845262", "Extended", 1120, 0.0240, "ui-connectors"),
    ("B4", ""): ("C2845262", "Extended", 1120, 0.0240, "ui-connectors"),
    ("ESP32-S3-WROOM-1-N16R8", ""): ("C2913202", "Extended", 31339, 4.7466, "passives (confirm)"),
    ("USBLC6-2SC6", ""): ("C2827654", "Extended", 103720, 0.0452, "power"),
    ("AP63203WU-7", ""): ("C780769", "Extended", 1337, 1.2115, "LCSC API 2026-11-09 (D-040)"),
    ("H11L1S-TA1-L", ""): ("C7435535", "Extended", 1541, 0.4051, "isolation"),
    ("PC817C-S", ""): ("C3008369", "Extended", 343540, 0.0366, "isolation"),
}
NO_PART = ("TestPoint", "MountingHole")
THT = ("C557656", "C474930", "C2897371", "C255515", "C2845262")

# JLCPCB Standard PCBA fees (sourcing/pcba-vendor.md, 2026-10-28)
SETUP, STENCIL, HAND_SOLDER, PER_UNIQUE = 25.56, 8.21, 3.58, 1.53
PER_SMT_JOINT, PER_THT_JOINT = 0.0016, 0.017
PCB_5PCS, SHIPPING = 10.0, 20.0     # estimates: 2-layer ~100x70 mm, 5 pcs; DHL-class shipping


def main(ns):
    rows = list(csv.DictReader(open(os.path.join(ROOT, "pcb/reports/bom-raw.csv"))))
    lines, missing = {}, []
    for r in rows:
        if any(x in r["Footprint"] for x in NO_PART):
            continue
        key = next((k for k in PRICE if k[0] == r["Value"] and k[1] in r["Footprint"]), None)
        if not key:
            missing.append(r["Value"])
            continue
        lcsc = PRICE[key][0]
        if lcsc in lines:
            lines[lcsc][1] += int(r["QUANTITY"])
            lines[lcsc][2] += "," + r["Reference"]
        else:
            lines[lcsc] = [key, int(r["QUANTITY"]), r["Reference"]]
    print("| LCSC | Value | Class | Qty/board | Unit $ | $/board | Stock (LCSC) | Refs |")
    print("|---|---|---|---|---|---|---|---|")
    per_board = 0.0
    smt_joints = tht_joints = 0
    for lcsc, (key, q, refs) in sorted(lines.items(), key=lambda x: -PRICE[x[1][0]][3] * x[1][1]):
        _l, cls, stock, unit, _src = PRICE[key]
        per_board += unit * q
        pins = 40 if "ESP" in key[0] else (16 if "TYPE-C" in key[0] else 4)
        if lcsc in THT:
            tht_joints += q * pins
        else:
            smt_joints += q * pins
        refs = refs if len(refs) < 40 else refs[:37] + "..."
        print(f"| {lcsc} | {key[0]} | {cls} | {q} | {unit:.4f} | {unit * q:.2f} | {stock:,} | {refs} |")
    uniq = len(lines)
    print(f"\nUnique LCSC parts: {uniq}. Components per board: ${per_board:.2f}. "
          f"Joints/board ≈ {smt_joints} SMT, {tht_joints} THT.")
    if missing:
        print("UNPRICED:", missing)
    for n in ns:
        fees = SETUP + STENCIL + HAND_SOLDER + PER_UNIQUE * uniq
        labor = n * (smt_joints * PER_SMT_JOINT + tht_joints * PER_THT_JOINT)
        total = fees + labor + n * per_board * 1.05 + PCB_5PCS + SHIPPING
        print(f"\n{n} assembled boards: fees ${fees:.2f} + joints ${labor:.2f} + parts ${n * per_board * 1.05:.2f} "
              f"(+5 % attrition) + PCBs ${PCB_5PCS:.2f} + shipping ${SHIPPING:.2f} ≈ **${total:.0f}** "
              f"(${total / n:.0f}/board)")


if __name__ == "__main__":
    main([int(a) for a in sys.argv[1:]] or [2, 5])

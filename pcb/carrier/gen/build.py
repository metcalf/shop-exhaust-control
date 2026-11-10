"""Generates pcb/carrier/carrier.kicad_sch. Run: .venv/bin/python pcb/carrier/gen/build.py

Carrier PCB for the Waveshare ESP32-S3-Touch-LCD-2.8B (D-054, D-055). Source of truth for the
schematic until layout starts. Signals, pins and values: docs/interfaces.md §2, pcb/carrier/DESIGN.md.
Reuses the schematic-as-code layer in pcb/gen (sch.py, route.py).
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "gen"))
import sch  # noqa: E402
from parts import P as OLD  # noqa: E402

sch.PROJECT = "carrier"
Sheet = sch.Sheet

# key -> (lib_id, footprint, LCSC, value, ref prefix). Footprints from the shared project library where
# the old board already checked them against LCSC drawings (pcb/layout/footprints.py).
P = {
    "R0603": OLD["R0603"], "R1206": OLD["R1206"], "C0603": OLD["C0603"], "C0805": OLD["C0805"],
    "PC817": ("Isolator:PC817", "exhaust:SOP-4_LTV-817S_LS10.3", "C109227", "LTV-817S-TA1-C", "U"),
    "BRIDGE": ("Diode_Bridge:MB6S", "exhaust:Bridge_MBS_MB10S", "C2488", "MB10S", "D"),
    "NFET": OLD["NFET"],
    "NFET_LL": OLD["NFET_LL"],
    "LED": ("LED:SK6812", "carrier:LED_SK6812SIDE-A_4.0x1.6mm", "C5378721", "SK6812SIDE-A", "D"),
    # Hand-soldered by Andrew (DNP at JLC, D-054)
    "TERM2": ("Connector:Screw_Terminal_01x02", "exhaust:TerminalBlock_KF128L-3.5-2P", "C474930",
              "KF128L-3.5-2P", "J"),
    "SENCONN": OLD["SENCONN"],
    "HDR": ("Connector_Generic:Conn_02x12_Odd_Even",
            "Connector_PinSocket_2.54mm:PinSocket_2x12_P2.54mm_Vertical", "", "Waveshare J7 2x12 socket", "J"),
    "TP": OLD["TP"],
}
N_LED = 6   # set by mech (diffuser length); 4-8 expected (D-055)

OUT = os.path.join(HERE, "..", "carrier.kicad_sch")
sh = Sheet("Shop exhaust carrier v1 (Waveshare 2.8B)")
_n = {}
RESERVED = {"J1", "J2", "J3", "J5", "J7", "U1", "U2", "U3", "Q1"}   # designators named in docs


def ref(prefix):
    while True:
        _n[prefix] = _n.get(prefix, 0) + 1
        r = f"{prefix}{_n[prefix]}"
        if r not in RESERVED:
            return r


def part(key, at, nets, value=None, rot=0, nc=(), r=None, dnp=False):
    lib_id, fp, lcsc, default_value, prefix = P[key]
    return sh.place(r or ref(prefix), lib_id, value or default_value, at, nets, footprint=fp,
                    lcsc=lcsc, rot=rot, nc=nc, dnp=dnp)


def res(value, at, a, b, key="R0603", rot=0, dnp=False):
    return part(key, at, {"1": a, "2": b}, value=value, rot=rot, dnp=dnp)


def cap(value, at, a, b, key="C0603", rot=0):
    return part(key, at, {"1": a, "2": b}, value=value, rot=rot)


def flag(net, at):
    sh.place(ref("#FLG"), "power:PWR_FLAG", "PWR_FLAG", at, {"1": net})


# ---------------------------------------------------------------- Waveshare header
# Waveshare J7 numbering (vendor schematic, docs/interfaces.md §2). Odd/even = the two rows.
J1 = {1: "+5V", 2: "+5V", 5: "GND", 6: "GND", 11: "IND_DATA", 13: "OCC_IN", 17: "SEN_SCL",
      18: "FAN_TACH", 19: "SEN_SDA", 20: "FAN_PWM", 21: "+3V3", 22: "+3V3", 23: "GND", 24: "GND"}
J1_NC = (3, 4, 7, 8, 9, 10, 12, 14, 15, 16)   # VCC, BAT, USB D-/D+, PSRAM GPIO33-37, GPIO16 (touch INT)
sh.begin("hdr")
X, Y = 40, 50
sh.note("J1: WAVESHARE ESP32-S3-Touch-LCD-2.8B J7 (2x12, 2.54 mm). 11 GPIO0, 13 GPIO4 (R24 lifted), "
        "17/19 I2C SCL/SDA (GPIO7/15), 18 GPIO43, 20 GPIO44", (X - 20, Y - 25))
sh.note("Hand-soldered. Stack-up mirrors the pin rows: check against the Waveshare STEP at layout.",
        (X - 20, Y - 20), size=1.27)
part("HDR", (X, Y), {str(k): v for k, v in J1.items()}, nc=[str(k) for k in J1_NC], r="J1", dnp=True)
flag("+5V", (X + 30, Y - 15))
flag("+3V3", (X + 40, Y - 15))
flag("GND", (X + 50, Y - 15))
for i, n in enumerate(["GND", "+3V3", "+5V", "FAN_PWM", "FAN_TACH", "OCC_IN", "IND_DRV"]):
    part("TP", (X + 30 + 8 * i, Y + 25), {"1": n}, value=n)

# ---------------------------------------------------------------- fan interface (fan domain)
sh.begin("fan")
X, Y = 40, 130
sh.note("FAN INTERFACE - FAN DOMAIN (GND_F). Fail-off, isolated (SR-08, SR-09, D-023, D-054; "
        "interfaces §2.1). >= 3 mm to node copper (pcb/SAFETY.md)", (X - 10, Y - 15))
part("TERM2", (X, Y + 5), {"1": "GND_F", "2": "+10V_F"}, r="J2", dnp=True)
part("TERM2", (X, Y + 25), {"1": "FAN_SPD", "2": "FAN_TACH_F"}, r="J7", dnp=True)
sh.note("J-FAN = J2 + J7: J2.1 GND (BLK), J2.2 +10V (RED), J7.1 SPD (YEL), J7.2 TACH (WHT)",
        (X - 10, Y + 45), size=1.27)
flag("GND_F", (X - 5, Y + 35))
flag("+10V_F", (X + 5, Y))
cap("1u", (X + 45, Y + 18), "+10V_F", "GND_F")   # 0603 1 uF is 50 V
# PWM: Q1 holds yellow low (fan off) unless U1's LED is lit
res("390", (X + 75, Y - 5), "FAN_PWM", "FAN_LED_A")
res("10k", (X + 75, Y + 30), "FAN_PWM", "GND")
part("PC817", (X + 100, Y + 10), {"1": "FAN_LED_A", "2": "GND", "3": "GND_F", "4": "Q_FAN_G"}, r="U1")
res("2.2k", (X + 120, Y - 5), "+10V_F", "Q_FAN_G")
part("NFET_LL", (X + 135, Y + 15), {"G": "Q_FAN_G", "D": "FAN_SPD", "S": "GND_F"}, r="Q1")
# Tach: white low -> LED lit -> FAN_TACH low
res("10k", (X + 165, Y - 5), "+10V_F", "TACH_LED_A")
part("PC817", (X + 180, Y + 10), {"1": "TACH_LED_A", "2": "FAN_TACH_F", "3": "GND", "4": "FAN_TACH"}, r="U2")
res("22k", (X + 195, Y - 5), "+3V3", "FAN_TACH")

# ---------------------------------------------------------------- 24 VAC occupancy (OCC field domain)
sh.begin("J3")
X, Y = 40, 210
sh.note("J-OCC: 24 VAC lighting signal (FR-07, interfaces §2.2) - OCC field domain", (X - 10, Y - 15))
part("TERM2", (X, Y + 10), {"1": "OCC_A", "2": "OCC_B"}, r="J3", dnp=True)
res("10k", (X + 35, Y + 5), "OCC_A", "OCC_AC", key="R1206", rot=90)
part("BRIDGE", (X + 65, Y + 15), {"1": "OCC_AC", "2": "OCC_B", "3": "OCC_P", "4": "OCC_N"})
part("PC817", (X + 90, Y + 15), {"1": "OCC_P", "2": "OCC_N", "3": "GND", "4": "OCC_IN"}, r="U3")
res("47k", (X + 110, Y), "+3V3", "OCC_IN")
cap("1u", (X + 118, Y + 25), "OCC_IN", "GND")

# ---------------------------------------------------------------- SEN65
sh.begin("sen")
X, Y = 200, 210
sh.note("SEN65 (D-012) on +3V3. Shares the Waveshare I2C bus; its pull-ups are on that board, "
        "so ours are DNP pads (D-054)", (X - 10, Y - 15))
cap("10u", (X + 30, Y + 20), "+3V3", "GND", key="C0805")
cap("100n", (X + 38, Y + 20), "+3V3", "GND")
res("10k", (X + 55, Y - 5), "+3V3", "SEN_SDA", dnp=True)
res("10k", (X + 63, Y - 5), "+3V3", "SEN_SCL", dnp=True)
part("SENCONN", (X + 85, Y + 10), OLD["SEN_PINOUT"], r="J5", nc=OLD["SEN_NC"], dnp=True)

# ---------------------------------------------------------------- indicator
sh.begin("ind")
X, Y = 40, 290
sh.note(f"INDICATOR: {N_LED} x SK6812SIDE-A on the carrier's room-side edge (D-055, FR-15). GPIO0 -> "
        "2N7002 inverter (RMT invert_out). 10k gate pull-up keeps GPIO0 high at reset (normal boot) "
        "and DIN low. Firmware caps LED current at 300 mA", (X - 10, Y - 15))
res("10k", (X, Y), "+3V3", "IND_DATA")
part("NFET", (X + 15, Y + 15), {"G": "IND_DATA", "D": "IND_DRV", "S": "GND"})
res("1k", (X + 30, Y), "+5V", "IND_DRV")
res("470", (X + 45, Y + 10), "IND_DRV", "LED_D1", rot=90)   # datasheet §14: ~500 ohm series at DIN
cap("1u", (X + 30, Y + 35), "+5V", "GND")
for i in range(N_LED):
    nc = ("4",) if i == N_LED - 1 else ()
    nets = {"1": "GND", "2": f"LED_D{i + 1}", "3": "+5V"}
    if i < N_LED - 1:
        nets["4"] = f"LED_D{i + 2}"
    part("LED", (X + 70 + 25 * i, Y + 15), nets, nc=nc)
    cap("100n", (X + 70 + 25 * i, Y + 35), "+5V", "GND")

# ---------------------------------------------------------------- mechanical
sh.begin("mech")
for i in range(4):
    sh.place(ref("H"), "Mechanical:MountingHole", "M2", (230 + 15 * i, 60), {},
             footprint="MountingHole:MountingHole_2.2mm_M2")

sh.write(OUT)
print("wrote", os.path.normpath(OUT), len(sh.parts), "symbols")

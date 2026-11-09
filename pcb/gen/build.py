"""Generates pcb/exhaust.kicad_sch. Run: .venv/bin/python pcb/gen/build.py

Source of truth for the schematic until layout starts (D-035). Values and the
reasoning behind them: pcb/design.md. Signals and GPIOs: docs/interfaces.md §2-3.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from parts import P  # noqa: E402
from sch import Sheet  # noqa: E402

OUT = os.path.join(os.path.dirname(__file__), "..", "exhaust.kicad_sch")
sh = Sheet("Shop exhaust controller v1")
_n = {}
# Fixed designators for parts named in docs/interfaces.md; the counter skips them.
RESERVED = {"J1", "J2", "J3", "J4", "J5", "J6", "U1"}


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


def res(value, at, a, b, key="R0603", rot=0):
    return part(key, at, {"1": a, "2": b}, value=value, rot=rot)


def cap(value, at, a, b, key="C0603", rot=0):
    return part(key, at, {"1": a, "2": b}, value=value, rot=rot)


def flag(net, at):
    sh.place(ref("#FLG"), "power:PWR_FLAG", "PWR_FLAG", at, {"1": net})


# ---------------------------------------------------------------- power in
sh.begin("power_in")
X, Y = 30, 40
sh.note("POWER IN  (D-030: 5 V USB-C, power + native USB flash/log)", (X, Y - 15))
part("USBC", (X, Y + 25), {"VBUS": "VBUS_RAW", "GND": "GND", "SHIELD": "GND", "CC1": "CC1",
                           "CC2": "CC2", "D+": "USB_DP", "D-": "USB_DN"},
     nc=("SBU1", "SBU2"), r="J1")
res("5.1k", (X + 30, Y + 30), "CC1", "GND")
res("5.1k", (X + 38, Y + 30), "CC2", "GND")
part("PTC", (X + 35, Y + 5), {"1": "VBUS_RAW", "2": "+5V"}, r="F1")
part("TVS5", (X + 50, Y + 12), {"1": "GND", "2": "+5V"}, rot=90)
part("ESD", (X + 65, Y + 30), {"I/O1": "USB_DP", "I/O2": "USB_DN", "VBUS": "+5V", "GND": "GND"})
cap("10u", (X + 60, Y + 12), "+5V", "GND", key="C0805")
flag("VBUS_RAW", (X + 30, Y))
flag("GND", (X + 45, Y + 50))

# 5 V -> 3.3 V
sh.begin("reg33")
X, Y = 30, 115
sh.note("3.3 V REGULATOR (pcb/design.md §1)", (X, Y - 10))
part("REG33", (X + 20, Y + 5), P["REG33_NETS"], nc=P["REG33_NC"])
for i, (k, a, b) in enumerate(P["REG33_EXTRAS"]):
    if k.startswith("C"):
        cap(a, (X + 45 + 9 * i, Y + 15), *b, key=k)
    elif k.startswith("R"):
        res(a, (X + 45 + 9 * i, Y + 15), *b, key=k)
    else:
        part(k, (X + 45 + 9 * i, Y + 15), {"1": b[0], "2": b[1]}, value=a)
flag("+3V3", (X + 45, Y))   # buck output reaches +3V3 through the (passive) inductor

# ---------------------------------------------------------------- MCU
sh.begin("mcu")
X, Y = 175, 70
sh.note("ESP32-S3-WROOM-1-N16R8 (D-022). GPIO plan: docs/interfaces.md §2", (X - 25, Y - 40))
part("ESP", (X, Y), {
    "GND": "GND", "3V3": "+3V3", "EN": "EN",
    "IO0": "BOOT", "IO1": "DC_IN",
    "IO4": "FAN_PWM", "IO5": "FAN_TACH", "IO6": "FAN_PRESENT", "IO7": "OCC_IN",
    "IO8": "SEN_SDA", "IO9": "SEN_SCL", "IO10": "SEN_PWR_EN",
    "IO11": "DISP_MOSI", "IO12": "DISP_SCLK", "IO13": "DISP_CS", "IO14": "DISP_DC",
    "IO21": "DISP_RST", "IO47": "DISP_BL",
    "IO15": "ENC_A", "IO16": "ENC_B", "IO17": "ENC_SW",
    "IO18": "BTN1", "IO38": "BTN2", "IO39": "BTN3", "IO40": "BTN4",
    "IO48": "IND_R_G", "IO41": "IND_G_G", "IO42": "IND_B_G",
    "USB_D+": "USB_DP", "USB_D-": "USB_DN", "TXD0": "TXD0", "RXD0": "RXD0",
}, nc=("IO2", "IO3", "IO45", "IO46", "IO35", "IO36", "IO37"), r="U1")
cap("10u", (X + 30, Y - 30), "+3V3", "GND", key="C0805")
cap("100n", (X + 38, Y - 30), "+3V3", "GND")
# EN RC per the Espressif hardware design guide; BOOT and EN switches (G2 review S-14)
res("10k", (X - 45, Y - 30), "+3V3", "EN")
cap("1u", (X - 37, Y - 30), "EN", "GND")
part("TACT_SMD", (X - 45, Y - 15), {"1": "EN", "2": "GND"}, value="EN")
res("10k", (X - 25, Y - 30), "+3V3", "BOOT")
part("TACT_SMD", (X - 25, Y - 15), {"1": "BOOT", "2": "GND"}, value="BOOT")
for i, n in enumerate(["+3V3", "GND", "TXD0", "RXD0", "+5V", "EN", "BOOT"]):
    part("TP", (X - 40 + 8 * i, Y + 45), {"1": n}, value=n)
flag("+5V", (X + 50, Y - 30))

# ---------------------------------------------------------------- fan interface (fan domain)
sh.begin("fan")
X, Y = 40, 200
sh.note("FAN INTERFACE - FAN DOMAIN (GND_F). Fail-off, isolated (SR-08, SR-09, D-023, "
        "interfaces §2.1). >= 3 mm to node copper (pcb/SAFETY.md)", (X - 10, Y - 15))
part("TERM4", (X, Y + 15), {"1": "GND_F", "2": "+10V_F", "3": "FAN_SPD", "4": "FAN_TACH_F"},
     value="J-FAN", r="J2")
sh.note("J-FAN 1 GND (BLK), 2 +10V (RED), 3 SPD (YEL), 4 TACH (WHT)", (X - 10, Y + 45), size=1.27)
flag("GND_F", (X - 5, Y + 35))
flag("+10V_F", (X + 5, Y))
part("TVS15", (X + 20, Y + 35), {"1": "GND_F", "2": "+10V_F"}, rot=90)
part("TVS15", (X + 28, Y + 35), {"1": "GND_F", "2": "FAN_SPD"}, rot=90)
part("TVS15", (X + 36, Y + 35), {"1": "GND_F", "2": "FAN_TACH_F"}, rot=90)
part("LDO5F", (X + 55, Y + 5), {"VIN": "+10V_F", "VOUT": "+5F", "GND": "GND_F"})
cap("1u", (X + 45, Y + 18), "+10V_F", "GND_F")   # 0603 1 uF is 50 V
cap("1u", (X + 68, Y + 18), "+5F", "GND_F")
# PWM: Q-FAN holds yellow low (fan off) unless the opto is lit
part("OPTO_PWM", (X + 100, Y + 10), {"1": "FAN_LED_A", "2": "GND", "4": "Q_FAN_G", "5": "GND_F",
                                      "6": "+5F"})
cap("100n", (X + 110, Y + 30), "+5F", "GND_F")
res("10k", (X + 120, Y - 5), "+5F", "Q_FAN_G")
part("NFET_LL", (X + 130, Y + 15), {"G": "Q_FAN_G", "D": "FAN_SPD", "S": "GND_F"})
res("390", (X + 85, Y - 5), "FAN_PWM", "FAN_LED_A")
res("10k", (X + 85, Y + 30), "FAN_PWM", "GND")
# Tach: white low -> LED lit -> FAN_TACH low
res("10k", (X + 150, Y - 5), "+5F", "FAN_TACH_F")
res("3.3k", (X + 160, Y - 5), "+5F", "TACH_LED_A")
part("PC817", (X + 175, Y + 10), {"1": "TACH_LED_A", "2": "TACH_LED_K", "3": "GND", "4": "FAN_TACH"})
part("D_SIG", (X + 160, Y + 30), {"A": "TACH_LED_K", "K": "FAN_TACH_F"})
res("22k", (X + 190, Y - 5), "+3V3", "FAN_TACH")
# Presence: fan side powered -> LED lit -> FAN_PRESENT low
res("4.7k", (X + 210, Y - 5), "+5F", "PRES_LED_A")
part("PC817", (X + 225, Y + 10), {"1": "PRES_LED_A", "2": "GND_F", "3": "GND", "4": "FAN_PRESENT"})
res("22k", (X + 240, Y - 5), "+3V3", "FAN_PRESENT")

# ---------------------------------------------------------------- 24 VAC / DC inputs (field domains)
def ac_input(X, Y, term, a, b, mid, out, title):
    sh.begin(term)
    sh.note(title, (X - 10, Y - 15))
    part("TERM2", (X, Y + 10), {"1": a, "2": b}, r=term)
    part("TVS48", (X + 15, Y + 20), {"1": a, "2": b}, rot=90)
    res("2.7k", (X + 30, Y + 5), a, mid + "_R", key="R1206", rot=90)
    res("2.7k", (X + 45, Y + 5), mid + "_R", mid + "_AC", key="R1206", rot=90)
    part("BRIDGE", (X + 65, Y + 15), {"1": mid + "_AC", "2": b, "3": mid + "_P", "4": mid + "_N"})
    part("PC817", (X + 90, Y + 15), {"1": mid + "_P", "2": mid + "_N", "3": "GND", "4": out})
    res("47k", (X + 110, Y), "+3V3", out)
    cap("1u", (X + 118, Y + 25), out, "GND")


ac_input(40, 270, "J3", "OCC_A", "OCC_B", "OCC", "OCC_IN",
         "J-OCC: 24 VAC lighting signal (FR-07, interfaces §2.2) - OCC field domain")
ac_input(200, 270, "J4", "DCI_A", "DCI_B", "DCI", "DC_IN",
         "J-DC: wired DC_RUNNING, 12-24 V AC/DC either polarity (IR-01, D-025) - DC field domain")

# ---------------------------------------------------------------- SEN65
sh.begin("sen")
X, Y = 300, 40
sh.note("SEN65 (D-012) on a switched rail: recovery power-cycle only (D-031, S-13)", (X - 10, Y - 15))
part("PFET", (X + 15, Y + 5), {"S": "+3V3", "D": "+3V3_SEN", "G": "SEN_G"})
res("100k", (X, Y - 5), "+3V3", "SEN_G")
res("10k", (X, Y + 15), "SEN_PWR_EN", "SEN_G")
cap("100n", (X + 8, Y + 15), "SEN_G", "+3V3")          # soft start: ~1 ms gate ramp, inrush ~30 mA
cap("10u", (X + 30, Y + 20), "+3V3_SEN", "GND", key="C0805")
cap("100n", (X + 38, Y + 20), "+3V3_SEN", "GND")
res("10k", (X + 46, Y + 20), "+3V3_SEN", "GND")          # bleed: rail < 0.3 V within ~0.3 s
res("10k", (X + 55, Y - 5), "+3V3_SEN", "SEN_SDA")
res("10k", (X + 63, Y - 5), "+3V3_SEN", "SEN_SCL")
part("SENCONN", (X + 85, Y + 10), P["SEN_PINOUT"], r="J5", nc=P["SEN_NC"])

# ---------------------------------------------------------------- display
sh.begin("disp")
X, Y = 300, 110
sh.note("DISPLAY: 2.8in 240x320 IPS SPI module, no touch (D-022). Header pinout set by the "
        "chosen module", (X - 10, Y - 15))
part("DISP_HDR", (X + 70, Y + 10), {"Pin_1": "+3V3", "Pin_2": "GND", "Pin_3": "DISP_CS",
                                    "Pin_4": "DISP_RST", "Pin_5": "DISP_DC", "Pin_6": "DISP_MOSI",
                                    "Pin_7": "DISP_SCLK", "Pin_8": "DISP_LED"}, r="J6")
part("PFET", (X + 25, Y + 5), {"S": "+3V3", "D": "DISP_LED", "G": "DISP_BL"})
res("100k", (X + 10, Y - 5), "+3V3", "DISP_BL")
cap("10u", (X + 45, Y + 25), "+3V3", "GND", key="C0805")

# ---------------------------------------------------------------- controls
sh.begin("controls")
X, Y = 300, 165
sh.note("CONTROLS: EC11 encoder + 4 buttons (D-009). 10k pull-up, 100 nF at the pin", (X - 10, Y - 15))
part("ENC", (X, Y + 10), {"A": "ENC_A", "B": "ENC_B", "C": "GND", "S1": "ENC_SW", "S2": "GND"},
     )
for i, n in enumerate(["ENC_A", "ENC_B", "ENC_SW", "BTN1", "BTN2", "BTN3", "BTN4"]):
    res("10k", (X + 25 + 9 * i, Y - 5), "+3V3", n)
    cap("100n", (X + 25 + 9 * i, Y + 25), n, "GND")
for i, n in enumerate(["BTN1", "BTN2", "BTN3", "BTN4"]):
    part("TACT", (X + 30 + 22 * i, Y + 50), {"1": n, "2": "GND"}, value=f"B{i + 1}")

# ---------------------------------------------------------------- indicator
sh.begin("ind")
X, Y = 40, 360
N_LED = 6
sh.note(f"INDICATOR: {N_LED} plain RGB LEDs, common anode on +5V, low-side FET per colour "
        "(D-031, FR-15). Firmware caps total current at 300 mA", (X - 10, Y - 15))
for i in range(N_LED):
    part("RGB", (X + 30 * i, Y + 10), {"A": "+5V", "RK": f"L{i + 1}_R", "GK": f"L{i + 1}_G",
                                        "BK": f"L{i + 1}_B"})
    res(P["R_RED"], (X + 30 * i + 12, Y + 30), f"L{i + 1}_R", "IND_R", rot=90)
    res(P["R_GB"], (X + 30 * i + 12, Y + 38), f"L{i + 1}_G", "IND_G", rot=90)
    res(P["R_GB"], (X + 30 * i + 12, Y + 46), f"L{i + 1}_B", "IND_B", rot=90)
for i, c in enumerate("RGB"):
    part("NFET_LL", (X + 200 + 25 * i, Y + 15), {"G": f"IND_{c}_G", "D": f"IND_{c}", "S": "GND"})
    res("100k", (X + 190 + 25 * i, Y + 30), f"IND_{c}_G", "GND")

# ---------------------------------------------------------------- mechanical
sh.begin("mech")
for i in range(4):
    sh.place(ref("H"), "Mechanical:MountingHole", "M3", (300 + 15 * i, 380), {},
             footprint="MountingHole:MountingHole_3.2mm_M3")

sh.write(OUT)
print("wrote", os.path.normpath(OUT), len(sh.parts), "symbols")

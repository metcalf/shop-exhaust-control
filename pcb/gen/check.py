"""Netlist assertions for the schematic (D-010). Run via pcb/gen/run.sh.

Parses the KiCad netlist exported by kicad-cli and checks the properties that the
design depends on: isolation domains, fail-safe default states, GPIO assignments
and that every placed part has a footprint. Exit status != 0 on any failure.
"""
import re
import sys
from collections import defaultdict

net_text = open(sys.argv[1]).read()

comps = {}
for m in re.finditer(r'\(comp\s+\(ref "([^"]+)"\)(.*?)\n\t\t\)', net_text, re.S):
    body = m.group(2)
    val = re.search(r'\(value "([^"]*)"\)', body)
    fp = re.search(r'\(footprint "([^"]*)"\)', body)
    lcsc = re.search(r'\(name "LCSC"\)\s*"([^"]*)"', body)
    comps[m.group(1)] = dict(value=val and val.group(1), fp=fp and fp.group(1),
                             lcsc=lcsc and lcsc.group(1))

nets = {}
pin_net = {}
for m in re.finditer(r'\(net\s+\(code "\d+"\)\s+\(name "([^"]+)"\)(.*?)\n\t\t\)', net_text, re.S):
    name = m.group(1).lstrip("/")
    nodes = re.findall(r'\(node\s+\(ref "([^"]+)"\)\s+\(pin "([^"]+)"\)', m.group(2))
    nets[name] = nodes
    for r, p in nodes:
        pin_net[(r, p)] = name

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def refs_on(net):
    return {r for r, _ in nets.get(net, [])}


def net_of(ref, pin):
    return pin_net.get((ref, str(pin)))


# --- every part has a footprint ------------------------------------------------
for r, c in comps.items():
    check(c["fp"], f"{r}: no footprint")

# --- isolation domains (pcb/SAFETY.md) ------------------------------------------
# Parts may touch nets of only one domain, except the barrier parts listed below,
# which must touch exactly two (LED side and output side).
DOMAIN_ROOTS = {
    "fan": {"GND_F", "+10V_F", "FAN_SPD", "FAN_TACH_F", "Q_FAN_G", "TACH_LED_A",
            "PRES_LED_A"},
    "occ": {"OCC_A", "OCC_B", "OCC_R", "OCC_AC", "OCC_P", "OCC_N"},
    "dci": {"DCI_A", "DCI_B", "DCI_R", "DCI_AC", "DCI_P", "DCI_N"},
}


def domain(net):
    for d, s in DOMAIN_ROOTS.items():
        if net in s:
            return d
    if net is None or net.startswith("unconnected-"):
        return None
    return "node"


part_domains = defaultdict(set)
for (r, p), n in pin_net.items():
    d = domain(n)
    if d:
        part_domains[r].add(d)

barrier = {r for r, ds in part_domains.items() if len(ds) > 1}
for r in barrier:
    check(comps[r]["value"] in ("H11L1S-TA1-L", "LTV-817S-TA1-C"),
          f"{r} ({comps[r]['value']}) bridges domains {sorted(part_domains[r])}")
    check(len(part_domains[r]) == 2, f"{r} touches {sorted(part_domains[r])}")
# exactly the four optos cross (U-PWM, tach, presence -> fan; OCC; DC)
crossings = sorted((sorted(part_domains[r]), r) for r in barrier)
check(len(barrier) == 5, f"expected 5 barrier parts, got {crossings}")
for d in ("fan", "occ", "dci"):
    check(sum(d in part_domains[r] for r in barrier) >= 1, f"no barrier part for domain {d}")
    for n in DOMAIN_ROOTS[d]:
        check(n in nets, f"domain {d}: net {n} missing")

# opto pin roles: LED on the field side for the inputs, LED on the node side for PWM
for r in barrier:
    v = comps[r]["value"]
    if v == "H11L1S-TA1-L":
        check(domain(net_of(r, 1)) == "node" and domain(net_of(r, 2)) == "node", f"{r}: LED not node-side")
        check(domain(net_of(r, 4)) == "fan" and net_of(r, 5) == "GND_F" and net_of(r, 6) == "+10V_F",
              f"{r}: output side not fan-powered")
    else:
        check(domain(net_of(r, 3)) == "node" and domain(net_of(r, 4)) == "node",
              f"{r}: transistor not node-side")

# --- fail-off (SR-08): Q_FAN gate pulled up to +10V_F, drain on the speed line --------
qfan = sorted({r for r, _p in pin_net if net_of(r, 3) == "FAN_SPD" and r.startswith("Q")})
check(len(qfan) == 1, "one FET on FAN_SPD")
if qfan:
    q = qfan[0]
    check(net_of(q, 1) == "Q_FAN_G" and net_of(q, 2) == "GND_F", "Q_FAN gate/source")
pullups = [r for r in refs_on("Q_FAN_G") if r.startswith("R")]
check(any({net_of(r, 1), net_of(r, 2)} == {"Q_FAN_G", "+10V_F"} for r in pullups), "Q_FAN gate pull-up to +10V_F")
check(any({net_of(r, 1), net_of(r, 2)} == {"FAN_PWM", "GND"} for r in refs_on("FAN_PWM") if r.startswith("R")),
      "FAN_PWM pull-down (LED dark through reset)")

# --- default-off pulls on the other outputs -------------------------------------
def has_res(a, b):
    return any({net_of(r, 1), net_of(r, 2)} == {a, b} for r in refs_on(a) if r.startswith("R"))


check(has_res("SEN_G", "+3V3"), "SEN P-FET gate pull-up (rail off at boot)")
check(has_res("DISP_BL", "+3V3"), "backlight P-FET gate pull-up")
check(any({net_of(c, 1), net_of(c, 2)} == {"SEN_G", "+3V3"} for c in refs_on("SEN_G") if c.startswith("C")),
      "SEN rail soft-start cap (gate-source)")
for c in "RGB":
    check(has_res(f"IND_{c}_G", "GND"), f"IND_{c} gate pull-down")
check(has_res("SEN_SDA", "+3V3_SEN") and has_res("SEN_SCL", "+3V3_SEN"),
      "I2C pull-ups on the switched rail only (S-13)")
check(not has_res("SEN_SDA", "+3V3") and not has_res("SEN_SCL", "+3V3"), "no I2C pull-up to +3V3")
check(has_res("EN", "+3V3"), "EN pull-up")

# --- GPIO plan (docs/interfaces.md §2) ------------------------------------------
GPIO = {"IO1": "DC_IN", "IO4": "FAN_PWM", "IO5": "FAN_TACH", "IO6": "FAN_PRESENT",
        "IO7": "OCC_IN", "IO8": "SEN_SDA", "IO9": "SEN_SCL", "IO10": "SEN_PWR_EN",
        "IO11": "DISP_MOSI", "IO12": "DISP_SCLK", "IO13": "DISP_CS", "IO14": "DISP_DC", "IO21": "DISP_RST",
        "IO47": "DISP_BL", "IO15": "ENC_A", "IO16": "ENC_B", "IO17": "ENC_SW", "IO18": "BTN1",
        "IO38": "BTN2", "IO39": "BTN3", "IO40": "BTN4", "IO48": "IND_R_G", "IO41": "IND_G_G",
        "IO42": "IND_B_G", "IO0": "BOOT"}
ESP_PIN = {"IO0": 27, "IO1": 39, "IO2": 38, "IO4": 4, "IO5": 5, "IO6": 6, "IO7": 7, "IO8": 12, "IO9": 17,
           "IO10": 18, "IO11": 19, "IO12": 20, "IO13": 21, "IO14": 22, "IO15": 8, "IO16": 9, "IO17": 10,
           "IO18": 11, "IO21": 23, "IO38": 31, "IO39": 32, "IO40": 33, "IO41": 34, "IO42": 35, "IO47": 24,
           "IO48": 25}
for io, n in GPIO.items():
    check(net_of("U1", ESP_PIN[io]) == n, f"U1 {io} should be {n}, is {net_of('U1', ESP_PIN[io])}")
for io_pin in (38, 15, 26, 16, 28, 29, 30):   # IO2 spare (D-039); IO3, IO45, IO46 strapping; IO35-37 octal PSRAM
    check(net_of("U1", io_pin).startswith("unconnected-"), f"U1 pin {io_pin} must be unconnected")

# --- USB input and 3.3 V buck (D-040) -------------------------------------------
UF = {"p": 1e-6, "n": 1e-3, "u": 1.0}


def cap_uf(ref):
    m = re.fullmatch(r"([\d.]+)([pnu])", comps[ref]["value"] or "")
    check(m, f"{ref}: can't read capacitor value {comps[ref]['value']!r}")
    return float(m.group(1)) * UF[m.group(2)] if m else 0.0


check("VBUS_RAW" not in nets and not any(r.startswith("F") for r in comps), "no series fuse on VBUS")
check("J1" in refs_on("+5V"), "J1 VBUS directly on +5V")
vbus_c = sum(cap_uf(r) for r in refs_on("+5V") if r.startswith("C")
             and {net_of(r, 1), net_of(r, 2)} == {"+5V", "GND"})
check(1.0 <= vbus_c <= 10.0, f"+5V capacitance {vbus_c} uF is outside the 1-10 uF non-PD USB sink limit")
buck = [r for r, c in comps.items() if c["value"] == "AP63203WU-7"]
check(len(buck) == 1, "one AP63203")
if buck:
    # TSOT-26: 1 FB, 2 EN, 3 VIN, 4 GND, 5 SW, 6 BST
    for pin, want in ((1, "+3V3"), (2, "+5V"), (3, "+5V"), (4, "GND"), (5, "BUCK_LX"), (6, "BUCK_BST")):
        check(net_of(buck[0], pin) == want, f"{buck[0]} pin {pin} should be {want}, is {net_of(buck[0], pin)}")
check(any({net_of(c, 1), net_of(c, 2)} == {"BUCK_BST", "BUCK_LX"} for c in refs_on("BUCK_BST") if c.startswith("C")),
      "BST cap to SW")

# --- EN/BOOT recovery pads (D-041) ----------------------------------------------
for n in ("EN", "BOOT"):
    check(any(r.startswith("TP") for r in refs_on(n)), f"{n}: no test pad")
    check(not any(r.startswith("SW") for r in refs_on(n)), f"{n}: switch should be pads only")
check(sum(r.startswith("TP") for r in refs_on("GND")) >= 2, "EN and BOOT each need their own GND pad")
for n in ("SEN_SDA", "SEN_SCL"):
    check(any(r.startswith("TP") for r in refs_on(n)), f"{n}: no test pad")

# --- nothing single-ended except intentional no-connects ----------------------
for n, nodes in nets.items():
    if not n.startswith("unconnected-"):
        check(len(nodes) >= 2, f"net {n} has one node")

print(f"{len(comps)} parts, {len(nets)} nets, barrier parts: "
      + ", ".join(f"{r}{sorted(part_domains[r])}" for r in sorted(barrier)))
if fails:
    print("FAIL:")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("all netlist assertions passed")

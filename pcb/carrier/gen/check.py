"""Netlist assertions for the carrier schematic (D-010, D-054). Run via pcb/carrier/gen/run.sh.

Checks what the design depends on: isolation domains, fail-off (SR-08), the Waveshare header map,
GPIO0 strapping safety, the indicator chain and footprints. Exit status != 0 on any failure.
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
    comps[m.group(1)] = dict(value=val and val.group(1), fp=fp and fp.group(1))

nets, pin_net = {}, {}
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


def unconnected(ref, pin):
    n = net_of(ref, pin)
    return n is None or n.startswith("unconnected-")


def has_res(a, b):
    return any({net_of(r, 1), net_of(r, 2)} == {a, b} for r in refs_on(a) if r.startswith("R"))


for r, c in comps.items():
    check(c["fp"], f"{r}: no footprint")

# --- isolation domains (pcb/SAFETY.md, D-050) ------------------------------------
DOMAIN_ROOTS = {
    "fan": {"GND_F", "+10V_F", "FAN_SPD", "FAN_TACH_F", "Q_FAN_G", "TACH_LED_A"},
    "occ": {"OCC_A", "OCC_B", "OCC_AC", "OCC_P", "OCC_N"},
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
    check(comps[r]["value"] == "LTV-817S-TA1-C", f"{r} ({comps[r]['value']}) bridges {sorted(part_domains[r])}")
    check(len(part_domains[r]) == 2, f"{r} touches {sorted(part_domains[r])}")
check(barrier == {"U1", "U2", "U3"}, f"barrier parts should be U1-U3, got {sorted(barrier)}")
for d, roots in DOMAIN_ROOTS.items():
    for n in roots:
        check(n in nets, f"domain {d}: net {n} missing")

# opto roles. LTV-817 (Isolator:PC817): 1 A, 2 K, 3 E, 4 C.
check(domain(net_of("U1", 1)) == "node" and net_of("U1", 2) == "GND", "U1 LED must be node-side, cathode GND")
check(net_of("U1", 4) == "Q_FAN_G" and net_of("U1", 3) == "GND_F", "U1 output must pull Q_FAN_G to GND_F")
for u in ("U2", "U3"):
    check(domain(net_of(u, 1)) != "node" and domain(net_of(u, 2)) != "node", f"{u}: LED must be field-side")
    check(net_of(u, 3) == "GND", f"{u}: emitter must be node GND")
check(net_of("U2", 4) == "FAN_TACH" and net_of("U3", 4) == "OCC_IN", "U2/U3 collectors on FAN_TACH/OCC_IN")

# --- fail-off (SR-08): Q1 on by default from +10V_F, off only while U1 is lit ---------
check(comps.get("Q1", {}).get("value") == "AO3400A", "Q1 is the AO3400A")
check(net_of("Q1", 1) == "Q_FAN_G" and net_of("Q1", 2) == "GND_F" and net_of("Q1", 3) == "FAN_SPD",
      "Q1 G/S/D = Q_FAN_G / GND_F / FAN_SPD")
check(has_res("Q_FAN_G", "+10V_F"), "Q_FAN_G pull-up to +10V_F")
check(has_res("FAN_PWM", "GND"), "FAN_PWM pull-down (U1 dark through reset and boot)")
check(not has_res("FAN_PWM", "+3V3"), "no pull-up on FAN_PWM")
check(refs_on("FAN_SPD") <= {"Q1", "J7"} | {r for r in refs_on("FAN_SPD") if r.startswith("TP")},
      "only Q1 drives FAN_SPD")

# --- Waveshare header J1 (docs/interfaces.md §2) ------------------------------------
J1 = {1: "+5V", 2: "+5V", 5: "GND", 6: "GND", 11: "IND_DATA", 13: "OCC_IN", 17: "SEN_SCL",
      18: "FAN_TACH", 19: "SEN_SDA", 20: "FAN_PWM", 21: "+3V3", 22: "+3V3", 23: "GND", 24: "GND"}
for pin, n in J1.items():
    check(net_of("J1", pin) == n, f"J1 pin {pin} should be {n}, is {net_of('J1', pin)}")
for pin in (3, 4, 7, 8, 9, 10, 12, 14, 15, 16):
    check(unconnected("J1", pin), f"J1 pin {pin} must be unconnected (VCC/BAT/USB/PSRAM/touch INT)")

# --- GPIO0 strapping: must read high at reset ---------------------------------------
check(has_res("IND_DATA", "+3V3"), "GPIO0 (IND_DATA) pull-up to +3V3")
for r in refs_on("IND_DATA"):
    if r.startswith("R"):
        check({net_of(r, 1), net_of(r, 2)} == {"IND_DATA", "+3V3"}, f"{r}: only a pull-up may sit on GPIO0")
    elif r.startswith("Q"):
        check(net_of(r, 1) == "IND_DATA", f"{r}: GPIO0 may only drive a FET gate")
    else:
        check(r in ("J1",) or r.startswith("TP"), f"{r} loads GPIO0")

# --- indicator chain (D-055) --------------------------------------------------------
leds = sorted((r for r, c in comps.items() if c["value"] == "SK6812SIDE-A"), key=lambda r: int(r[1:]))
check(len(leds) >= 4, f"expected >= 4 SK6812SIDE-A, got {len(leds)}")
q = [r for r in refs_on("IND_DRV") if r.startswith("Q")]
check(len(q) == 1 and net_of(q[0], 2) == "GND", "one 2N7002 pulls IND_DRV to GND")
check(has_res("IND_DRV", "+5V"), "IND_DRV pull-up to +5V")
check(has_res("IND_DRV", "LED_D1"), "series resistor into the first DIN")
for i, d in enumerate(leds):     # LED:SK6812: 1 VSS, 2 DIN, 3 VDD, 4 DOUT
    check(net_of(d, 1) == "GND" and net_of(d, 3) == "+5V", f"{d}: supply pins")
    check(net_of(d, 2) == f"LED_D{i + 1}", f"{d}: DIN should be LED_D{i + 1}, is {net_of(d, 2)}")
    if i < len(leds) - 1:
        check(net_of(d, 4) == f"LED_D{i + 2}", f"{d}: DOUT should chain to LED_D{i + 2}")
    else:
        check(unconnected(d, 4), f"{d}: last DOUT unconnected")
n100 = sum(1 for r, c in comps.items() if r.startswith("C") and c["value"] == "100n"
           and {net_of(r, 1), net_of(r, 2)} == {"+5V", "GND"})
check(n100 >= len(leds), f"one 100 nF per LED on +5V ({n100} for {len(leds)})")

# --- SEN65 ---------------------------------------------------------------------------
check(net_of("J5", 1) == "+3V3" and net_of("J5", 6) == "+3V3", "SEN65 VDD on +3V3")
check(net_of("J5", 3) == "SEN_SDA" and net_of("J5", 4) == "SEN_SCL", "SEN65 SDA/SCL")

# --- nothing single-ended -----------------------------------------------------------
for n, nodes in nets.items():
    if not n.startswith("unconnected-"):
        check(len(nodes) >= 2, f"net {n} has one node")

print(f"{len(comps)} parts, {len(nets)} nets, barrier: "
      + ", ".join(f"{r}{sorted(part_domains[r])}" for r in sorted(barrier)))
if fails:
    print("FAIL:")
    for f in fails:
        print("  -", f)
    sys.exit(1)
print("all netlist assertions passed")

"""Scripted, locked placement for the carrier (D-010, D-056, D-057): writes pcb/carrier/carrier-placed.kicad_pcb.

Run via pcb/carrier/layout/run.sh (KiCad's bundled Python). Inputs: the carrier netlist and
mech/out/carrier_layout.json (outline, holes, J8 position, LED edge, keepouts; frame E from the
Waveshare STEP, never retyped). Board coordinates: top-left (0, 0), +x right, +y down, seen from the
front (F.Cu faces the display). x = x_E - carrier_x0, y = carrier_y1 - y_E.

Every position is a layout choice unless it comes from the JSON. Layout rationale: pcb/carrier/LAYOUT.md.
"""
import json
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
CARRIER = os.path.dirname(HERE)
ROOT = os.path.dirname(os.path.dirname(CARRIER))
sys.path.insert(0, os.path.join(ROOT, "pcb", "layout"))
import netlist  # noqa: E402

STOCK = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
LIBS = {"exhaust": os.path.join(ROOT, "pcb", "lib", "exhaust.pretty"),
        "carrier": os.path.join(CARRIER, "lib", "carrier.pretty")}
X0, Y0 = 100.0, 100.0

M = json.load(open(os.path.join(ROOT, "mech", "out", "carrier_layout.json")))
CX0, CX1 = M["carrier_x"]
CY0, CY1 = M["carrier_y"]
W, H = CX1 - CX0, CY1 - CY0


def k(xe, ye):
    """frame E -> board coordinates"""
    return (xe - CX0, CY1 - ye)


# --- J8 header from the STEP -----------------------------------------------------------------
# Rev 2.0 numbering: odd pins on the inner row, even on the outer row, pin 1/2 at the USB-C end.
# PinHeader_2x16 pin 1 is the origin, pin 2 at +x, pin 3 at +y; rotated 90 deg, pin 2 lands above
# pin 1 (-y) and pin 3 to its right (+x). Asserted after placement.
J1_POS = k(M["j8_pin1_x"], M["j8_row_rev2_odd_y"])
PITCH = 2.54 * M["j8_pitch_dir"]


def j8_pin_xy(n):
    col = (n - 1) // 2
    ye = M["j8_row_rev2_odd_y"] if n % 2 else M["j8_row_rev2_even_y"]
    return k(M["j8_pin1_x"] + col * PITCH, ye)


# --- barrier geometry (pcb/SAFETY.md, D-050) -------------------------------------------------------
OPTO_X = 21.0                 # opto centre; field pads at x - 5, node pads at x + 5 (LTV-817S, LS10.3)
BARRIER_X0, BARRIER_X1 = 18.5, 23.5
# Optos in the one column the Waveshare back leaves clear for a 4.0 mm part (Q-48 option b): frame E
# y -8.4 (1.0 mm part below) to +19.69 (J8 socket). 5.6 mm pitch keeps courtyards apart and the field
# pads of adjacent groups 1.56 mm apart (>= 1.5 functional). Checked by mech/tests (part heights).
OPTO_Y0, OPTO_PITCH = 11.55, 5.6
OPTO_Y = [OPTO_Y0 + i * OPTO_PITCH for i in range(5)]
# Terminals inboard, wire entry facing the left wall (Andrew: room to dress the wires). Pin column x is
# as far right as the OCC|DC gap allows: J3 pads | 1.5 mm gap | U5 field pads.
TERM_X = 11.0
# Field-field gaps (>= 1.5 mm functional). fan|OCC runs straight; OCC|DC leaves the opto gap, drops down
# between J3 and U5, and runs out to the left edge between the OCC and DC parts.
_FO = (OPTO_Y[2] + 2.05, OPTO_Y[3] - 2.05)
_OD = (OPTO_Y[3] + 2.05, OPTO_Y[4] - 2.05)
FIELD_GAPS = [
    [(0.0, _FO[0]), (BARRIER_X0, _FO[0]), (BARRIER_X0, _FO[1]), (0.0, _FO[1])],
    [(BARRIER_X0, _OD[0]), (12.4, _OD[0]), (12.4, 40.0), (0.0, 40.0), (0.0, 41.5), (13.9, 41.5),
     (13.9, _OD[1]), (BARRIER_X0, _OD[1])],
]

HOLES = [k(x, y) for x, y in M["holes"]]
# Anchors so groups move with what they serve when the outline changes (D-058 rev 2)
J1X = J1_POS[0]                       # PWRON one-shot sits by J8 pin 23
KF = k(M["keep_flat_back"][0], 0)[0]  # left edge of the SEN65 keep-flat zone
LED_X = W - 1.44 - 0.2        # SK6812SIDE-A body reaches +1.44 from its origin toward the light face
LED_Y = sorted(k(0, y)[1] for y in M["led_y"])

# ref: (x, y, rotation_deg, side)
POS = {
    # Waveshare J8 (male header on the display side)
    "J1": (J1_POS[0], J1_POS[1], 90, "F"),
    # --- field: terminals on the back, inboard, wire entry toward the left wall (ASSUME: KF128L entry side) ---
    "J2": (TERM_X, 10.75, "entry-left", "B"),    # fan GND (BLK) / +10V (RED)
    "J7": (TERM_X, 18.25, "entry-left", "B"),    # fan SPD (YEL) / TACH (WHT)
    "J3": (TERM_X, 29.6, "entry-left", "B"),     # OCC 24 VAC: pads clear the fan|OCC gap
    "J4": (TERM_X, 46.0, "entry-left", "B"),     # DC backup: below the OCC|DC gap, clear of the H1 screw head
    # field parts on the front, left of the terminal pins (USB pocket edge x < 3.6 kept clear)
    # fan island
    "R5": (6.5, 8.6, 90, "F"),       # Q_FAN_G pull-up 2.2k
    "Q1": (6.0, 12.6, 0, "F"),
    "C2": (6.5, 16.6, 90, "F"),
    "R8": (4.0, 16.6, 90, "F"),      # presence LED 10k
    "R6": (6.5, 20.4, 90, "F"),      # tach LED 10k
    # OCC island
    "R10": (7.0, 29.6, 90, "F"),
    "D2": (7.9, 36.9, 0, "F"),
    # DC island
    "D3": (5.0, 45.0, 0, "F"),
    "R12": (15.5, 45.0, 0, "F"),
    # --- barrier optos ---
    "U1": (OPTO_X, OPTO_Y[0], 90, "F"),   # LED on the node side (PWM)
    "U2": (OPTO_X, OPTO_Y[1], 270, "F"),
    "U3": (OPTO_X, OPTO_Y[2], 270, "F"),
    "U4": (OPTO_X, OPTO_Y[3], 270, "F"),
    "U5": (OPTO_X, OPTO_Y[4], 270, "F"),
    # --- node: opto partners ---
    "R3": (30.5, OPTO_Y[0] - 0.6, 0, "F"),   # 390 into U1's LED
    "R4": (30.5, OPTO_Y[0] + 2.0, 0, "F"),   # FAN_PWM pull-down
    "R7": (30.5, OPTO_Y[1], 0, "F"),         # FAN_TACH 22k
    "R9": (30.5, OPTO_Y[2], 0, "F"),         # FAN_PRESENT 22k
    "R11": (30.5, OPTO_Y[3] - 0.8, 0, "F"),
    "C3": (30.5, OPTO_Y[3] + 1.8, 0, "F"),
    "R13": (30.5, OPTO_Y[4] - 0.8, 0, "F"),
    "C4": (30.5, OPTO_Y[4] + 1.8, 0, "F"),
    # --- PWRON one-shot (DNP) near J8 pin 23 ---
    "Q2": (J1X + 27.86, 11.5, 0, "F"),
    "C1": (J1X + 23.86, 11.5, 90, "F"),
    "R1": (J1X + 23.86, 15.0, 90, "F"),
    "R2": (J1X + 25.86, 15.0, 90, "F"),
    "D1": (J1X + 28.36, 15.0, 0, "F"),
    # --- SEN65: connector on the back, left of the keep-flat zone; decoupling on the front ---
    "J5": (KF - 7.1, 18.5, None, "B"),  # rotation chosen below so the plug entry faces the SEN65 (+x)
    "C5": (KF - 9.6, 11.5, 90, "F"),
    "C6": (KF - 7.6, 11.5, 90, "F"),
    "R14": (KF - 4.6, 11.5, 90, "F"),    # DNP pull-up pads
    "R15": (KF - 2.6, 11.5, 90, "F"),
    # --- indicator driver near the first LED ---
    "R16": (W - 12.44, 9.0, 0, "F"),
    "Q3": (W - 8.94, 11.0, 0, "F"),
    "R17": (W - 8.94, 14.5, 0, "F"),
    "R18": (W - 5.44, 9.0, 90, "F"),
    "C7": (W - 7.94, 20.0, 90, "F"),
}
# LEDs down the right edge, light face toward the wall (+x); D4 first in the chain, at the top.
for i, y in enumerate(LED_Y):
    POS[f"D{4 + i}"] = (LED_X, y, 90, "F")
    POS[f"C{8 + i}"] = (W - 4.94, y, 90, "F")
for i, (x, y) in enumerate(HOLES):
    POS[f"H{i + 1}"] = (x, y, 0, "F")
# Test pads on the back, clear of the SEN65 keep-flat zone and the terminals
for i in range(10):
    POS[f"TP{i + 1}"] = (36.0 + 4.0 * (i % 5), 40.0 + 5.0 * (i // 5), 0, "B")

LAYER = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu, "F.SilkS": pcbnew.F_SilkS, "B.SilkS": pcbnew.B_SilkS,
         "F.Fab": pcbnew.F_Fab, "Edge.Cuts": pcbnew.Edge_Cuts, "User.Drawings": pcbnew.Dwgs_User}


def mm(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(X0 + x), pcbnew.FromMM(Y0 + y))


def load_fp(fpid):
    lib, name = fpid.split(":")
    fp = pcbnew.FootprintLoad(LIBS.get(lib, STOCK + lib + ".pretty"), name)
    if fp is None:
        raise SystemExit(f"footprint not found: {fpid}")
    return fp


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def add_rule_area(board, pts, name, layers=("F.Cu", "B.Cu"), no_fp=False):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetZoneName(name)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowZoneFills(True)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(no_fp)
    ls = pcbnew.LSET()
    for l in layers:
        ls.AddLayer(LAYER[l])
    z.SetLayerSet(ls)
    o = z.Outline()
    o.NewOutline()
    for x, y in pts:
        o.Append(mm(x, y))
    board.Add(z)


def add_rect(board, x0, y0, x1, y1, layer, width=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_RECT)
    s.SetStart(mm(x0, y0))
    s.SetEnd(mm(x1, y1))
    s.SetLayer(LAYER[layer])
    s.SetWidth(pcbnew.FromMM(width))
    board.Add(s)


def add_text(board, txt, x, y, layer="F.SilkS", size=0.8, rot=0):
    t = pcbnew.PCB_TEXT(board)
    t.SetText(txt)
    t.SetPosition(mm(x, y))
    t.SetLayer(LAYER[layer])
    t.SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(size), pcbnew.FromMM(size)))
    t.SetTextThickness(pcbnew.FromMM(0.12 if size <= 1.0 else 0.15))
    t.SetTextAngleDegrees(rot)
    if layer.startswith("B."):
        t.SetMirrored(True)
    board.Add(t)


def entry_rotation(fp, want):
    """Rotation that points a side-entry connector's mating face along `want`. The entry is the direction
    from the signal pads toward the mounting tabs (JST GH side entry: tabs at the mating end)."""
    for rot in (0, 90, 180, 270):
        fp.SetOrientationDegrees(rot)
        sig = [p.GetPosition() for p in fp.Pads() if p.GetNumber() != "MP"]
        mp = [p.GetPosition() for p in fp.Pads() if p.GetNumber() == "MP"]
        dx = sum(p.x for p in mp) / len(mp) - sum(p.x for p in sig) / len(sig)
        dy = sum(p.y for p in mp) / len(mp) - sum(p.y for p in sig) / len(sig)
        if dx * want[0] + dy * want[1] > 0 and abs(dx * want[1] - dy * want[0]) < abs(dx * want[0] + dy * want[1]):
            return rot
    raise SystemExit("no rotation points the connector entry the right way")


def terminal_rotation(fp, want):
    """Rotation that points a screw terminal's wire entry along `want`. The KF128L footprint marks the
    wire openings with short silk segments on the entry side (the long ones are the body outline), the
    side the old board pointed at its top wall (pcb/layout/place.py, rotation 180)."""
    for rot in (0, 90, 180, 270):
        fp.SetOrientationDegrees(rot)
        c = fp.GetPosition()
        pts = []
        for g in fp.GraphicalItems():
            if g.GetLayer() in (pcbnew.F_SilkS, pcbnew.B_SilkS) and g.GetShape() == pcbnew.SHAPE_T_SEGMENT:
                a, b = g.GetStart(), g.GetEnd()
                if 0.5 < pcbnew.ToMM(((a.x - b.x) ** 2 + (a.y - b.y) ** 2) ** 0.5) < 2.5:
                    pts.append(((a.x + b.x) / 2 - c.x, (a.y + b.y) / 2 - c.y))
        dx, dy = sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts)
        if dx * want[0] + dy * want[1] > 0 and abs(dx * want[1] - dy * want[0]) < dx * want[0] + dy * want[1]:
            return rot
    raise SystemExit("no rotation points the terminal entry the right way")


def pad_mm(board, ref, pad):
    p = board.FindFootprintByReference(ref).FindPadByNumber(pad).GetPosition()
    return (pcbnew.ToMM(p.x) - X0, pcbnew.ToMM(p.y) - Y0)


def build(net_path, out_path):
    comps, nets = netlist.read(net_path)
    board = pcbnew.BOARD()
    board.SetCopperLayerCount(2)
    netitems = {}
    for name in nets:
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        netitems[name] = ni
    pin_net = {(r, p): n for n, nodes in nets.items() for r, p in nodes}
    missing, extra = sorted(set(comps) - set(POS)), sorted(set(POS) - set(comps))
    if missing or extra:
        raise SystemExit(f"placement table mismatch: missing {missing}, extra {extra}")

    for ref, c in sorted(comps.items()):
        fp = load_fp(c["footprint"])
        fp.SetReference(ref)
        fp.SetValue(c["value"])
        fp.SetFPID(pcbnew.LIB_ID(*c["footprint"].split(":")))
        lcsc = c["fields"].get("LCSC", "")
        if lcsc:
            f = pcbnew.PCB_FIELD(fp, pcbnew.FIELD_T_USER, "LCSC")
            f.SetText(lcsc)
            f.SetVisible(False)
            f.SetLayer(LAYER["F.Fab"])
            fp.Add(f)
        if "dnp" in c["fields"]:
            fp.SetDNP(True)
            fp.SetExcludedFromBOM(False)
        board.Add(fp)
        for pad in fp.Pads():
            n = pin_net.get((ref, pad.GetNumber()))
            if n is not None:
                pad.SetNet(netitems[n])
        x, y, rot, side = POS[ref]
        if side == "B":
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
        fp.SetPosition(mm(x, y))
        if rot is None:
            rot = entry_rotation(fp, (1.0, 0.0))
        elif rot == "entry-left":
            rot = terminal_rotation(fp, (-1.0, 0.0))
        fp.SetOrientationDegrees(rot)
        fp.Reference().SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8)))
        fp.Reference().SetTextThickness(pcbnew.FromMM(0.12))
        fp.SetLocked(True)

    # J8 pins must land on the Waveshare header positions from the STEP
    for n in (1, 2, 3, 23, 31, 32):
        got, want = pad_mm(board, "J1", str(n)), j8_pin_xy(n)
        if abs(got[0] - want[0]) > 0.01 or abs(got[1] - want[1]) > 0.01:
            raise SystemExit(f"J1 pin {n} at {got}, Waveshare J8 at {want}")
    # LEDs: body (light face) must reach toward the right edge
    for i in range(len(LED_Y)):
        bb = board.FindFootprintByReference(f"D{4 + i}").GetBoundingBox(False)
        if pcbnew.ToMM(bb.GetRight()) - X0 < W - 0.6:
            raise SystemExit(f"D{4 + i}: light face not at the right edge")

    # Barrier keepouts: no tracks, vias or pour across the band; field-field gaps
    add_rule_area(board, rect(BARRIER_X0, 0.0, BARRIER_X1, H), "barrier: field-node")
    for i, pts in enumerate(FIELD_GAPS):
        add_rule_area(board, pts, f"gap: field-field {('fan|OCC', 'OCC|DC')[i]}")
    # Back face behind the SEN65 stays flat: no parts on B (Andrew, D-057)
    x0, y0, x1, y1 = M["keep_flat_back"]
    (bx0, by1), (bx1, by0) = k(x0, y0), k(x1, y1)
    add_rule_area(board, rect(bx0, max(by0, 0.0), min(bx1, W), min(by1, H)), "SEN65 keep-flat (B)", ("B.Cu",),
                  no_fp=True)
    # Waveshare camera 1.7 mm above the carrier top: low parts only (mech test checks heights)
    for cx0, cy0, cx1, cy1 in M["tall_part_keepout_front"]:
        (ax, ay), (bx, byy) = k(cx0, cy1), k(cx1, cy0)
        add_rect(board, ax, ay, bx, byy, "User.Drawings", 0.1)
        add_text(board, "Waveshare camera 1.7 mm above: low parts only", (ax + bx) / 2, (ay + byy) / 2, "User.Drawings", 0.8)

    add_rect(board, 0, 0, W, H, "Edge.Cuts", 0.1)
    # Reference outlines for review (User.Drawings, not fabricated)
    (sx, sy), (ex, ey) = k(x0, y1), k(x1, y0)
    add_rect(board, sx, max(sy, 0), min(ex, W), min(ey, H), "User.Drawings", 0.1)
    add_text(board, "SEN65 behind (keep back flat)", (sx + min(ex, W)) / 2, H / 2, "User.Drawings", 1.0, 90)

    labels = {("J2", "1"): "GND BLK", ("J2", "2"): "+10V RED", ("J7", "1"): "SPD YEL", ("J7", "2"): "TACH WHT",
              ("J3", "1"): "OCC", ("J3", "2"): "OCC", ("J4", "1"): "DC", ("J4", "2"): "DC"}
    for (ref, pad), txt in labels.items():
        px, py = pad_mm(board, ref, pad)
        add_text(board, txt, px + 6.0, py, "B.SilkS", 0.8)
    add_text(board, "SEN65", KF - 7.1, 18.5, "B.SilkS", 0.8)
    add_text(board, "FIELD | NODE  >= 3 mm", (BARRIER_X0 + BARRIER_X1) / 2, H - 1.5, "F.SilkS", 0.8)

    pcbnew.SaveBoard(out_path, board)
    export_parts(board, os.path.join(os.path.dirname(out_path), "reports", "placed-parts.json"))
    return board


def export_parts(board, path):
    """Footprint extents in frame E for the mech clearance checks (D-011: positions from KiCad)."""
    out = {}
    for fp in board.GetFootprints():
        bb = fp.GetBoundingBox(False)
        x0, x1 = pcbnew.ToMM(bb.GetLeft()) - X0, pcbnew.ToMM(bb.GetRight()) - X0
        y0, y1 = pcbnew.ToMM(bb.GetTop()) - Y0, pcbnew.ToMM(bb.GetBottom()) - Y0
        out[fp.GetReference()] = {
            "side": "B" if fp.IsFlipped() else "F",
            "footprint": str(fp.GetFPID().GetLibItemName()),
            "bbox_e": [x0 + CX0, CY1 - y1, x1 + CX0, CY1 - y0],
        }
    json.dump(out, open(path, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    net = sys.argv[1] if len(sys.argv) > 1 else os.path.join(CARRIER, "reports", "carrier.net")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(CARRIER, "carrier-placed.kicad_pcb")
    build(net, out)
    print("wrote", out)

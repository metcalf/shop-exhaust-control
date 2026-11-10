"""Scripted, locked placement (D-010): writes pcb/exhaust-placed.kicad_pcb from the schematic netlist.

Run via pcb/layout/run.sh (KiCad's bundled Python). Inputs: pcb/reports/exhaust.net (exported from
pcb/exhaust.kicad_sch, the source since layout started, D-035) and the footprints named in it.

Coordinates: board top-left at (X0, Y0); +x right, +y down, looking at the front (F.Cu, display side).
The board stands vertical behind the bezel with the cable entries at the top (interfaces §5). Every
number below is either from a drawing (cited) or a layout assumption (marked ASSUME, in
pcb/LAYOUT.md for Andrew's review).
"""
import os
import sys

import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
PCB = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import netlist  # noqa: E402

STOCK = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"
LIBS = {"exhaust": os.path.join(PCB, "lib", "exhaust.pretty")}

X0, Y0 = 100.0, 100.0
W, H = 72.0, 123.0  # ASSUME: outline set by the display + top terminal band + LED column

# Display module (MSP2834 outline drawing V1.0, 2023-06-02; interfaces §5): 50.00 x 86.00 PCB,
# holes 44.00 x 76.08, 3.00 from the sides and top; header row 2.00 above the bottom edge,
# pin 1 8.49 from the left edge (front view), 14 pins at 2.54.
DX, DY = 10.0, 34.0  # ASSUME: display left/top edge on our board
DISP_W, DISP_H = 50.0, 86.0
HOLES = [(DX + 3.0, DY + 3.0), (DX + 47.0, DY + 3.0),
         (DX + 3.0, DY + 3.0 + 76.08), (DX + 47.0, DY + 3.0 + 76.08)]
J6_PIN1 = (DX + 8.49, DY + DISP_H - 2.0)

# Barrier geometry (pcb/SAFETY.md): field copper above BARRIER_Y0, node copper below BARRIER_Y1.
OPTO_Y = 24.0               # opto centre line; LED/output pads straddle it
BARRIER_Y0, BARRIER_Y1 = 21.5, 26.5
NODE_X_MAX = 25.5           # top band: node (USB, buck) left of this, field islands right of the gap
FIELD_X_MIN = 28.5
FIELD_GAPS = [(36.2, 37.7), (45.0, 46.5)]  # OCC|DCI and DCI|FAN functional gaps (>= 1.5 mm)

# ref: (x, y, rotation_deg, side) in board coordinates. side "F" or "B".
POS = {
    # --- top band, node: USB-C and 3.3 V buck --------------------------------------------
    "J1": (8.0, 4.2, 180, "F"),       # mouth up through the top wall (ASSUME: top entry, interfaces §5)
    "D1": (5.0, 12.5, 0, "F"),
    "U2": (5.0, 17.0, 0, "F"),
    "R1": (9.5, 16.5, 90, "F"),
    "R2": (11.5, 16.5, 90, "F"),
    "C1": (15.5, 9.5, 90, "F"),       # buck input 10 uF, tight to VIN/GND (AP63203 Fig. 25)
    "U3": (18.5, 5.5, 0, "F"),
    "C2": (18.5, 9.5, 0, "F"),
    "L1": (23.0, 5.5, 90, "F"),
    "C3": (18.5, 13.0, 0, "F"),
    "C4": (22.5, 13.0, 90, "F"),
    "TP5": (14.0, 19.0, 0, "B"),
    # --- OCC island -------------------------------------------------------------------------
    "J3": (32.5, 3.9, 180, "F"),
    "R12": (29.9, 12.0, 90, "F"),
    "D2": (33.6, 12.5, 90, "F"),
    "U7": (32.5, OPTO_Y, 180, "F"),
    # --- DC island --------------------------------------------------------------------------
    "J4": (41.0, 3.9, 180, "F"),
    "R14": (38.4, 12.0, 90, "F"),
    "D3": (42.0, 12.5, 90, "F"),
    "U8": (41.0, OPTO_Y, 180, "F"),
    # --- fan island (D-050): J2 + J7 adjacent (D-049) ------------------------------------
    "J2": (54.0, 3.9, 180, "F"),
    "J7": (61.6, 3.9, 180, "F"),
    "C8": (48.5, 12.0, 90, "F"),
    "C9": (48.5, 16.0, 90, "F"),
    "R5": (51.5, 13.0, 90, "F"),
    "Q1": (55.0, 13.0, 0, "F"),
    "R8": (59.0, 13.0, 90, "F"),
    "R10": (62.5, 13.0, 90, "F"),
    "U4": (51.0, OPTO_Y, 180, "F"),
    "U5": (58.5, OPTO_Y, 180, "F"),
    "U6": (65.5, OPTO_Y, 180, "F"),
    # --- node side of the barrier ------------------------------------------------------------
    "R13": (30.5, 32.5, 90, "F"),
    "C10": (33.0, 32.5, 90, "F"),
    "R15": (39.0, 32.5, 90, "F"),
    "C11": (41.5, 32.5, 90, "F"),
    "R6": (48.0, 32.5, 90, "F"),
    "R7": (50.5, 32.5, 90, "F"),
    "R9": (61.5, 32.0, 0, "F"),
    "R11": (66.0, 32.0, 0, "F"),
    # --- MCU: antenna out the left edge, clear of the display (ASSUME) -----------------------
    "U1": (12.75, 98.0, 90, "F"),
    "C5": (21.0, 85.5, 0, "F"),
    "C6": (24.5, 85.5, 0, "F"),
    "R3": (22.0, 111.0, 0, "F"),
    "C7": (25.5, 111.0, 0, "F"),
    "R4": (22.0, 113.0, 0, "F"),
    # --- indicator FETs (gates from GPIO48/41/42) ---------------------------------------------
    "Q4": (54.0, 80.0, 0, "F"),
    "Q5": (54.0, 85.0, 0, "F"),
    "Q6": (54.0, 90.0, 0, "F"),
    "R40": (57.5, 80.0, 90, "F"),
    "R41": (57.5, 85.0, 90, "F"),
    "R42": (57.5, 90.0, 90, "F"),
    # --- display socket and touch shifters (D-048) -------------------------------------------
    "J6": (J6_PIN1[0], J6_PIN1[1], 90, "F"),
    "Q2": (40.0, 112.0, 0, "F"),
    "Q3": (45.0, 112.0, 0, "F"),
    "R18": (38.5, 108.5, 0, "F"),
    "R19": (43.5, 108.5, 0, "F"),
    "R20": (48.5, 108.5, 0, "F"),
    "R21": (48.5, 111.5, 0, "F"),
    # --- SEN65 connector at the bottom edge, cable down into the sensor bay -----------------
    "J5": (65.5, 119.5, 0, "F"),
    "R16": (62.5, 113.0, 90, "F"),
    "R17": (65.0, 113.0, 90, "F"),
    "C13": (67.5, 113.0, 90, "F"),
    "C12": (70.2, 113.0, 90, "F"),
    # --- mounting: the display's four holes, shared with the enclosure bosses (ASSUME) ------
    "H1": (*HOLES[0], 0, "F"), "H2": (*HOLES[1], 0, "F"),
    "H3": (*HOLES[2], 0, "F"), "H4": (*HOLES[3], 0, "F"),
    # --- test pads on the back, reachable with the rear lid off (ASSUME); D-041 pairs -------
    "TP6": (4.0, 42.0, 0, "B"), "TP2": (5.7, 42.0, 0, "B"),    # EN + GND
    "TP7": (4.0, 54.0, 0, "B"), "TP8": (5.7, 54.0, 0, "B"),    # BOOT + GND (12 mm from the EN pair)
    "TP1": (4.0, 64.0, 0, "B"),
    "TP3": (4.0, 68.0, 0, "B"),
    "TP4": (4.0, 72.0, 0, "B"),
    "TP9": (4.0, 76.0, 0, "B"),
    "TP10": (4.0, 80.0, 0, "B"),
}

# Indicator column (D-031): six LEDs down the room-side edge of the display (ASSUME: right side
# from the front), one resistor per colour just below each LED.
for i in range(6):
    y = 44.0 + 12.0 * i
    POS[f"D{4 + i}"] = (66.0, y, 0, "F")
    for j, x in enumerate((63.0, 66.0, 69.0)):
        POS[f"R{22 + 3 * i + j}"] = (x, y + 3.6, 90, "F")


LAYER = {"F.Cu": pcbnew.F_Cu, "B.Cu": pcbnew.B_Cu, "F.SilkS": pcbnew.F_SilkS, "B.SilkS": pcbnew.B_SilkS,
         "F.Fab": pcbnew.F_Fab, "B.Mask": pcbnew.B_Mask, "Edge.Cuts": pcbnew.Edge_Cuts,
         "User.Drawings": pcbnew.Dwgs_User}


def mm(x, y):
    return pcbnew.VECTOR2I(pcbnew.FromMM(X0 + x), pcbnew.FromMM(Y0 + y))


def load_fp(fpid):
    lib, name = fpid.split(":")
    path = LIBS.get(lib, STOCK + lib + ".pretty")
    fp = pcbnew.FootprintLoad(path, name)
    if fp is None:
        raise SystemExit(f"footprint not found: {fpid}")
    return fp


def add_rule_area(board, pts, name, layers=("F.Cu", "B.Cu")):
    z = pcbnew.ZONE(board)
    z.SetIsRuleArea(True)
    z.SetZoneName(name)
    z.SetDoNotAllowTracks(True)
    z.SetDoNotAllowVias(True)
    z.SetDoNotAllowZoneFills(True)
    z.SetDoNotAllowPads(False)
    z.SetDoNotAllowFootprints(False)
    ls = pcbnew.LSET()
    for l in layers:
        ls.AddLayer(LAYER[l])
    z.SetLayerSet(ls)
    o = z.Outline()
    o.NewOutline()
    for x, y in pts:
        o.Append(mm(x, y))
    board.Add(z)


def rect(x0, y0, x1, y1):
    return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]


def add_line(board, a, b, layer, width=0.1):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_SEGMENT)
    s.SetStart(mm(*a))
    s.SetEnd(mm(*b))
    s.SetLayer(LAYER[layer])
    s.SetWidth(pcbnew.FromMM(width))
    board.Add(s)


def add_rect(board, x0, y0, x1, y1, layer, width=0.1, fill=False):
    s = pcbnew.PCB_SHAPE(board)
    s.SetShape(pcbnew.SHAPE_T_RECT)
    s.SetStart(mm(x0, y0))
    s.SetEnd(mm(x1, y1))
    s.SetLayer(LAYER[layer])
    s.SetWidth(pcbnew.FromMM(width))
    s.SetFilled(fill)
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

    missing = sorted(set(comps) - set(POS))
    extra = sorted(set(POS) - set(comps))
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
        if c["uuid"]:
            fp.SetPath(pcbnew.KIID_PATH("/" + c["uuid"]))
        board.Add(fp)
        for pad in fp.Pads():
            n = pin_net.get((ref, pad.GetNumber()))
            if n is not None:
                pad.SetNet(netitems[n])
        x, y, rot, side = POS[ref]
        if side == "B":
            fp.Flip(fp.GetPosition(), pcbnew.FLIP_DIRECTION_TOP_BOTTOM)
        fp.SetOrientationDegrees(rot)
        fp.SetPosition(mm(x, y))
        fp.Reference().SetTextSize(pcbnew.VECTOR2I(pcbnew.FromMM(0.8), pcbnew.FromMM(0.8)))
        fp.Reference().SetTextThickness(pcbnew.FromMM(0.12))
        fp.SetLocked(True)

    # The stock module's antenna keepout (48 x 21 mm) is removed in footprints.py. This one is sized
    # to this placement (ASSUME):
    # no copper under the antenna end of the module (5.5 mm, the stock zone's depth into the
    # module) and 3 mm either side, out to the board edge.
    ux, uy = POS["U1"][:2]
    ant_end = ux - 12.25  # module top (antenna end) after rotation; footprint y = -12.25
    add_rule_area(board, rect(0.0, uy - 12.0, ant_end + 5.5, uy + 12.0), "antenna keepout")

    # Barrier keepouts (pcb/SAFETY.md): no tracks, vias or pour; opto pads sit on either side.
    add_rule_area(board, rect(FIELD_X_MIN - 3.0, BARRIER_Y0, W, BARRIER_Y1), "barrier: field-node (horizontal)")
    add_rule_area(board, rect(NODE_X_MAX, 0.0, FIELD_X_MIN, BARRIER_Y1), "barrier: field-node (vertical)")
    for x0, x1 in FIELD_GAPS:
        add_rule_area(board, rect(x0, 0.0, x1, BARRIER_Y0), f"gap: field-field {x0}")

    # Board outline
    add_rect(board, 0, 0, W, H, "Edge.Cuts", 0.1)

    # Display module outline and header row for mech and review (User.Drawings, not fabricated)
    add_rect(board, DX, DY, DX + DISP_W, DY + DISP_H, "User.Drawings", 0.1)
    add_text(board, "MSP2834 outline (display above, 8.5 mm socket)", DX + DISP_W / 2, DY + 45, "User.Drawings", 1.0)

    # Silkscreen
    # Terminal labels per pad, fan ones in cable colours (Q-15; D-049)
    labels = {("J2", "1"): ("GND", "BLK"), ("J2", "2"): ("+10V", "RED"),
              ("J7", "1"): ("SPD", "YEL"), ("J7", "2"): ("TACH", "WHT"),
              ("J3", "1"): ("OCC", ""), ("J3", "2"): ("OCC", ""),
              ("J4", "1"): ("DC", ""), ("J4", "2"): ("DC", "")}
    for (ref, pad), (l1, l2) in labels.items():
        p = board.FindFootprintByReference(ref).FindPadByNumber(pad).GetPosition()
        px = pcbnew.ToMM(p.x) - X0
        add_text(board, l1, px, 9.0 if ref in ("J2", "J7") else 8.6, size=0.8)
        if l2:
            add_text(board, l2, px, 10.0 if ref in ("J2", "J7") else 9.6, size=0.8)
    add_text(board, "5V USB-C", 8.0, 10.0, size=0.8)
    add_text(board, "SEN65", 65.5, 115.8, size=0.8)
    for ref, label in (("TP6", "EN"), ("TP7", "BOOT")):
        x, y = POS[ref][:2]
        add_text(board, f"{label} + GND", x + 0.85, y - 2.0, "B.SilkS", 0.8)
    # Recovery pairs (D-041): GND partner pads drop their courtyard so the pair can sit at the
    # copper minimum. Each pad keeps its own mask opening; a shared opening reads as a mask bridge.
    for ref in ("TP2", "TP8"):
        fp = board.FindFootprintByReference(ref)
        for g in list(fp.GraphicalItems()):
            if g.GetLayer() in (pcbnew.F_CrtYd, pcbnew.B_CrtYd):
                fp.Remove(g)

    board.SetDesignSettings(board.GetDesignSettings())
    pcbnew.SaveBoard(out_path, board)
    return board


if __name__ == "__main__":
    net = sys.argv[1] if len(sys.argv) > 1 else os.path.join(PCB, "reports", "exhaust.net")
    out = sys.argv[2] if len(sys.argv) > 2 else os.path.join(PCB, "exhaust-placed.kicad_pcb")
    build(net, out)
    print("wrote", out)

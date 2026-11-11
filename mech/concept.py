"""Concept enclosure and stack-up for the Waveshare 3.5 + carrier + SEN65 (D-056, D-057).

Run: .venv/bin/python mech/concept.py  (needs mech/fetch_vendor.sh first)
Writes mech/out/: concept.step (our parts only), carrier_layout.json (outline, holes, J8, LED edge,
keep-flat and keepout zones for pcb/carrier/layout), stackup.json, and SVG/PNG views.
Frame E and every choice: params.py. Waveshare geometry: waveshare.py (from the STEP).
"""
import json
import math
import os
import sys

from build123d import (Box, Compound, Cylinder, Pos, Rot, export_step)

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import params as P  # noqa: E402
import waveshare as WS  # noqa: E402

OUT = os.path.join(HERE, "out")


def box(x0, y0, z0, x1, y1, z1):
    return Pos((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2) * Box(x1 - x0, y1 - y0, z1 - z0)


PLACED = os.path.join(os.path.dirname(HERE), "pcb", "carrier", "carrier-placed.kicad_pcb")


def carrier_positions():
    """{ref: (x_E, y_E, side)} from the placed carrier board (D-011: positions come from KiCad, never retyped).
    Empty if the board hasn't been placed yet."""
    if not os.path.exists(PLACED):
        return {}
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pcb", "layout"))
    import netlist
    root = netlist.parse_sexpr(open(PLACED).read())
    out = {}
    for fp in (n for n in root if isinstance(n, list) and n and n[0] == "footprint"):
        at = next(n for n in fp if isinstance(n, list) and n and n[0] == "at")
        layer = next(n for n in fp if isinstance(n, list) and n and n[0] == "layer")[1]
        ref = next(n[2] for n in fp if isinstance(n, list) and len(n) > 2 and n[0] == "property" and n[1] == "Reference")
        x, y = float(at[1]) - 100.0, float(at[2]) - 100.0       # place.py origin (X0, Y0)
        out[ref] = (x + P.CARRIER_X[0], P.CARRIER_Y[1] - y, "B" if layer.startswith("B") else "F")
    return out


def cable_slots():
    """Strain-relief slots centred on the placed terminals (fan: J2 + J7 together), else params.py."""
    pos = carrier_positions()
    if not all(r in pos for r in ("J2", "J7", "J3", "J4")):
        return P.CABLE_SLOTS
    by = {n: (h, w) for n, _, h, w in P.CABLE_SLOTS}
    return [("fan", (pos["J2"][1] + pos["J7"][1]) / 2, *by["fan"]),
            ("occ", pos["J3"][1], *by["occ"]),
            ("dc", pos["J4"][1], *by["dc"])]


def stackup():
    f = WS.features()
    lens = f["lens"]
    s = {}
    s["lens"] = lens
    s["pcb_back_z"] = f["pcb_back_z"]
    s["header_face_z"] = f["header_face_z"]
    s["carrier_top_z"] = f["standoff_bottom_z"] - P.SPACER
    s["carrier_back_z"] = s["carrier_top_z"] - P.CARRIER_T
    s["male_body_top_z"] = s["carrier_top_z"] + P.MALE_HDR_BODY
    s["pin_tip_z"] = s["male_body_top_z"] + P.MALE_HDR_MATE
    s["pin_insertion"] = s["pin_tip_z"] - f["header_face_z"]
    s["pin_tip_to_pcb"] = f["pcb_back_z"] - s["pin_tip_z"]
    # SEN65 standing on end: ports (L x W face) against the right wall, H along x, L along y, W along z.
    s["inner_x"] = (lens[0] - P.CLR, lens[3] + P.CLR)
    s["inner_y"] = (lens[1] - P.CLR, lens[4] + P.CLR)
    sx1 = s["inner_x"][1] - P.SEN_PORT_GASKET
    sz1 = s["carrier_back_z"] - P.SEN_GAP
    s["sen"] = (sx1 - P.SEN_H, -P.SEN_L / 2, sz1 - P.SEN_W, sx1, P.SEN_L / 2, sz1)
    s["inner_z"] = (s["sen"][2] - P.CLR, lens[5] + P.LENS_GASKET)
    s["outer"] = (s["inner_x"][0] - P.WALL, s["inner_y"][0] - P.WALL, s["inner_z"][0] - P.WALL,
                  s["inner_x"][1] + P.WALL, s["inner_y"][1] + P.WALL, s["inner_z"][1] + P.BEZEL_LIP)
    s["outer_size"] = tuple(round(s["outer"][i + 3] - s["outer"][i], 2) for i in range(3))
    return s


def sen_ports(s):
    """Wall apertures on the right wall for the SEN65 inlets and outlet (y, z in frame E)."""
    x0, y0, z0, x1, y1, z1 = s["sen"]
    # L runs +y from the bottom (inlets at the bottom, outlet above: warm exhaust rises away from the inlets).
    # W runs -z from the module's front face.
    def yz(L, W):
        return (y0 + L, z1 - W)
    l0, l1, w0, w1 = P.SEN_INLET_SQ
    lc, wc, dia = P.SEN_INLET_RD
    ya, za = yz(l0, w0)
    yb, zb = yz(l1, w1)
    yr, zr = yz(lc, wc)
    pad = 1.0
    inlet = (min(ya, yr - dia / 2) - pad, min(zb, zr - dia / 2) - pad,
             max(yb, yr + dia / 2) + pad, max(za, zr + dia / 2) + pad)   # y0, z0, y1, z1 slot
    oc_l, oc_w, od = P.SEN_OUTLET
    oy, oz = yz(oc_l, oc_w)
    return {"inlet_slot": inlet, "outlet_circle": (oy, oz, od)}


def build():
    f = WS.features()
    s = stackup()
    ix, iy, iz = s["inner_x"], s["inner_y"], s["inner_z"]
    o = s["outer"]
    shell = box(*o) - box(ix[0], iy[0], iz[0], ix[1], iy[1], iz[1])
    # front window: lens view area + 1 mm, centred (Waveshare drawing: borders symmetric)
    va_w, va_h = 73.44 + 2.0, 48.96 + 2.0      # Waveshare dimension drawing (view area)
    shell -= box(-va_w / 2, -va_h / 2, iz[1] - 0.1, va_w / 2, va_h / 2, o[5] + 0.1)

    # USB-C pocket, left wall: open to the outside, mouth at the receptacle face.
    u = f["usb"]
    uy, uz = (u[1] + u[4]) / 2, (u[2] + u[5]) / 2
    ow, oh, _ = P.USB_OVERMOLD
    pk = (ow / 2 + P.USB_POCKET_CLR, oh / 2 + P.USB_POCKET_CLR)
    pocket = box(o[0] - 0.1, uy - pk[0], uz - pk[1], u[0] - 0.5, uy + pk[0], uz + pk[1])
    pocket_wall = box(o[0], uy - pk[0] - P.WALL, uz - pk[1] - P.WALL, u[0] - 0.5,
                      uy + pk[0] + P.WALL, uz + pk[1] + P.WALL)
    shell = (shell + pocket_wall) - pocket
    # mouth through the pocket's back wall into the receptacle (shell outline + 0.5)
    sw, st, _ = P.USB_SHELL
    shell -= box(u[0] - 0.6, uy - sw / 2 - 0.5, uz - st / 2 - 0.5, u[0] + 0.1, uy + sw / 2 + 0.5, uz + st / 2 + 0.5)

    # Cable strain-relief slots, left wall, at terminal height (behind the carrier)
    tz = s["carrier_back_z"] - 6.0
    for name, yc, h, wz in cable_slots():
        shell -= box(o[0] - 0.1, yc - h / 2, tz - wz / 2, ix[0] + 0.1, yc + h / 2, tz + wz / 2)

    # LED diffuser slot, right wall, in the board-to-board gap
    led_z = s["carrier_top_z"] + P.LED_H / 2
    span = (P.N_LED - 1) * P.LED_PITCH
    diff = (-span / 2 - 3, led_z - P.DIFFUSER_Z_PAD, span / 2 + 3, led_z + P.DIFFUSER_Z_PAD)
    shell -= box(ix[1] - 0.1, diff[0], diff[1], o[3] + 0.1, diff[2], diff[3])

    # SEN65 apertures, right wall
    ports = sen_ports(s)
    y0, z0, y1, z1 = ports["inlet_slot"]
    shell -= box(ix[1] - 0.1, y0, z0, o[3] + 0.1, y1, z1)
    oy, oz, od = ports["outlet_circle"]
    shell -= Pos(ix[1] + P.WALL / 2, oy, oz) * Rot(0, 90, 0) * Cylinder(od / 2, P.WALL + 0.4)

    # split into bezel (front) and rear shell
    big = 500
    bezel = shell & box(-big, -big, P.SPLIT_Z, big, big, big)
    rear = shell & box(-big, -big, -big, big, big, P.SPLIT_Z)

    # carrier and friends
    cx, cy = P.CARRIER_X, P.CARRIER_Y
    carrier = box(cx[0], cy[0], s["carrier_back_z"], cx[1], cy[1], s["carrier_top_z"])
    h = f["header"]
    male = box(h[0], h[1], s["carrier_top_z"], h[3], h[4], s["male_body_top_z"])
    sen = box(*s["sen"])
    sx0, sy0, sz0, sx1, sy1, sz1 = s["sen"]
    foam = box(sx0, sy0 + 3.0, sz1, sx1, sy1 - 3.0, sz1 + P.FOAM_T)
    leds = [box(cx[1] - 1.6, y - 2.0, s["carrier_top_z"], cx[1], y + 2.0, s["carrier_top_z"] + P.LED_H)
            for y in [-span / 2 + i * P.LED_PITCH for i in range(P.N_LED)]]
    spacers = [Pos(x, y, (f["standoff_bottom_z"] + s["carrier_top_z"]) / 2) * Cylinder(2.0, P.SPACER)
               for x, y in f["holes"]]
    terminals = []  # KF128L-3.5-2P bodies on the carrier back, wire entry facing left (approximate block)
    for name, yc, hgt, _ in cable_slots():
        n = 2 if name == "fan" else 1
        terminals.append(box(cx[0], yc - 3.5 * n, s["carrier_back_z"] - 10.0, cx[0] + 8.0, yc + 3.5 * n,
                             s["carrier_back_z"]))
    parts = {"bezel": bezel, "rear": rear, "carrier": carrier, "male_header": male, "sen65": sen, "foam": foam,
             "leds": Compound(leds), "spacers": Compound(spacers), "terminals": Compound(terminals)}
    return f, s, ports, diff, parts


def layout_json(f, s, ports, diff):
    """Inputs for pcb/carrier/layout (frame E; the layout converts to KiCad coordinates)."""
    cx, cy = P.CARRIER_X, P.CARRIER_Y
    sen = s["sen"]
    span = (P.N_LED - 1) * P.LED_PITCH
    cam = [b for l, b in ((l, WS.bbox(x)) for l, x in WS.parts()) if l == "CAMER"]
    return {
        "frame": "E: +x right, +y up, seen from the front; KiCad x = x_E - carrier_x0, y = carrier_y1 - y_E",
        "carrier_x": cx, "carrier_y": cy,
        "holes": f["holes"],
        "j8_pin1_x": f["j8_pin1_x"], "j8_pitch_dir": f["j8_pitch_dir"],
        "j8_row_rev2_odd_y": f["j8_row_inner_y"],    # Rev 2.0 odd pins (VBUS, GND, U_N, ...) = inner row
        "j8_row_rev2_even_y": f["j8_row_outer_y"],   # Rev 2.0 even pins (VBAT, GND, GPIO21, ...) = outer row
        "led_edge_x": cx[1], "led_y": [-span / 2 + i * P.LED_PITCH for i in range(P.N_LED)],
        "keep_flat_back": [sen[0] - 1.0, sen[1] - 1.0, cx[1], sen[4] + 1.0],   # x0, y0, x1, y1 on the back side
        "tall_part_keepout_front": [[b[0], b[1], b[3], b[4]] for b in cam],       # Waveshare camera (if fitted)
        "max_front_part_height": round(s["pcb_back_z"] - s["carrier_top_z"] - 0.5, 2),
        "terminal_slots_y": {n: y for n, y, _, _ in cable_slots()},
        "sen65_connector_face": "rear (toward the back wall); cable loops round the module's left face to J5",
        "j5_zone_back": [sen[0] - 14.0, 10.0, sen[0] - 2.0, cy[1] - 1.0],
    }


def export_views(parts, s):
    """SVG projections (front, right, top, iso) of our parts plus the Waveshare outline boxes."""
    from build123d import ExportSVG, LineType
    f = WS.features()
    ws_boxes = [box(*f["lens"]), box(*f["pcba"])]
    shapes = list(parts.values()) + ws_boxes
    asm = Compound(shapes)
    views = {"front": ((0, 0, 200), (0, 1, 0)), "right": ((200, 0, 0), (0, 1, 0)),
             "top": ((0, 200, 0), (0, 0, -1)), "iso": ((150, 90, 180), (0, 1, 0))}
    paths = []
    for name, (origin, up) in views.items():
        vis, hid = asm.project_to_viewport(origin, up, (0, 0, -20))
        exp = ExportSVG(scale=6.0, margin=12)
        exp.add_layer("visible", line_weight=0.3)
        exp.add_layer("hidden", line_color="gray", line_type=LineType.ISO_DOT, line_weight=0.15)
        exp.add_shape(vis, layer="visible")
        exp.add_shape(hid, layer="hidden")
        p = os.path.join(OUT, f"concept-{name}.svg")
        exp.write(p)
        paths.append(p)
    return paths


def main():
    os.makedirs(OUT, exist_ok=True)
    f, s, ports, diff, parts = build()
    export_step(Compound(list(parts.values())), os.path.join(OUT, "concept.step"))
    st = {k: (list(v) if isinstance(v, tuple) else v) for k, v in s.items()}
    st["ports"] = ports
    st["diffuser_slot_y0_z0_y1_z1"] = diff
    st["volume_cm3"] = round(math.prod(s["outer_size"]) / 1000, 1)
    json.dump(st, open(os.path.join(OUT, "stackup.json"), "w"), indent=1, default=float)
    json.dump(layout_json(f, s, ports, diff), open(os.path.join(OUT, "carrier_layout.json"), "w"), indent=1,
              default=float)
    if "--no-views" not in sys.argv:
        for p in export_views(parts, s):
            print("view", p)
    print("outer size (x, y, z) mm:", s["outer_size"], " volume", st["volume_cm3"], "cm3")
    print("pin insertion", round(s["pin_insertion"], 2), "tip-to-PCB", round(s["pin_tip_to_pcb"], 2))


if __name__ == "__main__":
    main()

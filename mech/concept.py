"""Concept enclosure and stack-up for the Waveshare 3.5 + carrier + SEN65 (D-056, D-057).

Run: .venv/bin/python mech/concept.py  (Waveshare STEP committed in mech/vendor/)
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
    sys.path.insert(0, os.path.join(os.path.dirname(HERE), "pcb", "common"))
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
    s["ws_lowest_z"] = f["lowest_back_parts"][0][1]
    # Loose pins in J8, carrier seated flush on the socket face (J1 unpopulated at PCBA). The M2 spacer
    # (a shim) fills what's left to the SMT standoffs.
    s["carrier_top_z"] = f["header_face_z"] - P.J8_SEAT_GAP
    s["carrier_back_z"] = s["carrier_top_z"] - P.CARRIER_T
    s["spacer"] = f["standoff_bottom_z"] - s["carrier_top_z"]
    s["j8_pin_len"] = f["pcb_back_z"] - s["carrier_back_z"] + P.J8_PIN_PROTRUDE   # socket floor to past the back
    s["male_body_z"] = (s["carrier_back_z"] - P.J8_PIN_PROTRUDE, s["carrier_back_z"])   # pin tails behind
    s["ws_to_carrier"] = s["ws_lowest_z"] - s["carrier_top_z"]
    # No bezel: outline = cover glass outline; walls run up to the glass's black border under a foam rim gasket.
    s["glass_back_z"] = f["glass_back_z_rim"]
    s["rim_z"] = s["glass_back_z"] - P.RIM_GASKET
    s["inner_x"] = (lens[0] + P.WALL, lens[3] - P.WALL)
    s["inner_y"] = (lens[1] + P.WALL, lens[4] - P.WALL)
    # SEN65 standing on end: ports (L x W face) against the right wall, H along x, L along y, W along z.
    sx1 = s["inner_x"][1] - P.SEN_PORT_GASKET
    sz1 = s["carrier_back_z"] - P.SEN_GAP
    s["sen"] = (sx1 - P.SEN_H, -P.SEN_L / 2, sz1 - P.SEN_W, sx1, P.SEN_L / 2, sz1)
    s["inner_z"] = (s["sen"][2] - P.SEN_BACK_CLR, s["rim_z"])
    s["outer"] = (lens[0], lens[1], s["inner_z"][0] - P.BACK_PANEL, lens[3], lens[4], lens[5])
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


def tabs(s):
    """Retention tabs behind the carrier at the four holes, each tied to the nearer top/bottom wall.
    One screw per hole from the back: tab -> carrier -> spacer -> Waveshare SMT standoff, which pulls
    the glass onto the rim gasket."""
    f = WS.features()
    iy = s["inner_y"]
    z1 = s["carrier_back_z"]
    out = []
    for x, y in f["holes"]:
        y0, y1 = (y - P.TAB_W / 2, iy[1]) if y > 0 else (iy[0], y + P.TAB_W / 2)
        out.append((x - P.TAB_W / 2, y0, z1 - P.TAB_T, x + P.TAB_W / 2, y1, z1))
    return out


def ribs(s):
    """Back-panel ribs, inside, left of the SEN65 and its plug bay."""
    ix, iy, iz = s["inner_x"], s["inner_y"], s["inner_z"]
    xr = s["sen"][0] - P.SEN_PLUG_BAY
    z0, z1 = iz[0], iz[0] + P.RIB_H
    out = [(ix[0], -P.RIB_T / 2, z0, xr, P.RIB_T / 2, z1)]                    # one along x
    x = ix[0] + P.RIB_PITCH
    while x < xr - 2:
        out.append((x - P.RIB_T / 2, iy[0], z0, x + P.RIB_T / 2, iy[1], z1))  # across y
        x += P.RIB_PITCH
    return out


def build():
    f = WS.features()
    s = stackup()
    ix, iy, iz = s["inner_x"], s["inner_y"], s["inner_z"]
    o = s["outer"]
    # shell: four walls from the back panel to the rim (open front: the glass is the face)
    shell = box(o[0], o[1], iz[0], o[3], o[4], s["rim_z"]) - box(ix[0], iy[0], iz[0] - 1, ix[1], iy[1], s["rim_z"] + 1)
    for t in tabs(s):
        shell += box(*t)

    # USB-C pocket, left wall: open to the outside, mouth at the receptacle face.
    u = f["usb"]
    uy, uz = (u[1] + u[4]) / 2, (u[2] + u[5]) / 2
    ow, oh, _ = P.USB_OVERMOLD
    pk = (ow / 2 + P.USB_POCKET_CLR, oh / 2 + P.USB_POCKET_CLR_Z)
    pocket = box(o[0] - 0.1, uy - pk[0], uz - pk[1], u[0] - 0.5, uy + pk[0], uz + pk[1])
    # Floor: down to the carrier top if there's no room for USB_POCKET_FLOOR; the carrier edge (kept free of
    # display-side parts) and a foam strip then close the pocket underneath.
    floor_z = max(uz - pk[1] - P.USB_POCKET_FLOOR, s["carrier_top_z"] + 0.05)
    s["usb_pocket_floor_on_carrier"] = floor_z > uz - pk[1] - P.USB_POCKET_FLOOR
    pocket_wall = box(o[0], uy - pk[0] - P.WALL, floor_z, u[0] - 0.5,
                      uy + pk[0] + P.WALL, uz + pk[1] + P.USB_POCKET_FLOOR)
    if s["usb_pocket_floor_on_carrier"]:
        pocket = box(o[0] - 0.1, uy - pk[0], floor_z - 0.1, u[0] - 0.5, uy + pk[0], uz + pk[1])
    shell = (shell + pocket_wall) - pocket
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

    back = box(o[0], o[1], o[2], o[3], o[4], iz[0])
    for r in ribs(s):
        back += box(*r)

    # carrier and friends
    cx, cy = P.CARRIER_X, P.CARRIER_Y
    carrier = box(cx[0], cy[0], s["carrier_back_z"], cx[1], cy[1], s["carrier_top_z"])
    h = f["header"]
    male = box(h[0], h[1], s["male_body_z"][0], h[3], h[4], s["male_body_z"][1])   # pin tails, carrier back
    sen = box(*s["sen"])
    sx0, sy0, sz0, sx1, sy1, sz1 = s["sen"]
    foam = box(sx0, sy0 + 3.0, sz1, sx1, sy1 - 3.0, sz1 + P.FOAM_T)
    for t in tabs(s):   # foam notched round the tabs and screw heads
        foam -= box(t[0] - 0.5, t[1] - 0.5, t[2] - P.SCREW_HEAD - 0.3, t[3] + 0.5, t[4] + 0.5, t[5])
    leds = [box(cx[1] - 1.6, y - 2.0, s["carrier_top_z"], cx[1], y + 2.0, s["carrier_top_z"] + P.LED_H)
            for y in [-span / 2 + i * P.LED_PITCH for i in range(P.N_LED)]]
    spacers = [Pos(x, y, (f["standoff_bottom_z"] + s["carrier_top_z"]) / 2) * Cylinder(2.0, s["spacer"])
               for x, y in f["holes"]]
    heads = [Pos(x, y, s["carrier_back_z"] - P.TAB_T - P.SCREW_HEAD / 2) * Cylinder(1.9, P.SCREW_HEAD)
             for x, y in f["holes"]]
    terminals = []  # KF128L-3.5-2P bodies on the carrier back, wire entry facing left (footprint extents)
    pos = carrier_positions()
    if all(r in pos for r in ("J2", "J7", "J3", "J4")):
        for r in ("J2", "J7", "J3", "J4"):
            x, y, _ = pos[r]
            terminals.append(box(x - 3.95, y - 3.8, s["carrier_back_z"] - 10.0, x + 3.75, y + 3.8,
                                 s["carrier_back_z"]))
    else:
        for name, yc, hgt, _ in cable_slots():
            n = 2 if name == "fan" else 1
            terminals.append(box(cx[0], yc - 3.5 * n, s["carrier_back_z"] - 10.0, cx[0] + 8.0, yc + 3.5 * n,
                                 s["carrier_back_z"]))
    plug_bay = box(sx0 - P.SEN_PLUG_BAY, sy0, sz0, sx0, sy1, sz1)   # GH plug + cable bend, kept clear
    parts = {"shell": shell, "back": back, "carrier": carrier, "male_header": male, "sen65": sen, "foam": foam,
             "leds": Compound(leds), "spacers": Compound(spacers), "screw_heads": Compound(heads),
             "terminals": Compound(terminals)}
    return f, s, ports, diff, parts, plug_bay


def usb_pocket_xy(f):
    u = f["usb"]
    uy = (u[1] + u[4]) / 2
    half = P.USB_OVERMOLD[0] / 2 + P.USB_POCKET_CLR + P.WALL
    return [P.CARRIER_X[0], uy - half, u[0] - 0.5, uy + half]


def layout_json(f, s, ports, diff):
    """Inputs for pcb/carrier/layout (frame E; the layout converts to KiCad coordinates)."""
    cx, cy = P.CARRIER_X, P.CARRIER_Y
    sen = s["sen"]
    span = (P.N_LED - 1) * P.LED_PITCH
    return {
        "frame": "E: +x right, +y up, seen from the front; KiCad x = x_E - carrier_x0, y = carrier_y1 - y_E",
        "carrier_x": cx, "carrier_y": cy,
        "holes": f["holes"],
        "j8_pin1_x": f["j8_pin1_x"], "j8_pitch_dir": f["j8_pitch_dir"],
        "j8_row_rev2_odd_y": f["j8_row_inner_y"],    # Rev 2.0 odd pins (VBUS, GND, U_N, ...) = inner row
        "j8_row_rev2_even_y": f["j8_row_outer_y"],   # Rev 2.0 even pins (VBAT, GND, GPIO21, ...) = outer row
        "led_edge_x": cx[1], "led_y": [-span / 2 + i * P.LED_PITCH for i in range(P.N_LED)],
        "keep_flat_back": [sen[0] - 1.0, sen[1] - 1.0, cx[1], sen[4] + 1.0],   # x0, y0, x1, y1 on the back side
        "usb_pocket_front": usb_pocket_xy(f),   # carrier edge under the USB pocket: no display-side parts
        "tall_part_keepout_front": [],   # camera module not shipped (params.NOT_FITTED); heights checked per part
        "carrier_top_z": s["carrier_top_z"],
        "terminal_slots_y": {n: y for n, y, _, _ in cable_slots()},
        "sen65_connector_face": "-x (module face opposite the ports), into the bay left of the module; short cable to J5",
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
    f, s, ports, diff, parts, _ = build()
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
    print("carrier top", round(s["carrier_top_z"], 2), "spacer", round(s["spacer"], 2), "J8 pin length", round(s["j8_pin_len"], 2), "USB pocket floor on carrier", s.get("usb_pocket_floor_on_carrier"))


if __name__ == "__main__":
    main()

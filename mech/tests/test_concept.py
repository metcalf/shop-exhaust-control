"""Geometry checks for the concept stack-up (D-011, D-056, D-057). Run: .venv/bin/python -m pytest mech/tests

Waveshare solids are only probed with small slabs or compared by per-solid bounding box: full booleans
against the vendor STEP run out of memory.
"""
import pytest
from build123d import Box, Pos

import concept as C
import params as P
import waveshare as WS


@pytest.fixture(scope="module")
def built():
    return C.build()


def overlap(a, b, tol=0.0):
    return all(a[i] < b[i + 3] - tol and b[i] < a[i + 3] - tol for i in range(3))


def test_j8_loose_pins_and_flush_seat():
    """J1 unpopulated; loose pins through J8 and the carrier, carrier flush on the socket face."""
    s = C.stackup()
    assert abs(s["carrier_top_z"] - s["header_face_z"]) < 1e-6
    assert 0.0 <= s["spacer"] <= 2.0, s["spacer"]          # shim between carrier and SMT standoff
    assert 7.0 <= s["j8_pin_len"] <= 9.0, s["j8_pin_len"]   # pulled from a standard header (11.5) and trimmed


def test_carrier_gap_to_waveshare():
    s = C.stackup()
    assert s["ws_to_carrier"] >= -1e-6, s["ws_to_carrier"]   # nothing on the Waveshare reaches past J8


def part_height(ref):
    if ref in P.PART_H:
        return P.PART_H[ref]
    return P.PART_H.get(ref.rstrip("0123456789"), P.PART_H_DEFAULT)


def test_carrier_parts_clear_waveshare_parts():
    """Each placed display-side carrier part, at its datasheet height, clears every Waveshare solid behind
    the PCB by >= 0.2 mm (per-solid boxes, J8 excepted: it mates). Footprint extents (pads and courtyard)
    are taken at full part height, which is conservative for gull-wing leads. Positions: placed-parts.json."""
    import json, os
    path = os.path.join(os.path.dirname(C.PLACED), "reports", "placed-parts.json")
    if not os.path.exists(path):
        pytest.skip("carrier not placed yet (pcb/carrier/layout/run.sh)")
    s = C.stackup()
    placed = json.load(open(path))
    clash = {}
    for ref, p in placed.items():
        if p["side"] != "F" or ref == "J1" or ref.startswith("H"):
            continue
        x0, y0, x1, y1 = p["bbox_e"]
        top = s["carrier_top_z"] + part_height(ref)
        for label, b in WS.back_obstacles():
            if label == "HEADER-SMD-F-2_54-2X16PIN":
                continue
            if b[0] < x1 and x0 < b[3] and b[1] < y1 and y0 < b[4]:
                gap = round(b[2] - top, 3)
                if gap < 0.2 - 1e-6:
                    clash[ref] = min(clash.get(ref, 9.0), gap)
    assert not clash, f"carrier part: gap to the Waveshare part above (mm, need >= 0.2): {clash}"


def test_carrier_parts_clear_j8_socket():
    """J8 itself is the mating part, so nothing else on the carrier may sit under its body."""
    import json, os
    path = os.path.join(os.path.dirname(C.PLACED), "reports", "placed-parts.json")
    if not os.path.exists(path):
        pytest.skip("carrier not placed yet")
    h = WS.features()["header"]
    hits = [r for r, p in json.load(open(path)).items() if p["side"] == "F" and r != "J1"
            and p["bbox_e"][0] < h[3] and h[0] < p["bbox_e"][2] and p["bbox_e"][1] < h[4] and h[1] < p["bbox_e"][3]]
    assert not hits, hits


def test_camera_keepout_is_exported():
    import json, os
    C.main.__globals__["sys"].argv = ["x", "--no-views"]
    C.main()
    lay = json.load(open(os.path.join(C.OUT, "carrier_layout.json")))
    assert not any(l in P.NOT_FITTED for l, _ in WS.parts())   # camera module isn't on the shipped board
    assert abs(lay["carrier_top_z"] - C.stackup()["carrier_top_z"]) < 1e-6


def test_sen65_gap_and_foam():
    s = C.stackup()
    gap = s["carrier_back_z"] - s["sen"][5]
    assert P.FOAM_T <= gap <= 6.35 + 1e-6, gap     # Andrew: <= 1/4"; must hold the 1/8" foam


def test_sen65_inside_and_ports_on_right_wall():
    s = C.stackup()
    sen, ix, iy, iz = s["sen"], s["inner_x"], s["inner_y"], s["inner_z"]
    assert ix[0] < sen[0] and sen[3] <= ix[1] and iy[0] < sen[1] and sen[4] < iy[1]
    assert abs((ix[1] - sen[3]) - P.SEN_PORT_GASKET) < 1e-6
    assert abs((sen[2] - iz[0]) - P.SEN_BACK_CLR) < 1e-6           # Andrew: 0.4 mm to the back panel
    assert WS.features()["pcba"][2] > sen[5]


def test_sen65_apertures():
    import math
    s = C.stackup()
    ports = C.sen_ports(s)
    y0, z0, y1, z1 = ports["inlet_slot"]
    oy, oz, od = ports["outlet_circle"]
    assert (y1 - y0) * (z1 - z0) >= P.SEN_IN_MIN_MM2
    assert math.pi * od * od / 4 >= P.SEN_OUT_MIN_MM2
    rib = (oy - od / 2) - y1
    assert rib >= 5.0, f"gasket rib between inlet and outlet only {rib:.1f} mm"
    sen = s["sen"]
    assert sen[1] < y0 and y1 < sen[4] and sen[1] < oy - od / 2 and oy + od / 2 < sen[4]
    assert sen[2] < z0 and z1 < sen[5] and sen[2] < oz - od / 2 and oz + od / 2 < sen[5]


def test_led_slot_separate_from_sen65_ports():
    s = C.stackup()
    led_z = s["carrier_top_z"] + P.LED_H / 2
    assert led_z + P.DIFFUSER_Z_PAD < s["pcb_back_z"]
    gap = (led_z - P.DIFFUSER_Z_PAD) - s["sen"][5]
    assert gap >= 3.0, f"diffuser slot only {gap:.1f} mm from the SEN65 zone"


def test_usb_plug_clears_display():
    """Slab-probe the standard plug overmold envelope outside the receptacle mouth."""
    f = WS.features()
    u = f["usb"]
    uy, uz = (u[1] + u[4]) / 2, (u[2] + u[5]) / 2
    ow, oh, _ = P.USB_OVERMOLD
    parts = dict(WS.parts())
    for x in (u[0] - 0.6, u[0] - 2.0, u[0] - 4.0, C.stackup()["inner_x"][0] + 0.2):
        probe = Pos(x, uy, uz) * Box(0.4, ow, oh)
        for label in ("3_5INCH-320X480-TOUCH", "HXR35014C30"):
            r = parts[label] & probe
            assert r is None or r.volume < 1e-3, (label, x)


def test_walls_and_size():
    """No bezel: the outline is the cover glass outline, walls 1.6 mm, rim on the glass's black border."""
    s = C.stackup()
    o, ix, iy = s["outer"], s["inner_x"], s["inner_y"]
    lens = WS.features()["lens"]
    assert all(abs(o[i] - lens[i]) < 1e-6 for i in (0, 1, 3, 4)), (o, lens)
    assert abs(o[5] - lens[5]) < 1e-6                                  # glass is the front face
    assert abs(ix[0] - o[0] - P.WALL) < 1e-6 and abs(iy[0] - o[1] - P.WALL) < 1e-6
    va_w, va_h = 73.44, 48.96                                         # Waveshare drawing: view area
    assert ix[1] < va_w / 2 + (lens[3] - va_w / 2) and ix[1] > va_w / 2 + 1.0   # rim stays on the border
    assert iy[1] > va_h / 2 + 1.0
    assert s["outer_size"][2] <= 49.0, s["outer_size"]                # Andrew's estimate 47.7


def test_waveshare_fits_inside_walls():
    f = WS.features()
    s = C.stackup()
    ix, iy = s["inner_x"], s["inner_y"]
    for name in ("lcd", "pcba"):
        b = f[name]
        assert ix[0] + 0.3 <= b[0] and b[3] <= ix[1] - 0.3 and iy[0] + 0.3 <= b[1] and b[4] <= iy[1] - 0.3, name
    assert s["rim_z"] < s["glass_back_z"]
    cx, cy = P.CARRIER_X, P.CARRIER_Y
    assert ix[0] + P.CLR - 1e-6 <= cx[0] and cx[1] <= ix[1] - P.CLR + 1e-6
    assert iy[0] + P.CLR - 1e-6 <= cy[0] and cy[1] <= iy[1] - P.CLR + 1e-6


def test_carrier_holes_and_header_inside_outline():
    f = WS.features()
    for x, y in f["holes"]:
        assert P.CARRIER_X[0] + 3 < x < P.CARRIER_X[1] - 3 and P.CARRIER_Y[0] + 3 < y < P.CARRIER_Y[1] - 3
    h = f["header"]
    assert P.CARRIER_X[0] < h[0] and h[3] < P.CARRIER_X[1] and h[4] < P.CARRIER_Y[1]


def test_parts_dont_collide(built):
    _, s, _, _, parts, bay = built
    pairs = [("carrier", "sen65"), ("carrier", "shell"), ("carrier", "back"), ("sen65", "shell"),
             ("sen65", "back"), ("foam", "carrier"), ("foam", "shell"), ("terminals", "sen65"),
             ("terminals", "shell"), ("terminals", "back"), ("spacers", "sen65"), ("screw_heads", "sen65"),
             ("male_header", "sen65"), ("male_header", "foam"),
             ("screw_heads", "foam"), ("male_header", "shell"), ("leds", "shell"), ("terminals", "screw_heads")]
    for a, b in pairs:
        r = parts[a] & parts[b]
        v = 0.0 if r is None else r.volume
        assert v < 1e-3, f"{a} intersects {b}: {v:.3f} mm3"


def test_sen65_plug_bay_clear(built):
    """The connector faces -x (mech guide Fig. 1): the bay beside the module stays free for the plug."""
    _, _, _, _, parts, bay = built
    for name in ("terminals", "back", "shell", "screw_heads", "male_header"):
        r = parts[name] & bay
        v = 0.0 if r is None else r.volume
        assert v < 1e-3, f"{name} intrudes on the SEN65 plug bay: {v:.3f} mm3"


def test_tabs_take_screws_from_the_back():
    s = C.stackup()
    f = WS.features()
    for (x, y), t in zip(f["holes"], C.tabs(s)):
        assert t[0] < x < t[3] and t[1] < y < t[4] and abs(t[5] - s["carrier_back_z"]) < 1e-6
        # screw head behind the tab clears the SEN65 front where they overlap in x
        assert t[2] - P.SCREW_HEAD > s["sen"][5] + 0.3 or t[3] < s["sen"][0]


def test_terminals_line_up_with_cable_slots():
    pos = C.carrier_positions()
    if not pos:
        pytest.skip("carrier not placed yet (pcb/carrier/layout/run.sh)")
    slots = {n: y for n, y, _, _ in C.cable_slots()}
    assert abs(slots["fan"] - (pos["J2"][1] + pos["J7"][1]) / 2) < 0.01
    assert abs(slots["occ"] - pos["J3"][1]) < 0.01 and abs(slots["dc"] - pos["J4"][1]) < 0.01
    for r in ("J2", "J7", "J3", "J4"):
        assert pos[r][2] == "B", r
    ys = sorted(slots.values())
    assert all(b - a >= 9.0 for a, b in zip(ys, ys[1:])), ys           # room for a clamp per cable


def test_terminals_inboard_with_wire_room():
    """Andrew: terminals mid-board facing the left wall, the back left of them clear to dress the wires.
    Only the screw heads at the left holes sit in that strip."""
    import json, os
    path = os.path.join(os.path.dirname(C.PLACED), "reports", "placed-parts.json")
    if not os.path.exists(path):
        pytest.skip("carrier not placed yet")
    placed = json.load(open(path))
    s = C.stackup()
    entry = min(placed[r]["bbox_e"][0] for r in ("J2", "J7", "J3", "J4"))
    room = entry - s["inner_x"][0]
    assert room >= 20.0, f"only {room:.1f} mm from the left wall to the terminal entries"   # mid-board (D-061)
    left = [r for r, p in placed.items() if p["side"] == "B" and p["bbox_e"][0] < entry - 0.5]
    assert not left, f"parts on the back left of the terminals: {left}"


def test_leds_and_sen_keep_flat_from_board():
    pos = C.carrier_positions()
    if not pos:
        pytest.skip("carrier not placed yet")
    s = C.stackup()
    leds = [pos[f"D{i}"] for i in range(4, 4 + P.N_LED)]
    assert all(p[2] == "F" and p[0] > P.CARRIER_X[1] - 2.0 for p in leds)
    sen = s["sen"]
    on_back = [r for r, p in pos.items() if p[2] == "B" and sen[0] - 1.0 < p[0] and sen[1] < p[1] < sen[4]]
    assert not on_back, f"parts on the back behind the SEN65: {on_back}"


def test_usb_pocket_edge_free_of_front_parts():
    import json, os
    path = os.path.join(os.path.dirname(C.PLACED), "reports", "placed-parts.json")
    if not os.path.exists(path):
        pytest.skip("carrier not placed yet")
    x0, y0, x1, y1 = C.usb_pocket_xy(WS.features())
    placed = json.load(open(path))
    hits = [r for r, p in placed.items() if p["side"] == "F" and p["bbox_e"][0] < x1 and x0 < p["bbox_e"][2]
            and p["bbox_e"][1] < y1 and y0 < p["bbox_e"][3]]
    assert not hits, hits

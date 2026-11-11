"""Geometry checks for the concept stack-up (D-011, D-056, D-057). Run: .venv/bin/python -m pytest mech/tests

Waveshare solids are only probed with small slabs or compared by bounding box: full booleans against
the vendor STEP run out of memory.
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


def test_header_engagement():
    s = C.stackup()
    assert 3.0 <= s["pin_insertion"] <= 5.1, s["pin_insertion"]   # contacts engage, inside the 5.1 mm socket
    assert s["pin_tip_to_pcb"] >= 0.8, s["pin_tip_to_pcb"]          # tips don't bottom on the socket floor


def test_carrier_clears_waveshare_parts():
    """Every Waveshare back-side part except the header leaves room for the tallest carrier part, or is
    in a keepout the layout honours (the camera, if fitted)."""
    s = C.stackup()
    top = s["carrier_top_z"] + P.CARRIER_MAX_PART
    clash = []
    for label, sh in WS.parts():
        b = WS.bbox(sh)
        if label in ("HEADER-SMD-F-2_54-2X16PIN", "CAMER"):
            continue
        if b[2] < top and b[0] < P.CARRIER_X[1] and b[3] > P.CARRIER_X[0]:
            clash.append((label, round(b[2], 2)))
    assert not clash, clash
    assert s["carrier_top_z"] < WS.features()["standoff_bottom_z"]


def test_camera_keepout_is_exported():
    import json, os
    C.main.__globals__["sys"].argv = ["x", "--no-views"]
    C.main()
    lay = json.load(open(os.path.join(C.OUT, "carrier_layout.json")))
    assert lay["tall_part_keepout_front"], "camera keepout missing"
    assert lay["max_front_part_height"] >= P.CARRIER_MAX_PART


def test_sen65_gap_and_foam():
    s = C.stackup()
    gap = s["carrier_back_z"] - s["sen"][5]
    assert P.FOAM_T <= gap <= 6.35 + 1e-6, gap     # Andrew: <= 1/4"; must hold the 1/8" foam


def test_sen65_inside_and_ports_on_right_wall():
    s = C.stackup()
    sen, ix, iy, iz = s["sen"], s["inner_x"], s["inner_y"], s["inner_z"]
    assert ix[0] < sen[0] and sen[3] <= ix[1] and iy[0] < sen[1] and sen[4] < iy[1] and iz[0] < sen[2]
    assert abs((ix[1] - sen[3]) - P.SEN_PORT_GASKET) < 1e-6
    # nothing of the Waveshare behind its PCB reaches the module
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
    s = C.stackup()
    o, ix = s["outer"], s["inner_x"]
    assert ix[0] - o[0] >= P.WALL - 1e-6 and o[3] - ix[1] >= P.WALL - 1e-6
    assert s["outer_size"][2] <= 56.0, s["outer_size"]          # concept target ~50-55 mm deep
    lens = WS.features()["lens"]
    window = 73.44 + 2.0
    assert (lens[3] - lens[0] - window) / 2 >= P.BEZEL_OVERLAP


def test_carrier_holes_and_header_inside_outline():
    f = WS.features()
    for x, y in f["holes"]:
        assert P.CARRIER_X[0] + 3 < x < P.CARRIER_X[1] - 3 and P.CARRIER_Y[0] + 3 < y < P.CARRIER_Y[1] - 3
    h = f["header"]
    assert P.CARRIER_X[0] < h[0] and h[3] < P.CARRIER_X[1] and h[4] < P.CARRIER_Y[1]


def test_parts_dont_collide(built):
    _, s, _, _, parts = built
    pairs = [("carrier", "sen65"), ("carrier", "rear"), ("carrier", "bezel"), ("sen65", "rear"),
             ("foam", "carrier"), ("terminals", "sen65"), ("spacers", "sen65"), ("male_header", "bezel")]
    for a, b in pairs:
        r = parts[a] & parts[b]
        v = 0.0 if r is None else r.volume
        assert v < 1e-3, f"{a} intersects {b}: {v:.3f} mm3"


def test_terminals_line_up_with_cable_slots():
    pos = C.carrier_positions()
    if not pos:
        pytest.skip("carrier not placed yet (pcb/carrier/layout/run.sh)")
    slots = {n: y for n, y, _, _ in C.cable_slots()}
    assert abs(slots["fan"] - (pos["J2"][1] + pos["J7"][1]) / 2) < 0.01
    assert abs(slots["occ"] - pos["J3"][1]) < 0.01 and abs(slots["dc"] - pos["J4"][1]) < 0.01
    for r in ("J2", "J7", "J3", "J4"):
        assert pos[r][2] == "B" and pos[r][0] < P.CARRIER_X[0] + 8.0, r   # back side, at the left edge
    ys = sorted(slots.values())
    assert all(b - a >= 9.0 for a, b in zip(ys, ys[1:])), ys           # room for a clamp per cable


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

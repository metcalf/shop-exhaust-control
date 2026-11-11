"""Waveshare ESP32-S3-Touch-LCD-3.5 features in frame E, read from the vendor STEP (never retyped, D-011).

Run `mech/fetch_vendor.sh` first. Labels are the STEP's own part names.
"""
import functools
import json
import os

from build123d import Axis, import_step

from params import WS_ROT_Z

HERE = os.path.dirname(os.path.abspath(__file__))
STEP = os.path.join(HERE, "vendor", "ESP32-S3-Touch-LCD-3_5.stp")


@functools.lru_cache(maxsize=1)
def model():
    if not os.path.exists(STEP):
        raise SystemExit("missing STEP: run mech/fetch_vendor.sh")
    return import_step(STEP)


@functools.lru_cache(maxsize=1)
def parts():
    """[(label, shape)] for the STEP's named parts, in frame E.

    Only the first two assembly levels carry global placement and meaningful labels (deeper children
    are in local coordinates), so take each level-1 assembly's children, or the level-1 part itself.
    Each is rotated individually: rotating the parent compound doesn't move its children.
    """
    out = []
    for a in model().children:
        kids = list(getattr(a, "children", []) or [])
        for k in (kids or [a]):
            out.append((getattr(k, "label", "") or "", k.rotate(Axis.Z, WS_ROT_Z)))
    return out


def bbox(shape):
    b = shape.bounding_box()
    return (b.min.X, b.min.Y, b.min.Z, b.max.X, b.max.Y, b.max.Z)


def find(label):
    hits = [s for l, s in parts() if l == label]
    if not hits:
        raise KeyError(label)
    return hits


def union_bbox(boxes):
    return (min(b[0] for b in boxes), min(b[1] for b in boxes), min(b[2] for b in boxes),
            max(b[3] for b in boxes), max(b[4] for b in boxes), max(b[5] for b in boxes))


@functools.lru_cache(maxsize=1)
def features():
    lens = bbox(find("3_5INCH-320X480-TOUCH")[0])
    lcd = bbox(find("HXR35014C30")[0])
    hdr = bbox(find("HEADER-SMD-F-2_54-2X16PIN")[0])
    usb = bbox(find("TYPE-C_16PIN-9X3X7_3")[0])
    standoffs = [bbox(s) for s in find("SMTSO-M2X4-4ET")]
    pcba = union_bbox([bbox(s) for l, s in parts() if l not in ("3_5INCH-320X480-TOUCH", "HXR35014C30",
                                                                 "ESP32-S3-TOUCH-LCD-3_5-PMMA")])
    holes = sorted(((b[0] + b[3]) / 2, (b[1] + b[4]) / 2) for b in standoffs)
    # J8: 2 x 16 at 2.54. Pin 1 is at the USB-C end (Waveshare pinout image); the V1-odd row
    # (BAT, GND, GPIO21, ...) is the outer row, nearest the board edge (+y in frame E).
    hx0, hx1 = hdr[0], hdr[3]
    cx = (hx0 + hx1) / 2
    usb_left = usb[0] < 0
    span = 15 * 2.54
    x_pin1 = cx - span / 2 if usb_left else cx + span / 2
    y_rows = sorted([(hdr[1] + hdr[4]) / 2 - 1.27, (hdr[1] + hdr[4]) / 2 + 1.27])
    return {
        "lens": lens, "lcd": lcd, "pcba": pcba, "header": hdr, "usb": usb,
        "holes": holes,
        "standoff_bottom_z": min(b[2] for b in standoffs),
        "pcb_back_z": hdr[5],             # the header sits on the PCB's back face
        "header_face_z": hdr[2],
        "j8_pin1_x": x_pin1, "j8_pitch_dir": 1 if usb_left else -1,
        "j8_row_outer_y": y_rows[1], "j8_row_inner_y": y_rows[0],
        "lowest_back_parts": sorted(((l, bbox(s)[2]) for l, s in parts()), key=lambda t: t[1])[:6],
    }


if __name__ == "__main__":
    f = features()
    print(json.dumps({k: v for k, v in f.items()}, indent=1, default=lambda o: round(o, 3)))

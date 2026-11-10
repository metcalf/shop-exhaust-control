"""Build pcb/lib/exhaust.pretty: project footprints checked against the LCSC drawings (design.md O-3).

Run with KiCad's bundled Python (pcb/layout/run.sh does). Sources:
- pcb/lib/lcsc.pretty: easyeda2kicad output by LCSC number (fetched 2026-11-09), kept verbatim.
- KiCad 10 stock libraries where the stock footprint matches the LCSC drawing pad for pad.

Renumbering maps datasheet pin numbers (as easyeda numbers them) to the KiCad symbol's pins:
- C601699 3528 RGB (TOGIALED datasheet p.2): pin 4 anode, 1 R, 2 G, 3 B.
  Symbol Device:LED_ARGB: 1 A, 2 RK, 3 GK, 4 BK.
- C2488 MB10S (MDD MB1S-MB10S datasheet p.1): 1 +, 2 -, 3 ~, 4 ~.
  Symbol Diode_Bridge:MB6S: 1 ~, 2 ~, 3 +, 4 -.
"""
import os
import pcbnew

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LCSC = os.path.join(ROOT, "lib", "lcsc.pretty")
OUT = os.path.join(ROOT, "lib", "exhaust.pretty")
STOCK = "/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints/"

# name -> (source lib path, source footprint, {datasheet pad: symbol pin} or None, note)
BUILD = {
    "RGB_3528_TJ-S3528": (LCSC, "LED-ARRAY-SMD_4P-L3.2-W2.7-TL-RD_TJ-S3528",
                          {"4": "1", "1": "2", "2": "3", "3": "4"}, "C601699; pads renumbered to LED_ARGB"),
    "Bridge_MBS_MB10S": (LCSC, "MBS_L4.7-W3.8-P2.40-LS7.0-TL",
                         {"1": "3", "2": "4", "3": "1", "4": "2"}, "C2488; pads renumbered to MB6S symbol"),
    "SOP-6_H11L1S_LS10.2": (LCSC, "SOP-6_L7.3-W6.5-P2.54-LS10.2-TR", None, "C7435535 H11L1S-TA1-L"),
    "SOP-4_LTV-817S_LS10.3": (LCSC, "OPTO-SMD-4_L4.6-W6.5-P2.54-LS10.3-BL", None, "C109227 LTV-817S-TA1-C"),
    "L_Murata_LQH44P": (LCSC, "IND-SMD_L4.0-W4.0_LQH44PN2R2MP0L", None, "C135262 LQH44PN2R2MP0L"),
    "TerminalBlock_KF128L-3.5-2P": (LCSC, "CONN-TH_P3.50_KF128L-3.5-2P", None, "C474930"),
    # Stock footprint, thermal-via PTH pads removed from the EPAD (Q-33: no EPAD vias). EPAD joins GND on F.Cu.
    # Its 48 x 21 mm antenna keepout is removed too; place.py draws one sized to the board.
    "ESP32-S3-WROOM-1_NoEPADVias": (STOCK + "RF_Module.pretty", "ESP32-S3-WROOM-1", "strip-epad-vias",
                                    "C2913202; stock with EPAD vias removed"),
}


def _drop_blocks(txt, head):
    """Remove every balanced s-expression starting with `head` (strings in them hold no parens)."""
    out, i = [], 0
    while True:
        j = txt.find(head, i)
        if j < 0:
            out.append(txt[i:])
            return "".join(out)
        k = txt.rfind("\n", 0, j) + 1
        out.append(txt[i:k])
        depth, m = 0, j
        while True:
            if txt[m] == "(":
                depth += 1
            elif txt[m] == ")":
                depth -= 1
                if depth == 0:
                    break
            m += 1
        i = m + 1
        if txt[i:i + 1] == "\n":
            i += 1


def build():
    os.makedirs(OUT, exist_ok=True)
    io = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)
    for name, (lib, src, remap, note) in BUILD.items():
        strip_zones = False
        fp = pcbnew.FootprintLoad(lib, src)
        if fp is None:
            raise SystemExit(f"missing {lib}:{src}")
        if remap == "strip-epad-vias":
            for p in list(fp.Pads()):
                if p.GetNumber() == "41" and p.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                    fp.Remove(p)
            # The stock antenna keepout is 48 x 21 mm (15 mm either side of the module). The board
            # adds its own, sized to the placement (place.py).
            strip_zones = True
        elif remap:
            for p in fp.Pads():
                p.SetNumber(remap[p.GetNumber()])
        # easyeda puts a 3D path relative to the repo; drop it (renders use the board only)
        if lib == LCSC:
            fp.Models().clear()
        fp.SetFPID(pcbnew.LIB_ID("exhaust", name))
        fp.SetLibDescription(note)
        io.FootprintSave(OUT, fp)
        if strip_zones:  # footprint Zones() isn't iterable from SWIG; drop the blocks from the file
            path = os.path.join(OUT, name + ".kicad_mod")
            with open(path) as fh:
                txt = fh.read()
            with open(path, "w") as fh:
                fh.write(_drop_blocks(txt, "(zone"))
        print("built", name)


if __name__ == "__main__":
    build()

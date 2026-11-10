"""Build pcb/carrier/lib/carrier.pretty: carrier-only footprints from pcb/lib/lcsc.pretty (easyeda2kicad).

Run with KiCad's bundled Python (pcb/carrier/gen/run.sh does).
- C5378721 SK6812SIDE-A (OPSCO datasheet SK6812SIDE-A-012 Rev B/2, §5): pad 1 DIN, 2 VDD, 3 DOUT, 4 GND.
  Symbol LED:SK6812: 1 VSS, 2 DIN, 3 VDD, 4 DOUT. Emission direction against the board edge: check at layout.
"""
import os
import pcbnew

HERE = os.path.dirname(os.path.abspath(__file__))
LCSC = os.path.normpath(os.path.join(HERE, "..", "..", "lib", "lcsc.pretty"))
OUT = os.path.normpath(os.path.join(HERE, "..", "lib", "carrier.pretty"))

BUILD = {
    "LED_SK6812SIDE-A_4.0x1.6mm": ("LED-SMD_4P-L4.0-W1.6-L", {"1": "2", "2": "3", "3": "4", "4": "1"},
                                   "C5378721 SK6812SIDE-A; pads renumbered to LED:SK6812"),
}

os.makedirs(OUT, exist_ok=True)
io = pcbnew.PCB_IO_MGR.FindPlugin(pcbnew.PCB_IO_MGR.KICAD_SEXP)
for name, (src, remap, note) in BUILD.items():
    fp = pcbnew.FootprintLoad(LCSC, src)
    if fp is None:
        raise SystemExit(f"missing {LCSC}:{src}")
    for p in fp.Pads():
        p.SetNumber(remap[p.GetNumber()])
    fp.Models().clear()
    fp.SetFPID(pcbnew.LIB_ID("carrier", name))
    fp.SetLibDescription(note)
    io.FootprintSave(OUT, fp)
    print("built", name)

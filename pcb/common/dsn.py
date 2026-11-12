"""Specctra DSN export / SES import around the locked placement (D-010).

  dsn.py export <placed.kicad_pcb> <out.dsn>
  dsn.py import <placed.kicad_pcb> <in.ses> <out.kicad_pcb>   # adds GND pours, saves the candidate

Run with KiCad's bundled Python. The barrier keepouts (place.py) go into the DSN as keepouts, so the
router can't cross them; the 3.0 / 1.5 mm domain rules are then checked by kicad-cli DRC
(the board's .kicad_dru), which the router never stands in for.
"""
import sys

import pcbnew


def gnd_zone(board, layer, netname="GND", priority=0):
    net = board.FindNet(netname)
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net)
    z.SetAssignedPriority(priority)
    z.SetLocalClearance(pcbnew.FromMM(0.3))
    z.SetMinThickness(pcbnew.FromMM(0.25))
    z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
    bb = board.GetBoardEdgesBoundingBox()
    o = z.Outline()
    o.NewOutline()
    for x, y in ((bb.GetLeft(), bb.GetTop()), (bb.GetRight(), bb.GetTop()),
                 (bb.GetRight(), bb.GetBottom()), (bb.GetLeft(), bb.GetBottom())):
        o.Append(pcbnew.VECTOR2I(x, y))
    board.Add(z)


if __name__ == "__main__":
    cmd = sys.argv[1]
    board = pcbnew.LoadBoard(sys.argv[2])
    if cmd == "export":
        if not pcbnew.ExportSpecctraDSN(board, sys.argv[3]):
            raise SystemExit("DSN export failed")
    elif cmd == "import":
        if not pcbnew.ImportSpecctraSES(board, sys.argv[3]):
            raise SystemExit("SES import failed")
        # Node GND on both layers; DRC rules keep it 3 mm off field copper and the keepouts
        # keep it out of the barrier and the antenna area.
        gnd_zone(board, pcbnew.F_Cu)
        gnd_zone(board, pcbnew.B_Cu)
        filler = pcbnew.ZONE_FILLER(board)
        filler.Fill(board.Zones())
        pcbnew.SaveBoard(sys.argv[4], board)
    print("ok", cmd)

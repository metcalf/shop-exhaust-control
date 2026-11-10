#!/usr/bin/env bash
# Layout pipeline (D-010). Netlist from the schematic (the source since layout, D-035), project
# footprints, scripted placement, then DRC on the placed board.
set -euo pipefail
cd "$(dirname "$0")/../.."
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
K=pcb/tools/kicad-cli
export KICAD_CONFIG_HOME="$PWD/.kicad-config"
$K sch export netlist --format kicadsexpr -o pcb/reports/exhaust.net pcb/exhaust.kicad_sch
.venv/bin/python pcb/gen/check.py pcb/reports/exhaust.net | tee pcb/reports/netlist-check.txt
$KPY pcb/layout/footprints.py 2>pcb/reports/layout-py.log
$KPY pcb/layout/place.py pcb/reports/exhaust.net pcb/exhaust-placed.kicad_pcb 2>>pcb/reports/layout-py.log
cp pcb/exhaust.kicad_pro pcb/exhaust-placed.kicad_pro
cp pcb/exhaust.kicad_dru pcb/exhaust-placed.kicad_dru
$K pcb drc --severity-all --schematic-parity -o pcb/reports/drc-placed.rpt pcb/exhaust-placed.kicad_pcb || true
grep -E "^\*\*|Found" pcb/reports/drc-placed.rpt || true

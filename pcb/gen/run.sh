#!/usr/bin/env bash
# Regenerate the schematic and run every check; reports land in pcb/reports/.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=.venv/bin/python
K=pcb/tools/kicad-cli
mkdir -p pcb/reports pcb/reports/svg
$PY ${BUILD:-pcb/gen/build.py}
$K sch erc --severity-all --exit-code-violations -o pcb/reports/erc.rpt pcb/exhaust.kicad_sch
$K sch export netlist --format kicadsexpr -o pcb/reports/exhaust.net pcb/exhaust.kicad_sch
$PY pcb/gen/check.py pcb/reports/exhaust.net | tee pcb/reports/netlist-check.txt
$K sch export svg -o pcb/reports/svg pcb/exhaust.kicad_sch >/dev/null
$K sch export bom --fields 'Reference,Value,Footprint,LCSC,${QUANTITY}' --group-by 'Value,Footprint,LCSC' \
   -o pcb/reports/bom-raw.csv pcb/exhaust.kicad_sch >/dev/null
echo "ok"

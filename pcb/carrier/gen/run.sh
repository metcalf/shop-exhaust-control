#!/usr/bin/env bash
# Carrier schematic checks (ERC, netlist assertions, SVG, raw BOM); reports land in pcb/carrier/reports/.
# build.py is the source until layout starts; set REGENERATE=0 once the .kicad_sch is edited by hand.
set -euo pipefail
cd "$(dirname "$0")/../../.."
PY=.venv/bin/python
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
K=pcb/tools/kicad-cli
C=pcb/carrier
mkdir -p $C/reports/svg
$KPY $C/gen/footprints.py 2>/dev/null
if [ "${REGENERATE:-1}" = 1 ]; then $PY $C/gen/build.py; fi
$K sch erc --severity-all --exit-code-violations -o $C/reports/erc.rpt $C/carrier.kicad_sch
$K sch export netlist --format kicadsexpr -o $C/reports/carrier.net $C/carrier.kicad_sch
$PY $C/gen/check.py $C/reports/carrier.net | tee $C/reports/netlist-check.txt
$K sch export svg -o $C/reports/svg $C/carrier.kicad_sch >/dev/null
$K sch export bom --fields 'Reference,Value,Footprint,LCSC,${DNP},${QUANTITY}' --group-by 'Value,Footprint,LCSC,${DNP}' \
   -o $C/reports/bom-raw.csv $C/carrier.kicad_sch >/dev/null
echo "ok"

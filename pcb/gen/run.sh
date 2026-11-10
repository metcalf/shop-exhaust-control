#!/usr/bin/env bash
# Run every schematic check (ERC, netlist assertions, SVG, raw BOM); reports land in pcb/reports/.
set -euo pipefail
cd "$(dirname "$0")/../.."
PY=.venv/bin/python
K=pcb/tools/kicad-cli
mkdir -p pcb/reports pcb/reports/svg
# Since layout started (2026-11-09, D-035) pcb/exhaust.kicad_sch is the source and build.py is frozen.
# Regenerating would overwrite GUI edits and the project-library footprints, so it needs an explicit opt-in.
if [ "${REGENERATE:-0}" = 1 ]; then $PY ${BUILD:-pcb/gen/build.py}; fi
$K sch erc --severity-all --exit-code-violations -o pcb/reports/erc.rpt pcb/exhaust.kicad_sch
$K sch export netlist --format kicadsexpr -o pcb/reports/exhaust.net pcb/exhaust.kicad_sch
$PY pcb/gen/check.py pcb/reports/exhaust.net | tee pcb/reports/netlist-check.txt
$K sch export svg -o pcb/reports/svg pcb/exhaust.kicad_sch >/dev/null
$K sch export bom --fields 'Reference,Value,Footprint,LCSC,${QUANTITY}' --group-by 'Value,Footprint,LCSC' \
   -o pcb/reports/bom-raw.csv pcb/exhaust.kicad_sch >/dev/null
echo "ok"

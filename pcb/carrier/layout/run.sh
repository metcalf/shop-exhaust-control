#!/usr/bin/env bash
# Carrier layout pipeline: schematic checks -> mech handoff -> locked placement -> DRC (barrier rules).
set -euo pipefail
cd "$(dirname "$0")/../../.."
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
K=pcb/tools/kicad-cli
C=pcb/carrier
export KICAD_CONFIG_HOME="$PWD/.kicad-config"
REGENERATE=${REGENERATE:-1} $C/gen/run.sh >/dev/null
[ -f mech/out/carrier_layout.json ] || .venv/bin/python mech/concept.py --no-views
$KPY $C/layout/place.py $C/reports/carrier.net $C/carrier-placed.kicad_pcb 2>$C/reports/layout-py.log
cp $C/carrier.kicad_pro $C/carrier-placed.kicad_pro
cp $C/carrier.kicad_dru $C/carrier-placed.kicad_dru
$K pcb drc --severity-all -o $C/reports/drc-placed.rpt $C/carrier-placed.kicad_pcb >/dev/null || true
grep -E '^\*\* Found|^\[' $C/reports/drc-placed.rpt | sed -E 's/^\[([a-z_]+)\].*/\1/' | sort | uniq -c
$K pcb render --side top -o $C/reports/placed-front.png $C/carrier-placed.kicad_pcb >/dev/null 2>&1 || true
$K pcb render --side bottom -o $C/reports/placed-back.png $C/carrier-placed.kicad_pcb >/dev/null 2>&1 || true
echo ok

#!/usr/bin/env bash
# Freerouting candidate from the locked placement (D-010, STATE next action 2d).
# Needs the jar in pcb/tools/bin/ (gitignored):
#   curl -L -o pcb/tools/bin/freerouting-2.5.0.jar \
#     https://github.com/freerouting/freerouting/releases/download/v2.5.0/freerouting-2.5.0.jar
# Steps: placed board -> DSN (KiCad) -> Freerouting headless -> SES -> routed board + GND pours -> DRC + renders.
set -euo pipefail
cd "$(dirname "$0")/../.."
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
K=pcb/tools/kicad-cli
JAR=${JAR:-pcb/tools/bin/freerouting-2.5.0.jar}
OUT=pcb/route
export KICAD_CONFIG_HOME="$PWD/.kicad-config"
mkdir -p $OUT
$KPY pcb/layout/dsn.py export pcb/exhaust-placed.kicad_pcb $OUT/exhaust.dsn 2>>pcb/reports/layout-py.log
java -jar "$JAR" -de $OUT/exhaust.dsn -do $OUT/exhaust.ses -mp ${PASSES:-100} --gui.enabled=false | tee $OUT/freerouting.log
$KPY pcb/layout/dsn.py import pcb/exhaust-placed.kicad_pcb $OUT/exhaust.ses pcb/exhaust-freerouting.kicad_pcb 2>>pcb/reports/layout-py.log
cp pcb/exhaust.kicad_pro pcb/exhaust-freerouting.kicad_pro
cp pcb/exhaust.kicad_dru pcb/exhaust-freerouting.kicad_dru
$K pcb drc --severity-all --refill-zones -o pcb/reports/drc-freerouting.rpt pcb/exhaust-freerouting.kicad_pcb || true
grep -E "Found" pcb/reports/drc-freerouting.rpt
for side in top bottom; do
  $K pcb render --side $side --width 1600 --height 2600 -o pcb/reports/render/freerouting-$side.png pcb/exhaust-freerouting.kicad_pcb
done

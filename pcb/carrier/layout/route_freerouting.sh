#!/usr/bin/env bash
# Freerouting candidate for the carrier, from the locked placement (pcb/carrier/layout/run.sh first).
# Needs the jar in pcb/tools/bin/ (gitignored):
#   curl -L -o pcb/tools/bin/freerouting-2.5.0.jar \
#     https://github.com/freerouting/freerouting/releases/download/v2.5.0/freerouting-2.5.0.jar
# Steps: placed board -> DSN (KiCad) -> Freerouting headless -> SES -> routed board -> DRC (barrier rules) + renders.
set -euo pipefail
cd "$(dirname "$0")/../../.."
KPY=/Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3
K=pcb/tools/kicad-cli
JAR=${JAR:-pcb/tools/bin/freerouting-2.5.0.jar}
C=pcb/carrier
OUT=$C/route
export KICAD_CONFIG_HOME="$PWD/.kicad-config"
mkdir -p $OUT
$KPY pcb/common/dsn.py export $C/carrier-placed.kicad_pcb $OUT/carrier.dsn 2>>$C/reports/layout-py.log
java -jar "$JAR" -de $OUT/carrier.dsn -do $OUT/carrier.ses -mp ${PASSES:-100} --gui.enabled=false | tee $OUT/freerouting.log
$KPY pcb/common/dsn.py import $C/carrier-placed.kicad_pcb $OUT/carrier.ses $C/carrier-freerouting.kicad_pcb 2>>$C/reports/layout-py.log
cp $C/carrier.kicad_pro $C/carrier-freerouting.kicad_pro
cp $C/carrier.kicad_dru $C/carrier-freerouting.kicad_dru
$K pcb drc --severity-all --refill-zones -o $C/reports/drc-freerouting.rpt $C/carrier-freerouting.kicad_pcb || true
grep -E "Found" $C/reports/drc-freerouting.rpt
for side in top bottom; do
  $K pcb render --side $side -o $C/reports/freerouting-$side.png $C/carrier-freerouting.kicad_pcb >/dev/null 2>&1 || true
done

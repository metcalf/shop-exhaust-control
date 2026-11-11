#!/usr/bin/env bash
# Fetch the Waveshare ESP32-S3-Touch-LCD-3.5 STEP (22 MB, not committed) into mech/vendor/.
set -euo pipefail
cd "$(dirname "$0")/vendor"
URL=https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-3.5/ESP32-S3-Touch-LCD-3.5-2Dand3D.zip
[ -f ESP32-S3-Touch-LCD-3_5.stp ] && { echo "already present"; exit 0; }
curl -sSL -A Mozilla/5.0 -o 2d3d.zip "$URL"
unzip -o -q 2d3d.zip ESP32-S3-Touch-LCD-3_5.stp
rm -f 2d3d.zip
echo "fetched mech/vendor/ESP32-S3-Touch-LCD-3_5.stp"

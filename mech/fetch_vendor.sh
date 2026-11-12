#!/usr/bin/env bash
# The Waveshare ESP32-S3-Touch-LCD-3.5 STEP (23 MB) is committed in mech/vendor/ so the model doesn't depend on
# Waveshare's download staying up. This script re-fetches it from upstream into a temp dir and compares it with
# the committed copy (pinned SHA-256), to spot a Waveshare revision. It never overwrites the committed file.
set -euo pipefail
cd "$(dirname "$0")/vendor"
URL=https://files.waveshare.com/wiki/ESP32-S3-Touch-LCD-3.5/ESP32-S3-Touch-LCD-3.5-2Dand3D.zip
PINNED=12b36e5977ce2ff08e7dbe10adb7fd3c69b1601048924008b8956a5af94c237a
have=$(shasum -a 256 ESP32-S3-Touch-LCD-3_5.stp | cut -d' ' -f1)
[ "$have" = "$PINNED" ] || echo "committed STEP doesn't match the pinned hash ($have)"
tmp=$(mktemp -d)
trap 'rm -rf "$tmp"' EXIT
curl -sSL -A Mozilla/5.0 -o "$tmp/2d3d.zip" "$URL"
unzip -o -q "$tmp/2d3d.zip" ESP32-S3-Touch-LCD-3_5.stp -d "$tmp"
up=$(shasum -a 256 "$tmp/ESP32-S3-Touch-LCD-3_5.stp" | cut -d' ' -f1)
if [ "$up" = "$PINNED" ]; then echo "upstream STEP unchanged"; else echo "upstream STEP differs ($up): review before replacing mech/vendor/"; fi

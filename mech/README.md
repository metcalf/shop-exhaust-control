# Mechanical (build123d, D-011)

Concept enclosure for the Waveshare ESP32-S3-Touch-LCD-3.5 + carrier + SEN65 (D-056, D-057).

- `fetch_vendor.sh`: downloads the Waveshare STEP (22 MB, gitignored) into `vendor/`. Run it first.
- `params.py`: frame E (+x right, +y up, +z out of the front) and every design choice.
- `waveshare.py`: Waveshare geometry read from the STEP. Never retype these numbers.
- `concept.py`: builds the bezel, rear shell, carrier, SEN65, foam, LEDs, spacers and terminal blocks. It writes `out/concept.step` (our parts only), `out/stackup.json`, `out/carrier_layout.json` (input to `pcb/carrier/layout`) and SVG/PNG views.
- `tests/`: geometry checks. Run `.venv/bin/python -m pytest mech/tests`, which takes about 2 min.

Status and open items: `docs/mech-concept.md`.

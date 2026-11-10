# GPIO47/48 supply rail on ESP32-S3-WROOM-1-N16R8

Checked 2026-11-09 against PDFs downloaded from espressif.com that day:
- **DS-S3**: ESP32-S3 Series Datasheet v2.2
- **DS-MOD**: ESP32-S3-WROOM-1 & WROOM-1U Datasheet v1.8
- **TRM**: ESP32-S3 Technical Reference Manual v1.8

## 1. Which power domain powers GPIO47/48?

It is not fixed. It is **VDD_SPI or VDD3P3_CPU, chosen by eFuse (ROM time) and a register (run time)**.

- DS-S3 Table 2-1 (Pin Overview), pins 36 (SPICLK_N, GPIO48) and 37 (SPICLK_P, GPIO47): Pin Providing Power = `VDD_SPI/VDD3P3_CPU`.
- DS-S3 Table 2-1 note 3: "Pin Providing Power (either VDD3P3_CPU or VDD_SPI) is decided by eFuse bit EFUSE_PIN_POWER_SELECTION ... and can be configured via the IO_MUX_PAD_POWER_CTRL bit".
- TRM eFuse chapter: "EFUSE_PIN_POWER_SELECTION Represents the power supply for GPIO33 ~ GPIO37, GPIO47, and GPIO48 while ROM code is executed. 0: VDD3P3_CPU. 1: VDD_SPI. (RO)"
- TRM IO MUX chapter: "IO_MUX_PAD_POWER_CTRL Select power voltage for GPIO33 ~ 37 and GPIO47 ~ 48. 1: select VDD_SPI 1.8 V; 0: select VDD3P3_CPU 3.3 V. (R/W)"

So "GPIO47/48 are in VDD_SPI" is only conditionally true. The documents do not state the default of either control for a non-V chip, and I could not read the register reset value from the PDF text (garbled). **Unconfirmed.** On the N16R8 (see 3) the answer is about 3.3 V whichever rail is selected.

## 2. How is VDD_SPI voltage selected?

DS-S3 sec 3.2, Table 3-4 (identical to DS-MOD sec 4.2, Table 4-4):

| EFUSE_VDD_SPI_FORCE | GPIO45 | EFUSE_VDD_SPI_TIEH | Source | Voltage |
|---|---|---|---|---|
| 0 | 0 | ignored | VDD3P3_RTC via RSPI | 3.3 V |
| 0 | 1 | ignored | flash voltage regulator | 1.8 V |
| 1 | ignored | 1 | VDD3P3_RTC via RSPI | 3.3 V |
| 1 | ignored | 0 | flash voltage regulator | 1.8 V |

- DS-S3 sec 3.2 text: "(Default) 3.3 V supplied by VDD3P3_RTC via RSP I". RSPI = 14 ohm typ (DS-S3 Table 5-3).
- GPIO45 default: DS-S3 Table 3-1 / DS-MOD Table 4-1: "Weak pull-down", bit value 0. R_PD is typ 45 kohm (DS-S3 Table 5-4). A floating GPIO45 therefore reads 0, which selects 3.3 V **if FORCE = 0**.
- TRM sec 8.4: "GPIO45 = 0, VDD_SPI pin is powered directly from VDD3P3_RTC via resistor RSPI. Typically this voltage is 3.3 V"; "This functionality can be overridden by setting eFuse bit EFUSE_VDD_SPI_FORCE to 1, in which case the EFUSE_VDD_SPI_TIEH determines the VDD_SPI voltage".
- TRM eFuse field descriptions: TIEH "0: connect to 1.8 V Flash Voltage Regulator. 1: Short connected to VDD3P3_RTC_IO"; XPD = whether the regulator is powered up; FORCE = whether to use the eFuse XPD/TIEH values.

## 3. N16R8 specifics and V variants

- DS-MOD Table 1-1: ESP32-S3-WROOM-1-N16R8 = 16 MB Quad SPI flash, 8 MB Octal SPI PSRAM, -40 to 65 C. The PSRAM is in the chip package (ESP32-S3R8).
- DS-S3 Table 1-1 (chip): ESP32-S3R8 VDD_SPI = **3.3 V**. ESP32-S3R16V = 1.8 V. ESP32-S3R8V (EOL) = 1.8 V.
- DS-MOD Table 1-1 footnote 7: "Please note that the VDD_SPI voltage is 1.8 V for ESP32-S3-WROOM-1-N16R16VA and ESP32-S3-WROOM-1U-N16R16VA only." There is no R8V module in the list.
- DS-MOD Table 3-1 note c (on IO47, IO48): "For modules embedded with ESP32-S3R16V, as the VDD_SPI voltage of the ESP32-S3R16V chip is set to 1.8 V, the working voltage for GPIO47 and GPIO48 is also 1.8 V, which is different from other GPIOs."
- DS-S3 Table 2-1 note 4: "For ESP32-S3R8V and ESP32-S3R16V chip, as the VDD_SPI voltage has been set to 1.8 V, the working voltage for pins SPICLK_N and SPICLK_P (GPIO47 and GPIO48) would also be 1.8 V, which is different from other GPIOs."
- DS-MOD sec 8 (Module Schematics) note: "For modules with PSRAM, the VDD_SPI voltage is fixed to 3.3 V or 1.8 V via eFuse, so their VDD_SPI voltage will not be affected by the GPIO45 level. However, for other modules, please ensure that GPIO45 is not pulled high when the module is powered up by the external circuit."
- Flash and PSRAM supply ranges (DS-MOD Tables 6-8, 6-9): 3.3 V is 2.7 to 3.6 V, 1.8 V is 1.62/1.65 to 2.0 V. The DS-MOD has no N16R8-specific sentence naming the flash or PSRAM voltage. The 3.3 V figure comes from the chip table row for ESP32-S3R8.
- No footnote applies to the N16R8 for GPIO47/48. The only GPIO47/48 footnote is the R16V one.

## 4. Restrictions on GPIO47/48 for the N16R8

None documented. DS-MOD Table 3-1 note b restricts only IO35, IO36 and IO37: "For modules with Octal SPI PSRAM, i.e., modules embedded with ESP32-S3R8 or ESP32-S3R16V, pins IO35, IO36, and IO37 are connected to the Octal SPI PSRAM and are not available for other uses." IO47 (module pin 24) and IO48 (pin 25) are listed as general I/O with no restriction. I did not search the TRM for other uses of these pads.

## 5. Protection diodes, clamps, abs-max

- **No pad clamp or protection-diode statement found** in DS-S3 v2.2 or DS-MOD v1.8 (searched "clamp", "diode", "protection"). The only ESD figure is qualification: HBM +/-2000 V (DS-S3 reliability table). That is not a clamp spec.
- DS-S3 Table 5-1 (Absolute Maximum Ratings) gives only "Input power pins: allowed input voltage -0.3 to 3.6 V". DS-MOD Table 6-1 gives only VDD33 -0.3 to 3.6 V. **There is no per-GPIO abs-max relative to the rail.**
- Closest figure: DS-S3 Table 5-4 (DS-MOD Table 6-3): V_IH max = VDD + 0.3 V, V_IL min = -0.3 V, with VDD defined as "voltage from a power pin of a respective power domain". That is a recommended input range, not an abs-max, and it is relative to the pad's own rail.
- Consequence: on a 1.8 V rail, a pull-up to 3.3 V would exceed VDD + 0.3 V (2.1 V), and nothing in the documents makes that safe. On the N16R8 the pad rail is about 3.3 V (VDD3P3_CPU, or VDD_SPI = VDD3P3_RTC minus the 14 ohm drop), so a 10 kohm pull-up to 3.3 V is within V_IH max.

## 6. Confirming the actual setting on a module

- Espressif's datasheets and TRM give eFuse field names only (EFUSE_VDD_SPI_FORCE, EFUSE_VDD_SPI_TIEH, EFUSE_VDD_SPI_XPD, EFUSE_PIN_POWER_SELECTION). They say nothing about boot-log output. **Boot-log indication not found.**
- `espefuse.py summary` is not documented in these PDFs. From the esptool 4.9.0 source on this machine (`espefuse/efuse_defs/esp32s3.yaml`, `esp32s3/fields.py`; secondary, not Espressif datasheet): the summary lists VDD_SPI_XPD, VDD_SPI_TIEH and VDD_SPI_FORCE, and prints "Flash voltage (VDD_SPI) set to 3.3V by efuse." or "... set to 1.8V by efuse.", or "determined by GPIO45 on reset" when FORCE = 0.
- I did not check whether `summary` shows PIN_POWER_SELECTION. Not run on hardware.

## Conclusion

On the ESP32-S3-WROOM-1-N16R8 the chip is ESP32-S3R8, which DS-S3 Table 1-1 lists at VDD_SPI = 3.3 V. DS-MOD footnote 7 and Table 3-1 note c give 1.8 V only for the N16R16VA module and the R16V chip. With GPIO45 left floating the weak pull-down gives bit 0, which selects 3.3 V when VDD_SPI_FORCE = 0, and the module datasheet says PSRAM modules fix VDD_SPI by eFuse so GPIO45 does not matter. So GPIO47/48 should be about 3.3 V whichever of VDD_SPI or VDD3P3_CPU supplies the pad. Unconfirmed: (a) the actual eFuse values on a delivered N16R8 (read them with `espefuse.py summary`); (b) the defaults of EFUSE_PIN_POWER_SELECTION and IO_MUX_PAD_POWER_CTRL; (c) any per-pad clamp or abs-max, none of which is documented.

**Contradicts or refines the premise:**
1. GPIO47/48 are not simply "in VDD_SPI". They are `VDD_SPI/VDD3P3_CPU`, selected by EFUSE_PIN_POWER_SELECTION and IO_MUX_PAD_POWER_CTRL.
2. GPIO45 is not what sets the voltage on the N16R8. Per the DS-MOD schematic note, PSRAM modules fix VDD_SPI via eFuse, so GPIO45 is ignored. The eFuse values themselves are not published.
3. "Only V variants force 1.8 V": true of the module list (N16R16VA only). The chip table also lists the EOL ESP32-S3R8V at 1.8 V. Datasheets say "set to 1.8 V" and "via eFuse" but do not name the V-variant eFuse bits.
4. There is no documented pad clamp or per-pin abs-max relative to the rail, so pull-up safety at 1.8 V rests on V_IH max = VDD + 0.3 V only.

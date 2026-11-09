"""Part catalogue for build.py: key -> (lib_id, footprint, LCSC, value, ref prefix).

LCSC numbers and stock come from sourcing/*.md (checked 2026-10-28). Footprints are
KiCad stock; confirm each against the LCSC drawing before layout.
"""

P = {
    # passives (JLC basic; LCSC numbers assigned per value in the priced parts list)
    "R0603": ("Device:R", "Resistor_SMD:R_0603_1608Metric", "", "", "R"),
    "R1206": ("Device:R", "Resistor_SMD:R_1206_3216Metric", "", "", "R"),
    "C0603": ("Device:C", "Capacitor_SMD:C_0603_1608Metric", "", "", "C"),
    "C0805": ("Device:C", "Capacitor_SMD:C_0805_2012Metric", "", "", "C"),
    "C1206": ("Device:C", "Capacitor_SMD:C_1206_3216Metric", "", "", "C"),
    "L": ("Device:L", "Inductor_SMD:L_Bourns-SRN4018", "C135262", "2.2u", "L"),
    "C0805_25V": ("Device:C", "Capacitor_SMD:C_0805_2012Metric", "", "", "C"),

    # MCU
    "ESP": ("RF_Module:ESP32-S3-WROOM-1", "RF_Module:ESP32-S3-WROOM-1", "C2913202",
            "ESP32-S3-WROOM-1-N16R8", "U"),

    # isolation (sourcing/isolation.md)
    "OPTO_PWM": ("Isolator:H11L1", "Package_DIP:SMDIP-6_W9.53mm", "C7435535", "H11L1S-TA1-L", "U"),
    "PC817": ("Isolator:PC817", "Package_DIP:SMDIP-4_W9.53mm", "C3008369", "PC817C-S", "U"),
    "BRIDGE": ("Diode_Bridge:MB6S", "Diode_SMD:Diode_Bridge_Vishay_MBLS", "C2488", "MB10S", "D"),
    "NFET": ("Transistor_FET:2N7002", "Package_TO_SOT_SMD:SOT-23", "C8545", "2N7002", "Q"),
    "NFET_LL": ("Transistor_FET:AO3400A", "Package_TO_SOT_SMD:SOT-23", "C20917", "AO3400A", "Q"),
    "PFET": ("Transistor_FET:AO3401A", "Package_TO_SOT_SMD:SOT-23", "C15127", "AO3401A", "Q"),

    # power (sourcing/power.md)
    "USBC": ("Connector:USB_C_Receptacle_USB2.0_16P",
             "Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12", "C165948", "TYPE-C-31-M-12", "J"),
    "TVS5": ("Device:D_TVS", "Diode_SMD:D_SMA", "C113952", "SMAJ5.0A", "D"),
    "TVS48": ("Device:D_TVS", "Diode_SMD:D_SMB", "C693510", "SMBJ48CA", "D"),
    "TVS15": ("Device:D_TVS", "Diode_SMD:D_SOD-123F", "C123802", "SMF15A", "D"),
    "ESD": ("Power_Protection:USBLC6-2SC6", "Package_TO_SOT_SMD:SOT-23-6", "C2827654", "USBLC6-2SC6", "U"),
    "LDO5F": ("Regulator_Linear:HT75xx-1-SOT89", "Package_TO_SOT_SMD:SOT-89-3", "C41355185", "HT7550-1", "U"),
    "D_SIG": ("Device:D", "Diode_SMD:D_SOD-123", "C81598", "1N4148W", "D"),

    # UI and connectors (sourcing/ui-connectors.md)
    "ENC": ("Device:RotaryEncoder_Switch",
            "Rotary_Encoder:RotaryEncoder_Alps_EC11E-Switch_Vertical_H20mm", "C255515", "EC11E18244A5", "SW"),
    "TACT": ("Switch:SW_Push", "Button_Switch_THT:SW_PUSH_6mm_H9.5mm", "C2845262", "TC-6610-9.5", "SW"),
    "RGB": ("Device:LED_ARGB", "LED_SMD:LED_Cree-PLCC4_3.2x2.8mm_CCW", "C601699", "RGB CA 3528", "D"),
    "TERM2": ("Connector:Screw_Terminal_01x02",
              "TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-2-3.5-H_1x02_P3.50mm_Horizontal",
              "C474930", "KF128L-3.5-2P", "J"),
    "TERM4": ("Connector:Screw_Terminal_01x04",
              "TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-4-3.5-H_1x04_P3.50mm_Horizontal",
              "C557656", "XY350V-3.5-4P", "J"),
    "SENCONN": ("Connector_Generic:Conn_01x06",
                "Connector_JST:JST_GH_SM06B-GHS-TB_1x06-1MP_P1.25mm_Horizontal", "C133065", "SM06B-GHS-TB", "J"),
    "DISP_HDR": ("Connector:Conn_01x08_Socket", "Connector_PinSocket_2.54mm:PinSocket_1x08_P2.54mm_Vertical",
                 "C2897371", "display 1x8", "J"),
    "TP": ("Connector:TestPoint", "TestPoint:TestPoint_Pad_D1.5mm", "", "", "TP"),

    # SEN6x connector (SEN6x datasheet §3 Table 17, sourcing/off-board.md):
    # 1 VDD, 2 GND, 3 SDA, 4 SCL, 5 GND, 6 VDD
    "SEN_PINOUT": {"Pin_1": "+3V3_SEN", "Pin_2": "GND", "Pin_3": "SEN_SDA", "Pin_4": "SEN_SCL",
                   "Pin_5": "GND", "Pin_6": "+3V3_SEN"},
    "SEN_NC": (),

    # indicator series resistors, ~15 mA per colour at 5 V (pcb/design.md §6)
    "R_RED": "200",
    "R_GB": "120",
}

# 3.3 V buck: AP63203WU-7, fixed 3.3 V, 35 V abs max VIN (D-040; datasheet DS41326 Rev. 2-2).
# FB goes straight to the output, EN to VIN (Fig. 21). 2.2 uH rather than Table 2's 3.9 uH: see
# pcb/design.md §1. The 10 uF is the only capacitance allowed on +5V (USB sink limit; check.py).
P["REG33"] = ("Regulator_Switching:AP63203WU", "Package_TO_SOT_SMD:TSOT-23-6", "C780769", "AP63203WU-7", "U")
P["REG33_NETS"] = {"IN": "+5V", "EN": "+5V", "SW": "BUCK_LX", "FB": "+3V3", "BST": "BUCK_BST", "GND": "GND"}
P["REG33_NC"] = ()
P["REG33_EXTRAS"] = [
    ("C0805", "10u", ("+5V", "GND")),
    ("C0603", "100n", ("BUCK_BST", "BUCK_LX")),
    ("L", "2.2u", ("BUCK_LX", "+3V3")),
    ("C1206", "22u", ("+3V3", "GND")),
    ("C1206", "22u", ("+3V3", "GND")),
]

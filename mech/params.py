"""Concept enclosure parameters (D-011, D-056, D-057).

Frame E (all mech and the carrier layout use it): +x right, +y up, +z out of the front, looking at the
display from the room. Origin = centre of the Waveshare lens, z = 0 at the lens's rear face plane of the
STEP's own origin (lens front is at z = +1.1). Waveshare geometry is never typed here: waveshare.py
reads it from the STEP. Values below are design choices (CHOICE) or datasheet figures (cited).
"""

# --- Waveshare STEP -> frame E -------------------------------------------------------------------
# Board rotated so the USB-C is on the left seen from the front (D-057): rotate -90 deg about z.
WS_ROT_Z = -90.0

# --- board stack ---------------------------------------------------------------------------------
SPACER = 6.0            # CHOICE: standard M2 x 6 nylon spacer between the Waveshare SMT standoff and the carrier
CARRIER_T = 1.6         # carrier PCB thickness
MALE_HDR_BODY = 2.5     # standard 2.54 mm male header plastic body
MALE_HDR_MATE = 6.0     # standard mating pin length above the body
CARRIER_MAX_PART = 4.0  # tallest SMT part on the carrier's display side (LTV-817S SOP-4, ~3.7 mm max)

# --- carrier outline (frame E) -------------------------------------------------------------------
CARRIER_X = (-45.7, 45.7)   # CHOICE: 1.0 mm inside the inner walls; terminals left, LEDs right
CARRIER_Y = (-28.5, 28.5)   # CHOICE: within the 61 mm lens height

# --- enclosure -----------------------------------------------------------------------------------
WALL = 2.0              # MJF PA12 minimum practical wall for a sealed box (CHOICE)
CLR = 0.5               # lens / module to wall clearance
LENS_GASKET = 1.0       # foam gasket between lens front and bezel lip
BEZEL_LIP = 1.5         # bezel thickness in front of the lens
BEZEL_OVERLAP = 2.0     # lip overlaps the lens's black border (border >= 6 mm per the Waveshare drawing)
SPLIT_Z = -8.0          # bezel / rear shell split, just behind the LCD module (STEP: LCD to z -7.5)

# --- SEN65 (SEN6x datasheet v1.0 Fig. 8; mech guide v1.01 Fig. 1) -----------------------------------
SEN_L, SEN_W, SEN_H = 55.2, 25.6, 21.3   # ports on the L x W face; connector on an L x H face
SEN_GAP = 4.0           # carrier back -> module (Andrew: <= 1/4"); holds the 1/8" foam strip
FOAM_T = 3.175          # 1/8" closed-cell PE/EPDM on the module face toward the carrier
SEN_PORT_GASKET = 1.0   # gasket between the port face and the right wall
# Port positions on the L x W face, from the datasheet top view (L from the inlet end, W from the edge).
SEN_INLET_SQ = (3.2, 10.2, 2.8, 9.8)     # L0, L1, W0, W1
SEN_INLET_RD = (6.7, 18.2, 6.0)          # L centre, W centre, diameter
SEN_OUTLET = (42.4, 12.8, 20.5)          # fan / outlet L centre, W centre, diameter
SEN_IN_MIN_MM2, SEN_OUT_MIN_MM2 = 56.0, 148.0   # mech guide §2.1

# --- indicator (D-055) -----------------------------------------------------------------------------
N_LED = 6
LED_PITCH = 9.0
LED_H = 2.0             # SK6812SIDE-A height above the board (4.0 x 1.6 x 2.0)
DIFFUSER_Z_PAD = 3.0    # diffuser slot extends this far beyond the LED face height either way

# --- cables (left wall) ----------------------------------------------------------------------------
# USB-C plug envelope (USB Type-C spec: plug shell 8.34 x 2.56, 6.65 insertion; typical overmold 12 x 6.5)
USB_SHELL = (8.34, 2.56, 6.65)
USB_OVERMOLD = (12.0, 6.5, 20.0)
USB_POCKET_CLR = 1.0
CABLE_SLOTS = [  # CHOICE: (name, y centre, height, width in z) for clamp-and-foam strain reliefs
    ("fan", 14.0, 7.0, 7.0),
    ("occ", -2.0, 5.0, 5.0),
    ("dc", -14.0, 5.0, 5.0),
]

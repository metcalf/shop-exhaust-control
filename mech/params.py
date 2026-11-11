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
# Andrew (2026-11-10): carrier as close behind the Waveshare as possible. The male header is fitted with its
# plastic body on the carrier's BACK (pins pushed through from behind, soldered on the display side), so the
# socket face no longer sets the spacing: the lowest Waveshare part does (the camera, z -12.3).
CARRIER_T = 1.6         # carrier PCB thickness
MALE_HDR_BODY = 2.5     # 2.54 mm male header plastic body, on the carrier back
MALE_HDR_MATE = 6.0     # standard post length on the body's mating side (protrudes MATE - CARRIER_T)
MALE_HDR_STUB = 1.0     # tail trimmed to this behind the body
WS_CLR = 0.5            # CHOICE: lowest Waveshare part (camera) to carrier top; no carrier parts under it
# Display-side part heights (max, datasheets) by reference prefix; anything unlisted uses PART_H_DEFAULT
PART_H = {"U": 4.0,     # LTV-817S SMD-4: 4.0 max
          "D4": 2.0, "D5": 2.0, "D6": 2.0, "D7": 2.0, "D8": 2.0, "D9": 2.0,   # SK6812SIDE-A
          "Q": 1.2, "D": 1.35}
PART_H_DEFAULT = 1.4    # 0603/0805 R and C, worst case 0805 10 uF at 1.4

# --- carrier outline (frame E) -------------------------------------------------------------------
CARRIER_X = (-44.12, 44.12)  # CHOICE: 0.5 mm inside the inner walls; terminals left, LEDs right
CARRIER_Y = (-28.4, 28.4)

# --- enclosure -----------------------------------------------------------------------------------
# Andrew (2026-11-10): no bezel. The cover glass is the front face, so the outline is the glass outline.
WALL = 1.6              # Andrew: 1.6 mm SLS nylon has worked; stiffen with ribs rather than thickness
RIB_T, RIB_H = 1.2, 4.0 # back-panel ribs (inside, left of the SEN65 bay)
RIB_PITCH = 15.0
CLR = 0.5               # carrier / module to wall clearance
RIM_GASKET = 0.8        # closed-cell foam tape between the glass's black border and the wall rim
BACK_PANEL = 1.6        # Andrew: 1.6 mm back panel, screwed to the shell
SEN_BACK_CLR = 0.4      # Andrew: SEN65 to back panel
TAB_T = 2.0             # retention tabs behind the carrier at the four holes (screws from the back)
TAB_W = 5.0
SCREW_HEAD = 1.3        # M2 nylon pan head height

# --- SEN65 (SEN6x datasheet v1.0 Fig. 8; mech guide v1.01 Fig. 1) -----------------------------------
SEN_L, SEN_W, SEN_H = 55.2, 25.6, 21.3   # ports on one L x W face, connector on the opposite L x W face
# (mech guide Fig. 1 "Rear View"; datasheet: "at the side ... adjacent to the air outlet"). Standing on end
# with the ports on the right wall, the connector faces -x, into the open bay behind the carrier.
SEN_PLUG_BAY = 12.0     # CHOICE: free depth in -x from the module's rear face for the GH plug and cable bend
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
USB_POCKET_CLR = 1.0    # pocket clearance round the overmold, sideways (y)
USB_POCKET_CLR_Z = 0.5  # and in z: the carrier top is 1.5 mm below the overmold envelope (fits <= 7.5 mm tall)
USB_POCKET_FLOOR = 1.0  # local floor/roof thickness of the pocket (carrier 0.4 mm under it)
CABLE_SLOTS = [  # CHOICE: (name, y centre, height, width in z) for clamp-and-foam strain reliefs
    ("fan", 14.0, 7.0, 7.0),
    ("occ", -2.0, 5.0, 5.0),
    ("dc", -14.0, 5.0, 5.0),
]

"""
Parametric 3D model of the ARTIGIANA STAMPI / BERRY "TANICA DYNO" 5-6 L
HDPE jerry can (drawing 240703A0), reconstructed from the 2D mould drawing.

The drawing is a blow-moulded container with complex organic surfaces; this
script produces a clean, dimensionally-faithful *representative* solid that
matches the principal dimensions and features of the 6 L version:

  Overall envelope   : 202.8 (W) x 151.3 (D) x 302.7 (H) mm
  Body height to top : 290.3 mm  (base 83 + middle 135 + shoulder 72.3)
  Neck (DIN 51)      : outer flange dia 53, thread major dia ~45.4, ~27 tall
  Recessed front/back label panels, rounded body corners, threaded neck.

Output: canister_240703A0_6L.step  (AP214 STEP)
Units : millimetres.
"""

import math
import cadquery as cq

# ----------------------------------------------------------------------------
# Key dimensions taken from drawing 240703A0 (6 LT VERSION)
# ----------------------------------------------------------------------------
W = 202.8          # overall width  (front view)
D = 151.3          # overall depth  (side view)
H_BODY = 290.3     # body height up to the top shoulder face
R_CORNER = 34.0    # plan-view corner radius of the body

Z_SHOULDER = H_BODY - 72.3    # 218.0 : where the shoulder taper begins

# Neck (DIN 51 detail)
NECK_OD = 53.0
NECK_THREAD_MAJ = 49.8
NECK_THREAD_MIN = 45.4
NECK_BORE = 40.8
NECK_TOTAL_H = 27.0
NECK_PROTRUDE = 302.7 - H_BODY  # 12.4 mm above the shoulder top face
NECK_OFFSET_X = -55.0           # neck offset toward one corner


def rr_wire(w, d, r, z):
    """Return a closed rounded-rectangle Wire centred on origin at height z."""
    a, b = w / 2.0, d / 2.0
    c = 0.70710678 * r
    wp = (
        cq.Workplane("XY").workplane(offset=z)
        .moveTo(-(a - r), -b)
        .lineTo(a - r, -b)
        .threePointArc((a - r + c, -(b - r) - c), (a, -(b - r)))
        .lineTo(a, b - r)
        .threePointArc((a - r + c, (b - r) + c), (a - r, b))
        .lineTo(-(a - r), b)
        .threePointArc((-(a - r) - c, (b - r) + c), (-a, b - r))
        .lineTo(-a, -(b - r))
        .threePointArc((-(a - r) - c, -(b - r) - c), (-(a - r), -b))
        .close()
    )
    return wp.val()


# ----------------------------------------------------------------------------
# 1. Main body - lofted through rounded-rectangle cross sections
# ----------------------------------------------------------------------------
sections = [
    (0.0,        174.0, 124.0, 24.0),   # tucked-in foot / bottom
    (10.0,       194.0, 144.0, 32.0),   # rounded bottom edge
    (22.0,       W,     D,     R_CORNER),  # full section reached
    (30.0,       W,     D,     R_CORNER),  # -- straight wall --
    (120.0,      W,     D,     R_CORNER),  # -- straight wall --
    (Z_SHOULDER, W,     D,     R_CORNER),  # straight body up to shoulder
    (238.0,      W,     D,     R_CORNER),  # shoulder start (still full)
    (262.0,      190.0, 140.0, 38.0),   # shoulder draws in
    (280.0,      168.0, 120.0, 42.0),
    (H_BODY,     146.0, 104.0, 46.0),   # top shoulder face
]

wires = [rr_wire(w, d, r, z) for (z, w, d, r) in sections]
body_solid = cq.Solid.makeLoft(wires, ruled=True)

# cap the bottom and top so the loft is a closed solid
body = cq.Workplane(obj=body_solid)

# ----------------------------------------------------------------------------
# 2. Neck with helical thread
# ----------------------------------------------------------------------------
neck_top_z = H_BODY + NECK_PROTRUDE          # 302.7
neck_base_z = neck_top_z - NECK_TOTAL_H       # embed base into shoulder

neck = (
    cq.Workplane("XY").workplane(offset=neck_base_z)
    .circle(NECK_OD / 2.0).extrude(3.0)          # bottom flange
)
neck = (
    neck.faces(">Z").workplane()
    .circle(NECK_THREAD_MAJ / 2.0).extrude(NECK_TOTAL_H - 3.0)
)

# Helical thread ridge swept around the neck barrel
pitch = 5.2
thread_len = NECK_TOTAL_H - 6.0
try:
    helix = cq.Wire.makeHelix(pitch=pitch, height=thread_len,
                              radius=NECK_THREAD_MIN / 2.0)
    path = cq.Workplane(obj=helix)
    thread = (
        cq.Workplane("XZ")
        .center(NECK_THREAD_MIN / 2.0, 0)
        .polygon(3, 3.4)
        .sweep(path, isFrenet=True)
    )
    thread = thread.translate((0, 0, neck_base_z + 3.0))
    neck = neck.union(thread)
except Exception as e:
    print("thread sweep skipped:", e)

neck = neck.translate((NECK_OFFSET_X, 0, 0))

# ----------------------------------------------------------------------------
# 3. Assemble, then bore the neck opening
# ----------------------------------------------------------------------------
model = body.union(neck)

bore = (
    cq.Workplane("XY").workplane(offset=neck_top_z + 1.0)
    .center(NECK_OFFSET_X, 0)
    .circle(NECK_BORE / 2.0)
    .extrude(-(NECK_TOTAL_H + 30.0))
)
model = model.cut(bore)

# ----------------------------------------------------------------------------
# 4. Recessed rectangular label panels on the front & back faces
# ----------------------------------------------------------------------------
label_w, label_h, label_depth = 120.0, 150.0, 2.0
label_center_z = 150.0
try:
    front = (
        cq.Workplane("XZ").workplane(offset=-(D / 2.0))
        .center(0, label_center_z)
        .sketch().rect(label_w, label_h).vertices().fillet(6.3).finalize()
        .extrude(label_depth)
    )
    model = model.cut(front)
    model = model.cut(front.mirror("XZ"))
except Exception as e:
    print("label recess skipped:", e)

# ----------------------------------------------------------------------------
# 5. Soften the vertical body edges
# ----------------------------------------------------------------------------
try:
    model = model.edges("|Z").fillet(1.2)
except Exception as e:
    print("global fillet skipped:", e)

# ----------------------------------------------------------------------------
# Export
# ----------------------------------------------------------------------------
out = "canister_240703A0_6L.step"
cq.exporters.export(model, out)
print("Exported", out)

bb = model.val().BoundingBox()
print(f"Bounding box  X:{bb.xlen:.1f}  Y:{bb.ylen:.1f}  Z:{bb.zlen:.1f}")
print(f"Volume       : {model.val().Volume()/1000.0:.1f} cm^3")

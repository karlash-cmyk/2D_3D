"""
Parametric 3D model of the ARTIGIANA STAMPI / BERRY "TANICA DYNO" 5-6 L
HDPE jerry can (drawing 240703A0), reconstructed from the 2D mould drawing.

Generates the 6 L version body with either neck finish drawn on the sheet:

  * DIN 51        -> canister_240703A0_6L_DIN51.step
  * 45 mm BERICAP -> canister_240703A0_6L_BERICAP45.step

Run:  python3 build_canister.py            (builds both)
      python3 build_canister.py bericap    (BERICAP only)
      python3 build_canister.py din51       (DIN 51 only)

Units: millimetres.
"""

import sys
import math
import cadquery as cq

# ----------------------------------------------------------------------------
# Body dimensions from drawing 240703A0 (6 LT VERSION)
# ----------------------------------------------------------------------------
W = 202.8          # overall width  (front view)
D = 151.3          # overall depth  (side view)
H_BODY = 290.3     # body height up to the top shoulder face
R_CORNER = 34.0    # plan-view corner radius of the body
Z_SHOULDER = H_BODY - 72.3   # 218.0 : where the shoulder taper begins
NECK_OFFSET_X = -55.0        # neck offset toward one corner (from front view)


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


def build_body():
    """Loft the rounded-rectangle jerry-can body (returns a Workplane)."""
    sections = [
        (0.0,        174.0, 124.0, 24.0),   # tucked-in foot / bottom
        (10.0,       194.0, 144.0, 32.0),   # rounded bottom edge
        (22.0,       W,     D,     R_CORNER),
        (30.0,       W,     D,     R_CORNER),
        (120.0,      W,     D,     R_CORNER),
        (Z_SHOULDER, W,     D,     R_CORNER),
        (238.0,      W,     D,     R_CORNER),
        (262.0,      190.0, 140.0, 38.0),   # shoulder draws in
        (280.0,      168.0, 120.0, 42.0),
        (H_BODY,     146.0, 104.0, 46.0),   # top shoulder face
    ]
    wires = [rr_wire(w, d, r, z) for (z, w, d, r) in sections]
    return cq.Workplane(obj=cq.Solid.makeLoft(wires, ruled=True))


def helical_thread(radius, pitch, height, tri_size, z0):
    """A swept helical triangular thread ridge, base of helix at z0."""
    helix = cq.Wire.makeHelix(pitch=pitch, height=height, radius=radius)
    path = cq.Workplane(obj=helix)
    thread = (
        cq.Workplane("XZ")
        .center(radius, 0)
        .polygon(3, tri_size)
        .sweep(path, isFrenet=True)
    )
    return thread.translate((0, 0, z0))


def ratchet_ring(root_d, crest_d, height, n_teeth, z0):
    """
    Anti-rotation ratchet collar as a toothed (sawtooth) extrusion.
    root_d / crest_d are the tooth root / crest diameters.
    """
    r_root = root_d / 2.0
    r_crest = crest_d / 2.0
    pts = []
    for i in range(n_teeth):
        a0 = 2 * math.pi * i / n_teeth             # root, start of tooth
        a1 = 2 * math.pi * (i + 0.7) / n_teeth     # crest, then sharp drop
        pts.append((r_root * math.cos(a0), r_root * math.sin(a0)))
        pts.append((r_crest * math.cos(a1), r_crest * math.sin(a1)))
    ring = (
        cq.Workplane("XY").workplane(offset=z0)
        .polyline(pts).close()
        .extrude(height)
    )
    return ring


# ----------------------------------------------------------------------------
# Neck finishes
# ----------------------------------------------------------------------------
def neck_din51():
    """DIN 51 neck: flange OD 53, thread major ~49.8/minor 45.4, bore 40.8."""
    p = dict(bore=40.8, total_h=27.0)
    # mount so the neck top reaches the drawing's overall height of 302.7 mm
    base_z = 302.7 - p["total_h"]     # 275.7 : lower part sits inside shoulder
    neck = (
        cq.Workplane("XY").workplane(offset=base_z)
        .circle(53.0 / 2.0).extrude(3.0)                      # flange
    )
    neck = neck.faces(">Z").workplane().circle(49.8 / 2.0).extrude(24.0)
    try:
        thread = helical_thread(radius=45.4 / 2.0, pitch=5.2, height=21.0,
                                tri_size=3.4, z0=base_z + 3.0)
        neck = neck.union(thread)
    except Exception as e:
        print("  din51 thread skipped:", e)
    top_z = base_z + p["total_h"]
    return neck.translate((NECK_OFFSET_X, 0, 0)), top_z, p["bore"]


def neck_bericap45():
    """
    45 mm BERICAP neck:
      thread crest Ø45.2, root Ø41.4, pitch 4, thread height 19.6, start 6.35
      barrel wall Ø40.8, bore Ø35.7, 1x45 top chamfer
      base ratchet collar: crest Ø57.1, root Ø50.8
    """
    bore = 35.7
    barrel_d = 40.8
    total_h = 25.8
    base_z = H_BODY - 4.0        # embed 4 mm into shoulder

    # ratchet collar at the base (anti-rotation)
    collar_h = 6.0
    neck = ratchet_ring(root_d=50.8, crest_d=57.1, height=collar_h,
                        n_teeth=18, z0=base_z)

    # barrel Ø40.8 up the full neck height
    barrel = (
        cq.Workplane("XY").workplane(offset=base_z)
        .circle(barrel_d / 2.0).extrude(total_h)
    )
    neck = neck.union(barrel)

    # helical thread: pitch 4, crest Ø45.2 (ridge 2.2 beyond barrel radius)
    try:
        thread = helical_thread(radius=barrel_d / 2.0, pitch=4.0, height=19.6,
                                tri_size=4.4, z0=base_z + 3.0)
        neck = neck.union(thread)
    except Exception as e:
        print("  bericap thread skipped:", e)

    # 1 x 45 top chamfer on the outer rim
    try:
        neck = neck.faces(">Z").edges(cq.selectors.RadiusNthSelector(-1)).chamfer(1.0)
    except Exception:
        try:
            neck = neck.faces(">Z").chamfer(1.0)
        except Exception as e:
            print("  bericap chamfer skipped:", e)

    top_z = base_z + total_h
    return neck.translate((NECK_OFFSET_X, 0, 0)), top_z, bore


# ----------------------------------------------------------------------------
# Assemble a full canister for a given neck finish
# ----------------------------------------------------------------------------
def build_canister(neck_fn, out_name):
    body = build_body()
    neck, neck_top_z, bore_d = neck_fn()
    model = body.union(neck)

    # bore the neck opening
    bore = (
        cq.Workplane("XY").workplane(offset=neck_top_z + 1.0)
        .center(NECK_OFFSET_X, 0)
        .circle(bore_d / 2.0)
        .extrude(-(neck_top_z - Z_SHOULDER + 10.0))
    )
    model = model.cut(bore)

    # recessed label panels on front & back (R6.3)
    try:
        front = (
            cq.Workplane("XZ").workplane(offset=-(D / 2.0))
            .center(0, 150.0)
            .sketch().rect(120.0, 150.0).vertices().fillet(6.3).finalize()
            .extrude(2.0)
        )
        model = model.cut(front)
        model = model.cut(front.mirror("XZ"))
    except Exception as e:
        print("  label recess skipped:", e)

    cq.exporters.export(model, out_name)
    bb = model.val().BoundingBox()
    print(f"Exported {out_name}")
    print(f"  envelope  {bb.xlen:.1f} x {bb.ylen:.1f} x {bb.zlen:.1f} mm"
          f"   volume {model.val().Volume()/1000.0:.0f} cm^3")
    return model


if __name__ == "__main__":
    which = sys.argv[1].lower() if len(sys.argv) > 1 else "both"
    if which in ("both", "din51"):
        build_canister(neck_din51, "canister_240703A0_6L_DIN51.step")
    if which in ("both", "bericap", "bericap45"):
        build_canister(neck_bericap45, "canister_240703A0_6L_BERICAP45.step")

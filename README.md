# 2D → 3D: TANICA DYNO 5–6 L jerry can (drawing 240703A0)

This repo converts the 2D mould drawing **`240703A0`** (ARTIGIANA STAMPI /
customer BERRY — *"TANICA DYNO 5-6 LT — QUOTE STAMPO"*, HDPE) into a
parametric **3D STEP** model.

## Deliverable

| File | Description |
|------|-------------|
| `canister_240703A0_6L.step` | AP214 STEP solid of the **6 L version** (mm) |
| `build_canister.py` | CadQuery script that generates the STEP file |

## What the drawing shows

A blow-moulded HDPE jerry can in two capacities (5 L and 6 L) plus neck
thread details (DIN 51 and 45 mm BERICAP). The model reproduces the 6 L
version.

## Dimensions used (6 L version)

| Feature | Value (mm) |
|---------|-----------|
| Overall width (W) | 202.8 |
| Overall depth (D) | 151.3 |
| Overall height (H) | 302.7 |
| Body height to shoulder | 290.3 (base 83 + middle 135 + shoulder 72.3) |
| Body plan corner radius | ≈ 34 |
| Neck flange OD | 53 |
| Neck thread major Ø | ≈ 45.4 |
| Neck bore | ≈ 40.8 |
| Neck height | 27 (protrudes 12.4 above shoulder) |
| Label recess corner radius | 6.3 |

The reconstructed solid measures **202.8 × 151.3 × 302.7 mm**, matching the
drawing envelope.

## Modelling approach & scope

The drawing describes a blow-moulded part with complex organic surfaces
(freeform handle, grip pockets, stiffening ribs, date-clock and cavity
inserts). Those cosmetic/tooling features cannot be reconstructed exactly
from orthographic views, so the STEP model is a **clean, dimensionally
faithful representation** of the principal geometry:

- rounded-rectangle body lofted through the base, straight walls and the
  drawn-in top shoulder;
- a **threaded neck** (helical thread) offset toward one corner, matching
  the DIN 51 detail proportions;
- recessed **label panels** (R 6.3) on the front and back faces;
- bored neck opening.

It is delivered as a single watertight solid — suitable for visualisation,
CAM/CAE reference and as a starting CAD body — rather than a hollow blow-
moulded shell.

## Regenerate

```bash
pip install cadquery
python3 build_canister.py
```

Edit the dimension constants at the top of `build_canister.py` to retarget
the model (e.g. build the 5 L version by scaling the height to 259 mm).

# 2D → 3D: TANICA DYNO 5–6 L jerry can (drawing 240703A0)

This repo converts the 2D mould drawing **`240703A0`** (ARTIGIANA STAMPI /
customer BERRY — *"TANICA DYNO 5-6 LT — QUOTE STAMPO"*, HDPE) into a
parametric **3D STEP** model.

## Deliverable

| File | Description |
|------|-------------|
| `canister_240703A0_6L_DIN51.step` | 6 L canister with the **DIN 51** neck finish |
| `canister_240703A0_6L_BERICAP45.step` | 6 L canister with the **45 mm BERICAP** neck finish |
| `build_canister.py` | CadQuery script that generates the STEP files |

Both are AP214 STEP solids in millimetres. Build them with
`python3 build_canister.py` (or pass `bericap` / `din51` to build just one).

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
| Label recess corner radius | 6.3 |

### Neck finishes (from the Scale 1:1 / 5:1 details)

| Feature | DIN 51 | 45 mm BERICAP |
|---------|--------|---------------|
| Thread major Ø (crest) | ≈ 49.8 | 45.2 |
| Thread minor Ø (root) | 45.4 | 41.4 |
| Barrel / bore Ø | 40.8 | 40.8 / 35.7 |
| Thread pitch | 5.2 | 4 |
| Thread height | ~21 | 19.6 |
| Neck height | 27 | 25.8 |
| Base ratchet collar | – | crest Ø57.1 / root Ø50.8 |

The **DIN 51** variant reproduces the drawing envelope exactly
(**202.8 × 151.3 × 302.7 mm**). The **45 mm BERICAP** variant uses the same
body with the shorter ratchet-collar neck finish (overall ≈ 312 mm; no
overall height is dimensioned on the sheet for this finish).

## Modelling approach & scope

The drawing describes a blow-moulded part with complex organic surfaces
(freeform handle, grip pockets, stiffening ribs, date-clock and cavity
inserts). Those cosmetic/tooling features cannot be reconstructed exactly
from orthographic views, so the STEP model is a **clean, dimensionally
faithful representation** of the principal geometry:

- rounded-rectangle body lofted through the base, straight walls and the
  drawn-in top shoulder;
- a **threaded neck** (helical thread + base ratchet collar for the BERICAP)
  positioned near the left top corner, matching the top-view layout;
- a **recessed neck well** — the shoulder dips into a circular pocket from
  which the neck rises, matching the concentric contours in the plan;
- a **top carry handle** — a grip bar bridging a recessed finger pocket,
  set to the right of the neck and centred in depth, as per the top view;
- recessed **label panel** (76 mm wide, R 6.3) on the front/back shoulder;
- **gull-wing base push-up** — the bottom arches up between the depth-side
  feet, matching the side/end-view base profile;
- bored neck opening.

It is delivered as a single watertight solid — suitable for visualisation,
CAM/CAE reference and as a starting CAD body — rather than a hollow blow-
moulded shell.

### Cross-checked against the drawing

Every feature was verified by projecting the model's edges orthographically
and **overlaying them on the top, front and side/end views** of the drawing
(scaled 1:1 to the sheet), then adjusting the parameters until the outlines
lined up in all three projections.

> **Note on fidelity.** An *exact* replica of a blow-moulded part cannot be
> reconstructed from 2D orthographic views alone — the freeform surface
> transitions, internal handle-loop topology, base rib pattern and exact
> draft/fillet radii are not fully determined by the projections. This model
> matches the drawing's **silhouette and every dimensioned feature** in all
> views; the remaining differences are cosmetic mould detail.

## Regenerate

```bash
pip install cadquery
python3 build_canister.py
```

Edit the dimension constants at the top of `build_canister.py` to retarget
the model (e.g. build the 5 L version by scaling the height to 259 mm).

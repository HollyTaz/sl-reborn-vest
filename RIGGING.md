# RIGGING.md — Reborn Body Rigging Guide

This guide covers everything you need to know to properly rig the leather vest
mesh to the **Second Life Reborn body skeleton** so that it deforms correctly
during animation.

---

## Table of Contents

1. [Reborn Body Skeleton Overview](#reborn-body-skeleton-overview)
2. [Bones Used by This Vest](#bones-used-by-this-vest)
3. [Weight Painting Guidelines](#weight-painting-guidelines)
4. [Testing in Blender](#testing-in-blender)
5. [Exporting for Second Life](#exporting-for-second-life)
6. [Common Issues and Fixes](#common-issues-and-fixes)

---

## Reborn Body Skeleton Overview

The Reborn body uses the **standard Second Life skeleton** (also called the
"SL skeleton" or "Bento skeleton") with a set of deformation bones whose names
must match exactly when uploading to Second Life.

Key bone naming rules:

- Bone names are **case-sensitive**.
- All deformation bones start with a lowercase `m` (e.g., `mChest`, `mTorso`).
- The skeleton is measured in **metres**.
- The root bone is `mPelvis` at approximately Z = 0.95 m (hip height).

The script creates a minimal subset of these bones sufficient for a vest:

```
mPelvis
└── mTorso
    └── mChest
        ├── mNeck
        │   └── mHead
        ├── mCollarLeft
        │   └── mShoulderLeft
        │       └── mElbowLeft
        │           └── mWristLeft
        └── mCollarRight
            └── mShoulderRight
                └── mElbowRight
                    └── mWristRight
```

---

## Bones Used by This Vest

The generator assigns **uniform weights** across the entire vest mesh as a
starting point. For a production vest you should refine these weights using
Blender's **Weight Paint** mode.

| Bone | Default Weight | Affects |
|------|---------------|---------|
| `mChest` | 0.70 | Main body of vest |
| `mTorso` | 0.20 | Lower vest / hem |
| `mShoulderLeft` | 0.05 | Left shoulder area |
| `mShoulderRight` | 0.05 | Right shoulder area |

> **Note:** Collar geometry benefits from a higher `mNeck` weight if you add
> neck movement bones. Add `"mNeck": 0.4` to the `torso_weights` dict in
> `build_vest()` and reduce `mChest` accordingly.

---

## Weight Painting Guidelines

### Step 1 — Enter Weight Paint Mode

1. Select the vest mesh object in Object Mode.
2. Press `Ctrl+Tab` → **Weight Paint**, or use the **Mode** menu.

### Step 2 — Understand the Colour Scale

| Colour | Weight Value | Meaning |
|--------|-------------|---------|
| Blue   | 0.0 | Not influenced by this bone |
| Green  | 0.5 | 50 % influence |
| Red    | 1.0 | Fully controlled by this bone |

### Step 3 — Recommended Weight Distribution

```
FRONT VIEW                  WEIGHT MAP (mChest)
┌─────────────────┐
│  shoulders: 0.4 │   ← blend to mShoulderL/R
│                 │
│  chest:     1.0 │   ← full mChest control
│                 │
│  mid:       0.8 │
│                 │
│  hem:       0.3 │   ← blend to mTorso
└─────────────────┘
```

### Step 4 — Normalise Weights

After painting, select the mesh, enter **Weight Paint** mode, and run:

**Weights → Normalize All** (`W` → *Normalize All*)

This ensures all vertex weights sum to exactly 1.0, which Second Life requires.

### Step 5 — Mirror Weights

If you paint one side only:

**Weights → Mirror Vertex Group** — tick **Mirror Weights** and choose the
correct axis (`X`).

---

## Testing in Blender

### Pose the Armature

1. Select the armature (`RebornArmature`).
2. Press `Ctrl+Tab` → **Pose Mode**.
3. Select `mChest` and press `R` to rotate — the vest should follow.
4. Test `mShoulderLeft`/`mShoulderRight` to check shoulder deformation.
5. Look for:
   - **Candy-wrapper twisting** — reduce the weight gradient transitions.
   - **Pinching at armpits** — increase `mShoulderLeft/Right` weight in that area.
   - **Hem flying away** — increase `mTorso` weight at the bottom edge.

### Use the Pose Library (optional)

Import a reference SL animation (`.bvh`) into Blender and use it to preview
deformation under movement:

```
File → Import → BVH Motion Capture (.bvh)
```

Then parent or constrain the armature to the imported action.

---

## Exporting for Second Life

When exporting via `blender --background --python blender_vest_generator.py`
the script calls:

```python
bpy.ops.wm.collada_export(
    filepath=...,
    apply_modifiers=True,
    include_armatures=True,
    include_animations=False,
    export_global_forward_selection="Y",
    export_global_up_selection="Z",
)
```

Important settings to verify in the SL uploader:

| Setting | Value |
|---------|-------|
| Axis Forward | Y |
| Axis Up | Z |
| Skin Weights | ✅ Enabled |
| Include Joints | ✅ Enabled |
| LOD | Auto-generate (3 levels) |

---

## Common Issues and Fixes

### Vest appears inside the body

**Cause:** Scale mismatch — SL uses metres, Blender default is metres but
avatar height may differ.  
**Fix:** Adjust `vest_scale` in `PARAMS`. Start with `1.0` and increase slightly
(e.g., `1.02`) until the vest sits outside the body without z-fighting.

---

### Mesh does not follow body on upload

**Cause:** Bone names do not match the SL skeleton.  
**Fix:** Confirm bone names match exactly (case-sensitive). Required names for
a vest: `mChest`, `mTorso`, `mShoulderLeft`, `mShoulderRight`.

---

### Z-fighting (flickering) on chest

**Cause:** Vest geometry is coplanar with body geometry.  
**Fix:** Apply a very small Solidify modifier (thickness `0.001 m`) to push the
vest surface outward before export.

---

### Collar clips into neck

**Cause:** Collar height too large or neck bone not weighted.  
**Fix:** Reduce `collar_height` in `PARAMS`, or add `mNeck` weights to the
collar vertices.

---

### Armhole gap visible

**Cause:** `armhole_depth` is too shallow.  
**Fix:** Increase `armhole_depth` (try `0.22`) so the cut extends further
inward and the arm passes cleanly through.

---

### Upload error: "No skin weights"

**Cause:** Collada export did not include the armature.  
**Fix:** In the Blender Collada export dialog → ensure **Include Armatures**
and **Include Skin Weights** are both ticked.  In the script, confirm
`include_armatures=True` is set in `collada_export`.

---

### Weight Normalization warning in SL uploader

**Fix:** In Blender Weight Paint mode → **Weights → Normalize All**, then
re-export.

---

*Last updated: 2026 — Reborn body v2.x / SL Bento skeleton*

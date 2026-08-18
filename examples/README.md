# examples/

This directory stores auto-generated and sample output files.

## Files

| File | Description |
|------|-------------|
| `vest_export.dae` | Auto-generated Collada file — created when you run `blender_vest_generator.py` |
| `README.md` | This file |

---

## Auto-Generated Output

When you run the script, `vest_export.dae` is placed here automatically:

```bash
blender --background --python blender_vest_generator.py
```

The `.dae` file contains:
- The full vest mesh (front panels, back panels, pockets, buttons, back patch)
- Rigging data for the Reborn-compatible armature
- Material slot names (`LeatherBase`, `BackPatch_SL`)

---

## Using the .dae File

### In Blender (verify before upload)

```
File → Import → Collada (.dae) → select vest_export.dae
```

Check that:
- The armature bones have correct names (`mChest`, `mTorso`, etc.)
- All material slots are present
- The mesh has no disconnected geometry

### In Second Life

Follow the upload steps in the main [README.md](../README.md#second-life-upload-instructions).

---

## Sample `.blend` Files

To generate a `.blend` file alongside the `.dae`, add this line at the end of
`build_vest()` in `blender_vest_generator.py`:

```python
bpy.ops.wm.save_as_mainfile(filepath=filepath.replace(".dae", ".blend"))
```

The `.blend` is useful for:
- Inspecting the mesh before upload
- Tweaking weight painting
- Batch-generating variations

---

## Before / After Textures

Place your reference PNG files here for documentation purposes:

```
examples/
├── vest_export.dae
├── before_texture.png    ← grey/untextured mesh screenshot
├── after_texture.png     ← fully textured in SL screenshot
└── README.md
```

These are optional and not required for the upload workflow.

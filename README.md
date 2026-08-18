# sl-reborn-vest

A complete Blender Python project that **procedurally generates a customizable
black leather motorcycle vest** rigged for the **Second Life Reborn body** and
exported as a `.dae` (Collada) file ready for upload.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Requirements](#requirements)
3. [Quick Start](#quick-start)
4. [How to Run the Script](#how-to-run-the-script)
5. [Customization Parameters](#customization-parameters)
6. [Second Life Upload Instructions](#second-life-upload-instructions)
7. [Directory Structure](#directory-structure)
8. [License](#license)

---

## Project Overview

The vest features:

| Feature | Details |
|---------|---------|
| Style | Classic outlaw / motorcycle sleeveless vest |
| Closure | Front button placket (5 buttons) |
| Pockets | Two chest pockets |
| Back | Flat embroidery patch area for skull & text graphics |
| Material | Black leather (Principled BSDF) with separate patch material slot |
| Rigging | Minimal Reborn-compatible bone set (`mChest`, `mTorso`, shoulders) |
| Export | Collada `.dae` — importable directly into Second Life |

---

## Requirements

| Requirement | Version |
|-------------|---------|
| [Blender](https://www.blender.org/download/) | **3.6 LTS or 4.x** |
| Python (bundled with Blender) | 3.10 + |
| Operating System | Windows 10/11, macOS 12+, Linux |

No additional Python packages are needed — the script uses only Blender's
built-in `bpy`, `bmesh`, and `mathutils` modules.

---

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/HollyTaz/sl-reborn-vest.git
cd sl-reborn-vest

# 2. Run the generator (headless / background mode)
blender --background --python blender_vest_generator.py

# 3. Find your export in examples/vest_export.dae
```

The script runs in about 10–20 seconds and places `vest_export.dae` inside the
`examples/` folder.

---

## How to Run the Script

### Option A — Blender GUI (Scripting Workspace)

1. Open Blender and switch to the **Scripting** workspace (top tab).
2. Click **Open** → navigate to `blender_vest_generator.py`.
3. Press **Run Script** (▶ button) or `Alt+P`.
4. The vest will be generated in the 3D viewport and exported automatically.

### Option B — Command Line (headless)

```bash
blender --background --python blender_vest_generator.py
```

Add `-- --my-flag` style args if you extend `PARAMS` parsing later.

### Option C — Inside Blender with Custom Parameters

Open the Scripting workspace, then at the bottom of the script call:

```python
build_vest({
    "top_banner":    "IRON WOLVES",
    "bottom_banner": "EST. 1987",
    "leather_color": (0.05, 0.02, 0.01, 1.0),   # dark brown
    "vest_scale":    1.05,
})
```

---

## Customization Parameters

All parameters live in the `PARAMS` dictionary at the top of
`blender_vest_generator.py`.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `vest_scale` | float | `1.0` | Uniform scale (clamped 0.5–2.0) |
| `chest_width` | float | `0.42` | Half chest width in metres |
| `vest_length` | float | `0.55` | Front/back length from collar to hem |
| `shoulder_width` | float | `0.44` | Shoulder span |
| `armhole_depth` | float | `0.18` | Armhole cut depth |
| `collar_height` | float | `0.06` | Collar stand height |
| `leather_color` | RGBA tuple | `(0.02,0.02,0.02,1.0)` | Base leather colour |
| `leather_roughness` | float | `0.65` | PBR roughness |
| `leather_specular` | float | `0.45` | PBR specular |
| `top_banner` | string | `"CUSTOM TOP"` | Back patch top text |
| `bottom_banner` | string | `"CUSTOM BOTTOM"` | Back patch bottom text |
| `export_path` | string | `examples/vest_export.dae` | Output file path |

---

## Second Life Upload Instructions

### Step 1 — Upload the Mesh

1. Log in to Second Life with a **mesh-enabled** viewer (official SL viewer or
   Firestorm).
2. Go to **Build → Upload → Model…** (or press `Ctrl+Shift+M` in some viewers).
3. Select `examples/vest_export.dae`.
4. In the **Rigging** tab:
   - Enable **Skin Weights**.
   - Select the **Reborn** body as the reference skeleton (if prompted).
5. Set LOD levels — Auto-generate is fine for clothing.
6. Click **Upload** and pay the L$ upload fee.

### Step 2 — Apply Textures

1. Upload `textures/leather_base_template.png` and
   `textures/back_patch_template.png` via **Build → Upload → Image…**.
2. In your inventory, locate the uploaded mesh and open it with **Edit**.
3. Apply textures to the correct material faces:
   - **LeatherBase** → `leather_base_template.png`
   - **BackPatch_SL** → `back_patch_template.png`

### Step 3 — Fit the Vest

1. Wear the vest and enter **Appearance** mode.
2. Use the Reborn body's **Alpha HUD** to hide body geometry under the vest.
3. Adjust the vest position with the **Edit** tool if needed.

---

## Directory Structure

```
sl-reborn-vest/
├── blender_vest_generator.py   ← Main Blender script
├── README.md                   ← This file
├── RIGGING.md                  ← Detailed rigging guide
├── textures/
│   ├── leather_base_template.png
│   ├── back_patch_template.png
│   ├── normal_map_template.png
│   └── README.md
└── examples/
    ├── vest_export.dae          ← Auto-generated on first run
    └── README.md
```

---

## License

MIT — free to use, modify, and distribute.  
Back-patch skull art is original and released under [CC0](https://creativecommons.org/publicdomain/zero/1.0/).

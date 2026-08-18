# textures/

This folder contains PNG texture templates for the leather vest.

## Files

| File | Size | Purpose |
|------|------|---------|
| `leather_base_template.png` | 1024×1024 | Base leather colour map (near-black) |
| `back_patch_template.png` | 1024×1024 | Back embroidery patch (skull + text) |
| `normal_map_template.png` | 1024×1024 | Leather surface normal / bump map |

---

## Texture Slots in Second Life

When you upload the vest mesh, Second Life will show the material names from
Blender:

| Material Name | Texture to Apply |
|--------------|-----------------|
| `LeatherBase` | `leather_base_template.png` |
| `BackPatch_SL` | `back_patch_template.png` |

---

## Creating Custom Textures

### Leather Base (`leather_base_template.png`)

1. Open in GIMP / Photoshop / Krita.
2. Fill background with very dark grey (`#050505`).
3. Add a **leather grain** filter or texture overlay.
4. Export as 1024×1024 PNG (no alpha needed, but alpha is fine).

### Back Patch (`back_patch_template.png`)

The patch layout (top to bottom):

```
┌───────────────────────────────────────┐
│        ╔═══════════════════╗          │
│        ║   CUSTOM TOP      ║  ← top banner (arc text, white on dark)
│        ╚═══════════════════╝          │
│                                       │
│          ☠  (skull & crossbones)      │  ← centre graphic
│                                       │
│        ╔═══════════════════╗          │
│        ║  CUSTOM BOTTOM    ║  ← bottom banner
│        ╚═══════════════════╝          │
└───────────────────────────────────────┘
```

Recommended design steps:
1. 1024×1024 canvas, dark olive/brown background.
2. Centre the skull SVG (see free resources below).
3. Add curved/arched text banners above and below.
4. Export as PNG with **premultiplied alpha** for best SL results.

#### Free Skull Resources
- [SVG Repo — skull](https://www.svgrepo.com/vectors/skull/)
- Inkscape free vector editor: https://inkscape.org/

### Normal Map (`normal_map_template.png`)

Generate from the leather base using:
- **GIMP**: Filters → Map → Normal Map
- **Krita**: Filter → Normal Map
- **Materialize** (free app): https://boundingboxsoftware.com/materialize/

Typical settings: strength `1.5–2.0`, smooth `0.3`.

---

## Uploading Textures to Second Life

1. In the SL viewer: **Build → Upload → Image…** (`Ctrl+Shift+U`)
2. Select the PNG file.
3. Preview — check "Preview" checkbox.
4. Click **Upload** (costs L$10 per texture).
5. Find the uploaded texture in **Inventory → Textures**.

---

*Replace the placeholder PNG files with your custom designs before uploading.*

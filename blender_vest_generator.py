"""
blender_vest_generator.py
=========================
Blender Python script that procedurally generates a customizable leather vest
mesh compatible with the Second Life Reborn body.

Usage (run inside Blender's scripting workspace or via CLI):
    blender --background --python blender_vest_generator.py

Blender 3.6 LTS, 4.1, or 4.2+ required.
"""

import bpy
import bmesh
import math
import os
from mathutils import Vector, Matrix

# ---------------------------------------------------------------------------
# CUSTOMIZATION PARAMETERS
# ---------------------------------------------------------------------------

PARAMS = {
    # --- Sizing ---
    "vest_scale": 1.0,          # Uniform scale multiplier (Reborn = 1.0)
    "chest_width": 0.42,        # Half-width of chest (metres)
    "vest_length": 0.55,        # Front/back length from collar to hem
    "shoulder_width": 0.44,     # Shoulder span (half, from centre)
    "armhole_depth": 0.18,      # Depth of the armhole cut
    "collar_height": 0.06,      # Height of the collar stand
    "torso_depth": 0.18,        # Front-to-back half-depth of the torso
    "front_gap": 0.015,         # Half-width of front opening (placket gap)

    # --- Material ---
    "leather_color": (0.02, 0.02, 0.02, 1.0),   # Near-black leather RGBA
    "leather_roughness": 0.65,
    "leather_specular": 0.45,

    # --- Back Patch Text ---
    "top_banner": "CUSTOM TOP",
    "bottom_banner": "CUSTOM BOTTOM",

    # --- Export ---
    "export_path": os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "examples", "vest_export.dae"),
}

# ---------------------------------------------------------------------------
# HELPER UTILITIES
# ---------------------------------------------------------------------------


def clear_scene():
    """Remove all mesh objects from the scene."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for col in list(bpy.data.collections):
        bpy.data.collections.remove(col)


def new_collection(name: str) -> bpy.types.Collection:
    col = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(col)
    return col


def link_to_collection(obj: bpy.types.Object, col: bpy.types.Collection):
    col.objects.link(obj)
    if obj.name in bpy.context.scene.collection.objects:
        bpy.context.scene.collection.objects.unlink(obj)


def add_material(obj: bpy.types.Object, name: str,
                 color=(0.02, 0.02, 0.02, 1.0),
                 roughness=0.65, specular=0.45) -> bpy.types.Material:
    """Create a Principled BSDF material and assign it to *obj*."""
    mat = bpy.data.materials.new(name=name)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = color
        bsdf.inputs["Roughness"].default_value = roughness
        # Blender 3.x uses "Specular", 4.x uses "Specular IOR Level"
        for spec_key in ("Specular", "Specular IOR Level"):
            if spec_key in bsdf.inputs:
                bsdf.inputs[spec_key].default_value = specular
                break
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)
    return mat


# ---------------------------------------------------------------------------
# VEST MESH GENERATION
# ---------------------------------------------------------------------------

def build_front_profile(p: dict) -> list[tuple[float, float, float]]:
    """
    Return an ordered list of (x, y, z) vertices for the *front* vest panel
    outline (right half only – will be mirrored for the left half).

    The panel sits at Y=0 (front of body).  The side seam curves slightly
    inward in Y to suggest the torso wrap without requiring a full cylinder.

    Coordinate system (Blender):
        +X  → right
        +Y  → towards viewer (depth / front)
        +Z  → up
    """
    cw  = p["chest_width"]
    vl  = p["vest_length"]
    sw  = p["shoulder_width"]
    ad  = p["armhole_depth"]
    ch  = p["collar_height"]
    gap = p["front_gap"]        # offset from centre so there's a front opening

    # Side seam curves inward (negative Y) by half the torso depth at the
    # bottom hem, tapering to 0 at the shoulder so the side seam blends.
    side_y = -p["torso_depth"] * 0.5

    verts = [
        # Centre-front edge (vertical strip along the placket)
        (gap,        0.0,     0.0),          # 0  centre hem
        # Bottom hem, sweeping out to side seam
        (cw,         side_y,  0.0),          # 1  side hem (curved in Y)
        # Side seam rising to armhole
        (cw,         side_y,  vl - ad),      # 2  armhole bottom (side)
        # Armhole notch
        (sw,         side_y * 0.3, vl - ad),# 3  armhole outer (eased toward front)
        (sw,         0.0,     vl),           # 4  shoulder top
        # Collar
        (gap + cw * 0.20, 0.0, vl + ch),    # 5  collar outer
        (gap,        0.0,     vl + ch),      # 6  collar centre top
    ]
    return verts


def build_back_profile(p: dict) -> list[tuple[float, float, float]]:
    """
    Return an ordered list of (x, y, z) vertices for the *back* vest panel
    outline (right half only – will be mirrored).

    The back panel sits at Y = -(2 * torso_depth) so it is behind the front.
    Side seam Y matches the front side seam so the two panels share edges.
    """
    cw  = p["chest_width"]
    vl  = p["vest_length"]
    sw  = p["shoulder_width"]
    ad  = p["armhole_depth"]
    ch  = p["collar_height"]
    td  = p["torso_depth"]

    back_y  = -td * 2.0      # rear face of back panel
    side_y  = -td * 0.5      # shared side-seam Y with the front panel

    verts = [
        (0.0,  back_y,  0.0),           # 0  centre-back hem (no gap at back)
        (cw,   side_y,  0.0),           # 1  side hem
        (cw,   side_y,  vl - ad),       # 2  armhole bottom
        (sw,   side_y * 0.3, vl - ad),  # 3  armhole outer
        (sw,   back_y,  vl),            # 4  shoulder top
        (cw * 0.20, back_y, vl + ch),   # 5  collar outer
        (0.0,  back_y,  vl + ch),       # 6  collar centre top
    ]
    return verts


# Keep old name as an alias so nothing else breaks
def build_vest_profile(p: dict) -> list[tuple[float, float, float]]:
    return build_front_profile(p)


def extrude_panel(bm: bmesh.types.BMesh,
                  profile: list[tuple[float, float, float]],
                  thickness: float = 0.004) -> list[bmesh.types.BMVert]:
    """
    Extrude a flat 2-D profile along the Y axis to give the panel a small
    leather thickness. Returns all created verts.
    """
    front_verts = [bm.verts.new(v) for v in profile]
    back_verts  = [bm.verts.new((v[0], v[1] - thickness, v[2]))
                   for v in profile]

    n = len(profile)

    # Front face
    bm.faces.new(front_verts)

    # Back face (reversed winding)
    bm.faces.new(list(reversed(back_verts)))

    # Side strip
    for i in range(n - 1):
        bm.faces.new([
            front_verts[i],
            front_verts[i + 1],
            back_verts[i + 1],
            back_verts[i],
        ])
    # Close the strip
    bm.faces.new([
        front_verts[n - 1],
        front_verts[0],
        back_verts[0],
        back_verts[n - 1],
    ])

    return front_verts + back_verts


def create_vest_panel(name: str, p: dict,
                      mirror_x: bool = False,
                      profile: list[tuple[float, float, float]] | None = None,
                      ) -> bpy.types.Object:
    """Create a single half-panel mesh object.

    *profile* defaults to the front profile if not supplied.
    """
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    if profile is None:
        profile = build_front_profile(p)
    extrude_panel(bm, profile, thickness=0.004)

    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)

    if mirror_x:
        obj.scale.x = -1.0
        bpy.context.view_layer.objects.active = obj
        bpy.ops.object.select_all(action="DESELECT")
        obj.select_set(True)
        bpy.ops.object.transform_apply(scale=True)

    return obj


def create_chest_pocket(name: str, x_offset: float,
                        z_offset: float) -> bpy.types.Object:
    """Create a small rectangular chest pocket."""
    mesh = bpy.data.meshes.new(name)
    bm = bmesh.new()

    w, h, depth = 0.06, 0.05, 0.003
    y = 0.001   # sit slightly proud of vest surface

    verts = [
        bm.verts.new((x_offset,         y,          z_offset)),
        bm.verts.new((x_offset + w,     y,          z_offset)),
        bm.verts.new((x_offset + w,     y,          z_offset + h)),
        bm.verts.new((x_offset,         y,          z_offset + h)),
        bm.verts.new((x_offset,         y - depth,  z_offset)),
        bm.verts.new((x_offset + w,     y - depth,  z_offset)),
        bm.verts.new((x_offset + w,     y - depth,  z_offset + h)),
        bm.verts.new((x_offset,         y - depth,  z_offset + h)),
    ]

    faces = [
        [verts[0], verts[1], verts[2], verts[3]],   # front
        [verts[7], verts[6], verts[5], verts[4]],   # back
        [verts[0], verts[4], verts[5], verts[1]],   # bottom
        [verts[2], verts[6], verts[7], verts[3]],   # top
        [verts[0], verts[3], verts[7], verts[4]],   # left
        [verts[1], verts[5], verts[6], verts[2]],   # right
    ]
    for f in faces:
        bm.faces.new(f)

    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new(name, mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def create_button(name: str, x: float, z: float) -> bpy.types.Object:
    """Create a small cylinder button."""
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.008,
        depth=0.003,
        location=(x, 0.005, z),
        rotation=(math.radians(90), 0, 0),
    )
    obj = bpy.context.active_object
    obj.name = name
    return obj


def create_back_patch(p: dict) -> bpy.types.Object:
    """Create the flat back embroidery patch plane."""
    cw  = p["chest_width"]
    vl  = p["vest_length"]

    pw, ph = cw * 1.6, vl * 0.55   # patch width / height
    px, pz = 0.0, vl * 0.25         # patch centre (X=0 = spine, Z from hem)

    mesh = bpy.data.meshes.new("BackPatch")
    bm = bmesh.new()

    # Simple quad, slightly behind vest surface
    y = -0.005
    verts = [
        bm.verts.new((-pw / 2, y, pz)),
        bm.verts.new(( pw / 2, y, pz)),
        bm.verts.new(( pw / 2, y, pz + ph)),
        bm.verts.new((-pw / 2, y, pz + ph)),
    ]
    bm.faces.new(verts)
    bm.normal_update()
    bm.to_mesh(mesh)
    bm.free()

    obj = bpy.data.objects.new("BackPatch", mesh)
    bpy.context.scene.collection.objects.link(obj)
    return obj


def create_banner_text(text: str, name: str,
                       x: float, y: float, z: float,
                       scale: float = 0.04) -> bpy.types.Object:
    """
    Create a Blender Text object, convert it to a mesh, and position it.

    The resulting flat mesh can be UV-projected and exported to .dae so the
    banner text appears as real geometry on the back patch.
    """
    # Create a font curve object
    bpy.ops.object.text_add(location=(x, y, z))
    text_obj = bpy.context.active_object
    text_obj.name = name
    text_obj.data.body = text
    text_obj.data.align_x = "CENTER"
    text_obj.data.size = scale
    text_obj.data.extrude = 0.001   # very thin, just enough for export

    # Convert to mesh so it joins cleanly with other mesh objects
    bpy.ops.object.select_all(action="DESELECT")
    text_obj.select_set(True)
    bpy.context.view_layer.objects.active = text_obj
    bpy.ops.object.convert(target="MESH")
    return text_obj




def apply_uv_project(obj: bpy.types.Object):
    """Apply a simple UV smart-project to the object."""
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.02)
    bpy.ops.object.mode_set(mode="OBJECT")


# ---------------------------------------------------------------------------
# ARMATURE (REBORN SKELETON SUBSET)
# ---------------------------------------------------------------------------

REBORN_BONES = {
    # name: (head_xyz, tail_xyz, parent_name_or_None)
    "mPelvis":       ((0, 0, 0.95),    (0, 0, 1.05), None),
    "mTorso":        ((0, 0, 1.05),    (0, 0, 1.25), "mPelvis"),
    "mChest":        ((0, 0, 1.25),    (0, 0, 1.45), "mTorso"),
    "mNeck":         ((0, 0, 1.45),    (0, 0, 1.55), "mChest"),
    "mHead":         ((0, 0, 1.55),    (0, 0, 1.70), "mNeck"),
    "mCollarLeft":   ((0, 0, 1.43),    (-0.12, 0, 1.45), "mChest"),
    "mShoulderLeft": ((-0.12, 0, 1.45),(-0.25, 0, 1.40), "mCollarLeft"),
    "mElbowLeft":    ((-0.25, 0, 1.40),(-0.38, 0, 1.25), "mShoulderLeft"),
    "mWristLeft":    ((-0.38, 0, 1.25),(-0.44, 0, 1.15), "mElbowLeft"),
    "mCollarRight":  ((0, 0, 1.43),    (0.12, 0, 1.45),  "mChest"),
    "mShoulderRight":((0.12, 0, 1.45), (0.25, 0, 1.40),  "mCollarRight"),
    "mElbowRight":   ((0.25, 0, 1.40), (0.38, 0, 1.25),  "mShoulderRight"),
    "mWristRight":   ((0.38, 0, 1.25), (0.44, 0, 1.15),  "mElbowRight"),
}


def create_armature(name: str = "RebornArmature") -> bpy.types.Object:
    """Build a minimal Reborn-compatible armature."""
    arm_data = bpy.data.armatures.new(name)
    arm_obj  = bpy.data.objects.new(name, arm_data)
    bpy.context.scene.collection.objects.link(arm_obj)

    bpy.context.view_layer.objects.active = arm_obj
    bpy.ops.object.mode_set(mode="EDIT")

    edit_bones = arm_data.edit_bones
    bone_map: dict[str, bpy.types.EditBone] = {}

    for bname, (head, tail, parent) in REBORN_BONES.items():
        eb = edit_bones.new(bname)
        eb.head = Vector(head)
        eb.tail = Vector(tail)
        bone_map[bname] = eb

    # Assign parents after all bones exist
    for bname, (_, _, parent) in REBORN_BONES.items():
        if parent:
            bone_map[bname].parent = bone_map[parent]

    bpy.ops.object.mode_set(mode="OBJECT")
    return arm_obj


def rig_object(obj: bpy.types.Object, arm_obj: bpy.types.Object,
               bone_weights: dict[str, float]):
    """
    Add an Armature modifier and set up vertex group weights for *obj*.

    *bone_weights* maps bone name → weight for ALL vertices (simple approach).
    For a production rig use per-vertex weight painting instead.
    """
    # Add modifier
    mod = obj.modifiers.new("Armature", "ARMATURE")
    mod.object = arm_obj
    mod.use_vertex_groups = True

    # Assign all verts to each bone group at the given weight
    for bone_name, weight in bone_weights.items():
        vg = obj.vertex_groups.new(name=bone_name)
        all_vert_indices = [v.index for v in obj.data.vertices]
        vg.add(all_vert_indices, weight, "REPLACE")


# ---------------------------------------------------------------------------
# MATERIAL SLOTS
# ---------------------------------------------------------------------------

def setup_materials(vest_parts: list[bpy.types.Object],
                    patch_obj: bpy.types.Object, p: dict):
    """Assign leather material to vest parts and a patch material to patch."""
    for part in vest_parts:
        add_material(part, "LeatherBase",
                     color=p["leather_color"],
                     roughness=p["leather_roughness"],
                     specular=p["leather_specular"])

    # Name the patch material "BackPatch_SL" from the start so that SL
    # importers can locate it by its material slot name without ambiguity.
    add_material(patch_obj, "BackPatch_SL",
                 color=(0.08, 0.05, 0.02, 1.0),
                 roughness=0.75, specular=0.1)


# ---------------------------------------------------------------------------
# JOIN & EXPORT
# ---------------------------------------------------------------------------

def join_objects(objects: list[bpy.types.Object],
                 name: str = "VestMesh") -> bpy.types.Object:
    """Join a list of mesh objects into one."""
    bpy.ops.object.select_all(action="DESELECT")
    for o in objects:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objects[0]
    bpy.ops.object.join()
    bpy.context.active_object.name = name
    return bpy.context.active_object


def export_dae(filepath: str):
    """Export the entire scene as a Collada (.dae) file.

    Handles parameter differences between Blender 3.x and 4.x automatically.
    """
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    blender_major = bpy.app.version[0]

    # Base kwargs supported by both 3.x and 4.x
    kwargs = dict(
        filepath=filepath,
        apply_modifiers=True,
        selected=False,
        include_children=True,
        include_armatures=True,
        include_shapekeys=False,
        deform_bones_only=False,
        include_animations=False,
        export_global_forward_selection="Y",
        export_global_up_selection="Z",
    )

    if blender_major >= 4:
        # Blender 4.x renamed this parameter
        kwargs["export_mesh_type"] = 0          # 0 = view (same as "view")
    else:
        # Blender 3.x name
        kwargs["export_mesh_type_selection"] = "view"

    bpy.ops.wm.collada_export(**kwargs)
    print(f"[vest_generator] Exported: {filepath}")


# ---------------------------------------------------------------------------
# MAIN BUILD ROUTINE
# ---------------------------------------------------------------------------

def build_vest(params: dict | None = None):
    """
    Main entry point.  Call this from Blender's scripting console or via
    the --python CLI flag.
    """
    p = PARAMS.copy()
    if params:
        p.update(params)

    p["vest_scale"] = max(0.5, min(p["vest_scale"], 2.0))  # clamp

    clear_scene()
    col = new_collection("VestCollection")

    # --- Front panels (two halves mirrored at X=0) ---
    front_profile = build_front_profile(p)
    front_right = create_vest_panel("FrontRight", p, mirror_x=False, profile=front_profile)
    front_left  = create_vest_panel("FrontLeft",  p, mirror_x=True,  profile=front_profile)

    # --- Back panels (own profile already placed at the correct Y depth) ---
    back_profile = build_back_profile(p)
    back_right = create_vest_panel("BackRight", p, mirror_x=False, profile=back_profile)
    back_left  = create_vest_panel("BackLeft",  p, mirror_x=True,  profile=back_profile)

    # --- Chest pockets ---
    pocket_y = 0.005   # just proud of the front panel surface (Y≈0)
    pocket_r = create_chest_pocket("PocketRight",  0.06,  p["vest_length"] * 0.60)
    pocket_l = create_chest_pocket("PocketLeft",  -0.12,  p["vest_length"] * 0.60)

    # --- Buttons (5 down the front placket) ---
    buttons = []
    for i in range(5):
        z = p["vest_length"] * 0.15 + i * (p["vest_length"] * 0.60 / 4)
        btn = create_button(f"Button_{i}", 0.0, z)
        buttons.append(btn)

    # --- Back patch ---
    patch = create_back_patch(p)

    # --- Back patch banner text (converted to mesh geometry) ---
    patch_y = -0.006   # just in front of the back panel surface
    patch_centre_x = 0.0
    patch_z_top    = p["vest_length"] * 0.76
    patch_z_bottom = p["vest_length"] * 0.27
    banner_top = create_banner_text(
        p["top_banner"],    "BannerTop",
        patch_centre_x, patch_y, patch_z_top,
        scale=0.035,
    )
    banner_bot = create_banner_text(
        p["bottom_banner"], "BannerBottom",
        patch_centre_x, patch_y, patch_z_bottom,
        scale=0.035,
    )

    # --- UV mapping ---
    all_mesh_parts = ([front_right, front_left, back_right, back_left,
                       pocket_r, pocket_l, patch,
                       banner_top, banner_bot] + buttons)
    for part in all_mesh_parts:
        try:
            apply_uv_project(part)
        except Exception as e:
            print(f"[vest_generator] UV project skipped for {part.name}: {e}")

    # --- Materials ---
    vest_parts = [front_right, front_left, back_right, back_left,
                  pocket_r, pocket_l] + buttons
    setup_materials(vest_parts, patch, p)
    # Give banner text a white material so it is visually distinct on the patch
    for banner in (banner_top, banner_bot):
        add_material(banner, "BannerText",
                     color=(0.9, 0.9, 0.9, 1.0),
                     roughness=0.4, specular=0.2)

    # --- Armature ---
    arm_obj = create_armature()

    # Rig vest to torso / chest bones with uniform weights
    # (production rigs should use proper weight painting)
    torso_weights = {
        "mChest": 0.70,
        "mTorso": 0.20,
        "mShoulderLeft":  0.05,
        "mShoulderRight": 0.05,
    }
    for part in vest_parts + [patch, banner_top, banner_bot]:
        rig_object(part, arm_obj, torso_weights)

    # --- Apply uniform scale via a single operator call on all selected objects ---
    # Scale each object individually so we do not double-scale anything that
    # is already parented; scale=1.0 (default) is a no-op.
    if p["vest_scale"] != 1.0:
        bpy.ops.object.select_all(action="DESELECT")
        for o in all_mesh_parts + [arm_obj]:
            if o is not None:
                o.select_set(True)
        bpy.context.view_layer.objects.active = arm_obj
        bpy.ops.transform.resize(value=(p["vest_scale"],) * 3)
        bpy.ops.object.transform_apply(scale=True)

    # --- Link everything to collection ---
    for o in all_mesh_parts + [arm_obj]:
        try:
            link_to_collection(o, col)
        except Exception:
            pass   # already linked or missing – not fatal

    # --- Export ---
    export_dae(p["export_path"])

    print("[vest_generator] Vest build complete.")
    return {
        "vest_parts":  vest_parts,
        "patch":       patch,
        "banner_top":  banner_top,
        "banner_bot":  banner_bot,
        "armature":    arm_obj,
    }


# ---------------------------------------------------------------------------
# RUN
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    build_vest()

#!/usr/bin/env python3
"""Create Soft Toy style Beep + room + props in Blender (run via blender -b --python)."""
import bpy
import math
from mathutils import Vector, Euler

OUT = "/workspace/godot_project"


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.curves):
        for b in list(block):
            block.remove(b)


def mat(name, color, rough=0.7, metal=0.0, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*color, 1.0)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    if emit > 0:
        b.inputs["Emission Color"].default_value = (*color, 1.0)
        b.inputs["Emission Strength"].default_value = emit
    return m


def smooth(obj):
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.shade_smooth()
    for poly in obj.data.polygons:
        poly.use_smooth = True


def add_subsurf(obj, levels=2):
    mod = obj.modifiers.new("sub", "SUBSURF")
    mod.levels = levels
    mod.render_levels = levels
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier="sub")
    smooth(obj)


def sphere(name, loc, radius, material, segs=32):
    bpy.ops.mesh.primitive_uv_sphere_add(
        radius=radius, location=loc, segments=segs, ring_count=max(16, segs // 2)
    )
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(material)
    smooth(o)
    return o


def cylinder(name, loc, radius, depth, material, verts=32):
    bpy.ops.mesh.primitive_cylinder_add(
        radius=radius, depth=depth, location=loc, vertices=verts
    )
    o = bpy.context.active_object
    o.name = name
    o.data.materials.append(material)
    smooth(o)
    return o


def box(name, loc, scale, material):
    bpy.ops.mesh.primitive_cube_add(size=1, location=loc)
    o = bpy.context.active_object
    o.name = name
    o.scale = scale
    bpy.ops.object.transform_apply(scale=True)
    o.data.materials.append(material)
    return o


def export_glb(path):
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        export_apply=True,
        export_animations=False,
    )
    print("EXPORT", path)


def create_beep():
    """Friendly soft-toy robot ~65cm tall, clear silhouette for toddlers."""
    clear_scene()
    turq = mat("BeepBody", (0.46, 0.83, 0.91), rough=0.55)  # #75D4E8 approx
    soft = mat("BeepSoft", (0.92, 0.95, 0.97), rough=0.6)
    dark = mat("BeepEyes", (0.08, 0.09, 0.12), rough=0.35)
    white = mat("BeepEyeWhite", (0.98, 0.98, 0.99), rough=0.4)
    yellow = mat("BeepAntenna", (1.0, 0.84, 0.18), rough=0.45)
    blush = mat("BeepBlush", (1.0, 0.55, 0.55), rough=0.7)
    mouth = mat("BeepMouth", (0.35, 0.15, 0.18), rough=0.5)

    root = bpy.data.objects.new("Beep", None)
    bpy.context.collection.objects.link(root)

    # Torso - rounded soft body
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.16, location=(0, 0, 0.30), segments=40, ring_count=28)
    torso = bpy.context.active_object
    torso.name = "Torso"
    torso.scale = (1.05, 0.95, 1.15)
    bpy.ops.object.transform_apply(scale=True)
    torso.data.materials.append(turq)
    add_subsurf(torso, 2)
    torso.parent = root

    # Belly highlight plate
    belly = sphere("Belly", (0, 0.08, 0.28), 0.07, soft, 24)
    belly.scale = (1.1, 0.5, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    belly.parent = root

    # Head
    head = sphere("Head", (0, 0, 0.52), 0.145, turq, 40)
    head.parent = root

    # Eyes - big and readable
    for x, name in ((-0.055, "EyeL"), (0.055, "EyeR")):
        ew = sphere(name + "White", (x, 0.11, 0.54), 0.045, white, 24)
        ew.parent = root
        pupil = sphere(name + "Pupil", (x, 0.145, 0.545), 0.028, dark, 20)
        pupil.parent = root
        shine = sphere(name + "Shine", (x - 0.01, 0.165, 0.56), 0.01, white, 12)
        shine.parent = root

    # Soft smile
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.035, minor_radius=0.008, location=(0, 0.13, 0.475),
        major_segments=24, minor_segments=10
    )
    smile = bpy.context.active_object
    smile.name = "Mouth"
    smile.rotation_euler = (math.radians(90), 0, 0)
    smile.scale = (1.0, 0.55, 1.0)
    bpy.ops.object.transform_apply(rotation=True, scale=True)
    # Keep only bottom arc-ish by scaling - simple mouth bar instead
    bpy.data.objects.remove(smile, do_unlink=True)
    mouth_obj = cylinder("Mouth", (0, 0.132, 0.475), 0.022, 0.012, mouth, 16)
    mouth_obj.rotation_euler = (math.radians(90), 0, 0)
    bpy.ops.object.transform_apply(rotation=True)
    mouth_obj.scale = (1.4, 0.35, 1.0)
    bpy.ops.object.transform_apply(scale=True)
    mouth_obj.parent = root

    # Cheeks
    for x in (-0.09, 0.09):
        c = sphere("Cheek", (x, 0.10, 0.50), 0.02, blush, 16)
        c.parent = root

    # Antenna
    stem = cylinder("AntennaStem", (0, 0, 0.70), 0.012, 0.10, yellow, 16)
    stem.parent = root
    tip = sphere("AntennaBall", (0, 0, 0.77), 0.028, yellow, 20)
    tip.parent = root

    # Arms - short rounded
    for x, side in ((-0.20, "L"), (0.20, "R")):
        arm = sphere(f"Arm{side}", (x, 0, 0.32), 0.055, turq, 24)
        arm.scale = (0.7, 0.7, 1.3)
        bpy.ops.object.transform_apply(scale=True)
        arm.parent = root
        hand = sphere(f"Hand{side}", (x * 1.15, 0.02, 0.22), 0.045, soft, 20)
        hand.parent = root

    # Legs - short rounded
    for x, side in ((-0.07, "L"), (0.07, "R")):
        leg = sphere(f"Leg{side}", (x, 0, 0.14), 0.055, turq, 24)
        leg.scale = (0.85, 0.85, 1.2)
        bpy.ops.object.transform_apply(scale=True)
        leg.parent = root
        foot = sphere(f"Foot{side}", (x, 0.03, 0.04), 0.05, soft, 20)
        foot.scale = (1.1, 1.3, 0.6)
        bpy.ops.object.transform_apply(scale=True)
        foot.parent = root

    export_glb(f"{OUT}/characters/beep/beep_soft.glb")


def create_room():
    clear_scene()
    cream = mat("WallCream", (0.94, 0.90, 0.82), 0.9)
    wood = mat("FloorWood", (0.80, 0.66, 0.45), 0.65)
    mint = mat("RugMint", (0.45, 0.80, 0.72), 0.95)
    frame = mat("WinFrame", (0.96, 0.95, 0.92), 0.45)
    glass = mat("Glass", (0.75, 0.88, 0.96), 0.12)
    sky = mat("Sky", (0.55, 0.78, 0.98), 1.0, emit=0.9)
    base = mat("Baseboard", (0.88, 0.82, 0.72), 0.7)
    ceil = mat("Ceiling", (0.96, 0.95, 0.92), 0.95)
    grass = mat("OutsideGrass", (0.45, 0.72, 0.38), 0.9)

    W, D, H = 6.0, 5.0, 2.7
    # Floor / ceiling
    box("Floor", (0, 0, -0.04), (W / 2, D / 2, 0.04), wood)
    box("Ceiling", (0, 0, H), (W / 2, D / 2, 0.04), ceil)
    # Four walls (camera shoots from -Y looking +Y-ish, leave doorway gap but keep readable room)
    box("WallBack", (0, D / 2, H / 2), (W / 2, 0.07, H / 2), cream)
    box("WallLeft", (-W / 2, 0, H / 2), (0.07, D / 2, H / 2), cream)
    box("WallRight", (W / 2, 0, H / 2), (0.07, D / 2, H / 2), cream)
    box("WallFrontL", (-2.0, -D / 2, H / 2), (1.0, 0.07, H / 2), cream)
    box("WallFrontR", (2.0, -D / 2, H / 2), (1.0, 0.07, H / 2), cream)
    box("WallFrontTop", (0, -D / 2, H - 0.4), (W / 2, 0.07, 0.4), cream)

    # Window on back
    ww, wh, wz = 2.4, 1.5, 1.5
    box("WinFrame", (0, D / 2 - 0.02, wz), (ww / 2 + 0.1, 0.06, wh / 2 + 0.1), frame)
    box("WinGlass", (0, D / 2 - 0.05, wz), (ww / 2, 0.02, wh / 2), glass)
    box("SkyPanel", (0, D / 2 + 0.1, wz + 0.15), (ww / 2, 0.02, wh / 2 - 0.15), sky)
    box("GrassPanel", (0, D / 2 + 0.1, wz - 0.55), (ww / 2, 0.02, 0.25), grass)

    # Baseboards
    box("BaseBack", (0, D / 2 - 0.08, 0.08), (W / 2 - 0.1, 0.03, 0.08), base)
    box("BaseLeft", (-W / 2 + 0.08, 0, 0.08), (0.03, D / 2 - 0.1, 0.08), base)
    box("BaseRight", (W / 2 - 0.08, 0, 0.08), (0.03, D / 2 - 0.1, 0.08), base)

    # Mint rug
    bpy.ops.mesh.primitive_cylinder_add(radius=1.45, depth=0.035, location=(0.1, -0.15, 0.02), vertices=64)
    rug = bpy.context.active_object
    rug.name = "MintRug"
    rug.data.materials.append(mint)
    smooth(rug)

    export_glb(f"{OUT}/locations/beep_room/room_shell.glb")


def create_yellow_chair():
    clear_scene()
    yellow = mat("ChairYellow", (0.98, 0.82, 0.18), 0.75)
    wood = mat("ChairWood", (0.72, 0.55, 0.32), 0.6)

    seat = box("Seat", (0, 0, 0.32), (0.42, 0.40, 0.10), yellow)
    add_subsurf(seat, 2)
    back = box("Back", (0, 0.28, 0.62), (0.42, 0.10, 0.32), yellow)
    add_subsurf(back, 2)
    for x in (-0.36, 0.36):
        arm = box("Arm", (x, 0, 0.45), (0.08, 0.34, 0.10), yellow)
        add_subsurf(arm, 2)
    for x, y in [(-0.30, -0.28), (0.30, -0.28), (-0.30, 0.28), (0.30, 0.28)]:
        cylinder("Leg", (x, y, 0.12), 0.035, 0.24, wood, 12)

    export_glb(f"{OUT}/props/toys/yellow_armchair.glb")


def create_basket():
    clear_scene()
    green = mat("BasketGreen", (0.28, 0.72, 0.40), 0.7)
    rim_c = mat("BasketRim", (0.22, 0.60, 0.32), 0.65)
    # Outer
    outer = cylinder("BasketOuter", (0, 0, 0.18), 0.30, 0.36, green, 40)
    # Inner darker smaller (visual hollow)
    inner = cylinder("BasketInner", (0, 0, 0.22), 0.25, 0.32, rim_c, 40)
    rim = cylinder("Rim", (0, 0, 0.36), 0.31, 0.04, rim_c, 40)
    export_glb(f"{OUT}/props/basket/green_basket.glb")


def create_ball():
    clear_scene()
    red = mat("BallRed", (0.90, 0.12, 0.12), 0.4)
    # Ø 28cm
    ball = sphere("RedBall", (0, 0, 0.14), 0.14, red, 48)
    # Soft highlight stripe
    stripe = mat("BallStripe", (1.0, 0.35, 0.35), 0.35)
    # Just the ball is enough for toddlers
    export_glb(f"{OUT}/props/ball/red_ball.glb")


def create_blocks():
    clear_scene()
    colors = [
        (0.95, 0.30, 0.35),
        (0.30, 0.55, 0.95),
        (0.98, 0.82, 0.15),
        (0.35, 0.78, 0.40),
        (0.85, 0.45, 0.85),
    ]
    for i, c in enumerate(colors):
        m = mat(f"Block{i}", c, 0.65)
        o = box(f"Block{i}", (i * 0.13 - 0.26, 0, 0.055), (0.055, 0.055, 0.055), m)
        add_subsurf(o, 1)
    export_glb(f"{OUT}/props/blocks/color_blocks.glb")


def create_shelf():
    clear_scene()
    wood = mat("ShelfWood", (0.78, 0.62, 0.42), 0.6)
    # Low toddler shelf ~0.9m
    box("ShelfBack", (0, 0.05, 0.45), (0.55, 0.03, 0.45), wood)
    box("ShelfBottom", (0, 0, 0.05), (0.55, 0.18, 0.03), wood)
    box("ShelfMid", (0, 0, 0.45), (0.55, 0.18, 0.03), wood)
    box("ShelfTop", (0, 0, 0.85), (0.55, 0.18, 0.03), wood)
    box("ShelfLeft", (-0.52, 0, 0.45), (0.03, 0.18, 0.45), wood)
    box("ShelfRight", (0.52, 0, 0.45), (0.03, 0.18, 0.45), wood)
    # Small books
    for i, c in enumerate([(0.9, 0.3, 0.3), (0.3, 0.5, 0.9), (0.95, 0.8, 0.2), (0.4, 0.75, 0.4)]):
        m = mat(f"Book{i}", c, 0.7)
        box(f"Book{i}", (-0.25 + i * 0.15, 0.02, 0.55), (0.05, 0.12, 0.12), m)
    export_glb(f"{OUT}/props/toys/shelf.glb")


def create_lamp():
    clear_scene()
    wood = mat("LampWood", (0.7, 0.55, 0.35), 0.55)
    shade = mat("LampShade", (1.0, 0.95, 0.8), 0.8, emit=0.35)
    cylinder("Pole", (0, 0, 0.55), 0.025, 1.1, wood, 16)
    sphere("Base", (0, 0, 0.06), 0.12, wood, 20)
    cylinder("Shade", (0, 0, 1.15), 0.22, 0.28, shade, 24)
    export_glb(f"{OUT}/props/toys/floor_lamp.glb")


def create_teddy():
    clear_scene()
    brown = mat("Teddy", (0.72, 0.48, 0.28), 0.85)
    dark = mat("TeddyNose", (0.15, 0.1, 0.08), 0.5)
    body = sphere("Body", (0, 0, 0.12), 0.10, brown, 24)
    head = sphere("Head", (0, 0, 0.26), 0.08, brown, 24)
    for x in (-0.07, 0.07):
        sphere("Ear", (x, 0, 0.32), 0.035, brown, 16)
    sphere("Nose", (0, 0.07, 0.26), 0.02, dark, 12)
    export_glb(f"{OUT}/props/toys/teddy.glb")


if __name__ == "__main__":
    create_beep()
    create_room()
    create_yellow_chair()
    create_basket()
    create_ball()
    create_blocks()
    create_shelf()
    create_lamp()
    create_teddy()
    print("ALL SOFT-TOY ASSETS DONE")

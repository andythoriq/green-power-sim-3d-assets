import bpy
import math

def clean_scene():
    """Delete all objects and purge orphan data to start fresh."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)

    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.materials:
        if block.users == 0:
            bpy.data.materials.remove(block)


def create_group_empty(name, location=(0, 0, 0)):
    """Create an Empty as a parent container for a model group."""
    bpy.ops.object.empty_add(type='PLAIN_AXES', location=location)
    empty = bpy.context.object
    empty.name = name
    empty.empty_display_size = 0.3
    return empty


def parent_to(child_obj, parent_obj):
    """Parent child to parent while keeping world transform."""
    child_obj.parent = parent_obj
    child_obj.matrix_parent_inverse = parent_obj.matrix_world.inverted()


def set_origin_to_point(obj, point):
    """Set an object's origin to a specific world-space point."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.context.scene.cursor.location = point
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')


def apply_scale(obj):
    """Apply scale transform to freeze geometry."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)


def apply_all_transforms(obj):
    """Apply location, rotation, and scale transforms."""
    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def frame_viewport():
    """Frame the viewport to show all objects."""
    for area in bpy.context.screen.areas:
        if area.type == 'VIEW_3D':
            for region in area.regions:
                if region.type == 'WINDOW':
                    override = bpy.context.copy()
                    override['area'] = area
                    override['region'] = region
                    with bpy.context.temp_override(**override):
                        bpy.ops.view3d.view_all()
                    break


def finalize():
    """Deselect all, reset cursor, and frame viewport."""
    bpy.ops.object.select_all(action='DESELECT')
    bpy.context.scene.cursor.location = (0, 0, 0)
    frame_viewport()


# ══════════════════════════════════════════════════════════════
#  WATER WHEEL
# ══════════════════════════════════════════════════════════════

def create_water_wheel():
    """
    Create a water wheel model centered at the world origin.

    Origin Points:
      - Frame/Supports (static): Center-bottom of support pillars (0, 0, 0).
      - Wheel (rim + paddles): Center of the axle cylinder.
    The axle-centered origin lets Roblox rotate the wheel smoothly
    on its shaft, like a bicycle wheel spinning on its hub.
    """
    wheel_center = (0, 0, 0.7)
    group = create_group_empty("WaterWheel_Group", (0, 0, 0))

    wheel_r = 0.6
    wheel_w = 0.5
    n_paddles = 12
    n_spokes = 8

    # --- 1. STATIC FRAME (Tiang Penyangga Kiri & Kanan) ---
    pillar_h = 0.7
    for side, tag in [(-1, 'L'), (1, 'R')]:
        y_pos = side * (wheel_w / 2 + 0.15)

        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, y_pos, pillar_h / 2))
        pillar = bpy.context.object
        pillar.scale = (0.08, 0.08, pillar_h)
        pillar.name = f"WaterWheel_Support_{tag}"
        parent_to(pillar, group)

    # --- 2. ROTATING WHEEL (Kincir Berputar) ---
    # Poros Tengah (Axle)
    axle_len = wheel_w + 0.5
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12, radius=0.06, depth=axle_len,
        location=wheel_center
    )
    axle = bpy.context.object
    axle.rotation_euler = (math.radians(90), 0, 0)
    axle.name = "WaterWheel_Axle"
    set_origin_to_point(axle, wheel_center)
    parent_to(axle, group)

    # Dua Cincin Luar (Rims)
    for side, tag in [(-1, 'L'), (1, 'R')]:
        y_pos = side * (wheel_w / 2)
        bpy.ops.mesh.primitive_torus_add(
            major_radius=wheel_r, minor_radius=0.02,
            major_segments=24, minor_segments=8,
            location=(0, y_pos, 0.7)
        )
        rim = bpy.context.object
        rim.rotation_euler = (math.radians(90), 0, 0)
        rim.name = f"WaterWheel_Rim_{tag}"
        set_origin_to_point(rim, wheel_center)
        parent_to(rim, group)

    # Ruji-ruji (Spokes)
    for side, tag in [(-1, 'L'), (1, 'R')]:
        y_pos = side * (wheel_w / 2)
        for i in range(n_spokes):
            angle = math.radians(i * (360 / n_spokes))
            spoke_len = wheel_r - 0.02

            bpy.ops.mesh.primitive_cylinder_add(
                vertices=6, radius=0.015, depth=spoke_len,
                location=(0, y_pos, 0.7 + spoke_len / 2)
            )
            spoke = bpy.context.object
            set_origin_to_point(spoke, wheel_center)
            spoke.rotation_euler = (0, -angle, 0)
            spoke.name = f"WaterWheel_Spoke_{tag}_{i+1}"
            parent_to(spoke, group)

    # --- 3. PADDLES (Pelat Pengayuh / Sekop) ---
    for i in range(n_paddles):
        angle = math.radians(i * (360 / n_paddles))

        # Meletakkan papan tepat di puncak atas kincir
        pz = 0.7 + wheel_r

        bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, pz))
        paddle = bpy.context.object

        paddle.scale = (0.02, wheel_w + 0.02, 0.16)
        apply_scale(paddle)

        # Pindahkan titik putar ke tengah poros
        set_origin_to_point(paddle, wheel_center)

        # Putar mengelilingi poros
        paddle.rotation_euler = (0, angle, 0)

        paddle.name = f"WaterWheel_Paddle_{i+1}"
        parent_to(paddle, group)

    return group


# Execute
if __name__ == "__main__":
    clean_scene()

    print("=" * 50)
    print("  Water Wheel — Asset Generator")
    print("=" * 50)

    water = create_water_wheel()

    finalize()

    children = [o for o in bpy.data.objects if o.parent == water]
    print(f"  WaterWheel_Group: {len(children)} child objects")

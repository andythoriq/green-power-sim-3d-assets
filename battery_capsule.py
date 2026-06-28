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
#  BATTERY / ENERGY CAPSULE
# ══════════════════════════════════════════════════════════════

def create_battery_capsule():
    """
    Create a futuristic battery / energy capsule centered at the world origin.

    Origin Points:
      - Glass Shell (static): Center-bottom of the bottom cap base (0, 0, 0).
      - Energy Core (neon): Bottom base of the inner core cylinder.
    The core's bottom-base origin is CRITICAL for Roblox: when scaling
    Size.Y, the core expands upward only (simulating charge fill).
    """
    group = create_group_empty("Battery_Group", (0, 0, 0))

    # Capsule dimensions
    total_h = 0.60         # total capsule height
    outer_r = 0.14         # outer shell radius
    inner_r = 0.10         # inner core radius
    cap_h = 0.04           # cap thickness
    shell_h = total_h - 2 * cap_h  # shell height (between caps)

    cap_bottom_z = 0.0     # bottom cap sits on ground
    shell_bottom_z = cap_h
    shell_top_z = shell_bottom_z + shell_h
    cap_top_z = shell_top_z

    # ────────────────────────────────────────────
    #  BOTTOM METALLIC CAP
    # ────────────────────────────────────────────
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=outer_r + 0.02,
        depth=cap_h,
        location=(0, 0, cap_bottom_z + cap_h / 2)
    )
    bot_cap = bpy.context.object
    bot_cap.name = "Battery_Cap_Bottom"
    parent_to(bot_cap, group)

    # Bottom cap detail ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=outer_r + 0.01,
        minor_radius=0.008,
        major_segments=16, minor_segments=4,
        location=(0, 0, cap_bottom_z + cap_h)
    )
    bot_ring = bpy.context.object
    bot_ring.name = "Battery_Cap_Bottom_Ring"
    parent_to(bot_ring, group)

    # Bottom terminal contact (small nub underneath)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.04, depth=0.02,
        location=(0, 0, cap_bottom_z - 0.01)
    )
    bot_term = bpy.context.object
    bot_term.name = "Battery_Terminal_Bottom"
    parent_to(bot_term, group)

    # ────────────────────────────────────────────
    #  TOP METALLIC CAP
    # ────────────────────────────────────────────
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=outer_r + 0.02,
        depth=cap_h,
        location=(0, 0, cap_top_z + cap_h / 2)
    )
    top_cap = bpy.context.object
    top_cap.name = "Battery_Cap_Top"
    parent_to(top_cap, group)

    # Top cap detail ring
    bpy.ops.mesh.primitive_torus_add(
        major_radius=outer_r + 0.01,
        minor_radius=0.008,
        major_segments=16, minor_segments=4,
        location=(0, 0, cap_top_z)
    )
    top_ring = bpy.context.object
    top_ring.name = "Battery_Cap_Top_Ring"
    parent_to(top_ring, group)

    # Top terminal contact (raised nub)
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.035, depth=0.025,
        location=(0, 0, cap_top_z + cap_h + 0.0125)
    )
    top_nub = bpy.context.object
    top_nub.name = "Battery_Terminal_Top"
    parent_to(top_nub, group)

    # Top terminal tip
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=6, radius=0.018, depth=0.015,
        location=(0, 0, cap_top_z + cap_h + 0.025 + 0.0075)
    )
    top_tip = bpy.context.object
    top_tip.name = "Battery_Terminal_Tip"
    parent_to(top_tip, group)

    # ────────────────────────────────────────────
    #  OUTER CYLINDER SHELL (transparent Glass in Roblox)
    # ────────────────────────────────────────────
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=16, radius=outer_r,
        depth=shell_h,
        location=(0, 0, shell_bottom_z + shell_h / 2)
    )
    shell = bpy.context.object
    shell.name = "Battery_Shell_Outer"
    parent_to(shell, group)

    # ────────────────────────────────────────────
    #  INNER ENERGY CORE (Neon material in Roblox)
    # ────────────────────────────────────────────

    core_h = shell_h - 0.04  # slightly shorter than shell
    core_bottom_z = shell_bottom_z + 0.02

    bpy.ops.mesh.primitive_cylinder_add(
        vertices=12, radius=inner_r,
        depth=core_h,
        location=(0, 0, core_bottom_z + core_h / 2)
    )
    core = bpy.context.object
    core.name = "Battery_EnergyCore"

    # *** SET ORIGIN TO BOTTOM BASE OF THE CORE ***
    # This is CRITICAL so Roblox can scale it upward from the bottom
    core_origin_point = (0, 0, core_bottom_z)
    set_origin_to_point(core, core_origin_point)

    parent_to(core, group)

    # ────────────────────────────────────────────
    #  ENERGY INDICATOR RINGS (Neon glow bands)
    # ────────────────────────────────────────────

    # Three evenly spaced rings on the outer shell
    ring_positions = [
        shell_bottom_z + shell_h * 0.25,
        shell_bottom_z + shell_h * 0.50,
        shell_bottom_z + shell_h * 0.75,
    ]
    for i, rz in enumerate(ring_positions):
        bpy.ops.mesh.primitive_torus_add(
            major_radius=outer_r + 0.008,
            minor_radius=0.010,
            major_segments=16, minor_segments=6,
            location=(0, 0, rz)
        )
        ering = bpy.context.object
        ering.name = f"Battery_EnergyRing_{i+1}"
        parent_to(ering, group)

    # ────────────────────────────────────────────
    #  STATUS LED (tiny sphere on body)
    # ────────────────────────────────────────────
    bpy.ops.mesh.primitive_ico_sphere_add(
        subdivisions=1, radius=0.012,
        location=(0, outer_r + 0.01, shell_bottom_z + shell_h * 0.85)
    )
    led = bpy.context.object
    led.name = "Battery_StatusLED"
    parent_to(led, group)

    return group


# Execute
if __name__ == "__main__":
    clean_scene()

    print("=" * 50)
    print("  Battery / Energy Capsule — Asset Generator")
    print("=" * 50)

    battery = create_battery_capsule()

    finalize()

    children = [o for o in bpy.data.objects if o.parent == battery]
    print(f"  Battery_Group: {len(children)} child objects")

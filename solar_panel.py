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
#  SOLAR PANEL
# ══════════════════════════════════════════════════════════════

def create_solar_panel():
    """
    Create a solar panel model centered at the world origin.

    Origin Point: Center of the bottom face of the base plate (0, 0, 0).
    This ensures the panel sits flush on the ground when placed in Roblox.
    """
    group = create_group_empty("SolarPanel_Group", (0, 0, 0))

    # ── Base Plate ──
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.03))
    base = bpy.context.object
    base.scale = (0.3, 0.3, 0.03)
    base.name = "SolarPanel_Base"
    parent_to(base, group)

    # ── Support Pole ──
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=8, radius=0.06, depth=0.65,
        location=(0, 0, 0.06 + 0.325)
    )
    pole = bpy.context.object
    pole.name = "SolarPanel_Pole"
    parent_to(pole, group)

    # ── Pivot Bracket (connects pole to panel — small cube) ──
    pivot_z = 0.72
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, pivot_z))
    bracket = bpy.context.object
    bracket.scale = (0.08, 0.06, 0.04)
    bracket.name = "SolarPanel_Bracket"
    parent_to(bracket, group)

    # ── Panel Frame (outer rim of the panel) ──
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, pivot_z + 0.042))
    frame = bpy.context.object
    frame.scale = (0.65, 0.55, 0.025)
    frame.rotation_euler = (math.radians(30), 0, 0)
    frame.name = "SolarPanel_Frame"
    parent_to(frame, group)

    # ── Panel Surface (the dark photovoltaic face — inset) ──
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, pivot_z + 0.042))
    surface = bpy.context.object
    surface.scale = (0.60, 0.50, 0.03)
    surface.rotation_euler = (math.radians(30), 0, 0)
    # Slight offset above frame to prevent z-fighting
    surface.location.z += 0.015
    surface.name = "SolarPanel_Surface"
    parent_to(surface, group)

    return group


# Execute
if __name__ == "__main__":
    clean_scene()

    print("=" * 50)
    print("  Solar Panel — Asset Generator")
    print("=" * 50)

    solar = create_solar_panel()

    finalize()

    children = [o for o in bpy.data.objects if o.parent == solar]
    print(f"  SolarPanel_Group: {len(children)} child objects")

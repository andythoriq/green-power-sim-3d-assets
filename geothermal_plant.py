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
#  GEOTHERMAL PLANT
# ══════════════════════════════════════════════════════════════

def create_geothermal_plant():
    """
    Create a geothermal plant model centered at the world origin.

    Origin Point: Center of the bottom face of the base concrete pad (0, 0, 0).
    This massive building needs a stable ground-level placement point
    for reliable positioning in Roblox.
    """
    group = create_group_empty("GeothermalPlant_Group", (0, 0, 0))

    # --- 1. BASE PAD (Fondasi Beton) ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.05))
    base = bpy.context.object
    base.scale = (1.0, 0.6, 0.1)
    base.name = "Geothermal_BasePad"
    parent_to(base, group)

    # --- 2. MAIN FACILITY (Bangunan Sentral / Kotak) ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0.15, 0, 0.5))
    bldg = bpy.context.object
    bldg.scale = (0.3, 0.4, 0.8)
    bldg.name = "Geothermal_FacilityBuilding"
    parent_to(bldg, group)

    # --- 3. COOLING TOWER (Cerobong Pendingin Menjulang) ---
    bpy.ops.mesh.primitive_cone_add(
        vertices=24, radius1=0.20, radius2=0.12,
        depth=2.4, location=(-0.25, 0, 1.3)
    )
    tower = bpy.context.object
    tower.name = "Geothermal_CoolingTower"
    parent_to(tower, group)

    # Bibir atas cerobong
    bpy.ops.mesh.primitive_torus_add(
        major_radius=0.12, minor_radius=0.015,
        major_segments=24, minor_segments=6,
        location=(-0.25, 0, 2.5)
    )
    rim = bpy.context.object
    rim.name = "Geothermal_CoolingTower_Rim"
    parent_to(rim, group)

    # Membuat dua tingkat pipa
    for z_pos, pipe_name in [(0.25, "Lower"), (0.75, "Upper")]:
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=8, radius=0.035, depth=0.4,
            location=(-0.05, 0, z_pos)
        )
        conn_pipe = bpy.context.object
        conn_pipe.rotation_euler = (0, math.radians(90), 0)
        conn_pipe.name = f"Geothermal_ConnectorPipe_{pipe_name}"
        parent_to(conn_pipe, group)

    # --- 4. EXTRACTION PIPES (Sistem Perpipaan Ekstraksi) ---
    for y_pos, pname in [(0.15, "PipeA"), (-0.15, "PipeB")]:
        pipe_x = 0.40

        # Pipa Vertikal menembus tanah
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=12, radius=0.04, depth=0.3,
            location=(pipe_x, y_pos, 0.1)
        )
        v_pipe = bpy.context.object
        v_pipe.name = f"Geothermal_{pname}_Vertical"
        parent_to(v_pipe, group)

        # Flange di tanah
        bpy.ops.mesh.primitive_torus_add(
            major_radius=0.05, minor_radius=0.015,
            major_segments=12, minor_segments=6,
            location=(pipe_x, y_pos, 0.1)
        )
        flange = bpy.context.object
        flange.name = f"Geothermal_{pname}_Flange"
        parent_to(flange, group)

        # Pipa Horizontal (masuk ke dinding bawah kotak sentral)
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=12, radius=0.04, depth=0.1,
            location=(pipe_x - 0.05, y_pos, 0.25)
        )
        h_pipe = bpy.context.object
        h_pipe.rotation_euler = (0, math.radians(90), 0)
        h_pipe.name = f"Geothermal_{pname}_Horizontal"
        parent_to(h_pipe, group)

        # Siku Pipa (Elbow)
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2, radius=0.045,
            location=(pipe_x, y_pos, 0.25)
        )
        elbow = bpy.context.object
        elbow.name = f"Geothermal_{pname}_Elbow"
        parent_to(elbow, group)

    return group


# Execute
if __name__ == "__main__":
    clean_scene()

    print("=" * 50)
    print("  Geothermal Plant — Asset Generator")
    print("=" * 50)

    geo = create_geothermal_plant()

    finalize()

    children = [o for o in bpy.data.objects if o.parent == geo]
    print(f"  GeothermalPlant_Group: {len(children)} child objects")

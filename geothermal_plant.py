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

    # ═══ DIMENSION CONSTANTS ═══
    pad_h = 0.1           # base pad thickness

    tower_r_bottom = 0.38  # cooling tower base radius
    tower_r_top = 0.24     # cooling tower top radius
    tower_depth = 1.5      # cooling tower height
    tower_z = pad_h + tower_depth / 2
    tower_x = -0.45        # X position of both towers
    tower_spacing_y = 0.50 # Y offset of each tower from center

    # Heat Exchanger 1 (formerly Generator) - lower Y side
    gen_w = 0.40   # width (X)
    gen_d = 0.45   # depth (Y)
    gen_h = 0.55   # height (Z)
    gen_x = 0.35
    gen_y = -tower_spacing_y

    # Heat Exchanger 2 — upper Y side
    hex_w = 0.40   # width (X)
    hex_d = 0.45   # depth (Y)
    hex_h = 0.55   # height (Z)
    hex_x = 0.35
    hex_y = tower_spacing_y

    # Extraction pipe X position
    ext_pipe_x = 0.80

    # Base pad scale - primitive_cube_add(size=1) has around 0.5 extent,
    # so actual half-extent = 0.5 * scale.
    # Objects extend: X = -0.83 to 0.72,  Y around 0.88
    # With ~0.22 padding: need around 1.05 in X, around 1.10 in Y
    # scale = desired_half / 0.5 = desired_half * 2
    pad_scale_x = 2
    pad_scale_y = 2

    # --- 1. BASE PAD (Fondasi Beton) ---
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, pad_h / 2))
    base = bpy.context.object
    base.scale = (pad_scale_x, pad_scale_y, pad_h)
    base.name = "Geothermal_BasePad"
    parent_to(base, group)

    # --- 2. HEAT EXCHANGER 1 ---
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(gen_x, gen_y, pad_h + gen_h / 2)
    )
    gen_bldg = bpy.context.object
    gen_bldg.scale = (gen_w, gen_d, gen_h)
    gen_bldg.name = "Geothermal_HeatExchanger"
    parent_to(gen_bldg, group)

    # --- 3. HEAT EXCHANGER 2 ---
    bpy.ops.mesh.primitive_cube_add(
        size=1,
        location=(hex_x, hex_y, pad_h + hex_h / 2)
    )
    hex_bldg = bpy.context.object
    hex_bldg.scale = (hex_w, hex_d, hex_h)
    hex_bldg.name = "Geothermal_HeatExchanger"
    parent_to(hex_bldg, group)

    # --- 4. TWO COOLING TOWERS (Cerobong Pendingin) ---
    tower_positions = [
        ("A", tower_x, -tower_spacing_y),
        ("B", tower_x,  tower_spacing_y),
    ]

    for t_label, t_x, t_y in tower_positions:
        # Tower body (truncated cone)
        bpy.ops.mesh.primitive_cone_add(
            vertices=128, radius1=tower_r_bottom, radius2=tower_r_top,
            depth=tower_depth, location=(t_x, t_y, tower_z)
        )
        tower = bpy.context.object
        tower.name = f"Geothermal_CoolingTower_{t_label}"
        parent_to(tower, group)

        # Bibir atas cerobong (top rim)
        rim_z = pad_h + tower_depth
        bpy.ops.mesh.primitive_torus_add(
            major_radius=tower_r_top, minor_radius=0.025,
            major_segments=32, minor_segments=8,
            location=(t_x, t_y, rim_z)
        )
        rim = bpy.context.object
        rim.name = f"Geothermal_CoolingTower_{t_label}_Rim"
        parent_to(rim, group)

        # --- CONNECTOR PIPES (Tower to Building) ---
        # Tower A (y<0) connects to Generator, Tower B (y>0) to Heat Exchanger
        bldg_x = gen_x if t_y < 0 else hex_x
        bldg_w = gen_w if t_y < 0 else hex_w

        pipe_start_x = t_x + tower_r_bottom * 0.6
        pipe_end_x = bldg_x - bldg_w / 2
        pipe_len = pipe_end_x - pipe_start_x
        pipe_mid_x = (pipe_start_x + pipe_end_x) / 2

        for z_pos, pipe_name in [(0.30, "Lower"), (0.50, "Upper")]:
            bpy.ops.mesh.primitive_cylinder_add(
                vertices=10, radius=0.045, depth=abs(pipe_len),
                location=(pipe_mid_x, t_y, z_pos)
            )
            conn_pipe = bpy.context.object
            conn_pipe.rotation_euler = (0, math.radians(90), 0)
            conn_pipe.name = f"Geothermal_ConnectorPipe_{t_label}_{pipe_name}"
            parent_to(conn_pipe, group)

    # --- 5. EXTRACTION PIPES (Sistem Perpipaan Ekstraksi) ---
    pipe_positions = [
        (ext_pipe_x,  tower_spacing_y - 0.15, "PipeA"),
        (ext_pipe_x, -tower_spacing_y - 0.15, "PipeB"),
        (ext_pipe_x,  tower_spacing_y + 0.15, "PipeC"),
        (ext_pipe_x, -tower_spacing_y + 0.15, "PipeD"),
    ]

    for pipe_x, pipe_y, pname in pipe_positions:
        # Pipa Vertikal menembus tanah
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=12, radius=0.05, depth=0.40,
            location=(pipe_x, pipe_y, pad_h + 0.10)
        )
        v_pipe = bpy.context.object
        v_pipe.name = f"Geothermal_{pname}_Vertical"
        parent_to(v_pipe, group)

        # Determine target building for horizontal pipe
        bldg_x = gen_x if pipe_y < 0 else hex_x
        bldg_w = gen_w if pipe_y < 0 else hex_w

        # Pipa Horizontal (menuju ke dinding kotak)
        h_pipe_start = bldg_x + bldg_w / 2
        h_pipe_len = pipe_x - h_pipe_start
        h_pipe_mid_x = (pipe_x + h_pipe_start) / 2
        bpy.ops.mesh.primitive_cylinder_add(
            vertices=12, radius=0.05, depth=abs(h_pipe_len),
            location=(h_pipe_mid_x, pipe_y, pad_h + 0.30)
        )
        h_pipe = bpy.context.object
        h_pipe.rotation_euler = (0, math.radians(90), 0)
        h_pipe.name = f"Geothermal_{pname}_Horizontal"
        parent_to(h_pipe, group)

        # Siku Pipa (Elbow)
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=2, radius=0.055,
            location=(pipe_x, pipe_y, pad_h + 0.30)
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

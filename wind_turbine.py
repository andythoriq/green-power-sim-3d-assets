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
#  WIND TURBINE
# ══════════════════════════════════════════════════════════════

def create_wind_turbine():
    """
    Create a wind turbine model centered at the world origin.

    Origin Points:
      - Tower (static): Center of the bottom face of the foundation (0, 0, 0).
      - Rotor (hub + blades): Center of the hub sphere.
    The hub's origin allows Roblox scripts to rotate the blades smoothly
    around the center of the hub, not swinging from the tower base.
    """
    group = create_group_empty("WindTurbine_Group", (0, 0, 0))
    tower_h = 1.8

    # ── Foundation (Fondasi Bawah) ──
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0, 0.04))
    foundation = bpy.context.object
    foundation.scale = (0.35, 0.35, 0.04)
    foundation.name = "WindTurbine_Foundation"
    parent_to(foundation, group)

    # ── Tower (Menara Utama) ──
    bpy.ops.mesh.primitive_cone_add(
        vertices=64,
        radius1=0.12,   # Diameter bawah lebih lebar
        radius2=0.07,   # Diameter atas meruncing
        depth=tower_h,
        location=(0, 0, 0.06 + tower_h / 2)
    )
    tower = bpy.context.object
    tower.name = "WindTurbine_Tower"
    parent_to(tower, group)

    # ── Nacelle (Kotak Mesin di belakang Baling-baling) ──
    hub_z = 0.06 + tower_h + 0.04
    bpy.ops.mesh.primitive_cube_add(size=1, location=(0, 0.0, hub_z))
    nacelle = bpy.context.object
    nacelle.scale = (0.10, 0.18, 0.08)
    nacelle.name = "WindTurbine_Nacelle"
    parent_to(nacelle, group)

    # ── Hub (Piringan Pusat Rotasi) ──
    hub_pos = (0, 0.18, hub_z)
    
    # Piringan pertama
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.10, depth=0.04,
        location=hub_pos,
        rotation=(math.radians(90), 0, 0)
    )
    hub = bpy.context.object
    hub.name = "WindTurbine_Hub"
    parent_to(hub, group)
    
    # Piringan kedua
    bpy.ops.mesh.primitive_cylinder_add(
        radius=0.06, depth=0.02,
        location=(0, 0.18 + 0.03, hub_z),
        rotation=(math.radians(90), 0, 0)
    )
    hub_front = bpy.context.object
    hub_front.name = "WindTurbine_Hub_Front"
    set_origin_to_point(hub_front, hub_pos)
    parent_to(hub_front, group)

    # ── 3 Blades (Baling-baling) ──
    blade_len = 0.75
    for i in range(3):
        angle = math.radians(i * 120)

        bpy.ops.mesh.primitive_cube_add(size=1, location=hub_pos)
        blade = bpy.context.object

        # X = Lebar, Y = Ketebalan, Z = Panjang total
        blade.scale = (0.055, 0.018, blade_len)
        apply_scale(blade)

        blade.location.z += (blade_len / 2) - 0.08

        # Mengembalikan titik pusat rotasi (Origin) tepat ke tengah hub
        set_origin_to_point(blade, hub_pos)

        # Rotasi Z dihilangkan agar baling-baling lurus.
        # Rotasi Y (-angle) mendistribusikan ke-3 baling dalam bentuk segitiga sama sisi.
        blade.rotation_euler = (0, -angle, 0)

        blade.name = f"WindTurbine_Blade_{i+1}"
        parent_to(blade, group)

    group.rotation_euler = (0, 0, math.radians(180))

    return group


# Execute
if __name__ == "__main__":
    clean_scene()

    print("=" * 50)
    print("  Wind Turbine — Asset Generator")
    print("=" * 50)

    wind = create_wind_turbine()

    finalize()

    children = [o for o in bpy.data.objects if o.parent == wind]
    print(f"  WindTurbine_Group: {len(children)} child objects")

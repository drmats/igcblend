#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

import bpy # type: ignore
from typing import cast

from lib.layout import (
    clear_selection,
    select_object,
)




# ...
def build_plane (
    point_data: list[tuple[float, float, float]],
    name: str = "Plane",
) -> tuple[bpy.types.Object, bpy.types.Mesh]:
    mesh_data = bpy.data.meshes.new(name = name + "_Mesh")
    plane_object = bpy.data.objects.new(name = name, object_data = mesh_data)
    mesh_data.from_pydata(point_data, [], [(0, 1, 2, 3)])
    mesh_data.update()
    bpy.context.collection.objects.link(plane_object)

    return (plane_object, mesh_data)




# ...
def merge_planes (
    name_prefix: str,
    new_name: str | None = None,
    merge_distance: int = 100,
) -> bpy.types.Object:
    # find all `name_prefix*` meshes
    objects = [
        obj for obj in bpy.data.objects
        if obj.type == "MESH" and obj.name.startswith(name_prefix)
    ]
    if not objects:
        raise ValueError(f"No meshes starting with '{name_prefix}' found.")

    # take care of selection
    clear_selection()
    for obj in objects:
        obj.select_set(True)
    select_object(objects[0])

    # join into one mesh
    bpy.ops.object.join()
    merged_obj = cast(bpy.types.Object, bpy.context.active_object)

    # enter edit mode
    bpy.ops.object.mode_set(mode = "EDIT")

    # merge by distance
    bpy.ops.mesh.select_all(action = "SELECT")
    bpy.ops.mesh.remove_doubles(threshold = merge_distance)

    # delete loose
    bpy.ops.mesh.delete_loose()

    # back to object mode
    bpy.ops.object.mode_set(mode = "OBJECT")

    # delete unused meshes
    meshes = [
        mesh for mesh in bpy.data.meshes
        if mesh.name.startswith(name_prefix) and mesh.users == 0
    ]
    for mesh in meshes:
        bpy.data.meshes.remove(mesh)

    # set new name
    if new_name is None:
        new_name = f"{name_prefix}_Merged"
    merged_obj.name = new_name
    cast(bpy.types.Mesh, merged_obj.data).name = f"{new_name}_Mesh"

    # leave nothing selected
    clear_selection()

    return merged_obj




# ...
def build_3d_curve (
    point_data: list[tuple[float, float, float]],
    name = "Curve",
    diameter = 8,
    resolution = 3,
) -> tuple[bpy.types.Object, bpy.types.Curve]:
    curve = bpy.data.curves.new(name + "_BezierCurve", type = "CURVE")
    curve.dimensions = "3D"
    curve.resolution_u = 12
    curve.bevel_depth = diameter / 2
    curve.bevel_resolution = resolution

    spline = curve.splines.new("BEZIER")
    spline.bezier_points.add(len(point_data) - 1)

    for bp, co in zip(spline.bezier_points, point_data):
        bp.co = co
        bp.handle_left_type = "AUTO"
        bp.handle_right_type = "AUTO"

    obj = bpy.data.objects.new(name, curve)
    bpy.context.collection.objects.link(obj)

    return (obj, curve)

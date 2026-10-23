#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

import bpy # type: ignore

from lib.simplegeom import compute_2d_bounds_with_range




# ...
def remove_all_uv_layers (mesh: bpy.types.Mesh) -> None:
    while mesh.uv_layers:
        mesh.uv_layers.remove(mesh.uv_layers[0])




# ...
def create_top_projected_uv (
    mesh: bpy.types.Mesh,
    uv_map_name: str = "UVMap",
) -> bpy.types.MeshUVLoopLayer:
    # create new UV layer
    uv_layer = mesh.uv_layers.new(name = uv_map_name)
    assert uv_layer is not None
    mesh.uv_layers.active = uv_layer

    # compute geometry (x, y) bounds
    bounds = compute_2d_bounds_with_range(mesh)
    if bounds.range_x == 0 or bounds.range_y == 0:
        raise ValueError("Plane has zero size.")

    # assign top projected UV (project from top view with bounds)
    for poly in mesh.polygons:
        for loop_index in poly.loop_indices:
            loop = mesh.loops[loop_index]
            vtx = mesh.vertices[loop.vertex_index]
            u = (vtx.co.x - bounds.min_x) / bounds.range_x
            v = (vtx.co.y - bounds.min_y) / bounds.range_y
            uv_layer.data[loop_index].uv = (u, v)

    return uv_layer




# ...
def adjust_uv_for_pixel_centers (
    uv_layer: bpy.types.MeshUVLoopLayer,
    texture_width: int,
    texture_height: int,
) -> None:
    for mesh_uv_loop in uv_layer.data:
        u, v = mesh_uv_loop.uv
        u = u * (texture_width - 1) / texture_width + 0.5 / texture_width
        v = v * (texture_height - 1) / texture_height + 0.5 / texture_height
        mesh_uv_loop.uv = (u, v)

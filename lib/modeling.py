#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

import bpy # type: ignore
from dataclasses import dataclass




# ...
def build_plane (point_data: list[tuple[float, float, float]], name="Plane"):
    mesh_data = bpy.data.meshes.new(name=name+"_Mesh")
    plane_object = bpy.data.objects.new(name=name, object_data=mesh_data)
    mesh_data.from_pydata(point_data, [], [(0, 1, 2, 3)])
    mesh_data.update()
    bpy.context.collection.objects.link(plane_object)




# ...
@dataclass
class Bounds2D:
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    range_x: float
    range_y: float




# ...
def compute_2d_bounds (mesh: bpy.types.Mesh) -> Bounds2D:
    min_x = min(v.co.x for v in mesh.vertices)
    max_x = max(v.co.x for v in mesh.vertices)
    min_y = min(v.co.y for v in mesh.vertices)
    max_y = max(v.co.y for v in mesh.vertices)
    range_x = max_x - min_x
    range_y = max_y - min_y
    return Bounds2D(min_x, max_x, min_y, max_y, range_x, range_y)

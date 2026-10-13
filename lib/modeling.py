#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

import bpy # type: ignore




# ...
def build_plane (point_data: list[tuple[float, float, float]], name="Plane"):
    mesh_data = bpy.data.meshes.new(name=name+"_Mesh")
    plane_object = bpy.data.objects.new(name=name, object_data=mesh_data)
    mesh_data.from_pydata(point_data, [], [(0, 1, 2, 3)])
    mesh_data.update()
    bpy.context.collection.objects.link(plane_object)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

from typing import cast
import bpy # type: ignore




# ...
def get_mesh (object_name: str) -> tuple[bpy.types.Object, bpy.types.Mesh]:
    obj = bpy.data.objects.get(object_name)
    if obj is None:
        raise ValueError(f"Object '{object_name}' does not exist.")
    if obj.type != "MESH":
        raise ValueError(f"Object '{object_name}' is not a Mesh.")
    obj = cast(bpy.types.Object, obj)
    mesh = cast(bpy.types.Mesh, obj.data)
    return (obj, mesh)




# ...
def clear_selection () -> None:
    bpy.ops.object.select_all(action="DESELECT")




# ...
def select_object (obj: bpy.types.Object) -> None:
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

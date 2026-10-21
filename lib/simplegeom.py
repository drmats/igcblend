# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

import bpy # type: ignore
from dataclasses import dataclass
from numpy import float64
from shapely import get_coordinates




# extract coordinates from geometry and add z = 0.0
def flat_coords_3d (geometry) -> list[tuple[float, float, float]]:
    return [(x, y, float64(0.0)) for x, y in get_coordinates(geometry)]




# 2d translate points (don't move in `z`)
def translate (
    coords_3d: list[tuple[float, float, float]],
    by = (0, 0),
) -> list[tuple[float, float, float]]:
    return [(x - by[0], y - by[1], z) for x, y, z in coords_3d]




# `compute_2d_bounds()` return value
@dataclass
class Bounds2D:
    min_x: float
    max_x: float
    min_y: float
    max_y: float
    range_x: float
    range_y: float




# 2D bounding rectangle in local coords
# (independent of object scale, rotation and translation)
def compute_2d_bounds (mesh: bpy.types.Mesh) -> Bounds2D:
    min_x = min(v.co.x for v in mesh.vertices)
    max_x = max(v.co.x for v in mesh.vertices)
    min_y = min(v.co.y for v in mesh.vertices)
    max_y = max(v.co.y for v in mesh.vertices)
    range_x = max_x - min_x
    range_y = max_y - min_y
    return Bounds2D(min_x, max_x, min_y, max_y, range_x, range_y)

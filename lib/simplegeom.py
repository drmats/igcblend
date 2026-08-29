# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

from numpy import float64
from shapely import get_coordinates




# extract coordinates from geometry and add z = 0.0
def flat_coords_3d (geometry) -> list[tuple[float, float, float]]:
    return [(x, y, float64(0.0)) for x, y in get_coordinates(geometry)]




# 2d translate points (don't move in `z`)
def translate (
    coords_3d: list[tuple[float, float, float]],
    by=(0, 0),
) -> list[tuple[float, float, float]]:
    return [(x - by[0], y - by[1], z) for x, y, z in coords_3d]

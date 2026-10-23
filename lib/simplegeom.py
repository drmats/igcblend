# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

import bpy # type: ignore
from dataclasses import dataclass
from shapely import (
    box,
    get_coordinates,
)
from shapely.geometry.base import BaseGeometry
from shapely.geometry import Polygon
from shapely.ops import transform

from lib.projections import CRSTransform




# 2D bounds - works with array of (x, y) coordinates, any CRS
def compute_2d_bounds (
    coords: list[tuple[float, ...]],
) -> tuple[float, float, float, float]:
    """
    2D bounds.

    :param coords: list of (x, y, ...) float coordinates (any CRS)
    :return: (min_x, min_y, max_x, max_y) float tuple
    """

    return (
        min(coord[0] for coord in coords),
        min(coord[1] for coord in coords),
        max(coord[0] for coord in coords),
        max(coord[1] for coord in coords),
    )




# center of 2D bounds (any CRS)
def compute_center_of_2d_bounds (
    min_x: float, min_y: float, max_x: float, max_y: float,
) -> tuple[float, float]:
    """
    Center of 2D bounds.

    :param min_x: east
    :param min_y: south
    :param max_x: west
    :param max_y: north
    :return: (x, y) float tuple
    """

    return ((min_x + max_x) / 2, (min_y + max_y) / 2)




# range of 2D bounds (any CRS)
def compute_range_of_2d_bounds (
    min_x: float, min_y: float, max_x: float, max_y: float,
) -> tuple[float, float]:
    """
    Range of 2D bounds.

    :param min_x: east
    :param min_y: south
    :param max_x: west
    :param max_y: north
    :return: (range_x, range_y) float tuple
    """

    return (max_x - min_x, max_y - min_y)




# enlarge bounds by distance (create buffer around it)
def enlarge_bounds_by_buffer (
    min_x: float, min_y: float, max_x: float, max_y: float,
    distance: float = 1000,
) -> tuple[float, float, float, float]:
    return box(min_x, min_y, max_x, max_y).buffer(
        distance, cap_style = "square", join_style = "mitre",
    ).bounds




# transform bounds CRS using provided transformer
def transform_bounds (
    min_x: float, min_y: float, max_x: float, max_y: float,
    transformer: CRSTransform,
) -> tuple[float, float, float, float]:
    return transform(
        transformer,
        Polygon.from_bounds(min_x, min_y, max_x, max_y)
    ).bounds




# return list of (x, y, 0.0) coords - 3rd coord ensured to be of 0.0 value
def get_flat_coords_3d (
    geometry: BaseGeometry,
) -> list[tuple[float, float, float]]:
    return [(x, y, 0.0) for x, y in get_coordinates(geometry)]




# `compute_2d_bounds_with_range()` return value
@dataclass
class Bounds2D:
    min_x: float
    min_y: float
    max_x: float
    max_y: float
    range_x: float
    range_y: float




# 2D bounding rectangle in local coords
# (independent of object scale, rotation and translation)
def compute_2d_bounds_with_range (mesh: bpy.types.Mesh) -> Bounds2D:
    bounds_2d = compute_2d_bounds(
        [(v.co.x, v.co.y) for v in mesh.vertices],
    )
    return Bounds2D(
        *bounds_2d,
        *compute_range_of_2d_bounds(*bounds_2d)
    )

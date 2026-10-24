#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Blender flight visualization.

https://github.com/drmats
"""

import bpy # type: ignore
import os

from lib.igc import parse_igc
from lib.projections import (
    custom_enu_transforms,
    custom_utm_transforms,
)
from lib.simplegeom import (
    compute_2d_bounds,
    compute_center_of_2d_bounds,
    enlarge_bounds_by_buffer,
    transform_bounds,
)
from lib.modeling import build_3d_curve
from lib.terrain import build_terrain




# ---------------------------------------
#
# import sys; import os; sys.path.append(os.path.dirname(bpy.data.filepath))
# import igcblend
# import importlib; r = lambda: importlib.reload(igcblend)
# r()
#
# ---------------------------------------




# ...
def main ():
    # path to flight file
    flight_file = "FLIGHT.IGC"

    # tiles storage folder
    tiles_path = os.path.dirname(bpy.data.filepath) + "/tiles"

    # parsed flight
    _, flight_coords_geo3d, flight_coords_ecef = parse_igc(flight_file)

    # flight boundary and center
    flight_geo2d_bounds = compute_2d_bounds(flight_coords_geo3d)
    flight_geo2d_center = compute_center_of_2d_bounds(*flight_geo2d_bounds)

    # transformations to euclidean space
    geo3d_to_utm, utm_to_geo3d = custom_utm_transforms(*flight_geo2d_center)
    ecef_to_enu, _ = custom_enu_transforms(*flight_geo2d_center)

    # buffer around boundary
    flight_geo2d_buffered_bounds = transform_bounds(
        *enlarge_bounds_by_buffer(
            *transform_bounds(
                *flight_geo2d_bounds,
                transformer = geo3d_to_utm,
            ),
            distance = 1200,
        ),
        transformer = utm_to_geo3d
    )

    # ...
    build_terrain(
        geo2d_bounds = flight_geo2d_buffered_bounds,
        ecef_to_enu_transform = ecef_to_enu,
        tiles_path = tiles_path,
    )

    # ...
    build_3d_curve(
        [ecef_to_enu(*coord) for coord in flight_coords_ecef],
        name = "Flight",
    )

    return

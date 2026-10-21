#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Blender flight visualization.

https://github.com/drmats
"""

import bpy # type: ignore
import os
from typing import cast

from lib.igc import parse_igc
from lib.simplegeom import (
    flat_coords_3d,
    translate,
)
from lib.net import (
    download_open_topo_tile,
    download_satellite_tile,
    download_terrarium_tile,
    download_xcontest_topo_tile,
)
from lib.tiles import (
    get_tiles_with_padding,
    tile_list_to_image_array,
    tile_to_polygon,
    tiles_subdivide,
)
from lib.raster import merge_tiles
from lib.fs import delete_file
from lib.modeling import (
    build_3d_curve,
    build_plane,
    merge_planes,
)
from lib.terrain import apply_terrarium_displace
from lib.uv import create_top_projected_uv
from lib.shading import (
    assign_material_to_mesh,
    create_terrain_material,
)




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
    flight_file = "FLIGHT_FILE.igc"

    # parsed flight (shapely linestring projected to ESPG:3857 - webmercator)
    _, flight_line = parse_igc(flight_file)

    # first point (needed to shift everything to the origin of blender's space)
    flight_origin = (flight_line.coords[0][0], flight_line.coords[0][1])

    # tiles storage folder
    tiles_path = os.path.dirname(bpy.data.filepath) + "/tiles"

    # tile naming functions
    terrarium_tile = lambda z, x, y: f"{tiles_path}/terrarium.{z}.{x}.{y}.png"
    satellite_tile = lambda z, x, y: f"{tiles_path}/satellite.{z}.{x}.{y}.jpg"
    xcontest_tile = lambda z, x, y: f"{tiles_path}/xcontest.{z}.{x}.{y}.jpg"
    opentopo_tile = lambda z, x, y: f"{tiles_path}/opentopo.{z}.{x}.{y}.png"

    # name prefix for plane object representing one terrain tile
    tilename_prefix = "TerrainTile"

    # create array with all tile coordinates covering flight line
    tiles_for_terrain = get_tiles_with_padding(
        flight_line,
        padding = 1000,
        zoom = 15,
    )

    # build terrain plane based on downloaded terrarium elevation data tiles
    for i, tile in enumerate(tiles_for_terrain):
        download_terrarium_tile(tile.z, tile.x, tile.y, terrarium_tile)
        tilename = f"{tilename_prefix}.{str(i).zfill(4)}"
        tilepolygon = tile_to_polygon(tile)
        build_plane(
            translate(
                flat_coords_3d(tilepolygon),
                by = flight_origin,
            ),
            name = tilename,
        )
        apply_terrarium_displace(
            tilename,
            terrarium_tile(tile.z, tile.x, tile.y),
            cuts_ratio = 8,
        )
    terrain_object = merge_planes(
        tilename_prefix,
        new_name = "Terrain",
        merge_distance = 20,
    )
    terrain_mesh = cast(bpy.types.Mesh, terrain_object.data)
    create_top_projected_uv(terrain_mesh)

    # delete source terrarium tiles after terrain geometry is created
    for tile in tiles_for_terrain:
        delete_file(terrarium_tile(tile.z, tile.x, tile.y))

    # derive tile coords from `tiles_displace`
    # in order to maintain the same padding expressed in tile widths
    tiles_for_materials = tiles_subdivide(tiles_for_terrain, steps = 2)

    # download sat and topo image tiles
    for tile in tiles_for_materials:
        try:
            download_satellite_tile(tile.z, tile.x, tile.y, satellite_tile)
            download_xcontest_topo_tile(tile.z, tile.x, tile.y, xcontest_tile)
            download_open_topo_tile(tile.z, tile.x, tile.y, opentopo_tile)
        except:
            print(tile)

    # sat map - merged image
    satellite_image_file = merge_tiles(
        tile_list_to_image_array(tiles_for_materials, satellite_tile),
        f"{tiles_path}/{os.path.basename(flight_file)}.satellite.jpg",
    )

    # xcontest topo map - merged image
    xcontest_image_file = merge_tiles(
        tile_list_to_image_array(tiles_for_materials, xcontest_tile),
        f"{tiles_path}/{os.path.basename(flight_file)}.xcontest.jpg",
    )

    # open topo map - merged image
    opentopo_image_file = merge_tiles(
        tile_list_to_image_array(tiles_for_materials, opentopo_tile),
        f"{tiles_path}/{os.path.basename(flight_file)}.opentopo.jpg",
    )

    # delete source material tiles after merging
    for tile in tiles_for_materials:
        delete_file(satellite_tile(tile.z, tile.x, tile.y))
        delete_file(xcontest_tile(tile.z, tile.x, tile.y))
        delete_file(opentopo_tile(tile.z, tile.x, tile.y))

    # terrain material
    assign_material_to_mesh(
        create_terrain_material(
            satellite_image_file,
            xcontest_image_file,
            opentopo_image_file,
        ),
        terrain_mesh,
    )

    # ...
    build_3d_curve(
        translate(
            list(flight_line.coords),
            by = flight_origin,
        ),
        name = "Flight",
    )

    return

# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

from mercantile import (
    bounds,
    children,
    Tile,
    tiles,
)
from shapely import box
from shapely.geometry import Polygon
from shapely.ops import transform

from lib.projections import geo2d_to_mercator2d
from lib.net import TileNameFunction




# compute smallest tile set (z, x, y) covering passed bounds
def get_tilelist (
    minx: float, miny: float, maxx: float, maxy: float,
    zoom: int = 15,
) -> list[Tile]:
    return list(tiles(
        minx, miny, maxx, maxy,
        zooms = zoom,
        truncate = True,
    ))




# given tiles array create denser array (zoomed-in by `steps`)
def tiles_subdivide (tiles: list[Tile], steps: int = 2) -> list[Tile]:
    if steps <= 0:
        return tiles
    return tiles_subdivide(
        [
            tile_child
            for tile in tiles
            for tile_child in children(tile)
        ],
        steps = steps - 1,
    )




# convert tile to polygon (mercator)
def tile_to_terrarium_polygon (tile: Tile) -> Polygon:
    tilebounds = bounds(tile)
    return transform(
        geo2d_to_mercator2d,
        box(
            tilebounds.west,
            tilebounds.south,
            tilebounds.east,
            tilebounds.north,
        ),
    )




# get flat tile list and return list of rows with filenames
def tile_list_to_image_array (
    tiles: list[Tile],
    namefunction: TileNameFunction = lambda t: f"{t.z}.{t.x}.{t.y}.jpg",
) -> list[list[str]]:
    if not tiles or not tiles[0]:
        raise ValueError("'tiles' is empty.")

    images = dict()

    for tile in tiles:
        if not tile.y in images:
            images[tile.y] = dict()
        images[tile.y][tile.x] = namefunction(tile)

    image_array = []

    for y, row in enumerate(sorted(images)):
        image_array.append([])
        for col in sorted(images[row]):
            image_array[y].append(images[row][col])

    return image_array

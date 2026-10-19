# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

from typing import Callable
from mercantile import bounds, children, Tile, tiles
from shapely import box, Polygon
from shapely.ops import transform

from lib.projections import project_to_3857, project_to_4326




# compute smallest tile set (z, x, y) containing geometry with some padding
def get_tiles_with_padding (
    geometry,
    padding: int = 1000,
    zoom: int = 15,
) -> list[Tile]:
    bbox = box(*geometry.bounds).buffer(
        padding, cap_style = "square", join_style = "mitre",
    )
    return list(tiles(
        *transform(project_to_4326, bbox).bounds,
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
def tile_to_polygon (tile: Tile) -> Polygon:
    tilebounds = bounds(tile)
    return transform(
        project_to_3857,
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
    namefunction: Callable[[int, int, int], str] = (lambda z, x, y: f"{z}.{x}.{y}"),
) -> list[list[str]]:
    if not tiles or not tiles[0]:
        raise ValueError("'tiles' is empty.")
    images = dict()
    for tile in tiles:
        if not tile.y in images:
            images[tile.y] = dict()
        images[tile.y][tile.x] = namefunction(tile.z, tile.x, tile.y)
    image_array = []
    for y, row in enumerate(sorted(images)):
        image_array.append([])
        for col in sorted(images[row]):
            image_array[y].append(images[row][col])
    return image_array

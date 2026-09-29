# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

from mercantile import bounds, children, Tile, tiles
from shapely import box, Polygon
from shapely.ops import transform

from lib.projections import project_to_3857, project_to_4326




# compute smallest tile set (z, x, y) containing geometry with some padding
def get_tiles_with_padding (
    geometry,
    padding=1000,
    zoom=15,
) -> list[Tile]:
    bbox = box(*geometry.bounds).buffer(
        padding, cap_style="square", join_style="mitre",
    )
    return list(tiles(
        *transform(project_to_4326, bbox).bounds,
        zooms=zoom,
        truncate=True,
    ))




# given tiles array create denser array (zoomed-in by `steps`)
def tiles_subdivide (tiles: list[Tile], steps=2) -> list[Tile]:
    if steps <= 0:
        return tiles
    return tiles_subdivide(
        [
            tile_child
            for tile in tiles
            for tile_child in children(tile)
        ],
        steps=steps-1,
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

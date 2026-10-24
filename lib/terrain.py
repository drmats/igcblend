#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

import bpy # type: ignore
import numpy
from typing import cast
import hashlib

from lib.layout import (
    clear_selection,
    get_obj_mesh,
    select_object,
)
from lib.uv import (
    adjust_uv_for_pixel_centers,
    create_top_projected_uv,
    remove_all_uv_layers,
)
from lib.tiles import (
    get_tilelist,
    tile_to_terrarium_polygon,
    tile_list_to_image_array,
    tiles_subdivide,
)
from lib.net import (
    download_open_topo_tile,
    download_satellite_tile,
    download_terrarium_tile,
    download_xcontest_topo_tile,
    TileNameFunction,
)
from lib.simplegeom import get_flat_coords_3d
from lib.modeling import (
    build_plane,
    merge_planes,
)
from lib.projections import (
    CRSTransform,
    terrarium_to_ecef,
)
from lib.fs import delete_file
from lib.raster import merge_tiles
from lib.shading import (
    assign_material_to_mesh,
    create_terrain_material,
)




# compute elevation in meters from RGB values
def decode_terrarium_rgb (r: float, g: float, b: float) -> float:
    return r * 256.0 + g + b / 256.0 - 32768.0




# convert terrarium RGB to 32-bit float image
# representing height as meters in each pixel
def decode_terrarium_image (
    source: bpy.types.Image,
    destination_image_name: str,
) -> bpy.types.Image:
    # remove any existing image of the same name
    old_image = bpy.data.images.get(destination_image_name)
    if old_image:
        bpy.data.images.remove(old_image)

    # create destination image
    source_width, source_height = cast(tuple[int, int], source.size)
    height_image = bpy.data.images.new(
        name = destination_image_name,
        width = source_width,
        height = source_height,
        alpha = False,
        float_buffer = True,
    )

    # get working copy of source pixels
    source_pixels = cast(list, source.pixels)[:]

    # allocate destination pixels list
    height_pixels = [0.0] * (source_width * source_height * 4)

    # enumerate over source pixels
    for y in range(source_height):
        for x in range(source_width):

            # index
            i = (y * source_width + x) * 4

            # translate 0-1 to 0-255
            R = source_pixels[i + 0] * 255.0
            G = source_pixels[i + 1] * 255.0
            B = source_pixels[i + 2] * 255.0

            # terrarium encoding
            elevation = decode_terrarium_rgb(R, G, B)

            # store elevation in all channels (grayscale)
            height_pixels[i + 0] = elevation
            height_pixels[i + 1] = elevation
            height_pixels[i + 2] = elevation

            # no transparency in alpha
            height_pixels[i + 3] = 1.0

    # copy height pixel list into height_image data
    height_image.pixels.foreach_set(height_pixels)

    # update display image
    height_image.update()

    return height_image




# build terrain - displace object geometry using provided terrarium image
# (resulting geometry is clean - contains no modifiers etc.)
def apply_terrarium_displace (
    object_name: str,
    terrarium_image_path: str,
    cuts_ratio: int = 32,
    displace_strength: float = 1.0,
) -> None:
    # find object
    obj, mesh = get_obj_mesh(object_name)

    # make it selected for all subsequent operations
    clear_selection()
    select_object(obj)

    # read terrarium image
    source = bpy.data.images.load(
        terrarium_image_path,
        check_existing = True,
    )

    # check image dimensions
    width, height = cast(tuple[int, int], source.size)
    if width < 2 or height < 2:
        raise ValueError("Height-map must be at least 2x2.")

    # convert terrarium RGB to height image
    height_image = decode_terrarium_image(source, f"{object_name}_HeightMap")

    # subdivide
    bpy.ops.object.mode_set(mode = "EDIT")
    bpy.ops.mesh.subdivide(number_cuts = int((width - 1) / cuts_ratio))
    bpy.ops.object.mode_set(mode = "OBJECT")

    # UV - create new map (adjusted for pixel centers)
    uv_layer_name = "TerrariumUV"
    uv_layer = create_top_projected_uv(mesh, uv_layer_name)
    adjust_uv_for_pixel_centers(uv_layer, width, height)

    # create blender texture for displace modifier
    texture_name = f"{object_name}_HeightTexture"
    old_texture = bpy.data.textures.get(texture_name)
    if old_texture:
        bpy.data.textures.remove(old_texture)
    height_texture = cast(
        bpy.types.ImageTexture,
            bpy.data.textures.new(
            name = texture_name,
            type = "IMAGE"
        ),
    )
    height_texture.image = height_image

    # displace
    old_displace = obj.modifiers.get("TerrainDisplace")
    if old_displace:
        obj.modifiers.remove(old_displace)
    displace = cast(
        bpy.types.DisplaceModifier,
        obj.modifiers.new(
            name = "TerrainDisplace",
            type = "DISPLACE",
        ),
    )
    displace.texture = height_texture
    displace.texture_coords = "UV"
    displace.uv_layer = uv_layer_name
    displace.direction = "Z"
    displace.strength = displace_strength
    displace.mid_level = 0.0

    # apply modifier to geometry (current object is selected)
    bpy.ops.object.convert(target = "MESH")
    mesh = cast(bpy.types.Mesh, obj.data)

    # ensure verts, edges and faces are up to date
    mesh.update()

    # clear all assets not needed anymore
    remove_all_uv_layers(mesh)
    bpy.data.textures.remove(height_texture, do_unlink = True)
    bpy.data.images.remove(height_image, do_unlink = True)
    bpy.data.images.remove(source, do_unlink = True)

    # leave nothing selected
    clear_selection()




# build terrain object with material
def build_terrain (
    geo2d_bounds: tuple[float, float, float, float],
    ecef_to_enu_transform: CRSTransform | None,
    terrarium_zoom: int = 15,
    mesh_grid_subdivide_ratio: int = 8,
    texture_tiles_subdivide_steps: int = 2,
    terrain_tiles_merge_distance: int = 20,
    tiles_path: str = "/tmp",
    terrain_name: str = "Terrain",
    tilename_prefix: str = "TerrainTile",
    delete_source_tiles: bool = True,
) -> tuple[bpy.types.Object, bpy.types.Mesh]:
    """
    Downloads appropriate tileset of terrarium, satellite and topographic
    map tiles and build 3D terrain object with textured material out of it.

    :param geo2d_bounds: list[minx, miny, maxx, maxy] (west, south, east, north)
        floats representing terrain boundary (decimal degrees, geo2D, lon-lat)
    :param ecef_to_enu_transform: optional CRS transformation to local ENU space
    :param terrarium_zoom: base zoom for terrain tiles resolution (max 15)
    :param mesh_grid_subdivide_ratio: cuts ratio per one plane corresponding
        to one terrarium tile - the greater the number, the lower the mesh grid
        resolution (255 - no subdivide, 128 - 2x2, 64 - 4x4, 32 - 16x16 etc.)
    :param texture_tiles_subdivide_steps: texture tiles zoom - computed as
        `terrarium_zoom` + `texture_tiles_subdivide_steps`
    :param terrain_tiles_merge_distance: distance in meters below which
        terrain vertices are being collapsed to one vertex
    :param tiles_path: path to store source tiles and produced texture images
    :param terrain_name: name for created terrain object
    :param tilename_prefix: name prefix for temporary tile planes
        representing one terrain tile
    :param delete_source_tiles: if set to False, then source tiles
        will be preserved
    """

    # tile naming functions
    terrarium_tile_name: TileNameFunction = (
        lambda t: f"{tiles_path}/terrarium.{t.z}.{t.x}.{t.y}.png"
    )
    satellite_tile_name: TileNameFunction = (
        lambda t: f"{tiles_path}/sat.{t.z}.{t.x}.{t.y}.jpg"
    )
    xcontest_tile_name: TileNameFunction = (
        lambda t: f"{tiles_path}/xc.{t.z}.{t.x}.{t.y}.jpg"
    )
    opentopo_tile_name: TileNameFunction = (
        lambda t: f"{tiles_path}/topo.{t.z}.{t.x}.{t.y}.png"
    )

    # create array with all tile coordinates covering given bounds
    tiles_for_terrain = get_tilelist(*geo2d_bounds, zoom = terrarium_zoom)

    # download terrarium elevation tiles
    terrarium_tiles_download_success = True
    for tile in tiles_for_terrain:
        try:
            download_terrarium_tile(tile, terrarium_tile_name)
        except Exception as e:
            print(f"Tile download failed: {terrarium_tile_name(tile)}")
            terrarium_tiles_download_success = False
    if not terrarium_tiles_download_success:
        raise Exception("Terrain tileset download error.")

    # derive tile coords from `tiles_for_terrain`
    # in order to maintain the same padding expressed in tile widths
    tiles_for_materials = tiles_subdivide(
        tiles_for_terrain,
        steps = texture_tiles_subdivide_steps,
    )

    # download sat and topo image tiles
    texture_tiles_download_success = True
    for tile in tiles_for_materials:
        try:
            download_satellite_tile(tile, satellite_tile_name)
            download_xcontest_topo_tile(tile, xcontest_tile_name)
            download_open_topo_tile(tile, opentopo_tile_name)
        except Exception as e:
            print(f"Tile download failed: {terrarium_tile_name(tile)}")
            texture_tiles_download_success = False
    if not texture_tiles_download_success:
        raise Exception("Texture tileset download error.")

    # build all terrarium planes based on downloaded terrarium elevation tiles
    for i, tile in enumerate(tiles_for_terrain):
        tilename = f"{tilename_prefix}.{str(i).zfill(4)}"
        build_plane(
            get_flat_coords_3d(tile_to_terrarium_polygon(tile)),
            name = tilename,
        )
        apply_terrarium_displace(
            tilename,
            terrarium_tile_name(tile),
            cuts_ratio = mesh_grid_subdivide_ratio,
        )

    # build terrain plane based on constructed terrarium planes
    terrain_object = merge_planes(
        tilename_prefix,
        new_name = terrain_name,
        merge_distance = terrain_tiles_merge_distance,
    )
    terrain_mesh = cast(bpy.types.Mesh, terrain_object.data)
    create_top_projected_uv(terrain_mesh)

    # delete source terrarium tiles after terrain geometry is created
    if delete_source_tiles:
        for tile in tiles_for_terrain:
            delete_file(terrarium_tile_name(tile))

    # transform built terrain plane to ECEF CRS
    # and translate it by `ecef_shift`
    try:
        # get flat array of floats
        coords = numpy.empty(
            len(terrain_mesh.vertices) * 3,
            dtype = numpy.float64,
        )
        terrain_mesh.vertices.foreach_get("co", coords)

        # three views, one for each coordinate
        x = coords[0::3]
        y = coords[1::3]
        z = coords[2::3]

        # vector transformation
        x_out, y_out, z_out = terrarium_to_ecef(x, y, z)
        if ecef_to_enu_transform is not None:
            x_out, y_out, z_out = ecef_to_enu_transform(
                x_out, y_out, z_out
            )

        # interleave the result back to flat array
        coords[0::3] = x_out
        coords[1::3] = y_out
        coords[2::3] = z_out

        # update vertices and refresh
        terrain_mesh.vertices.foreach_set("co", coords)
        terrain_mesh.update()

    except Exception as e:
        print(f"CRS mesh transformation error: {e}")

    # unique texture prefix based on provided bounds
    merged_image_prefix = hashlib.sha256(
        ".".join(str(b) for b in geo2d_bounds).encode("utf-8"),
    ).hexdigest()

    # sat map - merged image
    satellite_image_file = merge_tiles(
        tile_list_to_image_array(tiles_for_materials, satellite_tile_name),
        f"{tiles_path}/{merged_image_prefix}.sat.jpg",
    )

    # xcontest topo map - merged image
    xcontest_image_file = merge_tiles(
        tile_list_to_image_array(tiles_for_materials, xcontest_tile_name),
        f"{tiles_path}/{merged_image_prefix}.xc.jpg",
    )

    # open topo map - merged image
    opentopo_image_file = merge_tiles(
        tile_list_to_image_array(tiles_for_materials, opentopo_tile_name),
        f"{tiles_path}/{merged_image_prefix}.topo.jpg",
    )

    # delete source material tiles after merging
    if delete_source_tiles:
        for tile in tiles_for_materials:
            delete_file(satellite_tile_name(tile))
            delete_file(xcontest_tile_name(tile))
            delete_file(opentopo_tile_name(tile))

    # terrain material
    assign_material_to_mesh(
        create_terrain_material(
            satellite_image_file,
            xcontest_image_file,
            opentopo_image_file,
        ),
        terrain_mesh,
    )

    return (terrain_object, terrain_mesh)

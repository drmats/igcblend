#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

import bpy # type: ignore
from typing import cast

from lib.layout import (
    get_mesh,
    clear_selection,
    select_object,
)
from lib.uv import (
    remove_all_uv_layers,
    create_top_projected_uv,
    adjust_uv_for_pixel_centers,
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
        name=destination_image_name,
        width=source_width,
        height=source_height,
        alpha=False,
        float_buffer=True,
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
    cuts_ratio=32,
    displace_strength=1.0,
) -> None:
    # find object
    obj, mesh = get_mesh(object_name)

    # make it selected for all subsequent operations
    clear_selection()
    select_object(obj)

    # read terrarium image
    source = bpy.data.images.load(
        terrarium_image_path,
        check_existing=True,
    )

    # check image dimensions
    width, height = cast(tuple[int, int], source.size)
    if width < 2 or height < 2:
        raise ValueError("Height-map must be at least 2x2.")

    # convert terrarium RGB to height image
    height_image = decode_terrarium_image(source, f"{object_name}_HeightMap")

    # subdivide
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.subdivide(number_cuts=int((width-1)/cuts_ratio))
    bpy.ops.object.mode_set(mode="OBJECT")

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
            name=texture_name,
            type="IMAGE"
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
            name="TerrainDisplace",
            type="DISPLACE",
        ),
    )
    displace.texture = height_texture
    displace.texture_coords = "UV"
    displace.uv_layer = uv_layer_name
    displace.direction = "Z"
    displace.strength = displace_strength
    displace.mid_level = 0.0

    # apply modifier to geometry (current object is selected)
    bpy.ops.object.convert(target="MESH")
    mesh = cast(bpy.types.Mesh, obj.data)

    # ensure verts, edges and faces are up to date
    mesh.update()

    # clear all assets not needed anymore
    remove_all_uv_layers(mesh)
    bpy.data.textures.remove(height_texture, do_unlink=True)
    bpy.data.images.remove(height_image, do_unlink=True)
    bpy.data.images.remove(source, do_unlink=True)

    # leave nothing selected
    clear_selection()

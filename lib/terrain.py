#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

from typing import cast
import bpy # type: ignore




# compute elevation in meters from RGB values
def decode_terrarium_rgb (r: float, g: float, b: float) -> float:
    return r * 256.0 + g + b / 256.0 - 32768.0




# convert terrarium RGB to 32-bit float image
# representing height as meters in each pixel
def decode_terrarum_image (
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

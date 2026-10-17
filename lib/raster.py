# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

from PIL import Image




# merge grid of images into one image
def merge_tiles (
    image_array: list[list[str]],
    output_path: str,
    quality: int = 95,
) -> None:
    """
    Merges a grid of images from the given two-dimensional array
    into a single output file.

    :param image_array: a two-dimensional list of image file paths
    :param output_path: target file path for the merged image
    :param quality: output compression quality
    :raises ValueError: If the array is empty, has uneven rows, or the images
    have different dimensions.
    """

    if not image_array or not image_array[0]:
        raise ValueError("'image_array' is empty.")

    num_rows = len(image_array)
    num_cols = len(image_array[0])

    # validate `image_array` structure
    for r_idx, row in enumerate(image_array):
        if len(row) != num_cols:
            raise ValueError(
                f"structure error: row {r_idx} has {len(row)} elements, "
                f"but {num_cols} is expected."
            )

    # tile dimensions
    first_image_path = image_array[0][0]
    with Image.open(first_image_path) as first_img:
        tile_width, tile_height = first_img.size

    # total canvas dimensions
    total_width = tile_width * num_cols
    total_height = tile_height * num_rows

    # buffer
    canvas = Image.new("RGB", (total_width, total_height))

    # merge
    for row_idx, row in enumerate(image_array):
        for col_idx, img_path in enumerate(row):
            with Image.open(img_path) as img:

                # image dimensions check
                if img.size != (tile_width, tile_height):
                    raise ValueError(
                        f"Image '{img_path}' has {img.size} dimensions, "
                        f"but {tile_width}x{tile_height} is expected."
                    )

                # paste offsets
                x_offset = col_idx * tile_width
                y_offset = row_idx * tile_height

                # paste current image to work buffer
                canvas.paste(img, (x_offset, y_offset))

    # save
    canvas.save(output_path, quality = quality)
    canvas.close()

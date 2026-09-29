# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

import pyproj




# ...
project_to_3857 = (
    pyproj
        .Transformer
        .from_crs("EPSG:4326", "EPSG:3857", always_xy=True)
        .transform
)




# ...
project_to_4326 = (
    pyproj
        .Transformer
        .from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
        .transform
)

# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

import pyproj




# Transform points between two Coordinate Reference Systems.
# input: Geographical 3D (lon, lat, alt)
#     - lon - decimal degrees
#     - lat - decimal degrees
#     - alt - meters as height over elipsoid
# output: Geocentric 3D (x, y, z)
#     - x - meters from the center of the earth
#     - y - meters from the center of the earth
#     - z - meters from the center of the earth
geo3d_to_ecef = (
    pyproj
        .Transformer
        .from_crs("EPSG:4979", "EPSG:4978", always_xy = True)
        .transform
)




# Transform points between two Coordinate Reference Systems.
# input: Compound 3D = Web Mercator 2D + Orometric altitude over geoid
#     - x - meters
#     - y - meters
#     - alt - meters as height over geoid (EGM96 or EGM2008)
# output: Geocentric 3D (x, y, z)
#     - x - meters from the center of the earth
#     - y - meters from the center of the earth
#     - z - meters from the center of the earth
terrarium_to_ecef = (
    pyproj
        .Transformer
        .from_crs("EPSG:3857+5773", "EPSG:4978", always_xy = True)
        .transform
)




# Transform points between two Coordinate Reference Systems.
# input: Geocentric 3D (x, y, z)
#     - x - meters from the center of the earth
#     - y - meters from the center of the earth
#     - z - meters from the center of the earth
# output: Web Mercator 2D
#     - x - meters
#     - y - meters
ecef_to_mercator2d = (
    pyproj
        .Transformer
        .from_crs("EPSG:4978", "EPSG:3857", always_xy = True)
        .transform
)




# Transform points between two Coordinate Reference Systems.
# input: Web Mercator 2D (x, y, [alt])
#     - x - meters
#     - y - meters
# output: Geographical 2D (lon, lat, [alt])
#     - lon - decimal degrees
#     - lat - decimal degrees
# altitude, if present, just rewritten (no units associated)
mercator2d_to_geo2d = (
    pyproj
        .Transformer
        .from_crs("EPSG:3857", "EPSG:4326", always_xy = True)
        .transform
)




# Transform points between two Coordinate Reference Systems.
# input: Geographical 2D (lon, lat, [alt])
#     - lon - decimal degrees
#     - lat - decimal degrees
# output: Web Mercator 2D (x, y, [alt])
#     - x - meters
#     - y - meters
# altitude, if present, just rewritten (no units associated)
geo2d_to_mercator2d = (
    pyproj
        .Transformer
        .from_crs("EPSG:4326", "EPSG:3857", always_xy = True)
        .transform
)

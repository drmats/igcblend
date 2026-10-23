# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

from typing import (
    Any,
    Callable,
)
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
# input: Geocentric 3D (x, y, z)
#     - x - meters from the center of the earth
#     - y - meters from the center of the earth
#     - z - meters from the center of the earth
# output: Geographical 3D (lon, lat, alt)
#     - lon - decimal degrees
#     - lat - decimal degrees
#     - alt - meters as height over elipsoid
ecef_to_geo3d = (
    pyproj
        .Transformer
        .from_crs("EPSG:4978", "EPSG:4979", always_xy = True)
        .transform
)




# Transform points between two Coordinate Reference Systems.
# input: Compound 3D = Web Mercator 2D + Orometric altitude over geoid
#     - x - meters
#     - y - meters
#     - alt - meters as height over geoid (EGM2008)
# output: Geocentric 3D (x, y, z)
#     - x - meters from the center of the earth
#     - y - meters from the center of the earth
#     - z - meters from the center of the earth
terrarium_to_ecef = (
    pyproj
        .Transformer
        .from_crs("EPSG:3857+3855", "EPSG:4978", always_xy = True)
        .transform
)




# Transform points between two Coordinate Reference Systems.
# input: Geocentric 3D (x, y, z)
#     - x - meters from the center of the earth
#     - y - meters from the center of the earth
#     - z - meters from the center of the earth
# output: Compound 3D = Web Mercator 2D + Orometric altitude over geoid
#     - x - meters
#     - y - meters
#     - alt - meters as height over geoid (EGM2008)
ecef_to_terrarium = (
    pyproj
        .Transformer
        .from_crs("EPSG:4978", "EPSG:3857+3855", always_xy = True)
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




# 2/3D-to-2/3D transformer:
# gets (x, y, z) as floats and returns (x, y, z) as float tuple
type CRSTransform = Callable[[Any, Any, Any | None], tuple[Any, ...]]




# Create custom local UTM CRS
# (Universal Transverse Mercator Coordinate Reference System)
# based on provided center point
# (longitude and latitude as decimal degrees in EPSG:4326)
def custom_utm_transforms (
    center_lon: float,
    center_lat: float,
) -> tuple[CRSTransform, CRSTransform]:
    """
    Custom local UTM CRS (euclidean).

    :param center_lon: area x center point longitude (decimal degrees, float)
    :param center_lat: area y center point latitude (decimal degrees, float)
    :return: tuple of transforms - (geo3d_to_utm, utm_to_geo3d)
    """

    y_0 = 10000000 if center_lat < 0 else 0

    local_crs = pyproj.CRS.from_proj4(
        f"+proj=tmerc +lat_0={center_lat} +lon_0={center_lon} "
        f"+k=0.9996 +x_0=500000 +y_0={y_0} +ellps=WGS84 +units=m +no_defs"
    )

    return (
        pyproj
            .Transformer
            .from_crs("EPSG:4979", local_crs, always_xy = True)
            .transform,
        pyproj
            .Transformer
            .from_crs(local_crs, "EPSG:4979", always_xy = True)
            .transform
    )




# Create local ENU CRS
# (East North Up Coordinate Reference System)
# based on provided center point
# (longitude and latitude as decimal degrees in EPSG:4326)
def custom_enu_transforms (
    center_lon: float,
    center_lat: float,
) -> tuple[CRSTransform, CRSTransform]:
    """
    Local ENU CRS (euclidean).

    :param center_lon: area x center point longitude (decimal degrees, float)
    :param center_lat: area y center point latitude (decimal degrees, float)
    :return: tuple of transforms - (ecef_to_enu, enu_to_ecef)
    """

    ecef_to_enu_pipeline = (
        "+proj=pipeline "
        "+step +proj=topocentric "
        f"+ellps=WGS84 "
        f"+lat_0={center_lat} "
        f"+lon_0={center_lon} "
        "+h_0=0"
    )

    enu_to_ecef_pipeline = (
        "+proj=pipeline "
        "+step +inv +proj=topocentric "
        "+ellps=WGS84 "
        f"+lat_0={center_lat} "
        f"+lon_0={center_lon} "
        "+h_0=0"
    )

    return (
        pyproj
            .Transformer
            .from_pipeline(ecef_to_enu_pipeline)
            .transform,
        pyproj
            .Transformer
            .from_pipeline(enu_to_ecef_pipeline)
            .transform
    )

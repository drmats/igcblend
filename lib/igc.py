# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

from libigc import Flight
from shapely import LineString

from lib.projections import geo2d_to_mercator2d




# read igc, project to mercator, construct LineString
def parse_igc (flight_file: str) -> tuple[Flight, LineString]:
    flight = Flight.create_from_file(flight_file)
    coords_3857 = [
        geo2d_to_mercator2d(fix.lon, fix.lat, fix.alt)
            for fix in flight.fixes
    ]
    return flight, LineString(coords_3857)

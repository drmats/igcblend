# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

from libigc import Flight

from lib.projections import geo3d_to_ecef




# read IGC file and extract coordinates
def parse_igc (
    flight_file: str,
) -> tuple[
    Flight,
    list[tuple[float, float, float]],
    list[tuple[float, float, float]],
]:
    flight = Flight.create_from_file(flight_file)
    coords_geo3d = [
        (fix.lon, fix.lat, fix.alt)
            for fix in flight.fixes
    ]
    coords_ecef = [
        geo3d_to_ecef(fix.lon, fix.lat, fix.alt)
            for fix in flight.fixes
    ]
    return (
        flight,
        coords_geo3d,
        coords_ecef,
    )

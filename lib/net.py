# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

from typing import Callable
import os
import urllib.request




# firefox headers
def browser_request_headers () -> dict[str, str]:
    return {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:125.0) Gecko/20100101 Firefox/125.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
    }




# generic file downloader
def download_file (
    source: str,
    destination: str,
    headers: dict[str, str] = browser_request_headers(),
    chunk_size: int = 8192,
) -> bool:
    if os.path.exists(destination):
        return False
    os.makedirs(os.path.dirname(destination), exist_ok = True)
    req = urllib.request.Request(source, headers = headers)
    with (
        urllib.request.urlopen(req) as response,
        open(destination, "wb") as out_file,
    ):
        while chunk := response.read(chunk_size):
            out_file.write(chunk)
    return True




# ...
def download_terrarium_tile (
    z: int, x: int, y: int,
    destination: Callable[[int, int, int], str] = (
        lambda z, x, y: f"terrarium.{z}.{x}.{y}.png"
    ),
) -> None:
    download_file(
        f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png",
        destination(z, x, y),
    )




# ...
def download_satellite_tile (
    z: int, x: int, y: int,
    destination: Callable[[int, int, int], str] = (
        lambda z, x, y: f"satellite.{z}.{x}.{y}.jpg"
    ),
) -> None:
    download_file(
        f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
        destination(z, x, y),
    )




# ...
def download_xcontest_topo_tile (
    z: int, x: int, y: int,
    destination: Callable[[int, int, int], str] = (
        lambda z, x, y: f"xcontest.{z}.{x}.{y}.jpg"
    ),
) -> None:
    download_file(
        f"https://topo.xcontest.app/elev/{z}/{x}/{y}.jpg",
        destination(z, x, y),
        headers = {
            **browser_request_headers(),
            "Referer": "https://www.xcontest.org/",
            "Origin":"https://www.xcontest.org",
        },
    )




# ...
def download_open_topo_tile (
    z: int, x: int, y: int,
    destination: Callable[[int, int, int], str] = (
        lambda z, x, y: f"opentopo.{z}.{x}.{y}.png"
    ),
) -> None:
    download_file(
        f"https://tile.opentopomap.org/{z}/{x}/{y}.png",
        destination(z, x, y),
    )

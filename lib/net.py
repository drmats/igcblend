# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

from typing import Callable
import os
import urllib.request
from mercantile import Tile




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
type TileNameFunction = Callable[[Tile], str]




# ...
def download_terrarium_tile (
    t: Tile,
    destination: TileNameFunction = (
        lambda t: f"terrarium.{t.z}.{t.x}.{t.y}.png"
    ),
) -> None:
    download_file(
        f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{t.z}/{t.x}/{t.y}.png",
        destination(t),
    )




# ...
def download_satellite_tile (
    t: Tile,
    destination: TileNameFunction = (
        lambda t: f"satellite.{t.z}.{t.x}.{t.y}.jpg"
    ),
) -> None:
    download_file(
        f"https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{t.z}/{t.y}/{t.x}",
        destination(t),
    )




# ...
def download_xcontest_topo_tile (
    t: Tile,
    destination: TileNameFunction = (
        lambda t: f"xcontest.{t.z}.{t.x}.{t.y}.jpg"
    ),
) -> None:
    download_file(
        f"https://topo.xcontest.app/elev/{t.z}/{t.x}/{t.y}.jpg",
        destination(t),
        headers = {
            **browser_request_headers(),
            "Referer": "https://www.xcontest.org/",
            "Origin":"https://www.xcontest.org",
        },
    )




# ...
def download_open_topo_tile (
    t: Tile,
    destination: TileNameFunction = (
        lambda t: f"opentopo.{t.z}.{t.x}.{t.y}.png"
    ),
) -> None:
    download_file(
        f"https://tile.opentopomap.org/{t.z}/{t.x}/{t.y}.png",
        destination(t),
    )

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""




# convert hex string to float tuple
def hex_to_rgba (color: str) -> tuple[float, float, float, float]:
    hex_color = color.lstrip("#")
    zeros = list(map(lambda _: 0.0, range(4)))
    converted = [
        int(hex_color[i:i + 2], 16) / 255.0
            for i in tuple(range(0, len(hex_color), 2))
    ]
    filled = [*converted[0:4], *zeros[len(converted):4]]
    return (filled[0], filled[1], filled[2], filled[3])

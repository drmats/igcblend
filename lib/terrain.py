#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""




# compute elevation in meters from RGB values
def decode_terrarium (r: float, g: float, b: float) -> float:
    return r * 256.0 + g + b / 256.0 - 32768.0

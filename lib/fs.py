# -*- coding: utf-8 -*-

"""
https://github.com/drmats
"""

import os




# ...
def delete_file (path: str) -> None:
    if os.path.exists(path):
        os.remove(path)

"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from __future__ import annotations


def removeprefix(string, prefix: str) -> str:
    """Backwards compatibility"""

    if string.startswith(prefix):
        return string[len(prefix) :]
    return string


def removesuffix(string: str, suffix: str) -> str:
    """Backwards compatibility"""

    if string.endswith(suffix):
        return string[: -len(suffix)]
    return string

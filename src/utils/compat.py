"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from __future__ import annotations


def removeprefix(string, prefix: str) -> str:
    """
    Backwards compatibility to remove a prefix of a string

    Args:
        string: String to remove prefix from
        prefix: Actual prefix

    Returns:
        New string
    """

    if string.startswith(prefix):
        return string[len(prefix) :]
    return string


def removesuffix(string: str, suffix: str) -> str:
    """
    Backwards compatibility to remove a suffix of a string

    Args:
        string: String to remove prefix from
        suffix: Actual suffix

    Returns:
        New string
    """

    if string.endswith(suffix):
        return string[: -len(suffix)]
    return string

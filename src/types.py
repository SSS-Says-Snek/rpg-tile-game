"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Tuple, Union

from src import pygame

# noinspection PyUnresolvedReferences
if TYPE_CHECKING:
    pass


Pos = Union[Tuple[int, int], List[int], pygame.Vector2, "Position"]
Size = Union[Tuple[int, int], List[int]]

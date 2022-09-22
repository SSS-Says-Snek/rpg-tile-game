"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Sequence, Union

from src import pygame

# noinspection PyUnresolvedReferences
if TYPE_CHECKING:
    pass


Pos = Union[tuple[int, int], list[int], pygame.Vector2, "Position"]
Size = Union[tuple[int, int], list[int]]
Color = Union[tuple[int, int, int], list[int], pygame.Color]
Events = list[pygame.event.Event]
Dts = dict[str, float]

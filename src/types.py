"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable, Union

from src import pygame

# noinspection PyUnresolvedReferences
if TYPE_CHECKING:
    pass


TupPos = tuple[int, int]
Pos = Union[TupPos, list[int], pygame.Vector2, "Position"]
TupSize = tuple[int, int]
Size = Union[TupSize, list[int]]
TupColor = Union[tuple[int, int, int], tuple[int, int, int, int]]
Color = Union[tuple[int, int, int], list[int], pygame.Color]
Events = list[pygame.event.Event]
Dts = dict[str, float]
VoidFunc = Callable[[], None]

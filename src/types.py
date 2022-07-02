from typing import TYPE_CHECKING, Union, Tuple, List

from src import pygame

if TYPE_CHECKING:
    from src.entities.component import Position


Pos = Union[Tuple[int, int], List[int], pygame.Vector2, "Position"]
Size = Union[Tuple[int, int], List[int]]

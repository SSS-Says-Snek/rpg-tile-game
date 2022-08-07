from typing import TYPE_CHECKING, Union, Tuple, List

from src import pygame

# noinspection PyUnresolvedReferences
if TYPE_CHECKING:
    pass


Pos = Union[Tuple[int, int], List[int], pygame.Vector2, "Position"]
Size = Union[Tuple[int, int], List[int]]

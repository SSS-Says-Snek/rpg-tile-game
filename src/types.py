from typing import TYPE_CHECKING, Union, TypedDict, Tuple, List

from src import pygame

if TYPE_CHECKING:
    from src.entities.component import Position


class DTs(TypedDict):
    dt: float
    raw_dt: float


Pos = Union[Tuple[int, int], List[int], pygame.Vector2, "Position"]
Size = Union[Tuple[int, int], List[int]]

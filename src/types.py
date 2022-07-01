import typing

from src import pygame

if typing.TYPE_CHECKING:
    from src.entities.component import Position


class DTs(typing.TypedDict):
    dt: float
    raw_dt: float


Pos = typing.Union[tuple[int, int], list[int], pygame.Vector2, "Position"]
Size = typing.Union[tuple[int, int], list[int]]

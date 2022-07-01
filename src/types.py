import typing

from src import pygame


class DTs(typing.TypedDict):
    dt: float
    raw_dt: float


Pos = typing.Union[tuple[int, int], list[int], pygame.Vector2]
Size = typing.Union[tuple[int, int], list[int]]

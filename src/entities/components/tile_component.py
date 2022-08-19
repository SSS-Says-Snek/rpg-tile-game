"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from src import pygame
from src.display.widgets.interactable_tiles import SignDialogue, TileHover


class Tile:
    def __init__(self, x: int, y: int, tile_width: int, tile_height: int):
        self.x = x
        self.y = y

        self.tile_width: int = tile_width
        self.tile_height: int = tile_height

        self.rect = pygame.Rect(x * tile_width, y * tile_height, tile_width, tile_height)


class Sign:
    def __init__(self, tile, text: str):
        self.tile = tile
        self.text: str = text

        self.hover = TileHover(tile)
        self.dialogue = SignDialogue(text)

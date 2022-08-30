"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""
from __future__ import annotations

import random

from src import pygame
from src.common import TILE_HEIGHT, TILE_WIDTH
from src.display.widgets.interactable_tiles import SignDialogue, TileHover


class Tile:
    def __init__(self, x: int, y: int, obj_width: int, obj_height: int):
        self.x = x
        self.y = y

        self.obj_width: int = obj_width
        self.obj_height: int = obj_height

        self.rect = pygame.Rect(x * TILE_WIDTH, y * TILE_HEIGHT, obj_width, obj_height)


class Interactable:
    def __init__(self, img):
        self.outline_img = self.create_outline_img(img)

    @staticmethod
    def create_outline_img(img: pygame.Surface):
        e = pygame.Surface((img.get_width() + 1, img.get_height() + 1))
        pass


class Sign:
    def __init__(self, tile: Tile, text: str):
        self.tile = tile
        self.text: str = text

        self.hover = TileHover(tile)
        self.dialogue = SignDialogue(text)


class Decoration:
    def __init__(self, img: pygame.Surface, layers: list):
        self.img = img
        self.layers = layers
        self.anim_offset = random.uniform(1, 6)

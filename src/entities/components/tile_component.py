"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from src import pygame, utils
from src.common import IMG_DIR, TILE_HEIGHT, TILE_WIDTH
from src.display.widgets.interactable_tiles import SignDialogue, TileHover


class Tile:
    def __init__(self, x: int, y: int, width: int, height: int):
        self.x = x
        self.y = y

        self.width: int = width
        self.height: int = height

        self.rect = pygame.Rect(x * TILE_WIDTH, y * TILE_HEIGHT, width, height)


class Interactable:
    def __init__(self, tile: Tile, img: pygame.Surface):
        self.outline_img = self.create_outline_img(img)
        self.hover = TileHover(tile, self.outline_img)

    @staticmethod
    def create_outline_img(img: pygame.Surface):
        surf = pygame.Surface((img.get_width() + 3, img.get_height() + 3), pygame.SRCALPHA)
        mask = pygame.mask.from_surface(img)
        mask_outline = mask.outline()

        # Blit semi-accurate outline of surf
        pygame.draw.polygon(surf, (255, 255, 255), mask_outline, 2)

        return surf


class Sign:
    def __init__(self, text: str):
        self.text = text
        self.dialogue = SignDialogue(text)


# TODO: Split into foliage
class Decoration:
    def __init__(self, img: pygame.Surface, layers: list[pygame.Surface]):
        self.img = img
        self.layers = layers
        self.anim_offset = random.uniform(1, 6)


class GrassBlades:
    GRASS_BLADES = utils.load_imgs(IMG_DIR / "misc" / "grass", colorkey=(0, 0, 0))

    def __init__(self, tile_x: int, tile_y: int, grass_section_width: int):
        self.tile_x = tile_x
        self.tile_y = tile_y
        self.tile_grass_section_width = grass_section_width // TILE_WIDTH
        self.grass_section_width = grass_section_width
        self.num_blades = random.randint(4, 10)  # Blades per tile
        self.blades = []

        for _ in range(int(self.num_blades * self.tile_grass_section_width)):
            self.blades.append(
                Blade(
                    random.randint(0, self.grass_section_width),
                    random.uniform(0.6, 1.2),
                    random.uniform(10, 24),
                    random.choice(self.GRASS_BLADES),
                )
            )
        self.blades.sort(key=lambda blade: blade.x)


@dataclass
class Blade:
    x: int
    rotate_weight: float
    rotate_angle: float
    img: pygame.Surface
    angle: int = 0
    target_angle: int = 0

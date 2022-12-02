"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines some utility functions
"""
from __future__ import annotations

from src import pygame, core
from src.common import TILE_HEIGHT, TILE_WIDTH
from src.types import Color

from .loaders import (DirLoader, load_font, load_img, load_img_dir, load_imgs,
                      load_mob_animations)


class Task:
    def __init__(self, period: int):
        # Period in milliseconds
        self.time_instantiated = core.time.get_ticks()
        self.last_invoked = 0
        self.period = period

    def update(self):
        if core.time.get_ticks() - self.last_invoked > self.period:
            self.last_invoked = core.time.get_ticks()
            return True
        return False

    def update_time(self):
        self.time_instantiated = core.time.get_ticks()

    def time_passed(self, time_threshold: float):
        if core.time.get_ticks() - self.time_instantiated > time_threshold:
            return True
        return False


def pixel_to_tile(
    pixel_pos: pygame.Vector2,
    tile_width: int = TILE_WIDTH,
    tile_height: int = TILE_HEIGHT,
) -> pygame.Vector2:
    """
    Maps a pixel coordinate to a tile coordinate

    Parameters:
        pixel_pos: The pixel coordinate
        tile_width: The tile width. Defaults to common.TILE_WIDTH
        tile_height: The tile height. Defaults to common.TILE_HEIGHT
    """

    return pygame.Vector2(round(pixel_pos.x / tile_width), round(pixel_pos.y / tile_height))


def tile_to_pixel(
    tile_pos: pygame.Vector2,
    tile_width: int = TILE_WIDTH,
    tile_height: int = TILE_HEIGHT,
) -> pygame.Vector2:
    """
    Maps a tile coordinate to a pixel coordinate

    Parameters:
        tile_pos: The tile coordinate
        tile_width: The tile width. Defaults to common.TILE_WIDTH
        tile_height: The tile height. Defaults to common.TILE_HEIGHT
    """

    return pygame.Vector2(tile_pos.x * tile_width, tile_pos.y * tile_height)


def extract_color(img: pygame.Surface, color: Color, add_surf: tuple[pygame.Surface, Color] = None) -> pygame.Surface:
    img = img.copy()
    img.set_colorkey(color)
    mask = pygame.mask.from_surface(img)
    surf = mask.to_surface(setcolor=(0, 0, 0, 0), unsetcolor=color)
    if add_surf is not None:
        base_surf = pygame.Surface(img.get_size())
        base_surf.fill(color)
        add_surf = (add_surf[0].convert(), add_surf[1])
        add_surf[0].set_colorkey(add_surf[1])
        base_surf.blit(add_surf[0], (0, 0))
        base_surf.blit(surf, (0, 0))
        base_surf.set_colorkey((0, 0, 0))
        return base_surf
    return surf


def rot_center(image: pygame.Surface, angle: float, x: int, y: int):
    """Rotates an image based on its center to avoid different"""
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(center=(x, y)).center)
    return rotated_image, new_rect


def rot_pivot(image: pygame.Surface, pos: tuple, origin_pos: tuple, angle: float):
    image_rect = image.get_rect(topleft=(pos[0] - origin_pos[0], pos[1] - origin_pos[1]))
    offset_center_to_pivot = pygame.Vector2(pos) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)
    return rotated_image, rotated_image_rect


def enum_eq(enum):
    # self is variant, other is type
    def __eq__(self, other):
        return isinstance(self, other)

    enum.__eq__ = __eq__
    return enum

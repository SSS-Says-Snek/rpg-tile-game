"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines some utility functions
"""
from __future__ import annotations

import pathlib
from functools import lru_cache
from typing import Optional

from src.types import Color

from src import common, pygame
from src.common import ANIM_DIR, TILE_HEIGHT, TILE_WIDTH
from src.display import animation
from src.utils.time import Time

time = Time()


class Task:
    def __init__(self, period: int):
        # Period in milliseconds
        self.time_instantiated = time.get_ticks()
        self.last_invoked = 0
        self.period = period

    def update(self):
        if time.get_ticks() - self.last_invoked > self.period:
            self.last_invoked = time.get_ticks()
            return True
        return False

    def update_time(self):
        self.time_instantiated = time.get_ticks()

    def time_passed(self, time_threshold: float):
        if time.get_ticks() - self.time_instantiated > time_threshold:
            return True
        return False


def removeprefix(string, prefix: str) -> str:
    """Backwards compatibility"""
    if string.startswith(prefix):
        return string[len(prefix) :]
    return string


def removesuffix(string: str, suffix: str) -> str:
    """Backwards compatibility"""
    if string.endswith(suffix):
        return string[: -len(suffix)]
    return string


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


@lru_cache(maxsize=256)
def load_img(path: pathlib.Path, mode: str = "alpha", colorkey: Optional[Color] = None) -> pygame.Surface:
    img = pygame.image.load(path)

    if mode == "alpha":
        img = img.convert_alpha()
    elif mode == "convert":
        img = img.convert()

    if colorkey is not None:
        img.set_colorkey(colorkey)

    return img


def load_img_dir(
    path: pathlib.Path, convert_mode: str = "alpha", colorkey: Optional[Color] = None
) -> list[pygame.Surface]:
    imgs = [pygame.image.load(file) for file in path.iterdir()]
    return load_imgs(imgs, convert_mode, colorkey)


def load_imgs(
    imgs: list[pygame.Surface], convert_mode: str = "alpha", colorkey: Optional[Color] = None
) -> list[pygame.Surface]:
    if convert_mode == "alpha":
        imgs = [img.convert_alpha() for img in imgs]
    elif convert_mode == "convert":
        imgs = [img.convert() for img in imgs]

    if colorkey is not None:
        for img in imgs:
            img.set_colorkey(colorkey)

    return imgs


@lru_cache(maxsize=512)
def load_font(size: int, font_name: str = "PixelMillenium"):
    return pygame.font.Font(common.FONT_DIR / f"{font_name}.ttf", size)


def load_mob_animations(mob_settings: dict, size: tuple[int, int] = (32, 32)):
    animations = {
        animation_type: animation.Animation(ANIM_DIR / mob_settings["animation_dir"] / f"{animation_type}.png", size)
        for animation_type in mob_settings["animation_types"]
    }

    return animations, mob_settings["animation_speed"]


def enum_eq(enum):
    # self is variant, other is type
    def __eq__(self, other):
        return isinstance(self, other)

    enum.__eq__ = __eq__
    return enum
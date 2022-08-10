"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines some utility functions
"""
import pathlib
from functools import lru_cache

from src import pygame, common
from src.common import TILE_WIDTH, TILE_HEIGHT, ANIM_DIR
from src.display import animation


class Task:
    def __init__(self, period):
        # Period in milliseconds
        self.last_invoked = 0
        self.period = period

    def update(self):
        if pygame.time.get_ticks() - self.last_invoked > self.period:
            self.last_invoked = pygame.time.get_ticks()
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


def get_neighboring_tile_entities(tilemap, radius: int, pos, interacting_tiles=False) -> list:
    neighboring_tile_entities = []

    for layer_id in range(len(tilemap.get_visible_tile_layers())):
        for x in range(int(pos.tile_pos.x) - radius, int(pos.tile_pos.x) + radius + 1):
            for y in range(int(pos.tile_pos.y) - radius, int(pos.tile_pos.y) + radius + 1):
                try:
                    if not interacting_tiles:
                        tile_entity = tilemap.entity_tiles[(layer_id, (x, y))]
                    else:
                        tile_entity = tilemap.interactable_tiles[(x, y)]
                except KeyError:
                    # Outside map boundaries (for some reason)
                    continue

                neighboring_tile_entities.append(tile_entity)

    return neighboring_tile_entities


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
def load_img(path: pathlib.Path):
    return pygame.image.load(path)


@lru_cache(maxsize=512)
def load_font(size: int, font_name="PixelMillenium"):
    return pygame.font.Font(common.FONT_DIR / f"{font_name}.ttf", size)


def load_mob_animations(mob_settings: dict, size: tuple = (32, 32)):
    animations = {
        animation_type: animation.Animation(
            ANIM_DIR / mob_settings["animation_dir"] / f"{animation_type}.png", size
        )
        for animation_type in mob_settings["animation_types"]
    }

    return animations, mob_settings["animation_speed"]

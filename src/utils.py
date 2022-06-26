"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines some utility functions
"""

from src import pygame
from src.common import TILE_WIDTH, TILE_HEIGHT


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

    return pygame.Vector2(
        round(pixel_pos.x / tile_width), round(pixel_pos.y / tile_height)
    )


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


def get_neighboring_tile_entities(tilemap, radius: int, pos) -> list:
    neighboring_tile_entities = []

    for layer_id in range(len(tilemap.get_visible_tile_layers())):
        for x in range(int(pos.tile_pos.x) - radius, int(pos.tile_pos.x) + radius + 1):
            for y in range(
                int(pos.tile_pos.y) - radius, int(pos.tile_pos.y) + radius + 1
            ):
                try:
                    tile_entity = tilemap.entity_tiles[(layer_id, (x, y))]
                except KeyError:
                    # Outside map boundaries (for some reason)
                    continue

                neighboring_tile_entities.append((tile_entity, {"x": x, "y": y}))

    return neighboring_tile_entities


def rot_center(image: pygame.Surface, angle: float, x: int, y: int):
    """Rotates an image based on its center to avoid different"""
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(center=(x, y)).center)
    return rotated_image, new_rect


def rot_pivot(image: pygame.Surface, pos: tuple, origin_pos: tuple, angle: float):
    image_rect = image.get_rect(
        topleft=(pos[0] - origin_pos[0], pos[1] - origin_pos[1])
    )
    offset_center_to_pivot = pygame.math.Vector2(pos) - image_rect.center
    rotated_offset = offset_center_to_pivot.rotate(-angle)
    rotated_image_center = (pos[0] - rotated_offset.x, pos[1] - rotated_offset.y)
    rotated_image = pygame.transform.rotate(image, angle)
    rotated_image_rect = rotated_image.get_rect(center=rotated_image_center)
    return rotated_image, rotated_image_rect

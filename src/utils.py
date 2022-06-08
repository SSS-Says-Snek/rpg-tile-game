from src import pygame
from src.common import TILE_WIDTH, TILE_HEIGHT

def pixel_to_tile(pixel_pos, tile_width=TILE_WIDTH, tile_height=TILE_HEIGHT):
    # return pixel_pos[0] // tile_width, pixel_pos[1] // tile_height
    return pygame.Vector2(round(pixel_pos.x / tile_width), round(pixel_pos.y / tile_height))

def tile_to_pixel(tile_pos, tile_width=TILE_WIDTH, tile_height=TILE_HEIGHT):
    return pygame.Vector2(tile_pos.x * tile_width, tile_pos.y * tile_height)


def get_neighboring_tile_entities(tilemap, radius, pos):
    neighboring_tile_entities = []

    for layer_id in range(len(tilemap.get_visible_tile_layers())):
        for x in range(int(pos.tile_pos.x) - radius, int(pos.tile_pos.x) + radius + 1):
            for y in range(int(pos.tile_pos.y) - radius, int(pos.tile_pos.y) + radius + 1):
                try:
                    tile_entity = tilemap.entity_tiles[(layer_id, (x, y))]
                except KeyError:
                    # Outside map boundaries (for some reason)
                    continue

                neighboring_tile_entities.append((tile_entity, {"x": x, "y": y}))

    return neighboring_tile_entities

def rot_center(image, angle, x, y):
    """Rotates an image based on its center to avoid different"""
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(center=(x, y)).center)
    return rotated_image, new_rect

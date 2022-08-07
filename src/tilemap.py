"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the TileMap class, which is used to further interact with pytmx
"""

import pathlib
import pygame
import pytmx

from src.common import TILE_WIDTH, TILE_HEIGHT

from src.entities.components import tile_component
from src.entities.components.component import *


class TileMap:
    def __init__(self, map_path: pathlib.Path, ecs_world):
        self.tilemap = pytmx.load_pygame(str(map_path))
        self.width = self.tilemap.width * self.tilemap.tilewidth
        self.height = self.tilemap.height * self.tilemap.tileheight

        self.ecs_world = ecs_world

        # Tiles will be filled in on render_map
        self.tiles = {}
        self.entity_tiles = {}

        # Interactable tiles are different: They are generally uncollidable (so players can walk through),
        # and are created through Tiled objects, rather than tiles. This is because
        # a lot of interactable tiles have specific data other tiles won't have.
        self.interactable_tiles = {}

    def render_map(self, surface: pygame.Surface) -> None:
        surface.set_colorkey((0, 0, 0))

        for layer_id, layer in enumerate(self.tilemap.visible_layers):
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    # Adds tile props to dict
                    tile_props = self.tilemap.get_tile_properties_by_gid(gid)
                    if tile_props is None:
                        continue

                    self.tiles[(layer_id, (x, y))] = tile_props
                    tile_img = self.tilemap.get_tile_image_by_gid(gid)
                    components = [tile_component.Tile(x, y, tile_props["width"], tile_props["height"])]
                    flag_kwargs = {}

                    if tile_props.get("unwalkable"):
                        flag_kwargs["collidable"] = True

                    if tile_props.get("type") == "dialogue":
                        flag_kwargs["has_dialogue"] = True

                    entity_id = self.ecs_world.create_entity(*components, Flags(**flag_kwargs))
                    self.entity_tiles[(layer_id, (x, y))] = entity_id

                    surface.blit(
                        tile_img,
                        (x * self.tilemap.tilewidth, y * self.tilemap.tileheight),
                    )

        for obj in self.tilemap.objects:
            obj_pos = (obj.x // TILE_WIDTH, obj.y // TILE_HEIGHT)
            if obj.name == "sign":
                self.interactable_tiles[obj_pos] = self.ecs_world.create_entity(
                    tile_component.Tile(*obj_pos, obj.width, obj.height),
                    tile_component.Sign(obj.text)
                )

    def make_map(self) -> pygame.Surface:
        temp_surface = pygame.Surface((self.width, self.height))
        self.render_map(temp_surface)
        return temp_surface

    def get_visible_tile_layers(self):
        return [
            layer
            for layer in self.tilemap.visible_layers
            if isinstance(layer, pytmx.TiledTileLayer)
        ]

    def get_unwalkable_rects(self, neighboring_tiles):
        unwalkable_tile_rects = []

        for tile_entity in neighboring_tiles:
            tile = self.ecs_world.component_for_entity(tile_entity, tile_component.Tile)

            if self.ecs_world.component_for_entity(tile_entity, Flags).collidable:
                unwalkable_tile_rect = pygame.Rect(
                    tile.x * tile.tile_width,
                    tile.y * tile.tile_height,
                    tile.tile_width,
                    tile.tile_height,
                )
                unwalkable_tile_rects.append(unwalkable_tile_rect)

        return unwalkable_tile_rects

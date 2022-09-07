"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the TileMap class, which is used to further interact with pytmx
"""

from __future__ import annotations

import pathlib

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.states.level_state import LevelState

import pygame
import pytmx

from src import utils
from src.common import IMG_DIR, TILE_HEIGHT, TILE_WIDTH
from src.entities.components import tile_component
from src.entities.components.component import *
from src.types import Color


def extract_color(img: pygame.Surface, color: Color, add_surf: tuple[pygame.Surface, Color] = None):
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


class TileMap:
    def __init__(self, map_path: pathlib.Path, level_state: "LevelState"):
        self.tilemap = pytmx.load_pygame(str(map_path))
        self.width = self.tilemap.width * self.tilemap.tilewidth
        self.height = self.tilemap.height * self.tilemap.tileheight

        self.level_state = level_state
        self.ecs_world = self.level_state.ecs_world
        self.ui = self.level_state.ui

        self.tilename_to_img = {}

        # Tiles will be filled in on render_map
        self.tiles = {}
        self.entity_tiles = {}

        # Interactable tiles are different: They are generally uncollidable (so players can walk through),
        # and are created through Tiled objects, rather than tiles. This is because
        # a lot of interactable tiles have specific data other tiles won't have.
        self.interactable_tiles = {}
        self.deco_tiles = {}

    def make_map(self) -> tuple[pygame.Surface, pygame.Surface]:
        normal_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        interactable_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        for layer_id, layer in enumerate(self.tilemap.visible_layers):
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    # Adds tile props to dict
                    tile_props = self.tilemap.get_tile_properties_by_gid(gid)
                    if tile_props is None:
                        continue

                    tile_img = self.tilemap.get_tile_image_by_gid(gid).convert_alpha()
                    self.tiles[(layer_id, (x, y))] = tile_props
                    blit_surf = normal_surf
                    components = [
                        tile_component.Tile(x, y, tile_props["width"], tile_props["height"])
                    ]
                    flag_kwargs = {}

                    if tile_props.get("unwalkable"):
                        flag_kwargs["collidable"] = True
                    if tile_props.get("interactable"):
                        blit_surf = interactable_surf
                    if tile_props.get("tile_img"):
                        tile_img_name = tile_props["tile_img"]
                        if tile_img_name not in self.tilename_to_img:
                            self.tilename_to_img[tile_img_name] = tile_img

                    entity_id = self.ecs_world.create_entity(*components, Flags(**flag_kwargs))
                    self.entity_tiles[(layer_id, (x, y))] = entity_id

                    blit_surf.blit(
                        tile_img,
                        (x * self.tilemap.tilewidth, y * self.tilemap.tileheight),
                    )

        for obj in self.tilemap.objects:
            obj_pos = (obj.x // TILE_WIDTH, obj.y // TILE_HEIGHT)

            tile = tile_component.Tile(*obj_pos, obj.width, obj.height)
            if obj.name == "sign":
                obj.text = (
                    "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor "
                    "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
                    "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
                )
                self.interactable_tiles[obj_pos] = self.ecs_world.create_entity(
                    tile,
                    tile_component.Interactable(tile, self.tilename_to_img["sign"]),
                    tile_component.Sign(obj.text),
                )

            if obj.name.startswith("tree"):
                tree_layer_col = [[192, 199, 65], [100, 125, 52], [23, 67, 75]]
                img = utils.load_img(IMG_DIR / "misc" / "foliage" / f"{obj.name}.png")
                img = pygame.transform.scale2x(img)
                img.set_colorkey((0, 0, 0))

                layers = []
                for i, color in enumerate(tree_layer_col):
                    if i == 0:
                        layers.append(extract_color(img, color))
                    else:
                        layers.append(
                            extract_color(
                                img,
                                color,
                                add_surf=(
                                    layers[-1],
                                    tree_layer_col[i - 1],
                                ),
                            )
                        )

                self.deco_tiles[obj_pos] = self.ecs_world.create_entity(
                    tile, tile_component.Decoration(img, layers)
                )

        return normal_surf, interactable_surf

    def get_visible_tile_layers(self) -> list[pytmx.TiledTileLayer]:
        return [
            layer
            for layer in self.tilemap.visible_layers
            if isinstance(layer, pytmx.TiledTileLayer)
        ]

    def get_unwalkable_rects(self, neighboring_tiles: list[int]) -> list[pygame.Rect]:
        unwalkable_tile_rects = []

        for tile_entity in neighboring_tiles:
            tile = self.ecs_world.component_for_entity(tile_entity, tile_component.Tile)

            if self.ecs_world.component_for_entity(tile_entity, Flags).collidable:
                unwalkable_tile_rect = pygame.Rect(
                    tile.x * tile.width,
                    tile.y * tile.height,
                    tile.width,
                    tile.height,
                )
                unwalkable_tile_rects.append(unwalkable_tile_rect)

        return unwalkable_tile_rects

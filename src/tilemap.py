"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the TileMap class, which is used to further interact with pytmx
"""

from __future__ import annotations

import pathlib
from typing import TYPE_CHECKING, Optional, Union

from src.entities.components.component import Position
from src.types import Entity

if TYPE_CHECKING:
    from src.states.level_state import LevelState

import pygame
import pytmx

from src import utils
from src.common import IMG_DIR, TILE_HEIGHT, TILE_WIDTH
from src.entities.components import tile_component


class TileMap:
    def __init__(self, map_path: pathlib.Path, level_state: "LevelState"):
        """
        A class that manages Tiled tilemaps with PyTMX

        Args:
            map_path: The Path to the tmx map
            level_state: The game state
        """

        self.tilemap = pytmx.load_pygame(str(map_path))
        self.width = self.tilemap.width * self.tilemap.tilewidth
        self.height = self.tilemap.height * self.tilemap.tileheight

        self.level = level_state
        self.world = self.level.world

        # Map tile name to image for other usages (such as tile outlines)
        self.tilename_to_img = {}

        # Tiles will be filled in on render_map
        self.tiles: dict[tuple, dict] = {}
        self.entity_tiles: dict[tuple, int] = {}

        # Interactable tiles are different: They are generally uncollidable (so players can walk through),
        # and are created through Tiled objects, rather than tiles. This is because
        # a lot of interactable tiles have specific data other tiles won't have.
        self.interactable_tiles: dict[tuple, int] = {}

    def make_map(self) -> tuple[pygame.Surface, pygame.Surface]:
        """
        Creates both the normal map and the interactable tiles surface

        Returns:
            A tuple of the normal map, as well as the interactable tiles map
        """

        normal_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        interactable_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        for layer_id, layer in enumerate(self.tilemap.visible_layers):
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    tile_img = self.tilemap.get_tile_image_by_gid(gid)
                    if tile_img is None:
                        continue
                    tile_img = tile_img.convert_alpha()

                    # Adds tile props to dict
                    tile_props = self.tilemap.get_tile_properties_by_gid(gid)
                    if tile_props is None:
                        tile_props = {}

                    self.tiles[(layer_id, (x, y))] = tile_props
                    blit_surf = normal_surf

                    tile_type = tile_component.Type.DEFAULT

                    if tile_props.get("unwalkable"):
                        tile_type |= tile_component.Type.COLLIDABLE
                    if tile_props.get("ramp"):
                        if tile_props["ramp"] == "up":
                            tile_type |= tile_component.Type.RAMP_UP
                        elif tile_props["ramp"] == "down":
                            tile_type |= tile_component.Type.RAMP_DOWN
                    if tile_props.get("interactable"):
                        blit_surf = interactable_surf
                    if tile_props.get("tile_img"):
                        tile_img_name = tile_props["tile_img"]
                        if tile_img_name not in self.tilename_to_img:
                            self.tilename_to_img[tile_img_name] = tile_img

                    tile = tile_component.Tile(x, y, self.tilemap.tilewidth, self.tilemap.tileheight, tile_type)
                    entity_id = self.world.create_entity(tile)
                    self.entity_tiles[(layer_id, (x, y))] = entity_id

                    blit_surf.blit(
                        tile_img,
                        (x * self.tilemap.tilewidth, y * self.tilemap.tileheight),
                    )

        for obj in self.tilemap.objects:
            obj_pos = (obj.x // TILE_WIDTH, obj.y // TILE_HEIGHT)

            tile = tile_component.Tile(*obj_pos, obj.width, obj.height)
            if obj.name == "sign":
                if obj.text is None:
                    obj.text = (
                        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor "
                        "incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud "
                        "exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat."
                    )
                self.interactable_tiles[obj_pos] = self.world.create_entity(
                    tile,
                    tile_component.Interactable(tile, self.tilename_to_img["sign"]),
                    tile_component.Sign(obj.text),
                )

            if obj.name.startswith("tree"):
                tree_layer_col = [[192, 199, 65], [100, 125, 52], [23, 67, 75]]
                img = utils.load_img(IMG_DIR / "deco" / "foliage" / f"{obj.name}.png")
                img = pygame.transform.scale2x(img)
                img.set_colorkey((0, 0, 0))

                layers = []
                for i, color in enumerate(tree_layer_col):
                    if i == 0:
                        layers.append(utils.extract_color(img, color))
                    else:
                        layers.append(
                            utils.extract_color(
                                img,
                                color,
                                add_surf=(
                                    layers[-1],
                                    tree_layer_col[i - 1],
                                ),
                            )
                        )

                self.world.create_entity(tile, tile_component.Decoration(img, layers))

            if obj.name == "grass":
                self.world.create_entity(tile, tile_component.GrassBlades(*obj_pos, obj.width))

        return normal_surf, interactable_surf

    def get_visible_tile_layers(self) -> list[pytmx.TiledTileLayer]:
        return [layer for layer in self.tilemap.visible_layers if isinstance(layer, pytmx.TiledTileLayer)]

    def get_neighboring_tile_entities(
        self, radius: int, pos: Position, interacting_tiles: bool = False
    ) -> list[Entity]:
        """
        Get (static) neighboring tiles within x tiles given position and radius.
        Setting interacting_tiles to True gives you neighboring interactables

        Args:
            radius: (Square) Radius to get tiles
            pos: Position to get tiles around
            interacting_tiles: Whether to output interacting tiles or not

        Returns:
            List of entity IDs
        """

        neighboring_tile_entities = []

        for layer_id in range(len(self.get_visible_tile_layers())):
            for x in range(int(pos.tile_pos.x) - radius, int(pos.tile_pos.x) + radius + 1):
                for y in range(int(pos.tile_pos.y) - radius, int(pos.tile_pos.y) + radius + 1):
                    try:
                        if not interacting_tiles:
                            tile_entity = self.entity_tiles[(layer_id, (x, y))]
                        else:
                            tile_entity = self.interactable_tiles[(x, y)]
                    except KeyError:
                        # Outside map boundaries (for some reason)
                        continue

                    neighboring_tile_entities.append(tile_entity)

        return neighboring_tile_entities

    def get_unwalkable_rects(
        self, neighboring_tiles: list[Entity]
    ) -> tuple[list[pygame.Rect], list[tuple[pygame.Rect, tile_component.Type]]]:
        """
        Gets unwalkable tile rects and ramps given list of entity IDs

        Args:
            neighboring_tiles: List of neighboring tiles' entity IDs

        Returns:
            A list of unwalkable rects, as well as a list of ramps
        """
        # TODO: Separate into two functions for unwalkables and ramps

        unwalkable_tile_rects = []
        ramps = []

        for tile_entity in neighboring_tiles:
            tile = self.world.component_for_entity(tile_entity, tile_component.Tile)
            unwalkable_tile_rect = pygame.Rect(
                tile.x * tile.width,
                tile.y * tile.height,
                tile.width,
                tile.height,
            )
            if tile_component.Type.RAMP_UP in tile.type:
                ramps.append((unwalkable_tile_rect, tile_component.Type.RAMP_UP))
            elif tile_component.Type.RAMP_DOWN in tile.type:
                ramps.append((unwalkable_tile_rect, tile_component.Type.RAMP_DOWN))
            elif tile_component.Type.COLLIDABLE in tile.type:
                unwalkable_tile_rects.append(unwalkable_tile_rect)

        return unwalkable_tile_rects, ramps

    def get_tile(self, tile_x: Union[int, float], tile_y: Union[int, float]) -> Optional[dict]:
        """
        Gets tile given x and y position

        Args:
            tile_x: Tile x
            tile_y: Tile y

        Returns:
            Properties of tile
        """

        return self.tiles.get((0, (tile_x, tile_y)))

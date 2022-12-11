"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the tile interaction system, used for entity-to-tile interaction
"""

from __future__ import annotations

import types

from src import pygame
from src.entities.components import tile_component
from src.entities.components.component import Position
from src.entities.systems.system import System
from src.types import Events


class TileInteractionSystem(System):
    class TileInteractions(types.SimpleNamespace):
        @staticmethod
        def handle_sign(interactable_tile_entity, sign):
            pass

    def __init__(self, level_state):
        super().__init__(level_state)

    @staticmethod
    def get_event(event_list: Events, event_type: int):
        for event in event_list:
            if event.type == event_type:
                return event
        return None

    def check_for_key(self, event_list: Events, key: int, event_type: int = pygame.KEYDOWN):
        event = self.get_event(event_list, event_type)
        if event is not None and event.key == key:
            return True
        return False

    def process(self):
        for entity, pos in self.world.get_component(Position):
            tile_entities = self.tilemap.get_neighboring_tile_entities(
                2, pos, interacting_tiles=True
            )  # Guaranteed to be ONLY interactable tiles
            player_rect = self.world.component_for_entity(self.player, Position).rect

            for tile_entity in tile_entities:
                tile = self.world.component_for_entity(tile_entity, tile_component.Tile)
                tile_rect = tile.rect
                interactable = self.world.component_for_entity(tile_entity, tile_component.Interactable)

                # No interaction? Skip
                if not player_rect.colliderect(tile_rect):
                    continue

                if self.world.has_component(tile_entity, tile_component.Sign):
                    sign = self.world.component_for_entity(tile_entity, tile_component.Sign)
                    self.send_to_graphics(sign.dialogue)
                    self.send_to_graphics(interactable.hover, when="post_interactables")

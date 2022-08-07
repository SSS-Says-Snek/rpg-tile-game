"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the tile interaction system, used for entity-to-tile interaction
"""

from src import pygame, screen, utils

from src.entities.components import tile_component
from src.entities.systems.system import System
from src.entities.components.component import *


class TestBlit:
    def __init__(self):
        self.text = "OMGGGGG"

        self.txt_surf = pygame.font.SysFont("arial", 24).render("OMG", True, (0, 0, 0))

    def draw(self, camera):
        screen.blit(self.txt_surf, camera.apply((400, 400)))


class TileInteractionSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    @staticmethod
    def get_event(event_list, event_type):
        for event in event_list:
            if event.type == event_type:
                return event

    def check_for_key(self, event_list, key, event_type=pygame.KEYDOWN):
        event = self.get_event(event_list, event_type)
        if event is not None and event.key == key:
            return True
        return False

    def process(self, event_list, dts) -> None:
        # super().process(event_list)

        for entity, (pos, *_) in self.world.get_components(Position, Movement):
            interactable_tile_entities = utils.get_neighboring_tile_entities(self.tilemap, 2, pos, interacting_tiles=True)
            player_rect = self.world.component_for_entity(self.player, Position).rect

            for interactable_tile_entity in interactable_tile_entities:
                interactable_tile = self.world.component_for_entity(interactable_tile_entity, tile_component.Tile)
                interactable_tile_rect = interactable_tile.rect
                if not player_rect.colliderect(interactable_tile_rect):
                    continue

                if self.world.has_component(interactable_tile_entity, tile_component.Sign):
                    pass

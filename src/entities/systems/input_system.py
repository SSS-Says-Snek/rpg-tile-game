"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the input system, used to get player inputs
"""

from __future__ import annotations

from src import pygame
from src.entities.components import item_component
from src.entities.components.component import Inventory

from src.entities.systems.system import System
from src.types import Events, Dts


class InputSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    def process(self, event_list: Events, dts: Dts):
        inventory = self.world.component_for_entity(self.player, Inventory)
        equipped_item = inventory.inventory[inventory.equipped_item_idx]

        for event in event_list:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left button
                hotbar_ui = self.level_state.ui.hud_widgets["hotbar"]["widget"]

                if hotbar_ui.frame_rect.collidepoint(event.pos):
                    for i, hotbar_rect in enumerate(hotbar_ui.hotbar_rects):
                        adjusted_hotbar_rect = pygame.Rect(
                            hotbar_rect.x + hotbar_ui.frame_rect.x,
                            hotbar_rect.y,
                            *hotbar_rect.size,
                        )

                        if adjusted_hotbar_rect.collidepoint(pygame.mouse.get_pos()):
                            hotbar_idx = i
                            break
                    else:
                        continue

                    inventory.equipped_item_idx = hotbar_idx
                else:
                    if equipped_item is not None:
                        item = self.world.component_for_entity(equipped_item, item_component.Item)
                        if (
                            pygame.time.get_ticks() - inventory.last_used
                            > inventory.cooldown * 1000
                        ):
                            item.use(inventory)
                            inventory.on_cooldown = True

        if pygame.time.get_ticks() - inventory.last_used > inventory.cooldown * 1000:
            inventory.on_cooldown = False

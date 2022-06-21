"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file contains widgets for the inventory
"""

import pygame.gfxdraw
from src import pygame, screen

from src.entities import item_component

from src.entities.component import Inventory


class Hotbar:
    def __init__(self, ui, entity, center_pos, frame_size):
        self.uuid = None
        self.ui = ui
        self.entity = entity

        self.center_pos = center_pos
        self.frame_size = frame_size

        self.inventory_component = self.ui.world.component_for_entity(self.entity, Inventory)
        self.hotbar_size = self.inventory_component.hotbar_size

        self.original_frame = pygame.Surface(((frame_size[0] + 15) * self.hotbar_size, frame_size[1] + 4), pygame.SRCALPHA)
        self.frame = self.original_frame
        self.frame_rect = self.frame.get_rect(center=self.center_pos)

        self.hotbar_rects = []
        for i in range(self.hotbar_size):
            hotbar_rect = pygame.draw.rect(
                self.original_frame, (0, 0, 0),  # (66, 118, 70),
                pygame.Rect(i * frame_size[0] + i * 15, 0, *frame_size), width=4
            )

            self.hotbar_rects.append(hotbar_rect)

    def draw(self, _):  # Camera not used
        frame = self.original_frame.copy()

        # Draw icons
        for hotbar_idx in range(self.hotbar_size):
            hotbar_rect = self.hotbar_rects[hotbar_idx]

            if self.inventory_component.inventory[hotbar_idx] is not None:
                item_id = self.inventory_component.inventory[hotbar_idx]
                item_graphics = self.ui.world.component_for_entity(item_id, item_component.ItemGraphics)

                blit_pos = item_graphics.icon.get_rect(center=hotbar_rect.center)
                frame.blit(item_graphics.icon, blit_pos)

        # Blit white rect for equipped item
        equipped_item_idx = self.inventory_component.equipped_item_idx
        pygame.draw.rect(
            frame, (255, 255, 255),
            pygame.Rect(self.frame_size[0] * equipped_item_idx + 15 * equipped_item_idx, 0, *self.frame_size),
            width=4
        )

        mouse_pos = pygame.mouse.get_pos()
        adjusted_mouse_pos = (mouse_pos[0] - self.frame_rect.x, mouse_pos[1] - self.frame_rect.y)

        # Blit gray rect for hovering
        for i, hotbar_rect in enumerate(self.hotbar_rects):
            if hotbar_rect.collidepoint(adjusted_mouse_pos) and i != equipped_item_idx:
                pygame.draw.rect(
                    frame, (128, 128, 128),
                    pygame.Rect(self.frame_size[0] * i + 15 * i, 0, *self.frame_size),
                    width=4
                )
                break

        # Cooldown indicator
        if self.inventory_component.on_cooldown:
            for i, hotbar_rect in enumerate(self.hotbar_rects):
                if self.inventory_component.cooldown != 0:
                    # Witchcraftery
                    rect_height = (
                        1 - (pygame.time.get_ticks() - self.inventory_component.last_used) / (self.inventory_component.cooldown * 1000)
                    ) * self.frame_size[1]
                else:
                    rect_height = 0

                rect = pygame.Rect(
                    self.frame_size[0] * i + 15 * i, 0,
                    self.frame_size[0], rect_height
                )
                rect.bottom = self.frame_size[1]

                # gfxdraw accepts alpha
                pygame.gfxdraw.box(frame, rect, (70, 70, 70, 160))

        # Blit frame to appropriate position
        screen.blit(frame, self.frame_rect)
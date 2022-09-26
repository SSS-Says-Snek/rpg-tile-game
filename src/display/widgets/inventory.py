"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file contains widgets for the inventory
"""

from __future__ import annotations

import pygame.gfxdraw

from src import pygame, screen
from src.display.ui import UI
from src.display.widgets.health_bar import ItemDurabilityBar
from src.display.widgets.widget import Widget
from src.entities.components import item_component
from src.entities.components.component import Inventory
from src.types import Pos, Size


class Hotbar(Widget):
    def __init__(self, ui: UI, entity: int, center_pos: Pos, frame_size: Size):
        super().__init__()

        self.uuid = None
        self.ui = ui
        self.entity = entity

        self.center_pos = center_pos
        self.frame_size = frame_size

        self.inventory_component = self.ui.world.component_for_entity(self.entity, Inventory)
        self.hotbar_size = self.inventory_component.hotbar_size
        self.inventory_size = self.inventory_component.size

        self.spacing = 15

        self.original_frame = pygame.Surface(
            ((frame_size[0] + self.spacing) * self.hotbar_size, frame_size[1] + 4),
            pygame.SRCALPHA,
        )
        self.frame = self.original_frame
        self.frame_rect = self.frame.get_rect(center=self.center_pos)

        # Populate hotbar rects and durability bars
        self.hotbar_rects = []
        self.hotbar_durability_bars = []
        for i in range(self.hotbar_size):
            hotbar_rect = pygame.draw.rect(
                self.original_frame,
                (0, 0, 0),  # (66, 118, 70),
                pygame.Rect(self.idx_to_pixelx(i), 0, *frame_size),
                width=4,
            )

            self.hotbar_rects.append(hotbar_rect)

            item_entity = self.inventory_component.inventory[i]
            if item_entity is None or not self.ui.world.has_component(
                item_entity, item_component.Consumable
            ):
                self.hotbar_durability_bars.append(None)
                continue

            durability_bar = ItemDurabilityBar(
                ui=self.ui,
                entity=item_entity,
                pos=(self.idx_to_pixelx(i) + 32, 55),
                width=45,
                height=5,
                border_width=1,
                center=True,
            )
            self.hotbar_durability_bars.append(durability_bar)

    def idx_to_pixelx(self, idx: int):
        return idx * self.frame_size[0] + idx * self.spacing

    def draw(self, _):  # Camera not used
        frame = self.original_frame.copy()

        # Draw icons and durability
        for hotbar_idx in range(self.hotbar_size):
            hotbar_rect = self.hotbar_rects[hotbar_idx]
            item_entity = self.inventory_component.inventory[hotbar_idx]

            if item_entity is not None:
                item_graphics = self.ui.world.component_for_entity(
                    item_entity, item_component.ItemGraphics
                )

                blit_pos = item_graphics.icon.get_rect(center=hotbar_rect.center)
                frame.blit(item_graphics.icon, blit_pos)

                # Creates new durability bar if item with consumable detected
                if (
                    self.ui.world.has_component(item_entity, item_component.Consumable)
                    and self.hotbar_durability_bars[hotbar_idx] is None
                ):
                    durability_bar = ItemDurabilityBar(
                        ui=self.ui,
                        entity=item_entity,
                        pos=(self.idx_to_pixelx(hotbar_idx) + 32, 55),
                        width=45,
                        height=5,
                        border_width=1,
                        center=True,
                    )

                    self.hotbar_durability_bars[hotbar_idx] = durability_bar

                hotbar_durability_bar = self.hotbar_durability_bars[hotbar_idx]
                if hotbar_durability_bar is not None:
                    # Monke patch
                    hotbar_durability_bar.screen = frame
                    hotbar_durability_bar.draw()

            # If durability bar entity died, durability bar dies
            hotbar_durability_bar = self.hotbar_durability_bars[hotbar_idx]
            if hotbar_durability_bar is not None and not self.ui.world.entity_exists(
                hotbar_durability_bar.entity
            ):
                self.hotbar_durability_bars[hotbar_idx] = None

        # Blit white rect for equipped item
        equipped_item_idx = self.inventory_component.equipped_item_idx
        pygame.draw.rect(
            frame,
            (255, 255, 255),
            pygame.Rect(self.idx_to_pixelx(equipped_item_idx), 0, *self.frame_size),
            width=4,
        )

        mouse_pos = pygame.mouse.get_pos()
        adjusted_mouse_pos = (
            mouse_pos[0] - self.frame_rect.x,
            mouse_pos[1] - self.frame_rect.y,
        )

        # Blit gray rect for hovering
        for idx, hotbar_rect in enumerate(self.hotbar_rects):
            if hotbar_rect.collidepoint(adjusted_mouse_pos) and idx != equipped_item_idx:
                pygame.draw.rect(
                    frame,
                    (128, 128, 128),
                    pygame.Rect(self.idx_to_pixelx(idx), 0, *self.frame_size),
                    width=4,
                )
                break

        # Cooldown indicator
        if self.inventory_component.on_cooldown:
            for idx, hotbar_rect in enumerate(self.hotbar_rects):
                if self.inventory_component.cooldown != 0:
                    # Witchcraftery
                    rect_height = (
                        1
                        - (pygame.time.get_ticks() - self.inventory_component.last_used)
                        / (self.inventory_component.cooldown * 1000)
                    ) * self.frame_size[1]
                else:
                    rect_height = 0

                # Rect of the hotbar cooldown
                rect = pygame.Rect(self.idx_to_pixelx(idx), 0, self.frame_size[0], rect_height)
                rect.bottom = self.frame_size[1]

                # gfxdraw accepts alpha
                pygame.gfxdraw.box(frame, rect, (0, 0, 0, 90 + 1.5 * rect_height))

        # Blit frame to appropriate position
        screen.blit(frame, self.frame_rect)

"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file contains widgets for all health bars
"""
from __future__ import annotations

import colorsys
import math
from typing import Any

from src import pygame, screen, utils
from src.common import IMG_DIR
from src.display.camera import Camera
from src.display.ui import UI
from src.display.widgets.widget import Widget
from src.entities.components import item_component
from src.entities.components.component import Health, Position
from src.types import Pos, TupColor


class HealthBar(Widget):
    def __init__(
        self,
        health_component,
        ui: UI,
        entity: int,
        pos: Pos,
        width: int,
        height: int,
        border_width: int = 2,
        center=False,
    ):
        super().__init__()
        self.uuid = None
        self.ui = ui
        self.entity = entity
        self.screen = screen

        self.pos = pos
        self.width = width
        self.height = height
        self.border_width = border_width

        self.health_component = self.ui.world.component_for_entity(self.entity, health_component)

        if isinstance(self.pos, Position):
            self.border_rect = pygame.Rect(
                self.pos.pos.x - border_width,
                self.pos.pos.y - border_width,
                width + 2 * border_width,
                height + 2 * border_width,
            )
            self.rect = pygame.Rect(
                *self.pos.pos,
                self.health_component.hp / self.health_component.max_hp * width,
                height,
            )
        else:
            self.border_rect = pygame.Rect(
                self.pos[0] - border_width,
                self.pos[1] - border_width,
                width + 2 * border_width,
                height + 2 * border_width,
            )
            self.rect = pygame.Rect(*self.pos, self.health_component.hp / self.health_component.max_hp * width, height)

        self.previous_health = self.health_component.hp
        self.flash_size = 0
        self.flash_duration = -1
        self.flash_width = 0
        self.flash_hp_diff = 0  # 1 for lost, -1 for gained

        if center:
            self.rect.center = pos
            self.border_rect.topleft = (
                self.rect.topleft[0] - border_width,
                self.rect.topleft[1] - border_width,
            )

    def draw_border(self, _):
        pygame.draw.rect(self.screen, (0, 0, 0), self.border_rect, width=self.border_width)

    def draw_body(self, _, hp_color):
        pygame.draw.rect(self.screen, hp_color, self.rect)

    def draw_flash(self, _):
        if self.flash_width > 0:
            flash_rect = pygame.Rect(
                self.rect.x + self.rect.width,
                self.rect.y,
                self.flash_width,
                self.height,
            )

            if self.flash_hp_diff == -1:
                flash_rect.right = self.rect.right

            pygame.draw.rect(self.screen, (255, 255, 255), flash_rect)
        else:
            self.flash_hp_diff = 0

    def draw(self, camera):
        self.flash_duration -= 1
        self.rect.width = self.health_component.hp / self.health_component.max_hp * self.width

        hp_percentage = self.rect.width / self.width
        hsv = (hp_percentage / 3, 1, 1)
        rgb = colorsys.hsv_to_rgb(*hsv)
        hp_color = [max(int(color_value * 255), 0) for color_value in rgb]

        hp_lost = self.previous_health - self.health_component.hp
        self.flash_size += abs(hp_lost)

        if hp_lost != 0:
            hurt_txt = f"{(-hp_lost):+} HP"
            if self.health_component.hp > 0:
                self.flash_duration = 10
            else:
                self.flash_duration = 40
            self.flash_hp_diff = math.copysign(1, hp_lost)

            if self.ui.world.has_component(self.entity, Position):
                entity_pos = self.ui.world.component_for_entity(self.entity, Position)
                self.ui.particle_system.create_text_particle(entity_pos.pos, hurt_txt)

        if self.flash_duration <= 0:
            if self.health_component.hp > 0:
                self.flash_size -= 1
                self.flash_size *= 0.98
                self.flash_size = max(0.0, self.flash_size - 0.8)
            else:
                self.flash_size -= 1 / 4
                self.flash_size *= 0.985
                self.flash_size = max(0.0, self.flash_size)

        self.draw_body(camera, hp_color)
        self.draw_border(camera)

        self.flash_width = self.flash_size * self.width / self.health_component.max_hp

        self.draw_flash(camera)

        self.previous_health = self.health_component.hp


class PlayerHealthBar(HealthBar):
    HEALTHBAR_BORDER = utils.load_img(IMG_DIR / "ui" / "player_healthbar.png")

    def __init__(
        self,
        ui: UI,
        entity: int,
        pos: Pos,
        width: int,
        height: int,
        border_width: int = 2,
        center: bool = False,
        health_component: Any = Health,
    ):
        super().__init__(
            health_component=health_component,
            ui=ui,
            entity=entity,
            pos=pos,
            width=width,
            height=height,
            border_width=border_width,
            center=center,
        )

    def draw_border(self, _):
        self.screen.blit(self.HEALTHBAR_BORDER, self.border_rect.topleft)


class MobHealthBar(HealthBar):
    def __init__(
        self,
        ui: UI,
        entity: int,
        width: int,
        height: int,
        border_width: int = 2,
        center: bool = False,
    ):
        super().__init__(
            health_component=Health,
            ui=ui,
            entity=entity,
            pos=ui.world.component_for_entity(entity, Position),
            width=width,
            height=height,
            border_width=border_width,
            center=center,
        )

        self.y_offset = 20

    def draw_border(self, camera: Camera):
        pygame.draw.rect(self.screen, (0, 0, 0), camera.apply(self.border_rect), width=self.border_width)

    def draw_body(self, camera: Camera, hp_color: TupColor):
        pygame.draw.rect(self.screen, hp_color, camera.apply(self.rect))

    def draw_flash(self, camera: Camera):
        if self.flash_width > 0:
            flash_rect = pygame.Rect(
                self.rect.x + self.rect.width,
                self.rect.y,
                self.flash_width,
                self.height,
            )

            if self.flash_hp_diff == -1:
                flash_rect.right = self.rect.right

            pygame.draw.rect(self.screen, (255, 255, 255), camera.apply(flash_rect))
        else:
            self.flash_hp_diff = 0

    def draw(self, camera):
        if self.health_component.hp == self.health_component.max_hp:
            # No health bar if max hp
            return

        entity_rect = self.pos.rect
        self.border_rect.center = (
            entity_rect.centerx - self.border_width,
            entity_rect.centery - self.y_offset - self.border_width,
        )
        self.rect.topleft = (
            self.border_rect.x + self.border_width,
            self.border_rect.y + self.border_width,
        )

        super().draw(camera)

        if self.health_component.hp <= 0:  # and self.flash_size <= 0:
            self.ui.remove_widget(self.uuid)

            # Delete entity FOR NOW. In the future, DeathSystem would and should handle item drops
            self.ui.world.delete_entity(self.entity)
            return


class ItemDurabilityBar(PlayerHealthBar):
    def __init__(
        self,
        ui: UI,
        entity: int,
        pos: Pos,
        width: int,
        height: int,
        border_width: int = 2,
        center: bool = False,
    ):
        super().__init__(
            health_component=item_component.Consumable,
            ui=ui,
            entity=entity,
            pos=pos,
            width=width,
            height=height,
            border_width=border_width,
            center=center,
        )
        self.draw_border = super(PlayerHealthBar, self).draw_border

    def draw(self, camera):
        if self.health_component.hp == self.health_component.max_hp:
            # No durability bar if max hp
            return

        super().draw(camera)

"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file contains widgets for all health bars
"""

import colorsys
import math

from src import pygame, screen

from src.entities.component import Position, Health


class PlayerHealthBar:
    def __init__(self, ui, entity, pos, width, height, border_width=2):
        self.uuid = None
        self.ui = ui
        self.entity = entity

        self.pos = pos
        self.width = width
        self.height = height
        self.border_width = border_width
        self.health_component = self.ui.world.component_for_entity(self.entity, Health)

        self.border_rect = pygame.Rect(
            pos[0] - border_width, pos[1] - border_width,
            width + 2 * border_width, height + 2 * border_width
        )
        self.rect = pygame.Rect(*pos, self.health_component.hp / self.health_component.max_hp * width, height)

        self.previous_health = self.health_component.hp
        self.flash_size = 0
        self.flash_duration = -1
        self.flash_width = 0
        self.flash_hp_diff = 0  # 1 for lost, -1 for gained

    def draw(self, *_): # Both camera and UI not used
        self.flash_duration -= 1
        self.rect.width = self.health_component.hp / self.health_component.max_hp * self.width

        hp_percentage = self.rect.width / self.width
        hsv = (hp_percentage / 3, 1, 1)
        rgb = colorsys.hsv_to_rgb(*hsv)
        hp_color = [max(int(color_value * 255), 0) for color_value in rgb]

        hp_lost = self.previous_health - self.health_component.hp
        self.flash_size += abs(hp_lost)

        if hp_lost != 0:
            self.flash_duration = 10
            self.flash_hp_diff = math.copysign(1, hp_lost)
        if self.flash_duration <= 0:
            self.flash_size -= 1
            self.flash_size *= 0.98
            self.flash_size = max(0, self.flash_size - 3)


        pygame.draw.rect(screen, (0, 0, 0), self.border_rect, width=self.border_width)
        pygame.draw.rect(screen, hp_color, self.rect)

        self.flash_width = self.flash_size * self.width / self.health_component.max_hp

        if self.flash_width > 0:
            flash_rect = pygame.Rect(
                self.rect.x + self.rect.width, self.rect.y,
                self.flash_width, self.height
            )

            if self.flash_hp_diff == -1:
                flash_rect.right = self.rect.right

            pygame.draw.rect(screen, (255, 255, 255), flash_rect)
        else:
            self.flash_hp_diff = 0

        self.previous_health = self.health_component.hp

        

class MobHealthBar:
    def __init__(self, ui, entity, width, height, border_width=2):
        self.uuid = None
        self.ui = ui
        self.entity = entity

        self.pos = self.ui.world.component_for_entity(entity, Position)
        self.width = width
        self.height = height
        self.border_width = border_width
        self.health_component = self.ui.world.component_for_entity(self.entity, Health)

        self.border_rect = pygame.Rect(
            self.pos.pos.x - border_width, self.pos.pos.y - 20 - border_width,
            width + 2 * border_width, height + 2 * border_width
        )
        self.rect = pygame.Rect(*self.pos.pos, self.health_component.hp / self.health_component.max_hp * width, height)

        self.previous_health = self.health_component.hp
        self.flash_size = 0
        self.flash_duration = -1

    def draw(self, camera):
        self.flash_duration -= 1

        if self.health_component.hp <= 0:
            self.ui.remove_widget(self.uuid)
            return

        entity_rect = self.pos.rect
        self.border_rect.center = (entity_rect.centerx - self.border_width, entity_rect.centery - 20 - self.border_width)
        self.rect.topleft = (self.border_rect.x + self.border_width, self.border_rect.y + self.border_width)
        self.rect.width = self.health_component.hp / self.health_component.max_hp * self.width

        hp_percentage = self.rect.width / self.width
        hsv = (hp_percentage / 3, 1, 1)
        rgb = colorsys.hsv_to_rgb(*hsv)
        hp_color = [max(int(color_value * 255), 0) for color_value in rgb]

        hp_lost = self.previous_health - self.health_component.hp
        self.flash_size += hp_lost

        if hp_lost > 0:
            self.flash_duration = 10
        if self.flash_duration <= 0:
            self.flash_size -= 1
            self.flash_size *= 0.98
            self.flash_size = max(0, self.flash_size - 3)

        pygame.draw.rect(screen, (0, 0, 0), camera.apply(self.border_rect), width=self.border_width)
        pygame.draw.rect(screen, hp_color, camera.apply(self.rect))

        flash_width = self.flash_size * self.width / self.health_component.max_hp

        if flash_width > 0:
            if hp_lost > 0:
                pygame.draw.rect(screen, (255, 255, 255), camera.apply(pygame.Rect(self.rect.x + self.rect.width, self.rect.y, flash_width, self.height)))
            elif hp_lost < 0:
                pygame.draw.rect(screen, (255, 255, 255), camera.apply(pygame.Rect(self.rect.x + self.rect.width, self.rect.y, flash_width, self.height)))

        self.previous_health = self.health_component.hp

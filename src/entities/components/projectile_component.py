"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines projectile components, similar to the components in component.py
"""
from __future__ import annotations

import math

from src import pygame, utils


class Projectile:
    def __init__(
        self,
        vel: int,
        angle: float,
        damage: float,
        shot_by: int = -1,
        gravity: float = 0.5,
    ):
        self.vel = vel
        self.shot_by = shot_by
        self.damage = damage

        self.initial_angle = angle
        self.gravity = gravity
        self.t = 0

        # Calculate velocity direction
        if math.cos(self.initial_angle) > 0:
            self.vel_dir = 1
        else:
            self.vel_dir = -1

    def rel_x(self, t: int):
        """
        Calculates relative x of the projectile given time
        Formula: x = vtcos(theta)
        """
        return math.cos(self.initial_angle) * self.vel * t

    def rel_y(self, t: int):
        """
        Calculates relative y of the projectile given time
        Formula: y = vtsin(theta) + gt^2/2
        """
        return math.sin(self.initial_angle) * self.vel * t + self.gravity * t**2 / 2


class ProjectilePosition:
    def __init__(self, pos: pygame.Vector2):
        self.pos = pos
        self.tile_pos = utils.pixel_to_tile(self.pos)
        self.rect = None

        self.spawn_pos = pygame.Vector2(self.pos)


class ProjectileGraphics:
    def __init__(self, sprite: pygame.Surface):
        self.original_img = sprite
        self.current_img = sprite
        self.size = sprite.get_bounding_rect().size

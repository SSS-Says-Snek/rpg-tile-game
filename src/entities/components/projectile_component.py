"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines projectile components, similar to the components in component.py
"""
import math

from src import pygame, utils


class Projectile:
    def __init__(
        self,
        vel: pygame.Vector2,
        shot_by: int,
        damage: float,
        angle: float,
        gravity: float = 0,
    ):
        self.vel = vel
        self.shot_by = shot_by
        self.damage = damage

        self.initial_angle = angle
        self.gravity = gravity

        # Calculate velocity direction
        if (
            -180 <= math.degrees(self.initial_angle) < -90
            or 90 <= math.degrees(self.initial_angle) <= 180
        ):
            self.vel_dir = 1
        elif (
            -90 <= math.degrees(self.initial_angle) < 0
            or 0 <= math.degrees(self.initial_angle) < 90
        ):
            self.vel_dir = -1


class ProjectilePosition:
    def __init__(self, pos: pygame.Vector2):
        self.pos = pos
        self.tile_pos = utils.pixel_to_tile(self.pos)
        self.rect = None


class ProjectileGraphics:
    def __init__(self, sprite: pygame.Surface):
        self.original_img = sprite
        self.current_img = sprite
        self.size = sprite.get_bounding_rect().size

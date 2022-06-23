"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines projectile components, similar to the components in component.py
"""
import math


class Projectile:
    def __init__(self, vel, angle, gravity=0):
        self.vel = vel
        self.initial_angle = angle
        self.gravity = gravity

        if math.degrees(self.initial_angle) < -90:
            self.vel_dir = 1
        else:
            self.vel_dir = -1
        print(math.degrees(self.initial_angle))


class ProjectilePosition:
    def __init__(self, pos):
        self.pos = pos
        self.rect = None


class ProjectileGraphics:
    def __init__(self, sprite):
        self.original_img = sprite
        self.current_img = sprite
        self.size = sprite.get_bounding_rect().size

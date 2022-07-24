"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the Camera class, used to shift objects around
with respect to the player
"""

import random
from typing import Union

from src import pygame


class Camera:
    def __init__(self, camera_width, camera_height):
        self.camera_width = camera_width
        self.camera_height = camera_height
        self.camera = pygame.Rect(0, 0, self.camera_width, self.camera_height)

        self.shake_offset = pygame.Vector2()
        self.shake_frames = 0
        self.shake_pixels = 5

    def apply(self, target_pos: Union[pygame.Rect, pygame.Vector2, tuple, list]):
        if isinstance(target_pos, tuple) or isinstance(target_pos, list):
            target_pos = pygame.Rect(target_pos[0], target_pos[1], 0, 0)
        elif isinstance(target_pos, pygame.Vector2):
            target_pos = pygame.Rect(target_pos.x, target_pos.y, 0, 0)

        return target_pos.move((-self.camera.x, -self.camera.y))

    def hard_apply(self, target_pos: Union[pygame.Rect, pygame.Vector2, tuple, list]):
        if isinstance(target_pos, tuple) or isinstance(target_pos, list):
            target_pos = pygame.Rect(target_pos[0], target_pos[1], 0, 0)
        elif isinstance(target_pos, pygame.Vector2):
            target_pos = pygame.Rect(target_pos.x, target_pos.y, 0, 0)

        return target_pos.move(self.camera.topleft)

    def adjust_to(self, dt, target_pos):
        self.camera.x += dt * (target_pos.x - self.camera.x - self.camera_width // 2) // 20

        self.camera.y += dt * (target_pos.y - self.camera.y - self.camera_height // 2) // 20

    def hard_adjust_to(self, target_pos):
        x = self.camera_width // 2 - target_pos.x + self.shake_offset.x
        y = self.camera_height // 2 - target_pos.y + self.shake_offset.y
        self.camera.topleft = (x, y)

    def start_shake(self, num_frames):
        self.shake_frames = num_frames

    def do_shake(self):
        self.shake_offset.x += random.randint(-self.shake_pixels, self.shake_pixels)
        self.shake_offset.y += random.randint(-self.shake_pixels, self.shake_pixels)

        self.shake_frames -= 1

        if self.shake_frames == 0:
            self.shake_offset.x, self.shake_offset.y = 0, 0

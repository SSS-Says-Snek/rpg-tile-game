"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the Camera class, used to shift objects around
with respect to the player
"""

from __future__ import annotations

import random
from typing import Optional, Union

from src import pygame


class Camera:
    def __init__(self, camera_width: int, camera_height: int, map_width: int, map_height: int):
        """
        A camera that follows an object

        Args:
            camera_width: Width of viewport
            camera_height: Height of viewport
            map_width: Width of map
            map_height: Height of map
        """

        self.camera_width = camera_width
        self.camera_height = camera_height

        # TODO: Stop scrolling on boundaries
        self.map_width = map_width
        self.map_height = map_height

        self.camera = pygame.Rect(0, 0, self.camera_width, self.camera_height)

        self.last_shake = pygame.Vector2()
        self.shake_frames = 0
        self.shake_pixels = 3

    def apply(
        self,
        target_pos: Union[tuple[int, int], list[int], pygame.Vector2, pygame.Rect],
        parallax: Optional[float] = None,
    ) -> pygame.Rect:
        """
        Offsets a position based on the camera

        Args:
            target_pos: Unadjusted position
            parallax: Parallax weight. Defaults to None

        Returns:
            A rectangle that is the adjusted position of the target position
        """

        if isinstance(target_pos, tuple) or isinstance(target_pos, list):
            target_pos = pygame.Rect(target_pos[0], target_pos[1], 0, 0)
        elif isinstance(target_pos, pygame.Vector2):
            target_pos = pygame.Rect(target_pos.x, target_pos.y, 0, 0)

        if parallax is None:
            return target_pos.move((-self.camera.x, -self.camera.y))

        # Parallax
        return pygame.Rect(
            target_pos.x - self.camera.x * parallax,
            target_pos.y - self.camera.y * parallax,
            *target_pos.size,
        )

    def hard_apply(self, target_pos: Union[tuple[int, int], list[int], pygame.Vector2, pygame.Rect]):
        target = target_pos
        if isinstance(target_pos, tuple) or isinstance(target_pos, list):
            target = pygame.Rect(target_pos[0], target_pos[1], 0, 0)
        elif isinstance(target_pos, pygame.Vector2):
            target = pygame.Rect(target_pos.x, target_pos.y, 0, 0)
        else:
            raise NotImplementedError

        return target.move(self.camera.topleft)

    def adjust_to(self, dt: float, target_pos: pygame.Vector2):
        """
        Smoothly moves camera to game object

        Args:
            dt: DT for framerate independence
            target_pos: Target position of game object
        """
        self.camera.x += dt * (target_pos.x - self.camera.x - self.camera_width // 2) // 20

        # 0.65 makes the player slightly off center on the y axis, which shows less ground
        self.camera.y += dt * (target_pos.y - self.camera.y - self.camera_height * 0.65) // 20

        # Restrict camera movement
        self.camera.x = max(self.camera.x, 0)

    def hard_adjust_to(self, target_pos: pygame.Vector2):
        """
        A hard version of `adjust_to`, with no smooth scrolling

        Args:
            target_pos: Target position of game object
        """

        x = self.camera_width // 2 - target_pos.x
        y = self.camera_height // 2 - target_pos.y
        self.camera.topleft = (x, y)

    def start_shake(self, num_frames):
        """Starts shaking screen"""

        self.shake_frames = num_frames
        self.last_shake.x, self.last_shake.y = self.camera.topleft

    def do_shake(self):
        """Performs shaking action"""

        self.camera.x += random.randint(-self.shake_pixels, self.shake_pixels)
        self.camera.y += random.randint(-self.shake_pixels, self.shake_pixels)

        self.shake_frames -= 1

        # if self.shake_frames == 0:
        #     self.camera.x, self.camera.y = self.last_shake.xy

    def visible(self, other_rect: pygame.Rect, strict: bool = False) -> bool:
        """
        Returns if a rectangle is within the camera viewport

        Args:
            other_rect: Rect to check
            strict: Whether or not the entire rect must be inside the viewport or not

        Returns:
            A boolean of whether it is in the viewport or not
        """

        return other_rect in self.camera or (not strict and self.camera.colliderect(other_rect))

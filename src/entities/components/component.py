"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines components (data-only) for the game entities (integer IDs)
"""

from __future__ import annotations

from typing import Optional

from src import pygame, utils
from src.types import Entity


class Graphics:
    def __init__(
        self,
        sprite: Optional[pygame.Surface] = None,
        animations: Optional[dict] = None,
        animation_speeds: Optional[dict] = None,
    ):
        # self.sprites usually for prototyping purposes, where I don't have animations yet
        # Assume that sprite is the sprite facing right
        self.sprites = (
            {
                "right": sprite,
                "left": pygame.transform.flip(sprite, True, False),
            }
            if sprite is not None
            else None
        )

        self.animations = animations if animations is not None else None
        self.animation_speeds = animation_speeds if animation_speeds is not None else None

        if sprite is not None:
            self.size = sprite.get_size()
        elif self.animations is not None:
            self.size = list(self.animations.values())[0].frames[0].get_size()


class Position:
    def __init__(self, pos: pygame.Vector2, rect_size: tuple[int, int]):
        self.original_pos = pos.copy()
        self.pos: pygame.Vector2 = pos
        self.tile_pos: pygame.Vector2 = utils.pixel_to_tile(pos)
        self.direction: int = 1  # 1 for right, -1 for left

        self.on_ground: bool = False
        self.rect: pygame.Rect = pygame.Rect(*self.pos, *rect_size)

    def in_range(self, other_tile_pos: pygame.Vector2, radius: int) -> bool:
        return self.tile_pos.distance_to(other_tile_pos) < radius


class Movement:
    def __init__(
        self,
        speed: float,
        acc: pygame.Vector2 = pygame.Vector2(0, 0),
        gravity_acc: float = 2.1,
    ):
        self.speed = speed
        self.vel = pygame.Vector2(0, 0)

        self.acc = acc
        self.gravity_acc = pygame.Vector2(0, gravity_acc)


class Health:
    def __init__(self, hp: float, max_hp: int):
        self._hp = hp
        self.max_hp = max_hp

        self.prev_hp = hp

    @property
    def hp(self) -> float:
        return self._hp

    @hp.setter
    def hp(self, value: float):
        self._hp = max(min(value, self.max_hp), 0)


class Inventory:
    def __init__(self, size: int, hotbar_size: Optional[int] = None):
        self.size = size
        self.hotbar_size = hotbar_size

        self.inventory: list[Optional[int]] = [None for _ in range(size)]
        self.equipped_item_idx = 0

        self.cooldown = 0  # Changes based on equipped item
        self.last_used = 0
        self.on_cooldown = False

    def get_available_idx(self) -> Optional[int]:
        for i, item in enumerate(self.inventory):
            if item is None:
                return i
        return None

    @property
    def equipped_item(self):
        return self.inventory[self.equipped_item_idx]

    def remove_item(self, idx: int):
        self.inventory[idx] = None

    def __getitem__(self, item: int) -> Optional[Entity]:
        return self.inventory[item]

    def __setitem__(self, key: int, value: Entity):
        self.inventory[key] = value


class NoCollidePlayer:
    pass

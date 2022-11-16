"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines components (data-only) for the game entities (integer IDs)
"""

from __future__ import annotations

__all__ = [
    "References",
    "Flags",
    "Graphics",
    "Position",
    "Movement",
    "Health",
    "MeleeAttack",
    "Inventory",
]

from typing import Optional

from src import pygame, utils


class References:  # Thinking about it
    def __init__(self, reference_dict: Optional[dict] = None):
        if reference_dict is None:
            self.references = {}
        else:
            self.references = reference_dict


class Flags:
    def __init__(
        self,
        mob_type: Optional[str] = None,
        collide_with_player: bool = False,
    ):
        self.collide_with_player = collide_with_player

        # TODO: Remove in favor of components
        self.mob_type = mob_type


class Graphics:
    def __init__(
        self,
        sprite: Optional[pygame.Surface] = None,
        animations: Optional[dict] = None,
        animation_speeds: Optional[dict] = None,
    ):
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
        else:
            self.size = list(self.animations.values())[0].frames[0].get_size()


class Position:
    def __init__(self, pos: pygame.Vector2):
        self.original_pos = pos.copy()
        self.pos: pygame.Vector2 = pos
        self.tile_pos: pygame.Vector2 = utils.pixel_to_tile(pos)
        self.direction: int = 1  # 1 for right, -1 for left

        self.on_ground: bool = False
        self.rect: pygame.Rect = pygame.Rect(0, 0, 0, 0)

    def in_range(self, other_tile_pos: pygame.Vector2, radius: int) -> bool:
        return self.tile_pos.distance_to(other_tile_pos) < radius


class Movement:
    def __init__(
        self,
        speed: float,
        acc: pygame.Vector2 = pygame.Vector2(0, 0),
        gravity_acc: float = 1.3,
    ):
        self.speed = speed
        self.vel = pygame.Vector2(0, 0)

        self.acc = acc
        self.gravity_acc = pygame.Vector2(0, gravity_acc)


class Health:
    def __init__(self, hp: float, max_hp: int):
        self._hp = hp
        self.max_hp = max_hp

    @property
    def hp(self) -> float:
        return self._hp

    @hp.setter
    def hp(self, value: float):
        self._hp = max(min(value, self.max_hp), 0)


class MeleeAttack:
    def __init__(
        self,
        attack_range: int,
        attack_cooldown: float,
        damage: float,
        collision: bool = False,
    ):
        self.attack_range = attack_range
        self.attack_cooldown = attack_cooldown
        self.damage = damage
        self.collision = collision

        self.last_attacked = 0


class Inventory:
    def __init__(self, size: int, hotbar_size: Optional[int] = None):
        self.size = size
        self.hotbar_size = hotbar_size

        self.inventory = [None for _ in range(size)]
        self.equipped_item_idx = 0

        self.cooldown = 0  # Changes based on equipped item
        self.last_used = 0
        self.on_cooldown = False

    def get_available_idx(self) -> Optional[int]:
        for i, item in enumerate(self.inventory):
            if item is None:
                return i
        return None

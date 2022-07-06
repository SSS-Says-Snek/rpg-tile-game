"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines components (data-only) for the game entities (integer IDs)
"""

__all__ = [
    "References",
    "Flags",
    "Tile",
    "Graphics",
    "Position",
    "Movement",
    "Health",
    "MeleeAttack",
    "Inventory",
]

import collections
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
        has_dialogue=False,
        collidable=False,
        rotatable=False,
        mob_type=None,
        damageable=False,
        collide_with_player=False,
    ):
        self.has_dialogue = has_dialogue
        self.collidable = collidable
        self.rotatable = rotatable
        self.damageable = damageable
        self.collide_with_player = collide_with_player

        self.alive = True
        self.mob_type = mob_type


class Tile:
    def __init__(self, tile_width: int, tile_height: int):
        self.tile_width: int = tile_width
        self.tile_height: int = tile_height


class Graphics:
    def __init__(
        self,
        sprite: Optional[pygame.Surface] = None,
        animations: Optional[dict] = None,
        animation_speeds: Optional[dict] = None,
    ):
        self.sprite: Optional[pygame.Surface] = sprite
        self.animations: dict = animations if animations is not None else {}
        self.animation_speeds: dict = animation_speeds if animation_speeds is not None else {}

        if self.sprite is not None:
            self.size: tuple = self.sprite.get_size()
        elif self.animations is not None:
            self.size: tuple = list(self.animations.values())[0].frames[0].get_size()


class Position:
    def __init__(self, pos: pygame.Vector2):
        self.pos: pygame.Vector2 = pos
        self.tile_pos: pygame.Vector2 = utils.pixel_to_tile(pos)
        self.direction: int = 1  # 1 for right, -1 for left

        self.on_ground: bool = False
        self.rect: Optional[pygame.Rect] = None


class Movement:
    def __init__(
        self,
        speed: float,
        acc: pygame.Vector2 = None,
        gravity_acc: float = 1.3,
        rot=0,
    ):
        self.speed: float = speed
        self.vel: pygame.Vector2 = pygame.Vector2(0, 0)

        if acc is None:
            self.acc: pygame.Vector2 = pygame.Vector2(0, 0)
        else:
            self.acc: pygame.Vector2 = acc
        self.gravity_acc: pygame.Vector2 = pygame.Vector2(0, gravity_acc)
        self.rot = rot

        self.mob_specifics: collections.defaultdict = collections.defaultdict(lambda: None)


class Health:
    def __init__(self, hp: float, max_hp: int):
        self._hp: float = hp
        self.max_hp: float = max_hp

    @property
    def hp(self):
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

"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines item components, similar to the components in component.py
"""
from __future__ import annotations

from typing import Optional

from src import core, pygame
from src.entities.components.component import Inventory


class Item:
    def __init__(self, name: str, cooldown: float, owner: Optional[int] = None):
        self.name = name
        self.cooldown = cooldown
        self.owner = owner

        self.used = False

    def use(self, inventory_component: Inventory):
        self.used = True

        inventory_component.cooldown = self.cooldown
        inventory_component.last_used = core.time.get_ticks()


class ItemPosition:
    def __init__(self, pos: pygame.Vector2, rect_size: tuple[int, int], in_inventory: bool = False):
        self.pos = pos
        self.rect = pygame.Rect(self.pos, rect_size)
        self.in_inventory = in_inventory


class ItemGraphics:
    def __init__(
        self,
        sprite: pygame.Surface,
        icon: Optional[pygame.Surface] = None,
        world_sprite: Optional[pygame.Surface] = None,
        flip_on_dir: bool = False,
    ):
        self.original_img = sprite
        self.current_img = sprite
        self.size = sprite.get_rect().size
        self.bound_size = sprite.get_bounding_rect().size

        if icon is None:
            self.icon = pygame.transform.smoothscale(self.original_img, (50, 50))
        else:
            self.icon = pygame.transform.smoothscale(icon, (50, 50))

        if world_sprite is None:
            self.world_sprite = sprite
        else:
            self.world_sprite = world_sprite

        self.flip_on_dir = flip_on_dir


class Consumable:
    def __init__(self, num_uses: int = 1):
        self.total_uses = num_uses
        self.uses_left = num_uses

        self.consumed = False

    @property
    def hp(self):
        return self.uses_left

    @property
    def max_hp(self):
        return self.total_uses


class MeleeWeapon:
    def __init__(self, attack_damage: int, effects=None):
        self.attack_damage = attack_damage
        self.effects = effects

        self.hit = False


class RangedWeapon:
    def __init__(self, projectile_damage: int, effects=None):
        self.projectile_damage = projectile_damage

        self.effects = effects


class SlashingSword:
    def __init__(self, angle: float = 0):
        self.angle = angle

        self.rect = pygame.Rect(0, 0, 0, 0)  # Reassign position after interaction with ItemPosition


class GravityBow:
    def __init__(self, launch_vel: pygame.Vector2, angle: float = 0):
        self.angle = angle
        self.launch_vel = launch_vel


class HealthPotion:
    def __init__(self, heal_power: int):
        self.heal_power = heal_power


class Projectile:
    def __init__(self, vel: pygame.Vector2, gravity: bool = False):
        self.vel = vel
        self.gravity = gravity


# Aliases
Durability = Consumable

"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines item components, similar to the components in component.py
"""

from src import pygame

class Item:
    def __init__(self, cooldown, owner=None):
        self.owner = owner
        self.used = False

        self.cooldown = cooldown
        self.last_used = 0


class ItemPosition:
    def __init__(self, pos, in_inventory=False):
        self.pos = pos
        self.rect = None
        self.in_inventory = in_inventory


class ItemGraphics:
    def __init__(self, sprite, icon=None):
        self.original_img = sprite
        self.current_img = sprite
        self.size = sprite.get_rect().size
        self.bound_size = sprite.get_bounding_rect().size

        if icon is None:
            self.icon = pygame.transform.smoothscale(self.original_img, (50, 50))
        else:
            self.icon = pygame.transform.smoothscale(icon, (50, 50))


class Consumable:
    def __init__(self, num_uses=1):
        self.uses_left = num_uses


class MeleeWeapon:
    def __init__(self, attack_damage, effects=None):
        self.attack_damage = attack_damage

        self.last_attacked = 0
        self.hit = False

        self.effects = effects


class RangedWeapon:
    def __init__(self):
        pass


class SlashingSword:
    def __init__(self, angle=0):
        self.angle = angle

        self.rect = None  # Reassign position after interaction with ItemPosition


class Medkit:
    def __init__(self, heal_power):
        self.heal_power = heal_power
__all__ = ["Flags", "Tile", "Graphics", "Position", "Movement", "Health", "MeleeAttack"]

import collections

from src import pygame, utils


class Flags:
    def __init__(self, has_dialogue=False, collidable=False, rotatable=False, mob_type=None, damageable=False):
        self.has_dialogue = has_dialogue
        self.collidable = collidable
        self.rotatable = rotatable
        self.damageable = damageable

        self.mob_type = mob_type


class Tile:
    def __init__(self, tile_width, tile_height):
        self.tile_width = tile_width
        self.tile_height = tile_height


class Graphics:
    def __init__(self, sprite):
        self.sprite = sprite
        self.size = self.sprite.get_size()


class Position:
    def __init__(self, pos):
        self.pos = pos
        self.tile_pos = utils.pixel_to_tile(pos)
        self.facing = None

        self.on_ground = False
        self.rect = None


class Movement:
    def __init__(self, speed, vx=0, vy=0, acc=None, gravity_acc=0.8, rot=0):
        self.speed = speed
        self.vel = pygame.Vector2(vx, vy)
        self.vx = vx
        self.vy = vy

        if acc is None:
            self.acc = pygame.Vector2(0, 0)
        else:
            self.acc = acc
        self.gravity_acc = pygame.Vector2(0, gravity_acc)
        self.rot = rot

        self.mob_specifics = collections.defaultdict(lambda: None)


class WalkerMovement(Movement):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.walk_direction = 1


class Health:
    def __init__(self, hp, max_hp):
        self.hp = hp
        self.max_hp = max_hp


class MeleeAttack:
    def __init__(self, attack_range, attack_cooldown, damage):
        self.attack_range = attack_range
        self.attack_cooldown = attack_cooldown
        self.damage = damage

        self.last_attacked = 0

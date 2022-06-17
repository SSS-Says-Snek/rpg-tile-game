from src import pygame


class Item:
    def __init__(self, cooldown, owner=None):
        self.owner = owner
        self.used = False

        self.cooldown = cooldown
        self.last_used = 0


class ItemPosition:
    def __init__(self, pos):
        self.pos = pos


class ItemGraphics:
    def __init__(self, sprite, icon=None):
        self.original_img = sprite
        self.current_img = sprite

        if icon is None:
            self.icon = pygame.transform.smoothscale(self.original_img, (50, 50))
        else:
            self.icon = pygame.transform.smoothscale(icon, (50, 50))


class MeleeWeapon:
    def __init__(self, attack_damage, effects=None):
        self.attack_damage = attack_damage

        self.last_attacked = 0
        self.hit = False

        self.effects = effects


class SlashingSword:
    def __init__(self, angle=0):
        self.angle = angle

        self.rect = None  # Reassign position after interaction with ItemPosition

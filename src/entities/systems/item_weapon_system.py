"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the ItemWeaponSystem, which is used to interact and use items
"""

import operator
import random

from src import pygame, utils

from src.display import particle

from src.entities.systems.system import System
from src.entities import item_component
from src.entities.component import Position, Movement, MeleeAttack, Health, Inventory


class ItemWeaponSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    def create_hit_particles(self, num_particles, pos, color_list):
        for _ in range(num_particles):
            self.level_state.particle_system.add(
                particle.Particle()
                    .builder()
                    .at(pos=pos.pos, angle=random.gauss(180, 180))
                    .color(color=random.choice(color_list))
                    .gravity(gravity_acc=0.35, gravity_y_vel=-3.5)
                    .lifespan(frames=40)
                    .speed(speed=random.gauss(1.4, 0.8))

                    .effect_fade(start_fade_frac=0.5)
                    .build()
            )

    def process(self, event_list):
        for entity, (pos, movement) in self.world.get_components(
            Position, Movement
        ):
            # Non-player to entity (including player) damage interaction
            # FOR NOW! SUPER INEFFICIENT
            for nested_entity, (nested_pos, nested_health) in self.world.get_components(
                Position, Health
            ):
                if nested_entity == entity:
                    continue

                if entity != self.player and nested_entity == self.player:
                    if self.world.has_component(entity, MeleeAttack):
                        melee_attack = self.world.component_for_entity(entity, MeleeAttack)

                        if melee_attack.collision:
                            conditional = pos.rect.colliderect(nested_pos.rect)
                        else:
                            conditional = pos.tile_pos.distance_to(nested_pos.tile_pos) <= melee_attack.attack_range

                        if conditional and pygame.time.get_ticks() - melee_attack.last_attacked > melee_attack.attack_cooldown * 1000:
                            nested_health.hp -= melee_attack.damage
                            nested_health.hp = max(nested_health.hp, 0)

                            melee_attack.last_attacked = pygame.time.get_ticks()

            # Player to entity combat
            if entity == self.player:
                inventory = self.world.component_for_entity(self.player, Inventory)
                equipped_item = inventory.inventory[inventory.equipped_item_idx]

                # No equipped item = no combat
                if equipped_item is None:
                    continue

                # Generator expr: less mem consumption yay
                interactable_entities = (
                    entity_stuff for entity_stuff in self.world.get_components(Position, Health)
                    if entity_stuff[0] != self.player
                )

                # Core components needed
                item = self.world.component_for_entity(equipped_item, item_component.Item)

                # Might have just picked
                if not self.world.has_component(equipped_item, item_component.ItemPosition):
                    item.owner = entity

                owner_pos = self.world.component_for_entity(item.owner, Position)  # Equipped item always has position

                # Might have just picked
                if not self.world.has_component(equipped_item, item_component.ItemPosition):
                    self.world.add_component(
                        equipped_item,
                        item_component.ItemPosition(pos=pygame.Vector2(*owner_pos.pos), in_inventory=True)
                    )

                item_pos = self.world.component_for_entity(equipped_item, item_component.ItemPosition)
                item_graphics = self.world.component_for_entity(equipped_item, item_component.ItemGraphics)

                if owner_pos.direction == 1:  # Facing right
                    item_pos.pos.x = owner_pos.rect.right
                    angle_comp_func = operator.le
                    pivot_pos = (0, item_graphics.size[1])
                else:  # Facing left
                    item_pos.pos.x = owner_pos.rect.left - item_graphics.original_img.get_bounding_rect().width
                    angle_comp_func = operator.ge
                    pivot_pos = (item_graphics.original_img.get_bounding_rect().width, item_graphics.size[1])  # IDK
                item_pos.pos.y = owner_pos.pos.y

                # Melee weapons (will refactor into small functions)
                # Must be "used" (player interacted with it)
                if self.world.has_component(equipped_item, item_component.MeleeWeapon):
                    item_pos.pos.y -= item_graphics.size[1] / 2

                    # Not used = no combat
                    if not item.used:
                        continue

                    melee_weapon = self.world.component_for_entity(equipped_item, item_component.MeleeWeapon)

                    # Slashing sword (different from stabbing sword)
                    if self.world.has_component(equipped_item, item_component.SlashingSword):
                        slashing_sword = self.world.component_for_entity(equipped_item, item_component.SlashingSword)

                        # Handle angle and positions
                        slashing_sword.angle -= 14 * owner_pos.direction
                        item_graphics.current_img, slashing_sword.rect = utils.rot_pivot(
                            item_graphics.original_img,
                            item_pos.pos, pivot_pos, slashing_sword.angle
                        )
                        item_pos.pos.x = slashing_sword.rect.x
                        item_pos.pos.y = slashing_sword.rect.y + 32

                        # Loop through all interactable entities
                        for nested_entity, (nested_pos, nested_health) in interactable_entities:
                            if slashing_sword.rect.colliderect(nested_pos.rect) and not melee_weapon.hit:
                                colors = self.level_state.settings["particle_colors"]["death"]
                                melee_weapon.hit = True
                                nested_health.hp -= melee_weapon.attack_damage
                                nested_health.hp = max(nested_health.hp, 0)

                                if nested_health.hp == 0:
                                    # Create particles
                                    self.create_hit_particles(30, nested_pos, colors)

                                    # Delete entity and continue looping
                                    self.world.delete_entity(nested_entity)
                                    continue

                                # "Blood" particles
                                self.create_hit_particles(5, nested_pos, [(255, 0, 0)])

                        # If slash angle > 150 deg, reset
                        if angle_comp_func(slashing_sword.angle, -150 * owner_pos.direction):
                            slashing_sword.angle = 0
                            item_graphics.current_img = item_graphics.original_img

                            # Resets position
                            if owner_pos.direction == 1:  # Facing right
                                item_pos.pos.x = owner_pos.rect.right
                            else:  # Facing left
                                item_pos.pos.x = owner_pos.rect.left - item_graphics.original_img.get_bounding_rect().width
                            item_pos.pos.y = owner_pos.rect.y - 16

                            slashing_sword.rect.x = item_pos.pos.x
                            slashing_sword.rect.y = item_pos.pos.y

                            item.used = False
                            melee_weapon.hit = False

                elif self.world.has_component(equipped_item, item_component.Consumable):
                    if self.world.has_component(equipped_item, item_component.Medkit) and item.used:
                        owner_health = self.world.component_for_entity(item.owner, Health)
                        medkit = self.world.component_for_entity(equipped_item, item_component.Medkit)
                        consumable = self.world.component_for_entity(equipped_item, item_component.Consumable)

                        owner_health.hp += medkit.heal_power
                        owner_health.hp = min(owner_health.hp, owner_health.max_hp)

                        consumable.uses_left -= 1
                        if consumable.uses_left == 0:
                            self.world.delete_entity(equipped_item)
                            inventory.inventory[inventory.equipped_item_idx] = None


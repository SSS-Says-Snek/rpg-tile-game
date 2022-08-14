"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the CombatSystem, which is used to interact and use items
"""
import math
import operator
import types
from dataclasses import dataclass
from typing import Generator

from src import pygame, utils, common
from src.entities.effect import RegenEffect

from src.entities.systems.system import System
from src.entities.components import item_component, projectile_component
from src.entities.components.component import Position, Movement, Health, Inventory


@dataclass
class ItemData:
    equipped_item: int
    pos: Position
    pivot_pos: tuple
    item: item_component.Item
    item_graphics: item_component.ItemGraphics
    item_pos: item_component.ItemPosition
    interactable_entities: Generator

    def __iter__(self):
        return iter(
            (
                self.equipped_item,
                self.pos,
                self.pivot_pos,
                self.item,
                self.item_graphics,
                self.item_pos,
                self.interactable_entities,
            )
        )


# Trying to refactor the item usages, still thinking
class ItemUsages(types.SimpleNamespace):
    def __init__(self, outer, **kwargs):
        super().__init__(**kwargs)

        self.outer = outer

    # Lazy me :sunglasses:
    def __getattr__(self, item):
        return self.outer.__dict__[item]

    # Slashing sword
    def handle_slashing_sword(self, item_data):
        # Initialization
        (
            equipped_item,
            pos,
            pivot_pos,
            item,
            item_graphics,
            item_pos,
            interactable_entities,
        ) = item_data
        melee_weapon = self.world.component_for_entity(equipped_item, item_component.MeleeWeapon)

        item_pos.pos.x -= pos.direction * 6

        # Not used = no combat
        if not item.used:
            return

        slashing_sword = self.world.component_for_entity(
            equipped_item, item_component.SlashingSword
        )

        # Handle angle and positions
        slashing_sword.angle -= 14 * pos.direction
        (item_graphics.current_img, slashing_sword.rect,) = utils.rot_pivot(
            item_graphics.original_img,
            item_pos.pos,
            pivot_pos,
            slashing_sword.angle,
        )
        item_pos.pos.x = slashing_sword.rect.x
        item_pos.pos.y = slashing_sword.rect.y + 32

        # Adjust sword pos
        if pos.direction == -1:
            item_pos.pos.x += 12

        # Loop through all interactable entities
        for nested_entity, (
            nested_pos,
            nested_health,
        ) in interactable_entities:
            if slashing_sword.rect.colliderect(nested_pos.rect) and not melee_weapon.hit:
                colors = self.level_state.settings["particle_colors"]["death"]
                melee_weapon.hit = True
                nested_health.hp -= melee_weapon.attack_damage

                if nested_health.hp == 0:
                    # Create particles
                    self.particle_system.create_hit_particles(30, nested_pos, colors)

                    # Delete entity and continue looping
                    # self.world.delete_entity(nested_entity)
                    continue

                # "Blood" particles
                self.particle_system.create_hit_particles(5, nested_pos, [(255, 0, 0)])

        # If slash angle > 150 deg, reset
        if pos.direction == 1:
            angle_comp_func = operator.le
        else:
            angle_comp_func = operator.ge

        if angle_comp_func(slashing_sword.angle, -150 * pos.direction):
            slashing_sword.angle = 0
            item_graphics.current_img = item_graphics.original_img

            # Resets position
            if pos.direction == 1:
                # Facing right
                item_pos.pos.x = pos.rect.right
            else:
                # Facing left
                item_pos.pos.x = (
                    pos.rect.left - item_graphics.original_img.get_bounding_rect().width
                )
            item_pos.pos.y = pos.rect.y - 16

            slashing_sword.rect.x = item_pos.pos.x
            slashing_sword.rect.y = item_pos.pos.y

            item.used = False
            melee_weapon.hit = False

    # Gravity Bow
    def handle_gravity_bow(self, item_data, entity):
        (
            equipped_item,
            pos,
            pivot_pos,
            item,
            item_graphics,
            item_pos,
            interactable_entities,
        ) = item_data
        # Not used = no combat
        if not item.used:
            return

        arrow_sprite = utils.load_img(
            common.IMG_DIR / "items" / "arrows_sprite.png"
        ).convert_alpha()

        ranged_weapon = self.world.component_for_entity(equipped_item, item_component.RangedWeapon)
        mouse_pos = pygame.mouse.get_pos()
        adj_item_pos = self.camera.apply(item_pos.pos)

        adj_y_vel = (
            math.sin(
                math.atan2(
                    mouse_pos[1] - adj_item_pos.y,
                    mouse_pos[0] - adj_item_pos.x,
                )
            )
            * 14
        )

        self.world.create_entity(
            projectile_component.Projectile(
                vel=pygame.Vector2(10, adj_y_vel),
                shot_by=entity,
                damage=ranged_weapon.projectile_damage,
                angle=math.atan2(
                    mouse_pos[1] - adj_item_pos.y,
                    mouse_pos[0] - adj_item_pos.x,
                ),
                gravity=0.3,
            ),
            projectile_component.ProjectilePosition(item_pos.pos.copy()),
            projectile_component.ProjectileGraphics(arrow_sprite),
        )

        item.used = False

    # Health potion
    def handle_health_potion(self, item_data):
        item, pos, equipped_item = item_data.item, item_data.pos, item_data.equipped_item

        owner_health = self.world.component_for_entity(item.owner, Health)
        medkit = self.world.component_for_entity(equipped_item, item_component.HealthPotion)

        # Actual HP addition
        owner_health.hp += medkit.heal_power

        # Particles
        self.particle_system.create_hit_particles(8, pos, [(255, 255, 255)])
        self.effect_system.add_effect(
            item.owner, RegenEffect(self.level_state).builder().heal(10).duration(9, 3).build()
        )

        item.used = False


class CombatSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

        self.item_usages = ItemUsages(self)

    def handle_items(
        self,
        equipped_item,
        item_pos,
        item_graphics,
        pos,
        item,
        pivot_pos,
        interactable_entities,
        inventory,
        entity,
    ):
        item_data = ItemData(
            equipped_item, pos, pivot_pos, item, item_graphics, item_pos, interactable_entities
        )

        # Melee weapons (will refactor into small functions)
        # Must be "used" (player interacted with it)
        if self.world.has_component(equipped_item, item_component.MeleeWeapon):
            # Adjust position
            item_pos.pos.y -= item_graphics.size[1] / 2

            # Slashing sword
            if self.world.has_component(equipped_item, item_component.SlashingSword):
                self.item_usages.handle_slashing_sword(item_data)

        elif self.world.has_component(equipped_item, item_component.RangedWeapon):

            if self.world.has_component(equipped_item, item_component.GravityBow):
                # Gravity Bow
                self.item_usages.handle_gravity_bow(item_data, entity)

        if self.world.has_component(equipped_item, item_component.Consumable):
            consumable = self.world.component_for_entity(equipped_item, item_component.Consumable)
            if not item.used:
                consumable.consumed = False

            if item.used and not consumable.consumed:
                consumable.consumed = True
                consumable.uses_left -= 1
                if consumable.uses_left == 0:
                    self.world.delete_entity(equipped_item)
                    inventory.inventory[inventory.equipped_item_idx] = None

            if self.world.has_component(equipped_item, item_component.HealthPotion) and item.used:
                self.item_usages.handle_health_potion(item_data)

    # Actual processing
    def process(self, event_list, dts) -> None:
        for entity, (pos, _) in self.world.get_components(Position, Movement):
            # Player to entity combat
            # For now, only player can wield weapons. Could definitely change
            # if entity == self.player:
            if not self.world.has_component(entity, Inventory):
                continue

            # inventory = self.world.component_for_entity(self.player, Inventory)
            inventory = self.world.component_for_entity(entity, Inventory)
            equipped_item = inventory.inventory[inventory.equipped_item_idx]

            # No equipped item = no combat
            if equipped_item is None:
                continue

            # Generator expr: less mem consumption yay
            interactable_entities = (
                entity_stuff
                for entity_stuff in self.world.get_components(Position, Health)
                if entity_stuff[0] != entity
            )

            # Core components needed
            item = self.world.component_for_entity(equipped_item, item_component.Item)
            item_pos = self.world.component_for_entity(equipped_item, item_component.ItemPosition)
            item_graphics = self.world.component_for_entity(
                equipped_item, item_component.ItemGraphics
            )

            # Handle equipped item position blitting
            if pos.direction == 1:  # Facing right
                item_pos.pos.x = pos.rect.right
                pivot_pos = (0, item_graphics.size[1])
            else:  # Facing left
                item_pos.pos.x = (
                    pos.rect.left - item_graphics.original_img.get_bounding_rect().width
                )
                pivot_pos = (
                    item_graphics.original_img.get_bounding_rect().width,
                    item_graphics.size[1],
                )  # IDK

            item_pos.pos.y = pos.pos.y
            item_pos.pos.y += math.sin(pygame.time.get_ticks() / 250) * 2  # Bobbing effect

            self.handle_items(
                equipped_item,
                item_pos,
                item_graphics,
                pos,
                item,
                pivot_pos,
                interactable_entities,
                inventory,
                entity,
            )

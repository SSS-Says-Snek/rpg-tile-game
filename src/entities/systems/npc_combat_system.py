"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the NPC combat system, which handles non-player entities to entity
combat
"""
from src import pygame
from src.entities import ai_component, item_component
from src.entities.systems.system import System

from src.entities.component import Position, Movement, Health, MeleeAttack, Inventory


class NPCCombatSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    def process(self, event_list, dts) -> None:
        for entity, (pos, movement) in self.world.get_components(Position, Movement):
            # Non-player to entity (including player) damage interaction
            # FOR NOW! SUPER INEFFICIENT
            for nested_entity, (nested_pos, nested_health) in self.world.get_components(
                Position, Health
            ):
                if nested_entity == entity:
                    continue

                # RN TESTING ENTITY TO PLAYER ONLY
                if entity != self.player and nested_entity == self.player:
                    if self.world.has_component(entity, MeleeAttack):
                        melee_attack = self.world.component_for_entity(entity, MeleeAttack)

                        if melee_attack.collision:
                            conditional = pos.rect.colliderect(nested_pos.rect)
                        else:
                            conditional = (
                                pos.tile_pos.distance_to(nested_pos.tile_pos)
                                <= melee_attack.attack_range
                            )

                        if (
                            conditional
                            and pygame.time.get_ticks() - melee_attack.last_attacked
                            > melee_attack.attack_cooldown * 1000
                        ):
                            self.camera.start_shake(10)

                            nested_health.hp -= melee_attack.damage
                            nested_health.hp = max(nested_health.hp, 0)

                            melee_attack.last_attacked = pygame.time.get_ticks()

                    elif self.world.has_component(entity, ai_component.MeleeWeaponAttack):
                        melee_weapon_attack = self.world.component_for_entity(
                            entity, ai_component.MeleeWeaponAttack
                        )
                        inventory = self.world.component_for_entity(entity, Inventory)
                        equipped_item = self.world.component_for_entity(
                            inventory.inventory[inventory.equipped_item_idx], item_component.Item
                        )

                        if (
                            pos.tile_pos.distance_to(nested_pos.tile_pos)
                            <= melee_weapon_attack.attack_range
                            and pygame.time.get_ticks() - inventory.last_used
                            > equipped_item.cooldown * 1000
                        ):
                            equipped_item.use(inventory)

"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the NPC combat system, which handles non-player entities to entity
combat
"""
from __future__ import annotations

import math

from src import core, pygame
from src.entities.components import (ai_component, item_component,
                                     projectile_component)
from src.entities.components.component import Health, Inventory, Position
from src.entities.systems.system import System


class NPCCombatSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    def process(self):
        for entity, pos in self.world.get_component(Position):
            # Non-player to entity (including player) damage interaction
            # FOR NOW! SUPER INEFFICIENT
            for nested_entity, (nested_pos, nested_health) in self.world.get_components(Position, Health):
                if nested_entity == entity:
                    continue

                # RN TESTING ENTITY TO PLAYER ONLY
                if entity != self.player and nested_entity == self.player:
                    if self.world.has_component(entity, ai_component.MeleeAttack):
                        melee_attack = self.world.component_for_entity(entity, ai_component.MeleeAttack)

                        if melee_attack.collision:
                            conditional = pos.rect.colliderect(nested_pos.rect)
                        else:
                            conditional = pos.in_range(nested_pos.tile_pos, melee_attack.attack_range)

                        if (
                            conditional
                            and core.time.get_ticks() - melee_attack.last_attacked
                            > melee_attack.attack_cooldown * 1000
                        ):
                            self.camera.start_shake(10)

                            nested_health.hp -= melee_attack.damage
                            melee_attack.last_attacked = core.time.get_ticks()

                    elif self.world.has_component(entity, ai_component.MeleeWeaponAttack):
                        melee_weapon_attack = self.world.component_for_entity(entity, ai_component.MeleeWeaponAttack)
                        inventory = self.world.component_for_entity(entity, Inventory)
                        equipped_item = self.world.component_for_entity(
                            inventory.equipped_item, item_component.Item
                        )

                        if (
                            pos.in_range(nested_pos.tile_pos, melee_weapon_attack.attack_range)
                            and core.time.get_ticks() - inventory.last_used > equipped_item.cooldown * 1000
                        ):
                            equipped_item.use(inventory)

                    elif self.world.has_component(entity, ai_component.RangeAttack):
                        range_attack = self.world.component_for_entity(entity, ai_component.RangeAttack)

                        target = self.world.component_for_entity(range_attack.target, Position)
                        target_pos = target.pos
                        x_target, y_target = target_pos.x - pos.pos.x, pos.pos.y - target_pos.y
                        v = 20
                        g = 0.6

                        discrim = v**4 - g * (g * x_target**2 + 2 * y_target * v**2)
                        if discrim < 0:
                            continue
                        theta = (
                            math.atan((v**2 + range_attack.ideal_parabola * math.sqrt(discrim)) / (g * x_target))
                            if x_target != 0
                            else math.pi / 2
                        )

                        # a, b = (-g / 2) / (v**2 * math.cos(theta) ** 2), v * math.sin(theta) / (v * math.cos(theta))
                        # print(a * (768 + 16 - pos.pos.x) ** 2 + b * (768 + 16 - pos.pos.x))
                        # top_discrim = b**2 + 4 * a * rect_top
                        # bottom_discrim = b**2 + 4 * a * rect_bottom
                        # if top_discrim >= 0:
                        #     l_1 = (-b + math.sqrt(top_discrim)) / (2 * a)
                        #     l_2 = (-b - math.sqrt(top_discrim)) / (2 * a)
                        #     # a, b,  v * math.cos(theta), l_1,
                        #     print("Top", a, b,  v * math.cos(theta), l_1,l_2, rect_left < l_1 < rect_right or rect_left < l_2 < rect_right)
                        # if bottom_discrim >= 0:
                        #     l_1 = (-b + math.sqrt(bottom_discrim)) / (2 * a)
                        #     l_2 = (-b - math.sqrt(bottom_discrim)) / (2 * a)
                        #     print("Bottom",a, b,  v * math.cos(theta), l_1, l_2, rect_left < l_1 < rect_right or rect_left < l_2 < rect_right)
                        # if rect_bottom < a * ((rect_left + rect_right) / 2) ** 2 + b * ((rect_left + rect_right) / 2) < rect_top:
                        #     print("INTERSECTION")

                        # neighboring_tile_entities = []
                        # for x in range(int(pos.tile_pos.x), int(pos.tile_pos.x + target_tile_pos.x + 1)):
                        #     for y in range(int(pos.tile_pos.y - target_tile_pos.y), int(pos.tile_pos.y + 1)):
                        #         try:
                        #             tile_entity = self.tilemap.entity_tiles[(0, (x, y))]
                        #         except KeyError:
                        #             continue
                        #
                        #         neighboring_tile_entities.append(tile_entity)
                        # gg, _ = self.tilemap.get_unwalkable_rects(
                        #         neighboring_tile_entities
                        # )
                        # for rect in gg:
                        #     if rect.bottom < a * ((rect.left + rect.right) / 2) ** 2 + b * ((rect.left + rect.right) / 2) < rect.top:
                        #         print("!")

                        if core.time.get_ticks() - range_attack.last_attacked > range_attack.attack_cooldown * 1000:
                            self.world.create_entity(
                                projectile_component.Projectile(
                                    vel=v,
                                    angle=-theta if x_target > 0 else -math.pi - theta,
                                    damage=1,
                                    gravity=g,
                                    shot_by=entity,
                                ),
                                projectile_component.ProjectilePosition(
                                    pygame.Vector2(target_pos.x - x_target, target_pos.y + y_target)
                                ),
                                projectile_component.ProjectileGraphics(self.imgs["items/arrows_sprite"]),
                            )

                            range_attack.last_attacked = core.time.get_ticks()

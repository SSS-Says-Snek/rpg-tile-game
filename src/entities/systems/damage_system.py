from src import pygame, utils

from src.entities.systems.system import System
from src.entities import item_component
from src.entities.component import Position, Movement, MeleeAttack, Health, Inventory


class DamageSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

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
                            nested_health.hp -= max(melee_attack.damage, 0)

                            melee_attack.last_attacked = pygame.time.get_ticks()
            if entity == self.player:
                inventory = self.world.component_for_entity(self.player, Inventory)
                equipped_item = inventory.inventory[inventory.equipped_item_idx]

                interactable_entities = (entity_stuff for entity_stuff in self.world.get_components(Position, Health) if entity_stuff[0] != self.player)

                if equipped_item is not None:
                    item = self.world.component_for_entity(equipped_item, item_component.Item)
                    item_pos = self.world.component_for_entity(equipped_item, item_component.ItemPosition)
                    owner_pos = self.world.component_for_entity(item.owner, Position)

                    item_pos.pos.x = owner_pos.rect.right
                    item_pos.pos.y = owner_pos.pos.y - 16

                    used = item.used

                    if self.world.has_component(equipped_item, item_component.MeleeWeapon) and used:
                        melee_weapon, melee_weapon_graphics, slashing_sword = (self.world.component_for_entity(
                            equipped_item, i
                        ) for i in [item_component.MeleeWeapon, item_component.ItemGraphics, item_component.SlashingSword])

                        slashing_sword.angle -= 14
                        melee_weapon_graphics.current_img, slashing_sword.rect = utils.rot_pivot(
                            melee_weapon_graphics.original_img,
                            item_pos.pos, (0, 32), slashing_sword.angle
                        )
                        item_pos.pos.x = slashing_sword.rect.x
                        item_pos.pos.y = slashing_sword.rect.y + 32

                        for nested_entity, (nested_pos, nested_health) in interactable_entities:
                            if slashing_sword.rect.colliderect(nested_pos.rect) and not melee_weapon.hit:
                                print("OW")
                                melee_weapon.hit = True
                                nested_health.hp -= melee_weapon.attack_damage

                                if nested_health.hp <= 0:
                                    self.world.delete_entity(nested_entity)
                                    continue

                        if slashing_sword.angle <= -150:
                            slashing_sword.angle = 0
                            melee_weapon_graphics.current_img = melee_weapon_graphics.original_img
                            item_pos.pos.x = owner_pos.rect.right
                            item_pos.pos.y = owner_pos.rect.y

                            slashing_sword.x = item_pos.pos.x
                            slashing_sword.y = item_pos.pos.y

                            item.used = False
                            melee_weapon.hit = False

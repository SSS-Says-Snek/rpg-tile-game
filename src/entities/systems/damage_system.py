from src import pygame

from src.entities.systems.system import System
from src.entities.component import Position, Movement, MeleeAttack, Health


class DamageSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    def process(self, event_list):
        for entity, (pos, movement) in self.world.get_components(
            Position, Movement
        ):
            # FOR NOW! SUPER INEFFICIENT
            for nested_entity, (nested_pos, nested_health) in self.world.get_components(
                Position, Health
            ):
                if nested_entity == entity:
                    continue

                if self.world.has_component(entity, MeleeAttack):
                    melee_attack = self.world.component_for_entity(entity, MeleeAttack)

                    if (pos.tile_pos.distance_to(nested_pos.tile_pos) <= melee_attack.attack_range and
                        pygame.time.get_ticks() - melee_attack.last_attacked > melee_attack.attack_cooldown * 1000):
                        nested_health.hp -= max(melee_attack.damage, 0)

                        melee_attack.last_attacked = pygame.time.get_ticks()

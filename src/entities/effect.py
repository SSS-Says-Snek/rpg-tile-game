import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.states.level_state import LevelState

from src import pygame
from src.entities.component import Health, Position, Graphics


class EffectSystem:
    def __init__(self, level_state: "LevelState"):
        self.effect_dict = {}

        self.level_state = level_state
        self.particle_system = self.level_state.particle_system
        self.camera = self.level_state.camera

    def update(self) -> None:
        for entity, effect in self.effect_dict.copy().items():
            effect.update(entity)

            if not effect.on:
                del self.effect_dict[entity]

    def draw(self):
        for entity, effect in self.effect_dict.items():
            effect.draw(entity, self.camera)


# TODO: Add effect inheritance


class Effect:
    def __init__(self, level_state: "LevelState"):
        self.level_state = level_state
        self.world = self.level_state.ecs_world

        self.damage = 0
        self.duration = 0
        self.interval = 0

        self.time_created = pygame.time.get_ticks()
        self.last_applied = 0

    class Builder:
        def __init__(self, effect):
            self.effect = effect

        def damage(self, damage: float):
            self.effect.damage = damage
            return self

        def duration(self, duration: float, interval: float):
            self.effect.duration = duration
            self.effect.interval = interval
            return self

        def build(self):
            return self.effect

    @property
    def on(self):
        return not pygame.time.get_ticks() - self.time_created > self.duration * 1000

    def builder(self):
        return self.Builder(self)

    def update(self, entity: int):
        if pygame.time.get_ticks() - self.last_applied > self.interval * 1000:
            self.last_applied = pygame.time.get_ticks()

            health_component = self.world.component_for_entity(entity, Health)
            health_component.hp -= self.damage


class BurnEffect(Effect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, entity, _):
        if random.random() < 0.3:
            pos = self.level_state.ecs_world.component_for_entity(entity, Position).pos
            size = self.level_state.ecs_world.component_for_entity(entity, Graphics).size
            self.level_state.particle_system.create_fire_particle(
                pos, offset=(random.randint(0, size[0]), random.randint(0, size[1]))
            )


"""            

class BurnEffect:
    def __init__(
        self,
        level_state: "LevelState",
        burn_damage: int,
        burn_duration: float,
        burn_interval: float,
    ):
        self.level_state = level_state

        self.burn_damage = burn_damage
        self.burn_duration = burn_duration
        self.burn_interval = burn_interval

        self.time_created = pygame.time.get_ticks()
        self.last_burnt = 0

    def update(self, entity: int):
        health_component = self.level_state.ecs_world.component_for_entity(entity, Health)

        if pygame.time.get_ticks() - self.last_burnt > self.burn_interval * 1000:
            health_component.hp -= 10
            self.last_burnt = pygame.time.get_ticks()

        if random.random() < 0.3:
            pos = self.level_state.ecs_world.component_for_entity(entity, Position).pos
            size = self.level_state.ecs_world.component_for_entity(entity, Graphics).size
            self.level_state.particle_system.create_fire_particle(
                pos, offset=(random.randint(0, size[0]), random.randint(0, size[1]))
            )

    @property
    def on(self):
        return not pygame.time.get_ticks() - self.time_created > self.burn_duration * 1000
"""

"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from __future__ import annotations

import random
from typing import TYPE_CHECKING

from src.display.camera import Camera
from src.types import Entity

if TYPE_CHECKING:
    from src.states.level_state import LevelState

from src import core, utils
from src.entities.components.component import Graphics, Health, Position


class EffectManager:
    def __init__(self, level_state: LevelState):
        self.effect_dict: dict[int, Effect] = {}

        self.level = level_state
        self.particle_system = self.level.particle_manager
        self.camera = self.level.camera

    def add_effect(self, entity: Entity, effect: Effect):
        self.effect_dict[entity] = effect

    def update(self):
        for entity, effect in self.effect_dict.copy().items():
            effect.update(entity)

            if not effect.on:
                del self.effect_dict[entity]

    def draw(self):
        for entity, effect in self.effect_dict.items():
            effect.draw(entity, self.camera)


class Effect:
    def __init__(self, level_state: LevelState):
        self.level = level_state
        self.world = self.level.world

        self.heal_power = 0
        self.damage = 0
        self.duration = 0
        self.interval = 0

        self.apply_effect = utils.Task(0)
        self.time_created = core.time.get_ticks()

        self.time_waiting = 0

    class Builder:
        def __init__(self, effect):
            self.effect = effect

        def heal(self, heal_power: float):
            self.effect.heal_power = heal_power
            return self

        def damage(self, damage: float):
            self.effect.damage = damage
            return self

        def duration(self, duration: float, interval: float):
            self.effect.duration = duration
            self.effect.interval = interval
            self.effect.apply_effect.period = interval * 1000

            return self

        def build(self):
            return self.effect

    @property
    def on(self):
        return not core.time.get_ticks() - self.time_created > self.duration * 1000

    def builder(self):
        return self.Builder(self)

    def update(self, entity: Entity):
        """
        Updates effect

        Args:
            entity: Entity ID of effect "owner"
        """

        if self.time_waiting == 0:
            self.time_waiting = core.time.get_ticks()
        if self.apply_effect.update() and core.time.get_ticks() - self.time_waiting > self.interval:
            health_component = self.world.component_for_entity(entity, Health)
            health_component.hp += self.heal_power
            health_component.hp -= self.damage

    def draw(self, entity: Entity, camera: Camera):
        """Draws some stuff for the effect"""

        pass


class BurnEffect(Effect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, entity: Entity, _):
        if random.random() < 0.7:
            pos = self.level.world.component_for_entity(entity, Position).pos
            size = self.level.world.component_for_entity(entity, Graphics).size
            self.level.particle_manager.create_fire_particle(
                pos, offset=(random.randint(0, size[0]), random.randint(0, size[1]))
            )


class RegenEffect(Effect):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def draw(self, entity: Entity, _):  # No camera >:(
        if random.random() < 0.12:
            pos = self.level.world.component_for_entity(entity, Position).pos
            size = self.level.world.component_for_entity(entity, Graphics).size
            self.level.particle_manager.create_regen_particle(
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

        self.time_created = core.time.get_ticks()
        self.last_burnt = 0

    def update(self, entity: int):
        health_component = self.level_state.ecs_world.component_for_entity(entity, Health)

        if core.time.get_ticks() - self.last_burnt > self.burn_interval * 1000:
            health_component.hp -= 10
            self.last_burnt = core.time.get_ticks()

        if random.random() < 0.3:
            pos = self.level_state.ecs_world.component_for_entity(entity, Position).pos
            size = self.level_state.ecs_world.component_for_entity(entity, Graphics).size
            self.level_state.particle_system.create_fire_particle(
                pos, offset=(random.randint(0, size[0]), random.randint(0, size[1]))
            )

    @property
    def on(self):
        return not core.time.get_ticks() - self.time_created > self.burn_duration * 1000
"""

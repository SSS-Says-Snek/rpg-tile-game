"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This system performs actions on entities depending on whether they've
been hit or not.
"""

from __future__ import annotations

import random

from src.display.particle import Particle
from src.entities.components.component import Position, Health
from src.entities.systems import System
from src.types import Dts, Events


class HitSystem(System):
    def process(self, event_list: Events, dts: Dts):
        for entity, (pos, health) in self.world.get_components(Position, Health):
            # Lost HP
            if health.hp - health.prev_hp < 0:
                if health.hp == 0:
                    self.particle_system.create_hit_particles(30, pos, self.settings["particles/death"])
                else:
                    self.particle_system.add(
                        Particle()
                        .builder()
                        .at(pos=pos.pos, angle=random.gauss(180, 180))
                        .color(color=random.choice([(255, 0, 0)]))
                        .gravity(gravity_acc=0.35, gravity_y_vel=-3.5)
                        .lifespan(frames=40)
                        .angular_speed(speed=random.gauss(0.9, 0.8))
                        .size(size=4)
                        .effect_fade(start_fade_frac=0.5)
                        .build(),
                        num_particles=25
                    )
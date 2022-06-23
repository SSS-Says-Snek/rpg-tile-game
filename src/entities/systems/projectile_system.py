"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the projectile system, used to move and handle projectiles
"""

import math

from src import utils

from src.entities.systems.system import System
from src.entities import projectile_component


class ProjectileSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    def process(self, event_list):
        for entity, (projectile, projectile_pos, projectile_graphics) in self.world.get_components(
            projectile_component.Projectile, projectile_component.ProjectilePosition, projectile_component.ProjectileGraphics
        ):
            # HEAVILY BUGGY IMPLEMENTATION: WILL WORK ON IT MORE

            projectile_pos.pos.x += math.cos(projectile.initial_angle) * projectile.vel.x

            projectile.vel.y += projectile.gravity
            projectile_pos.pos.y += projectile.vel.y

            projectile_graphics.current_img, _ = utils.rot_center(
                projectile_graphics.original_img, math.degrees(math.atan2(projectile.vel.y, projectile.vel.x)) * projectile.vel_dir,
                *projectile_pos.pos
            )


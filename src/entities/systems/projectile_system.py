"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the projectile system, used to move and handle projectiles
"""

import math

from src import pygame, utils

from src.entities.systems.system import System
from src.entities import projectile_component, component


class ProjectileSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    def process(self, event_list, dt) -> None:
        # HEAVILY BUGGY IMPLEMENTATION: WILL WORK ON IT MORE

        for entity, (
            projectile,
            projectile_pos,
            projectile_graphics,
        ) in self.world.get_components(
            projectile_component.Projectile,
            projectile_component.ProjectilePosition,
            projectile_component.ProjectileGraphics,
        ):
            # Update position
            projectile_pos.pos.x += (
                math.cos(projectile.initial_angle) * projectile.vel.x
            )

            projectile.vel.y += projectile.gravity
            projectile_pos.pos.y += projectile.vel.y
            projectile_pos.rect = pygame.Rect(
                *projectile_pos.pos, *projectile_graphics.size
            )
            projectile_pos.tile_pos = utils.pixel_to_tile(projectile_pos.pos)

            # Update image with angle
            projectile_graphics.current_img, _ = utils.rot_center(
                projectile_graphics.original_img,
                math.degrees(math.atan2(projectile.vel.y, projectile.vel.x))
                * projectile.vel_dir,
                *projectile_pos.pos
            )

            # Handle projectile to entity collision
            for nested_entity, (nested_pos, nested_health) in self.world.get_components(
                component.Position, component.Health
            ):
                if projectile.shot_by == nested_entity:
                    continue

                if nested_pos.rect.colliderect(projectile_pos.rect):
                    nested_health.hp = max(0, nested_health.hp - projectile.damage)

                    if nested_health.hp == 0:
                        colors = self.level_state.settings["particle_colors"]["death"]
                        self.particle_system.create_hit_particles(
                            30, nested_pos, colors
                        )
                    else:
                        self.particle_system.create_hit_particles(
                            15, nested_pos, [(255, 0, 0)]
                        )

                    self.world.delete_entity(entity)
                    break

            # Delete in out-of-bounds area / collision
            if projectile_pos.pos.y > self.tilemap.height:
                self.world.delete_entity(entity)

            neighboring_tile_rects = self.tilemap.get_unwalkable_rects(
                utils.get_neighboring_tile_entities(
                    self.tilemap, 1, projectile_pos
                )
            )

            for neighboring_tile_rect in neighboring_tile_rects:
                if neighboring_tile_rect.colliderect(projectile_pos.rect):
                    self.world.delete_entity(entity)
                    break

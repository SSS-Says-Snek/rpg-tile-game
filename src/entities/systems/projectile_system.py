"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the projectile system, used to move and handle projectiles
"""

from __future__ import annotations

import math
import random

from src import pygame, utils
from src.display.particle import RoundParticle
from src.entities.components import component, projectile_component
from src.entities.systems.system import System
from src.types import Dts, Events


class ProjectileSystem(System):
    def process(self, event_list: Events, dts: Dts):
        # HEAVILY BUGGY IMPLEMENTATION: WILL WORK ON IT MORE

        for entity, (projectile, projectile_pos, projectile_graphics,) in self.world.get_components(
            projectile_component.Projectile,
            projectile_component.ProjectilePosition,
            projectile_component.ProjectileGraphics,
        ):
            # Update t
            projectile.t += 1

            # Update position
            rel_x, rel_y = projectile.rel_x(projectile.t), projectile.rel_y(projectile.t)
            projectile_pos.pos.x = projectile_pos.spawn_pos.x + rel_x
            projectile_pos.pos.y = projectile_pos.spawn_pos.y + rel_y

            projectile_pos.rect = pygame.Rect(*projectile_pos.pos, *projectile_graphics.size)
            projectile_pos.tile_pos = utils.pixel_to_tile(projectile_pos.pos)

            projectile_rotate_angle = 180 + math.degrees(
                math.atan2(
                    rel_y - projectile.rel_y(projectile.t - 1),
                    rel_x - projectile.rel_x(projectile.t - 1),
                )
            )

            # Update image with angle
            projectile_graphics.current_img, _ = utils.rot_center(
                projectile_graphics.original_img,
                180 - projectile_rotate_angle
                if projectile.vel_dir == 1
                else projectile_rotate_angle * projectile.vel_dir,
                *projectile_pos.pos,
            )

            if random.random() < 0.2:
                for i in range(-1, 2):
                    self.particle_system.add(
                        RoundParticle()
                        .builder()
                        .size(2)
                        .color((255, 255, 255))
                        .at(
                            pygame.Vector2(projectile_pos.rect.bottomright)
                            if projectile_rotate_angle > 0
                            else projectile_pos.pos,
                            angle=(90 - i * 5),
                        )
                        .angular_speed(1)
                        .lifespan(20)
                        .effect_fade(0.6)
                        .build()
                    )

            # Handle projectile to entity collision
            for nested_entity, (nested_pos, nested_health) in self.world.get_components(
                component.Position, component.Health
            ):
                if projectile.shot_by == nested_entity:
                    continue

                if nested_pos.rect.colliderect(projectile_pos.rect):
                    nested_health.hp -= projectile.damage
                    self.world.delete_entity(entity)
                    break

            # Delete in out-of-bounds area / collision
            if projectile_pos.pos.y > self.tilemap.height:
                self.world.delete_entity(entity)

            neighboring_tile_rects, _ = self.tilemap.get_unwalkable_rects(
                self.tilemap.get_neighboring_tile_entities(2, projectile_pos)
            )
            for neighboring_tile_rect in neighboring_tile_rects:
                if neighboring_tile_rect.colliderect(projectile_pos.rect):
                    self.world.delete_entity(entity)
                    break

        """if random.random() < 0.01:
            for _ in range(1):
                player_pos = self.world.component_for_entity(self.player, Position)
                x_target, y_target = random.choice((random.randint(-1000, -700), random.randint(700, 1000))), 100
                if x_target == 0:
                    x_target = 1
                v = 10
                g = 0.07
                theta = math.atan(
                    (v**2 + math.sqrt(v**4 - g * (g * x_target**2 + 2 * y_target * v**2))) / (g * x_target)
                )
                self.world.create_entity(
                    projectile_component.Projectile(
                        vel=v, angle=-theta if x_target > 0 else -math.pi - theta, damage=10, gravity=g
                    ),
                    projectile_component.ProjectilePosition(
                        pygame.Vector2(player_pos.pos.x - x_target, player_pos.pos.y + y_target)
                    ),
                    projectile_component.ProjectileGraphics(self.imgs["items/arrows_sprite"]),
                )"""

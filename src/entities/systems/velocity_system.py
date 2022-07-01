"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the velocity system, used to "move" entities around
"""

import math

from src import pygame, utils

from src.entities import ai_component, component
from src.entities.component import Flags, Position, Movement, Graphics
from src.entities.systems.system import System


class VelocitySystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

        self.settings = self.level_state.settings
        self.player_settings = self.settings["mobs"]["player"]

    def handle_player_keys(self, event_list):
        keys = pygame.key.get_pressed()
        player_movement = self.world.component_for_entity(self.player, Movement)
        player_pos = self.world.component_for_entity(self.player, Position)
        player_graphics = self.world.component_for_entity(self.player, Graphics)

        player_movement.vx, player_movement.vy = 0, 0
        player_movement.vel.x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_movement.vel.x = -player_movement.speed
            player_pos.direction = -1
            player_graphics.sprites_state = "left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_movement.vel.x = player_movement.speed
            player_pos.direction = 1
            player_graphics.sprites_state = "right"

        for event in event_list:
            if event.type == pygame.KEYDOWN:
                if (
                    event.key == pygame.K_SPACE or event.key == pygame.K_w
                ) and player_pos.on_ground:
                    player_pos.on_ground = False
                    player_movement.vel.y = self.player_settings["jump_vel"]

    def process(self, event_list, dts) -> None:
        self.handle_player_keys(event_list)

        for entity, (flags, pos, movement) in self.world.get_components(Flags, Position, Movement):
            if flags.rotatable:
                movement.rot = (
                    self.world.component_for_entity(self.player, Position).pos - pos.pos
                ).angle_to(pygame.Vector2(1, 0))

            # AI: Follow entity closely
            if self.world.has_component(entity, ai_component.FollowsEntityClose):
                follows_entity_close = self.world.component_for_entity(
                    entity, ai_component.FollowsEntityClose
                )
                entity_followed = follows_entity_close.entity_followed
                entity_followed_pos = self.world.component_for_entity(
                    entity_followed, component.Position
                )

                # Follow entity if and ONLY if:
                # 1. The entity's tile y coordinate is the same as the enemy's
                # 2. The distance from entity to enemy is less than 10, in tile space
                if (
                    entity_followed_pos.tile_pos.y == pos.tile_pos.y
                    and pos.tile_pos.distance_to(entity_followed_pos.tile_pos) < follows_entity_close.follow_range
                ):
                    if entity_followed_pos.pos.x > pos.pos.x:
                        movement.vel.x = movement.speed
                        pos.direction = 1
                    elif entity_followed_pos.pos.x < pos.pos.x:
                        movement.vel.x = -movement.speed
                        pos.direction = -1

            if flags.mob_type == "walker_enemy":
                movement.vel.x = movement.speed * movement.mob_specifics["movement_direction"]

                mob_tile = utils.pixel_to_tile(pos.pos)
                tile_next_beneath = (
                    mob_tile.x + math.copysign(1, movement.vel.x),
                    mob_tile.y + 1,
                )
                tile_next = (tile_next_beneath[0], mob_tile.y)

                if self.tilemap.tiles.get((0, tile_next)) or not self.tilemap.tiles.get(
                    (0, tile_next_beneath)
                ):
                    movement.mob_specifics["movement_direction"] *= -1

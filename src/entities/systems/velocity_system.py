"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the velocity system, used to "move" entities around
"""

from __future__ import annotations

import math

from src import pygame, utils
from src.entities.components import ai_component, component
from src.entities.components.component import Flags, Movement, Position
from src.entities.systems.system import System
from src.types import Dts, Events


class VelocitySystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

        self.settings = self.level_state.settings
        self.player_settings = self.settings["mobs/player"]

    def about_to_fall(self, pos: Position):
        return self.tilemap.get_tile(pos.tile_pos.x + math.copysign(1, pos.direction), pos.tile_pos.y + 1) is None

    def handle_player_keys(self, event_list: Events):
        keys = pygame.key.get_pressed()
        player_movement = self.world.component_for_entity(self.player, Movement)
        player_pos = self.world.component_for_entity(self.player, Position)

        player_movement.vel.x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_movement.vel.x = -player_movement.speed
            player_pos.direction = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_movement.vel.x = player_movement.speed
            player_pos.direction = 1

        for event in event_list:
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_SPACE or event.key == pygame.K_w) and player_pos.on_ground:
                    player_pos.on_ground = False
                    player_movement.vel.y = self.player_settings["jump_vel"]

                    # TODO: Add jump particles

        # if player_pos.pos.y > 960:
        #     print("A")

    def process(self, event_list: Events, dts: Dts):
        self.handle_player_keys(event_list)

        for entity, (flags, pos, movement) in self.world.get_components(Flags, Position, Movement):
            if entity == self.player:
                continue

            # AI: Follow entity closely
            if self.world.has_component(entity, ai_component.FollowsEntityClose):
                follows_entity_close = self.world.component_for_entity(entity, ai_component.FollowsEntityClose)
                entity_state = self.world.component_for_entity(entity, ai_component.EntityState)
                entity_followed = follows_entity_close.entity_followed
                entity_followed_pos = self.world.component_for_entity(entity_followed, component.Position)

                if entity_state.state == entity_state.Patrol:
                    # Patrol if and ONLY if:
                    # 1. The entity following is out of range of it OR
                    # 2. The entity following is on a different y coordinate than itself

                    entity_state.state.patrol(self.tilemap, pos, movement)

                    if (
                        pos.in_range(entity_followed_pos.tile_pos, follows_entity_close.follow_range)
                        and entity_followed_pos.tile_pos.y == pos.tile_pos.y
                    ):
                        print(f"Entity {entity} switched to follow")
                        entity_state.state = entity_state.Follow

                elif entity_state.state == entity_state.Follow:
                    # Follow entity if and ONLY if:
                    # 1. The entity's tile y coordinate is the same as itself's AND
                    # 2. The distance from entity to itself is less than 10, in tile space

                    pos.direction = math.copysign(1, entity_followed_pos.pos.x - pos.pos.x)
                    movement.vel.x = movement.speed * pos.direction

                    if (
                        not pos.in_range(entity_followed_pos.tile_pos, follows_entity_close.follow_range)
                        or entity_followed_pos.tile_pos.y != pos.tile_pos.y
                    ):
                        print(f"Entity {entity} switched to patrol")
                        entity_state.state = entity_state.Patrol
                    elif self.about_to_fall(pos):
                        print(f"Entity {entity} switched to flee")
                        entity_state.state = entity_state.Flee
                        entity_state.state.flee_start_time = pygame.time.get_ticks()
                        pos.direction *= -1

                elif entity_state.state == entity_state.Flee:
                    # Flee if and ONLY if:
                    # 1. Its chances of falling of a platform is very high

                    movement.vel.x = entity_state.state.flee_speed * pos.direction

                    if (
                        pygame.time.get_ticks() - entity_state.state.flee_start_time
                        > entity_state.state.flee_time * 1000
                    ):
                        entity_state.state = entity_state.Patrol
                    if self.about_to_fall(pos):
                        # Just go back and forth until timer expires
                        pos.direction *= -1

            # TODO: ABANDON flags.mob_type
            if flags.mob_type == "walker_enemy":
                movement.vel.x = movement.speed * pos.direction

                mob_tile = utils.pixel_to_tile(pos.pos)
                tile_next_beneath = self.tilemap.get_tile(
                    mob_tile.x + math.copysign(1, movement.vel.x),
                    mob_tile.y + 1,
                )
                tile_next = self.tilemap.get_tile(mob_tile.x + math.copysign(1, movement.vel.x), mob_tile.y)

                if tile_next or not tile_next_beneath:
                    if tile_next is not None and not tile_next.get("unwalkable"):
                        continue
                    pos.direction *= -1

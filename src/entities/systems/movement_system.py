"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the velocity system, used to "move" entities around
"""

from __future__ import annotations

import math

from src import core, pygame, utils
from src.display.particle import RoundParticle
from src.entities.components import ai_component, component
from src.entities.components.component import Movement, Position
from src.entities.systems.system import System
from src.types import Events


class MovementSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

        self.player_settings = self.settings["mobs/player"]

    def about_to_fall(self, pos: Position):
        return self.tilemap.get_tile(pos.tile_pos.x + math.copysign(1, pos.direction), pos.tile_pos.y + 1) is None

    def handle_player_keys(self, event_list: Events):
        keys = pygame.key.get_pressed()
        player_movement = self.component_for_player(Movement)
        player_pos = self.component_for_player(Position)

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

                    # Jump effects
                    for angle in range(-1, 1 + 1):
                        self.particle_manager.add(
                            RoundParticle()
                            .builder()
                            .at(pos=pygame.Vector2(player_pos.rect.midbottom), angle=angle * 30 + 90)
                            .angular_speed(speed=1.3)
                            .size(size=2)
                            .color(color=(255, 255, 255))
                            .lifespan(frames=40)
                            .effect_fade(start_fade_frac=0.7)
                            .effect_angular_slowdown(slowdown_factor=0.95, start_slowdown_frac=0.3)
                            .build()
                        )

    def process(self):
        self.handle_player_keys(core.event.get())

        for entity, (pos, movement) in self.world.get_components(Position, Movement):
            # Apply gravity
            # Cap vel so it doesn't just fly straight through the tiles
            movement.vel.y += movement.gravity_acc.y / 2 * core.dt.dt
            movement.vel.y = min(movement.vel.y, 170)

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
                        # print(f"Entity {entity} switched to follow")
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
                        # print(f"Entity {entity} switched to patrol")
                        entity_state.state = entity_state.Patrol
                    elif self.about_to_fall(pos):
                        # print(f"Entity {entity} switched to flee")
                        entity_state.state = entity_state.Flee
                        entity_state.state.flee_start_time = core.time.get_ticks()
                        pos.direction *= -1

                elif entity_state.state == entity_state.Flee:
                    # Flee if and ONLY if:
                    # 1. Its chances of falling of a platform is very high

                    movement.vel.x = entity_state.state.flee_speed * pos.direction

                    if (
                        core.time.get_ticks() - entity_state.state.flee_start_time
                        > entity_state.state.flee_time * 1000
                    ):
                        entity_state.state = entity_state.Patrol
                    if self.about_to_fall(pos):
                        # Just go back and forth until timer expires
                        pos.direction *= -1

            if self.world.has_component(entity, ai_component.Patroller):
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

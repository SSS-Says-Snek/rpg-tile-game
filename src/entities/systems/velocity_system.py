import math

from src import pygame, utils

from src.entities.component import Flags, Position, Movement
from src.entities.systems.system import System

class VelocitySystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    def handle_player_keys(self, event_list):
        keys = pygame.key.get_pressed()
        player_movement = self.world.component_for_entity(
            self.player, Movement
        )
        player_pos = self.world.component_for_entity(
            self.player, Position
        )

        player_movement.vx, player_movement.vy = 0, 0
        player_movement.vel.x = 0

        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            player_movement.vel.x = -player_movement.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            player_movement.vel.x = player_movement.speed

        for event in event_list:
            if event.type == pygame.KEYDOWN:
                if (event.key == pygame.K_SPACE or event.key == pygame.K_w) and player_pos.on_ground:
                    player_pos.on_ground = False
                    player_movement.vel.y = -17

    def process(self, event_list):
        self.handle_player_keys(event_list)

        for entity, (flags, pos, movement) in self.world.get_components(
            Flags, Position, Movement
        ):
            if flags.rotatable:
                movement.rot = (
                        self.world.component_for_entity(self.player, Position).pos - pos.pos
                ).angle_to(pygame.Vector2(1, 0))

            if flags.mob_type == "walker_enemy":
                movement.vel.x = movement.speed * movement.mob_specifics["movement_direction"]

                mob_tile = utils.pixel_to_tile(pos.pos)
                tile_next_beneath = (mob_tile.x + math.copysign(1, movement.vel.x), mob_tile.y + 1)
                tile_next = (tile_next_beneath[0], mob_tile.y)

                if self.level_state.tilemap.tiles.get((0, tile_next)) or not self.level_state.tilemap.tiles.get((0, tile_next_beneath)):
                    movement.mob_specifics["movement_direction"] *= -1


                """if flags.mob_type == "melee_enemy":
                    movement.acc = pygame.Vector2(1, 0).rotate(-movement.rot)
                    movement.acc.scale_to_length(movement.speed)
                    movement.acc.x -= movement.vx
                    movement.acc.y -= movement.vy

                    movement.vx += movement.acc.x * self.level_state.game_class.dt
                    movement.vy += movement.acc.y * self.level_state.game_class.dt

                    print(movement.vx, movement.vy)"""

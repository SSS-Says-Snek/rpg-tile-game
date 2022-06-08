from src import pygame

from src.entities.component import Flags, Position, Movement
from src.entities.systems.system import System

class VelocitySystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    def handle_player_keys(self):
        keys = pygame.key.get_pressed()
        player_vel = self.world.component_for_entity(
            self.player, Movement
        )

        player_vel.vx, player_vel.vy = 0, 0

        if keys[pygame.K_UP]:
            player_vel.vy = -player_vel.speed
        if keys[pygame.K_DOWN]:
            player_vel.vy = player_vel.speed
        if keys[pygame.K_LEFT]:
            player_vel.vx = -player_vel.speed
        if keys[pygame.K_RIGHT]:
            player_vel.vx = player_vel.speed

        if player_vel.vx and player_vel.vy:
            # Adjust diagonal speed to match normal
            player_vel.vx *= 0.707
            player_vel.vy *= 0.707

    def process(self, event_list):
        self.handle_player_keys()

        for entity, (flags, pos, movement) in self.world.get_components(
            Flags, Position, Movement
        ):
            if flags.rotatable:
                movement.rot = (
                        self.world.component_for_entity(self.player, Position).pos - pos.pos
                ).angle_to(pygame.Vector2(1, 0))

                if flags.mob_type == "melee_enemy":
                    movement.acc = pygame.Vector2(1, 0).rotate(-movement.rot)
                    movement.acc.scale_to_length(movement.speed)
                    movement.acc.x -= movement.vx
                    movement.acc.y -= movement.vy

                    movement.vx += movement.acc.x * self.level_state.game_class.dt
                    movement.vy += movement.acc.y * self.level_state.game_class.dt

                    print(movement.vx, movement.vy)

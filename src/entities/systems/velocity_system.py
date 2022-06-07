from src import pygame

from src.entities.component import Movement
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



import esper

from src import pygame, common
from src.tilemap import TileMap
from src.display.camera import Camera

from src.entities.component import Collidable, Position, Velocity, Graphics

from src.entities.systems.collision_system import CollisionSystem
from src.entities.systems.graphics_system import GraphicsSystem
from src.entities.systems.tile_interaction_system import TileInteractionSystem

from .state import State

class LevelState(State):
    PLAYER_SPEED = 175

    def __init__(self, game_class):
        super().__init__(game_class)

        self.camera = Camera(common.WIDTH, common.HEIGHT)
        self.ui = self.game_class.ui
        self.ui.camera = self.camera

        self.ecs_world = esper.World()
        self.tilemap = TileMap(common.MAP_DIR / "placeholder_map.tmx", self.ecs_world)
        self.map_surface = self.tilemap.make_map()

        # self.entities includes player
        self.temp_sprite = pygame.Surface((16, 16))
        self.temp_sprite.fill((255, 0, 0))

        self.player = self.ecs_world.create_entity(
            Collidable(),
            Position([200, 400]), Velocity(), Graphics(self.temp_sprite)
        )

        # self.ecs_world.add_processor(MovementSystem(self), priority=2)
        self.ecs_world.add_processor(CollisionSystem(self), priority=3)
        self.ecs_world.add_processor(TileInteractionSystem(self), priority=2)
        self.ecs_world.add_processor(GraphicsSystem(self), priority=1)

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.map_surface, self.camera.apply((0, 0)))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.change_state("level_state.TestState")

    def update(self):
        keys = pygame.key.get_pressed()
        player_vel = self.ecs_world.component_for_entity(self.player, Velocity)

        player_vel.vx, player_vel.vy = 0, 0

        if keys[pygame.K_UP]:
            player_vel.vy = -self.PLAYER_SPEED
        if keys[pygame.K_DOWN]:
            player_vel.vy = self.PLAYER_SPEED
        if keys[pygame.K_LEFT]:
            player_vel.vx = -self.PLAYER_SPEED
        if keys[pygame.K_RIGHT]:
            player_vel.vx = self.PLAYER_SPEED

        if player_vel.vx and player_vel.vy:
            # Adjust diagonal speed to match normal
            player_vel.vx *= 0.707
            player_vel.vy *= 0.707

        self.ecs_world.process(self.game_class.events)


class TestState(State):
    def draw(self):
        self.screen.fill((128, 128, 128))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.change_state("level_state.LevelState")

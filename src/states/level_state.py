import esper

from src import pygame, common
from src.tilemap import TileMap
from src.display.camera import Camera

from src.entities.component import Flags, Position, Movement, Graphics

from src.entities.systems.collision_system import CollisionSystem
from src.entities.systems.graphics_system import GraphicsSystem
from src.entities.systems.tile_interaction_system import TileInteractionSystem
from src.entities.systems.velocity_system import VelocitySystem

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

        self.player = None
        self.load_spawns()

        # self.ecs_world.add_processor(MovementSystem(self), priority=2)
        self.ecs_world.add_processor(VelocitySystem(self), priority=4)
        self.ecs_world.add_processor(CollisionSystem(self), priority=3)
        self.ecs_world.add_processor(TileInteractionSystem(self), priority=2)
        self.ecs_world.add_processor(GraphicsSystem(self), priority=1)

    def load_spawns(self):
        mob_sprite = pygame.transform.scale(
            pygame.image.load(common.ASSETS_DIR / "imgs" / "placeholder_mob.png").convert(),
            (16, 16)
        )

        for obj in self.tilemap.tilemap.objects:
            if obj.name == "player_spawn":
                self.player = self.ecs_world.create_entity(
                    Flags(collidable=True),
                    Position(pygame.Vector2(obj.x, obj.y)), Movement(self.PLAYER_SPEED),
                    Graphics(self.temp_sprite)
                )
            if obj.name == "melee_spawn":
                self.temp_sprite = pygame.Surface((16, 16))
                self.temp_sprite.fill((0, 0, 255))

                self.ecs_world.create_entity(
                    Flags(collidable=True, rotatable=True),
                    Position(pygame.Vector2(obj.x, obj.y)), Movement(100),
                    Graphics(mob_sprite)
                )

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.screen.blit(self.map_surface, self.camera.apply((0, 0)))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.change_state("level_state.TestState")

    def update(self):
        self.ecs_world.process(self.game_class.events)


class TestState(State):
    def draw(self):
        self.screen.fill((128, 128, 128))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.change_state("level_state.LevelState")

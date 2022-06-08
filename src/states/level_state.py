import esper

from src import pygame, common
from src.tilemap import TileMap

from src.display.camera import Camera
from src.display.widgets.health_bar import HealthBar

from src.entities.component import Flags, Position, Movement, Graphics, Health, MeleeAttack

from src.entities.systems.collision_system import CollisionSystem
from src.entities.systems.graphics_system import GraphicsSystem
from src.entities.systems.tile_interaction_system import TileInteractionSystem
from src.entities.systems.velocity_system import VelocitySystem
from src.entities.systems.damage_system import DamageSystem

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
        self.ecs_world.add_processor(VelocitySystem(self), priority=5)
        self.ecs_world.add_processor(CollisionSystem(self), priority=4)
        self.ecs_world.add_processor(TileInteractionSystem(self), priority=3)
        self.ecs_world.add_processor(DamageSystem(self), priority=2)
        self.ecs_world.add_processor(GraphicsSystem(self), priority=1)

    def load_spawns(self):
        mob_sprite = pygame.transform.scale(
            pygame.image.load(common.ASSETS_DIR / "imgs" / "placeholder_mob.png").convert_alpha(),
            (16, 16)
        )

        for obj in self.tilemap.tilemap.objects:
            if obj.name == "player_spawn":
                health_component = Health(100, 100)
                self.player = self.ecs_world.create_entity(
                    Flags(collidable=True, mob_type="player", damageable=True),
                    Position(pygame.Vector2(obj.x, obj.y)), Movement(self.PLAYER_SPEED),
                    health_component,
                    Graphics(self.temp_sprite)
                )

                self.ui.add_widget(HealthBar((10, 20), 150, 10, health_component))

            if obj.name == "melee_spawn":
                self.temp_sprite = pygame.Surface((16, 16), pygame.SRCALPHA).convert_alpha()
                pygame.draw.rect(self.temp_sprite, (0, 0, 255), pygame.Rect(0, 0, 16, 16))

                self.ecs_world.create_entity(
                    Flags(collidable=True, rotatable=True, mob_type="melee_enemy", damageable=True),
                    Position(pygame.Vector2(obj.x, obj.y)), Movement(150),
                    Health(50, 50), MeleeAttack(1, 1.3, 15),
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

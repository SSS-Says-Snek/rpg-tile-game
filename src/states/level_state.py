"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the level state, which is the state where the main game happens
"""

# ECS system
import esper

# Important modules
from src import pygame, common
from src.tilemap import TileMap

# Display modules
from src.display import particle
from src.display.camera import Camera
from src.display.widgets.health_bar import PlayerHealthBar, MobHealthBar
from src.display.widgets.inventory import Hotbar

# Components
from src.entities import item_component
from src.entities.component import (
    Flags, Position, Movement, Graphics,
    Health, MeleeAttack, Inventory
)

# Systems
from src.entities.systems.collision_system import CollisionSystem
from src.entities.systems.graphics_system import GraphicsSystem
# from src.entities.systems.tile_interaction_system import TileInteractionSystem
from src.entities.systems.velocity_system import VelocitySystem
from src.entities.systems.item_weapon_system import ItemWeaponSystem
from src.entities.systems.projectile_system import ProjectileSystem
from src.entities.systems.input_system import InputSystem

# State (for inheritance)
from .state import State

class LevelState(State):
    PLAYER_SPEED = 300

    def __init__(self, game_class):
        super().__init__(game_class)

        # esper and tilemap stuff
        self.ecs_world = esper.World()
        self.tilemap = TileMap(common.MAP_DIR / "placeholder_platformer.tmx", self.ecs_world)
        self.map_surface = self.tilemap.make_map()

        # UI stuff
        self.camera = Camera(common.WIDTH, common.HEIGHT)
        self.ui = self.game_class.ui
        self.ui.camera = self.camera
        self.ui.world = self.ecs_world

        # Particle stuff
        self.particle_system = particle.ParticleSystem(self.camera)

        self.temp_sprite = pygame.Surface((32, 32))
        self.temp_sprite.fill((255, 0, 0))

        # Other stuff
        self.settings = self.game_class.settings

        self.player = None
        self.load_spawns()

        self.debug = False

        # Add ECS systems
        self.ecs_world.add_processor(InputSystem(self), priority=6)
        self.ecs_world.add_processor(VelocitySystem(self), priority=5)
        self.ecs_world.add_processor(CollisionSystem(self), priority=4)
        # self.ecs_world.add_processor(TileInteractionSystem(self), priority=3)
        self.ecs_world.add_processor(ItemWeaponSystem(self), priority=3)
        self.ecs_world.add_processor(ProjectileSystem(self), priority=2)
        self.ecs_world.add_processor(GraphicsSystem(self), priority=1)

    def load_spawns(self):
        walker_enemy_sprite = pygame.transform.scale(
            pygame.image.load(common.ASSETS_DIR / "imgs" / "placeholder_enemy_walker.png").convert_alpha(),
            (32, 32)
        )

        for obj in self.tilemap.tilemap.objects:
            if obj.name == "player_spawn":
                player_surfs = {
                    "right": pygame.image.load(common.ASSETS_DIR / "imgs" / "player_right.png").convert_alpha(),
                    "left": pygame.image.load(common.ASSETS_DIR / "imgs" / "player_left.png").convert_alpha()
                }

                weapon_surf = pygame.image.load(common.ASSETS_DIR / "imgs" / "items" / "sword_hold.png") # pygame.Surface((32, 32), pygame.SRCALPHA)
                # pygame.draw.rect(weapon_surf, (0, 255, 0), pygame.Rect(0, 0, 10, 32))

                weapon_icon = pygame.Surface((50, 50), pygame.SRCALPHA)
                weapon_icon.fill((0, 255, 0))

                inventory_component = Inventory(size=14, hotbar_size=5)

                self.player = self.ecs_world.create_entity(
                    Flags(collidable=True, mob_type="player", damageable=True),
                    Position(pos=pygame.Vector2(obj.x, obj.y)), Movement(speed=self.PLAYER_SPEED),
                    Graphics(sprites=player_surfs, sprites_state="right"),
                    Health(hp=100, max_hp=100), inventory_component
                )

                inventory_component.inventory[0] = self.ecs_world.create_entity(
                    item_component.Item(cooldown=1, owner=self.player),
                    item_component.ItemPosition(pos=pygame.Vector2(obj.x, obj.y), in_inventory=True),
                    item_component.ItemGraphics(sprite=weapon_surf, icon=weapon_icon),
                    item_component.MeleeWeapon(attack_damage=20),
                    item_component.SlashingSword()
                )

                self.ui.add_widget(PlayerHealthBar(self.ui, self.player, (700, 10), 230, 20))
                self.ui.add_widget(
                    Hotbar(self.ui, self.player, (common.WIDTH // 2, 40), (64, 64)),
                    hud=True, hud_name="hotbar"
                )

            elif obj.name == "walker_enemy_spawn":
                self.temp_sprite = pygame.Surface((16, 16), pygame.SRCALPHA).convert_alpha()
                pygame.draw.rect(self.temp_sprite, (0, 0, 255), pygame.Rect(0, 0, 16, 16))

                # references = References()
                movement = Movement(200)
                movement.mob_specifics["movement_direction"] = 1

                walker_enemy = self.ecs_world.create_entity(
                    Flags(collidable=True, mob_type="walker_enemy", damageable=True),
                    Position(pos=pygame.Vector2(obj.x, obj.y)),
                    Health(hp=60, max_hp=80), Graphics(walker_enemy_sprite),
                    MeleeAttack(attack_range=1, attack_cooldown=1.3, damage=15, collision=True),
                    movement
                )
                self.ui.add_widget(MobHealthBar(self.ui, walker_enemy, 40, 10))
                # references.references["healthbar"] = hp_uuid  Thinking about it

            elif obj.name == "medkit_item":
                health_potion = pygame.image.load(common.ASSETS_DIR / "imgs" / "health_potion.png").convert_alpha()
                health_potion_holding = pygame.transform.scale(health_potion, (16, 16))  # pygame.Surface((16, 16))

                self.ecs_world.create_entity(
                    item_component.Item(cooldown=0),
                    item_component.ItemPosition(pos=pygame.Vector2(obj.x, obj.y)),
                    item_component.ItemGraphics(sprite=health_potion_holding, icon=health_potion, world_sprite=health_potion),
                    item_component.Consumable(), item_component.Medkit(heal_power=45)
                )
            elif obj.name == "bow_item":
                temp_surface = pygame.Surface((32, 32))
                temp_surface.fill((0, 0, 180))

                temp_surface_holding = pygame.Surface((16, 32))
                temp_surface_holding.fill((0, 0, 180))

                self.ecs_world.create_entity(
                    item_component.Item(cooldown=2),
                    item_component.ItemPosition(pos=pygame.Vector2(obj.x, obj.y)),
                    item_component.ItemGraphics(sprite=temp_surface_holding, world_sprite=temp_surface),
                    item_component.RangedWeapon(projectile_damage=30),
                    item_component.GravityBow(launch_vel=pygame.Vector2(100, 0))
                )


    def draw(self):
        self.particle_system.draw()

        if self.camera.shake_frames > 0:
            self.camera.do_shake()

    def handle_event(self, event):
        # self.change_state("level_state.TestState")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                self.debug = not self.debug

    def update(self):
        self.ecs_world.process(self.game_class.events)
        self.particle_system.update()


class TestState(State):
    def draw(self):
        self.screen.fill((128, 128, 128))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.change_state("level_state.LevelState")

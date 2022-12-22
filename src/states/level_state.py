"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the level state, which is the state where the main game happens
"""
from __future__ import annotations

from typing import Optional

# ECS system
import esper
from pytmx import TiledObject

# Important modules
from src import common, core, pygame, screen, utils
# Display modules
from src.display import particle
from src.display.camera import Camera
from src.display.widgets.health_bar import MobHealthBar, PlayerHealthBar
from src.display.widgets.inventory import Hotbar
# Non-ECS systems
from src.entities import effect
# Components
from src.entities.components import ai_component, item_component
from src.entities.components.component import (Graphics, Health,
                                               Inventory, Movement, Position, NoCollidePlayer)
# Systems
from src.entities.systems import (CollisionSystem, CombatSystem,
                                  GraphicsSystem, HitSystem, InputSystem,
                                  NPCCombatSystem, ParticleGenSystem,
                                  ProjectileSystem, TileInteractionSystem,
                                  MovementSystem)
from src.entities.systems.single_target import ItemInfoSystem
from src.tilemap import TileMap
from src.types import Entity

# State (for inheritance)
from .state import State


class LevelState(State):
    def __init__(self, game_class):
        super().__init__(game_class)

        # esper and tilemap stuff
        self.world = esper.World()
        self.tilemap = TileMap(common.MAP_DIR / "map2.tmx", self)

        # Stuff
        self.camera = Camera(common.WIDTH, common.HEIGHT, self.tilemap.width, self.tilemap.height)
        self.particle_manager = particle.ParticleManager(self.camera)
        self.effect_manager = effect.EffectManager(self)

        # UI stuff
        self.ui = self.game_class.ui
        self.ui.level = self
        self.ui.camera = self.camera
        self.ui.world = self.world
        self.ui.particle_manager = self.particle_manager

        # Other stuff
        self.settings = self.game_class.settings
        self.imgs = self.game_class.imgs

        self.player: Optional[Entity] = None
        self.load_map()

        self.debug = False

        # Add ECS systems
        self.core_processes = list(
            map(lambda tup: (tup[0](self), tup[1]), ((GraphicsSystem, -9), (ItemInfoSystem, -10)))
        )
        self.pausable_processes = list(
            map(
                lambda tup: (tup[0](self), tup[1]),
                (
                    (InputSystem, 0),
                    (MovementSystem, -1),
                    (CollisionSystem, -2),
                    (TileInteractionSystem, -3),
                    (NPCCombatSystem, -4),
                    (CombatSystem, -5),
                    (ProjectileSystem, -6),
                    (HitSystem, -7),
                    (ParticleGenSystem, -8),
                ),
            )
        )

        for core_process_class, core_priority in self.core_processes:
            self.world.add_processor(core_process_class, priority=core_priority)
        for normal_process_class, normal_priority in self.pausable_processes:
            self.world.add_processor(normal_process_class, priority=normal_priority)

        # Discard priority because chad
        self.core_processes = list(map(lambda tup: tup[0], self.core_processes))
        self.pausable_processes = list(map(lambda tup: tup[0], self.pausable_processes))

    def load_spawn(self, obj: TiledObject):
        if obj.name == "player_spawn":
            player_settings, sword_settings = self.settings["mobs/player", "items/weapons/slashing_sword"]
            weapon_surf, weapon_icon = self.imgs["items/sword_hold", "items/sword_icon"]

            player_anims, player_anim_speeds = utils.load_mob_animations(player_settings)

            # Inventory outside self.player to add sword
            inventory = Inventory(
                size=player_settings["inventory_size"],
                hotbar_size=player_settings["hotbar_size"],
            )

            self.player = self.world.create_entity(
                Movement(speed=player_settings["speed"]),
                Health(hp=player_settings["hp"], max_hp=player_settings["max_hp"]),
                Position(pos=pygame.Vector2(obj.x, obj.y), rect_size=utils.get_size(player_anims)),
                Graphics(animations=player_anims, animation_speeds=player_anim_speeds),
                inventory,
            )

            # Add initial sword
            inventory[0] = self.world.create_entity(
                item_component.Item(
                    name="Newbie's Sword",
                    cooldown=sword_settings["cooldown"],
                    owner=self.player,
                ),
                item_component.ItemPosition(
                    pos=pygame.Vector2(obj.x, obj.y), rect_size=utils.get_size(weapon_surf), in_inventory=True
                ),
                item_component.MeleeWeapon(attack_damage=sword_settings["damage"]),
                item_component.SlashingSword(),
                item_component.ItemGraphics(sprite=weapon_surf, icon=weapon_icon),
            )

            self.ui.add_widget(PlayerHealthBar(self.ui, self.player, (700, 10), 230, 20))
            hotbar = self.ui.add_widget(
                Hotbar(self.ui, self.player, (common.WIDTH // 2, 40), (64, 64)),
            )
            self.ui.add_hud_widget(hotbar, "hotbar")
            # self.effect_manager.add_effect(
            #     self.player,
            #     effect.BurnEffect(self).builder().damage(10).duration(5, 1).build(),
            # )

        elif obj.name == "walker_enemy_spawn":
            walker_settings = self.settings["mobs/enemy/melee/walker"]
            walker_anims, walker_anim_speeds = utils.load_mob_animations(walker_settings)

            walker_enemy = self.world.create_entity(
                Graphics(animations=walker_anims, animation_speeds=walker_anim_speeds),
                Position(pos=pygame.Vector2(obj.x, obj.y), rect_size=utils.get_size(walker_anims)),
                Health(hp=walker_settings["hp"], max_hp=walker_settings["max_hp"]),
                Movement(walker_settings["speed"]),
                NoCollidePlayer(),
                ai_component.MeleeAttack(
                    attack_range=0,
                    attack_cooldown=walker_settings["attack_cooldown"],
                    damage=walker_settings["attack_damage"],
                    collision=walker_settings["attack_collision"],
                ),
                ai_component.Patroller(),
            )
            self.ui.add_widget(MobHealthBar(self.ui, walker_enemy, 40, 10))

        elif obj.name == "simple_melee_enemy_spawn":
            simple_melee_settings, mob_confs = self.settings["mobs/enemy/melee/simple", "mobs/conf"]
            simple_melee_animations, simple_melee_animation_speeds = utils.load_mob_animations(
                simple_melee_settings, (32, 37)
            )

            weapon_surf = self.imgs["items/bronze_sword"]
            speed = simple_melee_settings["speed"]

            inventory = Inventory(size=1)

            simple_melee_enemy = self.world.create_entity(
                Graphics(animations=simple_melee_animations, animation_speeds=simple_melee_animation_speeds),
                Position(pos=pygame.Vector2(obj.x, obj.y), rect_size=utils.get_size(simple_melee_animations)),
                Health(hp=simple_melee_settings["hp"], max_hp=simple_melee_settings["max_hp"]),
                Movement(speed=simple_melee_settings["speed"]),
                ai_component.FollowsEntityClose(
                    entity=self.player, follow_range=simple_melee_settings["follow_range"]
                ),
                ai_component.MeleeWeaponAttack(attack_range=simple_melee_settings["attack_range"]),
                ai_component.EntityState(
                    available_states=[
                        ai_component.EntityState.Patrol(patrol_speed=speed * mob_confs["patrol_speed_factor"]),
                        ai_component.EntityState.Flee(
                            flee_speed=speed * mob_confs["flee_speed_factor"],
                            flee_time=self.settings["mobs/conf/flee_time"],
                        ),
                        ai_component.EntityState.Follow(),
                    ],
                    starting_state=ai_component.EntityState.Patrol,
                ),
                inventory,
            )

            # Adds sword
            inventory[0] = self.world.create_entity(
                item_component.Item(
                    name="Newbie's Sword",
                    cooldown=simple_melee_settings["attack_cooldown"],
                    owner=simple_melee_enemy,
                ),
                item_component.ItemGraphics(sprite=weapon_surf),
                item_component.ItemPosition(
                    pos=pygame.Vector2(obj.x, obj.y), rect_size=utils.get_size(weapon_surf), in_inventory=True
                ),
                item_component.MeleeWeapon(attack_damage=simple_melee_settings["attack_damage"]),
                item_component.SlashingSword(),
            )

            self.ui.add_widget(MobHealthBar(self.ui, simple_melee_enemy, 40, 10))

        elif obj.name == "test_shooter_enemy_spawn":
            test_shooter_enemy = self.world.create_entity(
                Graphics(sprite=self.imgs["mobs/test_shooter"]),
                Position(pos=pygame.Vector2(obj.x, obj.y), rect_size=utils.get_size(self.imgs["mobs/test_shooter"])),
                Health(hp=10000, max_hp=10000),
                Movement(speed=0.0),
                ai_component.RangeAttack(target=self.player, attack_cooldown=2.0),
            )
            self.ui.add_widget(MobHealthBar(self.ui, test_shooter_enemy, 40, 10))

    def load_item(self, obj: TiledObject):
        if obj.name == "health_potion_item":
            health_potion_settings = self.settings["items/consumables/health_potion"]
            health_potion_surf = self.imgs["items/health_potion"]
            health_potion_holding = pygame.transform.scale(health_potion_surf, (16, 16))

            self.world.create_entity(
                item_component.Item(name="Health Potion", cooldown=health_potion_settings["cooldown"]),
                item_component.ItemGraphics(
                    sprite=health_potion_holding,
                    icon=health_potion_surf,
                    world_sprite=health_potion_surf,
                ),
                item_component.ItemPosition(
                    pos=pygame.Vector2(obj.x, obj.y), rect_size=utils.get_size(health_potion_holding)
                ),
                item_component.Consumable(num_uses=health_potion_settings["uses"]),
                item_component.HealthPotion(heal_power=health_potion_settings["heal_power"]),
            )

        elif obj.name == "gravity_bow_item":
            gravity_bow_settings = self.settings["items/weapons/gravity_bow"]
            gravity_bow_surf, gravity_bow_icon = self.imgs["items/gravity_bow_hold", "items/gravity_bow_icon"]

            self.world.create_entity(
                item_component.Item(name="Newbie's Bow", cooldown=gravity_bow_settings["cooldown"]),
                item_component.ItemGraphics(
                    sprite=gravity_bow_surf,
                    world_sprite=gravity_bow_icon,
                    icon=gravity_bow_icon,
                    flip_on_dir=True,
                ),
                item_component.ItemPosition(
                    pos=pygame.Vector2(obj.x, obj.y), rect_size=utils.get_size(gravity_bow_surf)
                ),
                item_component.RangedWeapon(projectile_damage=gravity_bow_settings["damage"]),
                item_component.GravityBow(launch_vel=pygame.Vector2(gravity_bow_settings["launch_vel"])),
            )

        elif obj.name == "jetpack_item":
            pass

    def load_map(self):
        # Sorts in a way that guarentees player be defined first
        for obj in sorted(self.tilemap.tilemap.objects, key=lambda x: x.name != "player_spawn"):
            self.load_spawn(obj)
            self.load_item(obj)

    def pause(self):
        if not core.time.paused:
            core.time.pause()
            for pausable_process in self.pausable_processes:
                self.world.remove_processor(type(pausable_process))

    def unpause(self):
        if core.time.paused:
            core.time.unpause()
            for pausable_process in self.pausable_processes:
                self.world.add_processor(pausable_process)

    def draw(self):
        self.effect_manager.draw()

        if self.camera.shake_frames > 0:
            self.camera.do_shake()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            # DEBUG stuff: F1 -> debug mode, F6 -> pause, F7 -> unpause, F8 -> transition state
            # F9 -> toggle FPS cap

            if event.key == pygame.K_F1:
                self.debug = not self.debug
            elif event.key == pygame.K_F6 and not core.time.paused:
                self.pause()
            elif event.key == pygame.K_F7 and core.time.paused:
                self.unpause()
            elif event.key == pygame.K_F8:
                core.time.pause()
                self.change_state("level_state.TestState")
            elif event.key == pygame.K_F9:
                if common.FPS == 60:
                    common.FPS = 600
                else:
                    common.FPS = 60

    def update(self):
        # Draws UI in GraphicsSystem
        self.world.process()

        if not core.time.paused:
            self.particle_manager.update()
            self.effect_manager.update()

        self.ui.update()


class TestState(State):
    def draw(self):
        screen.fill((128, 128, 128))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F8:
                core.time.unpause()
                self.change_state("level_state.LevelState")

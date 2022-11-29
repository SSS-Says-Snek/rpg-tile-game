"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the level state, which is the state where the main game happens
"""
from __future__ import annotations

# ECS system
import esper

# Important modules
from src import common, pygame, screen, utils
# Display modules
from src.display import particle
from src.display.camera import Camera
from src.display.widgets.health_bar import MobHealthBar, PlayerHealthBar
from src.display.widgets.inventory import Hotbar
# Non-ECS systems
from src.entities import effect
# Components
from src.entities.components import ai_component, item_component
from src.entities.components.component import (Flags, Graphics, Health,
                                               Inventory, MeleeAttack,
                                               Movement, Position)
# Systems
from src.entities.systems import (CollisionSystem, CombatSystem,
                                  GraphicsSystem, HitSystem, InputSystem,
                                  NPCCombatSystem, ProjectileSystem,
                                  TileInteractionSystem, VelocitySystem)
from src.tilemap import TileMap
from src.types import Dts, Events

# State (for inheritance)
from .state import State


class LevelState(State):
    def __init__(self, game_class):
        super().__init__(game_class)

        # esper and tilemap stuff
        self.ecs_world = esper.World()
        self.tilemap = TileMap(common.MAP_DIR / "map2.tmx", self)

        # Stuff
        self.camera = Camera(common.WIDTH, common.HEIGHT, self.tilemap.width, self.tilemap.height)
        self.particle_system = particle.ParticleSystem(self.camera)
        self.effect_system = effect.EffectSystem(self)

        # UI stuff
        self.ui = self.game_class.ui
        self.ui.level_state = self
        self.ui.camera = self.camera
        self.ui.world = self.ecs_world
        self.ui.particle_system = self.particle_system

        self.placeholder_background = pygame.transform.scale(
            utils.load_img(common.ASSETS_DIR / "imgs" / "placeholder_background2.png", mode="convert"),
            (common.WIDTH, common.HEIGHT),
        ).convert()

        # Other stuff
        self.settings = self.game_class.settings
        self.imgs = self.game_class.imgs

        self.player = None
        self.load_spawns()

        self.debug = False

        # Add ECS systems
        self.ecs_world.add_processor(InputSystem(self), priority=9)
        self.ecs_world.add_processor(VelocitySystem(self), priority=8)
        self.ecs_world.add_processor(CollisionSystem(self), priority=7)
        self.ecs_world.add_processor(TileInteractionSystem(self), priority=6)
        self.ecs_world.add_processor(NPCCombatSystem(self), priority=5)
        self.ecs_world.add_processor(CombatSystem(self), priority=4)
        self.ecs_world.add_processor(ProjectileSystem(self), priority=3)
        self.ecs_world.add_processor(HitSystem(self), priority=2)
        self.ecs_world.add_processor(GraphicsSystem(self), priority=1)

    def load_spawns(self):
        # Sorts in a way that guarentees player be defined first
        for obj in sorted(self.tilemap.tilemap.objects, key=lambda x: x.name != "player_spawn"):
            if obj.name == "player_spawn":
                player_settings, sword_settings = self.settings["mobs/player", "items/weapons/slashing_sword"]
                weapon_surf, weapon_icon = self.imgs["items/sword_hold", "items/sword_icon"]

                player_anims, player_anim_speeds = utils.load_mob_animations(player_settings)

                # Inventory outside self.player to add sword
                inventory_component = Inventory(
                    size=player_settings["inventory_size"],
                    hotbar_size=player_settings["hotbar_size"],
                )

                self.player = self.ecs_world.create_entity(
                    Movement(speed=player_settings["speed"]),
                    Health(hp=player_settings["hp"], max_hp=player_settings["max_hp"]),
                    Graphics(animations=player_anims, animation_speeds=player_anim_speeds),
                    Position(pos=pygame.Vector2(obj.x, obj.y)),
                    Flags(),
                    inventory_component,
                )

                # Add initial sword
                inventory_component.inventory[0] = self.ecs_world.create_entity(
                    item_component.Item(
                        name="Newbie's Sword",
                        cooldown=sword_settings["cooldown"],
                        owner=self.player,
                    ),
                    item_component.ItemGraphics(sprite=weapon_surf, icon=weapon_icon),
                    item_component.ItemPosition(pos=pygame.Vector2(obj.x, obj.y), in_inventory=True),
                    item_component.MeleeWeapon(attack_damage=sword_settings["damage"]),
                    item_component.SlashingSword(),
                )

                self.ui.add_widget(PlayerHealthBar(self.ui, self.player, (700, 10), 230, 20))
                self.ui.add_widget(
                    Hotbar(self.ui, self.player, (common.WIDTH // 2, 40), (64, 64)),
                    hud=True,
                    hud_name="hotbar",
                )
                self.effect_system.add_effect(
                    self.player,
                    effect.BurnEffect(self).builder().damage(10).duration(5, 1).build(),
                )

            elif obj.name == "walker_enemy_spawn":
                walker_settings = self.settings["mobs/enemy/melee/walker"]
                walker_anims, walker_anim_speeds = utils.load_mob_animations(walker_settings)

                walker_enemy = self.ecs_world.create_entity(
                    Flags(mob_type="walker_enemy"),
                    Position(pos=pygame.Vector2(obj.x, obj.y)),
                    Health(hp=walker_settings["hp"], max_hp=walker_settings["max_hp"]),
                    Graphics(animations=walker_anims, animation_speeds=walker_anim_speeds),
                    MeleeAttack(
                        attack_range=0,
                        attack_cooldown=walker_settings["attack_cooldown"],
                        damage=walker_settings["attack_damage"],
                        collision=walker_settings["attack_collision"],
                    ),
                    Movement(walker_settings["speed"]),
                )
                self.ui.add_widget(MobHealthBar(self.ui, walker_enemy, 40, 10))

            elif obj.name == "simple_melee_enemy_spawn":
                simple_melee_settings, mob_confs = self.settings["mobs/enemy/melee/simple", "mobs/conf"]
                simple_melee_animations, simple_melee_animation_speeds = utils.load_mob_animations(
                    simple_melee_settings, (32, 37)
                )

                weapon_surf = self.imgs["items/bronze_sword"]
                speed = simple_melee_settings["speed"]

                # temporary
                inventory_component = Inventory(size=1, hotbar_size=1)

                simple_melee_enemy = self.ecs_world.create_entity(
                    Flags(collide_with_player=True),
                    Position(pos=pygame.Vector2(obj.x, obj.y)),
                    Health(hp=simple_melee_settings["hp"], max_hp=simple_melee_settings["max_hp"]),
                    Movement(speed=simple_melee_settings["speed"]),
                    Graphics(animations=simple_melee_animations, animation_speeds=simple_melee_animation_speeds),
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
                    inventory_component,
                )

                inventory_component.inventory[0] = self.ecs_world.create_entity(
                    item_component.Item(
                        name="Newbie's Sword",
                        cooldown=simple_melee_settings["attack_cooldown"],
                        owner=simple_melee_enemy,
                    ),
                    item_component.ItemGraphics(sprite=weapon_surf),
                    item_component.ItemPosition(pos=pygame.Vector2(obj.x, obj.y), in_inventory=True),
                    item_component.MeleeWeapon(attack_damage=simple_melee_settings["attack_damage"]),
                    item_component.SlashingSword(),
                )

                self.ui.add_widget(MobHealthBar(self.ui, simple_melee_enemy, 40, 10))

            elif obj.name == "health_potion_item":
                health_potion_settings = self.settings["items/consumables/health_potion"]
                health_potion_surf = self.imgs["items/health_potion"]
                health_potion_holding = pygame.transform.scale(health_potion_surf, (16, 16))

                self.ecs_world.create_entity(
                    item_component.Item(name="Health Potion", cooldown=health_potion_settings["cooldown"]),
                    item_component.ItemPosition(pos=pygame.Vector2(obj.x, obj.y)),
                    item_component.ItemGraphics(
                        sprite=health_potion_holding,
                        icon=health_potion_surf,
                        world_sprite=health_potion_surf,
                    ),
                    item_component.Consumable(num_uses=health_potion_settings["uses"]),
                    item_component.HealthPotion(heal_power=health_potion_settings["heal_power"]),
                )

            elif obj.name == "gravity_bow_item":
                gravity_bow_settings = self.settings["items/weapons/gravity_bow"]
                gravity_bow_surf, gravity_bow_icon = self.imgs["items/gravity_bow_hold", "items/gravity_bow_icon"]

                self.ecs_world.create_entity(
                    item_component.Item(name="Newbie's Bow", cooldown=gravity_bow_settings["cooldown"]),
                    item_component.ItemPosition(pos=pygame.Vector2(obj.x, obj.y)),
                    item_component.ItemGraphics(
                        sprite=gravity_bow_surf,
                        world_sprite=gravity_bow_icon,
                        icon=gravity_bow_icon,
                        flip_on_dir=True,
                    ),
                    item_component.RangedWeapon(projectile_damage=gravity_bow_settings["damage"]),
                    item_component.GravityBow(launch_vel=pygame.Vector2(gravity_bow_settings["launch_vel"])),
                )
            elif obj.name == "jetpack_item":
                pass

    def reset(self):
        self.ecs_world.clear_database()

    def draw(self):
        self.effect_system.draw()

        if self.camera.shake_frames > 0:
            self.camera.do_shake()

    def handle_event(self, event: pygame.event.Event):
        # self.change_state("level_state.TestState")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F1:
                self.debug = not self.debug

    def update(self, events: Events, dts: Dts):
        # Draws UI in GraphicsSystem
        self.ecs_world.process(events, dts)

        self.particle_system.update()
        self.effect_system.update()


class TestState(State):
    def draw(self):
        screen.fill((128, 128, 128))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.change_state("level_state.LevelState")

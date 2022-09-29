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
from src import common, pygame, utils
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
                                  GraphicsSystem, InputSystem, NPCCombatSystem,
                                  ProjectileSystem, TileInteractionSystem,
                                  VelocitySystem)
from src.tilemap import TileMap
from src.types import Dts, Events

# State (for inheritance)
from .state import State


class LevelState(State):
    PLAYER_SPEED = 300

    def __init__(self, game_class):
        super().__init__(game_class)

        # esper and tilemap stuff
        self.ecs_world = esper.World()

        # Stuff
        self.camera = Camera(common.WIDTH, common.HEIGHT)
        self.particle_system = particle.ParticleSystem(self.camera)
        self.effect_system = effect.EffectSystem(self)

        # UI stuff
        self.ui = self.game_class.ui
        self.ui.level_state = self
        self.ui.camera = self.camera
        self.ui.world = self.ecs_world
        self.ui.particle_system = self.particle_system

        self.tilemap = TileMap(common.MAP_DIR / "map.tmx", self)

        self.placeholder_background = pygame.transform.scale(
            utils.load_img(common.ASSETS_DIR / "imgs" / "placeholder_background.png").convert(),
            (common.WIDTH, common.HEIGHT),
        )

        # Other stuff
        self.settings = self.game_class.settings

        self.player = None
        self.load_spawns()

        self.debug = False

        # Add ECS systems
        self.ecs_world.add_processor(InputSystem(self), priority=8)
        self.ecs_world.add_processor(VelocitySystem(self), priority=7)
        self.ecs_world.add_processor(CollisionSystem(self), priority=6)
        self.ecs_world.add_processor(TileInteractionSystem(self), priority=5)
        self.ecs_world.add_processor(NPCCombatSystem(self), priority=4)
        self.ecs_world.add_processor(CombatSystem(self), priority=3)
        self.ecs_world.add_processor(ProjectileSystem(self), priority=2)
        self.ecs_world.add_processor(GraphicsSystem(self), priority=1)
        # self.ecs_world.add_processor(TileInteractionSystem(self), priority=3)

    def load_spawns(self):
        # Sorts in a way that guarentees player be defined first
        for obj in sorted(self.tilemap.tilemap.objects, key=lambda x: x.name != "player_spawn"):
            if obj.name == "player_spawn":
                player_settings, sword_settings = self.settings[
                    "mobs/player", "items/weapons/slashing_sword"
                ]
                player_animations, player_animation_speeds = utils.load_mob_animations(
                    player_settings
                )

                weapon_surf, weapon_icon = [
                    pygame.image.load(common.ASSETS_DIR / "imgs" / "items" / img_file)
                    for img_file in ["sword_hold.png", "sword_icon.png"]
                ]

                # Inventory outside self.player to add sword
                inventory_component = Inventory(
                    size=player_settings["inventory_size"],
                    hotbar_size=player_settings["hotbar_size"],
                )

                self.player = self.ecs_world.create_entity(
                    Movement(speed=player_settings["speed"]),
                    Health(hp=player_settings["hp"], max_hp=player_settings["max_hp"]),
                    Graphics(
                        animations=player_animations, animation_speeds=player_animation_speeds
                    ),
                    Flags(collidable=True, mob_type="player", damageable=True),
                    Position(pos=pygame.Vector2(obj.x, obj.y)),
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
                    item_component.ItemPosition(
                        pos=pygame.Vector2(obj.x, obj.y), in_inventory=True
                    ),
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
                walker_animations, walker_animation_speeds = utils.load_mob_animations(
                    walker_settings
                )

                walker_enemy = self.ecs_world.create_entity(
                    Flags(collidable=True, mob_type="walker_enemy", damageable=True),
                    Position(pos=pygame.Vector2(obj.x, obj.y)),
                    Health(hp=walker_settings["hp"], max_hp=walker_settings["max_hp"]),
                    Graphics(
                        animations=walker_animations, animation_speeds=walker_animation_speeds
                    ),
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
                simple_melee_settings = self.settings["mobs/enemy/melee/simple"]
                temp_sprite = pygame.Surface((32, 32))
                temp_sprite.fill((255, 40, 30))

                weapon_surf, weapon_icon = [
                    pygame.image.load(common.ASSETS_DIR / "imgs" / "items" / img_file)
                    for img_file in ["sword_hold.png", "sword_icon.png"]
                ]

                inventory_component = Inventory(size=1, hotbar_size=1)

                simple_melee_enemy = self.ecs_world.create_entity(
                    Flags(collide_with_player=True),
                    Position(pos=pygame.Vector2(obj.x, obj.y)),
                    Health(hp=simple_melee_settings["hp"], max_hp=simple_melee_settings["max_hp"]),
                    Movement(speed=simple_melee_settings["speed"]),
                    Graphics(sprite=temp_sprite),
                    ai_component.FollowsEntityClose(
                        entity=self.player, follow_range=simple_melee_settings["follow_range"]
                    ),
                    ai_component.MeleeWeaponAttack(
                        attack_range=simple_melee_settings["attack_range"]
                    ),
                    inventory_component,
                )

                inventory_component.inventory[0] = self.ecs_world.create_entity(
                    item_component.Item(
                        name="Newbie's Sword",
                        cooldown=simple_melee_settings["attack_cooldown"],
                        owner=simple_melee_enemy,
                    ),
                    item_component.ItemGraphics(sprite=weapon_surf, icon=weapon_icon),
                    item_component.ItemPosition(
                        pos=pygame.Vector2(obj.x, obj.y), in_inventory=True
                    ),
                    item_component.MeleeWeapon(
                        attack_damage=simple_melee_settings["attack_damage"]
                    ),
                    item_component.SlashingSword(),
                )

                self.ui.add_widget(MobHealthBar(self.ui, simple_melee_enemy, 40, 10))

            elif obj.name == "health_potion_item":
                health_potion_settings = self.settings["items/consumables/health_potion"]
                health_potion_surf = utils.load_img(
                    common.IMG_DIR / "items" / health_potion_settings["sprite"]
                ).convert_alpha()
                health_potion_holding = pygame.transform.scale(health_potion_surf, (16, 16))

                self.ecs_world.create_entity(
                    item_component.Item(
                        name="Health Potion", cooldown=health_potion_settings["cooldown"]
                    ),
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
                gravity_bow_surf, gravity_bow_icon = [
                    pygame.image.load(common.ASSETS_DIR / "imgs" / "items" / img_file)
                    for img_file in ["gravity_bow_hold.png", "gravity_bow_icon.png"]
                ]

                self.ecs_world.create_entity(
                    item_component.Item(
                        name="Newbie's Bow", cooldown=gravity_bow_settings["cooldown"]
                    ),
                    item_component.ItemPosition(pos=pygame.Vector2(obj.x, obj.y)),
                    item_component.ItemGraphics(
                        sprite=gravity_bow_surf,
                        world_sprite=gravity_bow_icon,
                        icon=gravity_bow_icon,
                        flip_on_dir=True,
                    ),
                    item_component.RangedWeapon(projectile_damage=gravity_bow_settings["damage"]),
                    item_component.GravityBow(
                        launch_vel=pygame.Vector2(gravity_bow_settings["launch_vel"])
                    ),
                )
            elif obj.name == "jetpack_item":
                pass

    def draw(self):
        self.effect_system.draw()

        if self.camera.shake_frames > 0:
            self.camera.do_shake()

    def handle_event(self, event: pygame.event.Event):
        # self.change_state("level_state.TestState")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                self.debug = not self.debug

    def update(self, events: Events, dts: Dts):
        # Draws UI in GraphicsSystem
        self.ecs_world.process(events, dts)

        self.particle_system.update()
        self.effect_system.update()


class TestState(State):
    def draw(self):
        self.screen.fill((128, 128, 128))

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.change_state("level_state.LevelState")

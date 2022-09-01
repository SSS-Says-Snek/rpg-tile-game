"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from __future__ import annotations

import math
import random

import pytmx

from src import common, pygame, screen, utils
from src.display import particle
from src.display.particle import ImageParticle
from src.entities.components import (item_component, projectile_component,
                                     tile_component)
from src.entities.components.component import (Flags, Graphics, Inventory,
                                               Movement, Position)
from src.entities.systems.system import System


class GraphicsSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

        self.normal_map_surf, self.interactable_map_surf = self.tilemap.make_map()
        self.wind_gusts = [-15, -15, -15]
        self.random_wind_gust_idx = random.randrange(0, len(self.wind_gusts))
        self.cloud_parallax = 0.3
        self.cloud_paths = list((common.IMG_DIR / "misc" / "clouds").iterdir())

    #####################################################################
    # DRAWING FUNCTIONS: Very similar to ParticleSystem's draw handling #
    #####################################################################

    def handle_widgets_base(self, event_list, dts, when):
        for widget, widget_when in self._send_to_graphics_widgets:
            if widget_when == when:
                widget.draw(self.camera)
                widget.update(event_list, dts)

    def handle_pre_interactable_widgets(self, event_list, dts):
        self.handle_widgets_base(event_list, dts, "pre_interactables")

    def handle_post_interactable_widgets(self, event_list, dts):
        self.handle_widgets_base(event_list, dts, "post_interactables")

    def handle_pre_tilemap_widgets(self, event_list, dts):
        self.handle_widgets_base(event_list, dts, "pre_tilemap")

    def handle_pre_ui_widgets(self, event_list, dts):
        self.handle_widgets_base(event_list, dts, "pre_ui")

    def handle_post_ui_widgets(self, event_list, dts):
        self.handle_widgets_base(event_list, dts, "post_ui")

    ####################
    # Helper functions #
    ####################

    def _draw_tree_layer(self, layer, adj_rect, anim_offset):
        screen.blit(
            pygame.transform.rotate(layer, math.sin(pygame.time.get_ticks() / 800) * 1.4),
            self.camera.apply(
                pygame.Vector2(adj_rect.topleft)
                + pygame.Vector2(
                    math.sin(pygame.time.get_ticks() / 600 + anim_offset) * 2,
                    math.sin(pygame.time.get_ticks() / 750 + anim_offset) * 1.5,
                )
                * (self.wind_gusts[self.random_wind_gust_idx] / 7.5)
            ),
        )

    def _draw_mob_debug(self):
        """Draws debug rects of the mobs"""
        tilemap = self.tilemap.tilemap

        for layer in tilemap.visible_layers:
            if isinstance(layer, pytmx.TiledTileLayer):
                for x, y, gid in layer:
                    # Adds tile props to dict
                    tile_props = tilemap.get_tile_properties_by_gid(gid)
                    if tile_props is None:
                        continue

                    # Draws entity rects
                    pygame.draw.rect(
                        screen,
                        (0, 255, 0),
                        self.camera.apply(
                            pygame.Rect(
                                x * tilemap.tilewidth,
                                y * tilemap.tileheight,
                                tilemap.tilewidth,
                                tilemap.tileheight,
                            )
                        ),
                        width=1,
                    )

    def _draw_mob(self, dts, entity, graphics, pos):
        """Draws the actual mob sprite and animations"""
        if not self.world.component_for_entity(entity, Flags).rotatable:
            if self.level_state.debug:
                pygame.draw.rect(
                    screen,
                    (255, 0, 0),
                    self.camera.apply(pos.rect),
                    width=1,
                )

            if graphics.sprite is not None:
                screen.blit(graphics.sprite, self.camera.apply(pos.pos))
            else:
                movement = self.world.component_for_entity(entity, Movement)

                if movement.vel.x > 0 and graphics.animations.get("move_right"):
                    graphics.animations["move_right"].play_anim(
                        self.camera.apply(pos.pos),
                        dts["raw_dt"],
                        graphics.animation_speeds["move"],
                    )
                elif movement.vel.x < 0 and graphics.animations.get("move_left"):
                    graphics.animations["move_left"].play_anim(
                        self.camera.apply(pos.pos),
                        dts["raw_dt"],
                        graphics.animation_speeds["move"],
                    )

                elif pos.direction == 1 and graphics.animations.get("idle_right"):
                    graphics.animations["idle_right"].play_anim(
                        self.camera.apply(pos.pos),
                        dts["raw_dt"],
                        graphics.animation_speeds["idle"],
                    )
                elif pos.direction == -1 and graphics.animations.get("idle_left"):
                    graphics.animations["idle_left"].play_anim(
                        self.camera.apply(pos.pos),
                        dts["raw_dt"],
                        graphics.animation_speeds["idle"],
                    )

        else:
            movement = self.world.component_for_entity(entity, Movement)
            rotated_sprite, new_pos = utils.rot_center(
                graphics.sprite, movement.rot, *pygame.Rect(*pos.pos, *graphics.size).center
            )
            screen.blit(rotated_sprite, self.camera.apply(new_pos))

    def _draw_mob_item(self, entity, pos):
        """Draws the mob's equipped item (if any)"""
        if self.world.has_component(entity, Inventory):  # entity == self.player:
            inventory = self.world.component_for_entity(entity, Inventory)
            equipped_item = inventory.inventory[inventory.equipped_item_idx]

            if equipped_item is not None:
                item_graphics = self.world.component_for_entity(
                    equipped_item, item_component.ItemGraphics
                )
                item_pos = self.world.component_for_entity(
                    equipped_item, item_component.ItemPosition
                )

                x_offset = 0
                if item_graphics.flip_on_dir:
                    if pos.direction == -1:
                        item_graphics.current_img = pygame.transform.flip(
                            item_graphics.current_img, flip_x=True, flip_y=False
                        )
                        x_offset = item_graphics.bound_size[0] + 6

                screen.blit(
                    item_graphics.current_img,
                    self.camera.apply((item_pos.pos[0] - x_offset, item_pos.pos[1])),
                )

                item_graphics.current_img = item_graphics.original_img

    def draw_mobs(self, dts):
        """Draws all mobs appropriately"""
        for entity, (graphics, pos) in self.world.get_components(Graphics, Position):
            if self.level_state.debug:
                self._draw_mob_debug()

            self._draw_mob(dts, entity, graphics, pos)

            self._draw_mob_item(entity, pos)

    def draw_world_items(self):
        for entity, (item_graphics, item_pos) in self.world.get_components(
            item_component.ItemGraphics, item_component.ItemPosition
        ):
            if not item_pos.in_inventory:
                screen.blit(
                    item_graphics.world_sprite,
                    self.camera.apply(
                        (
                            item_pos.pos[0],
                            item_pos.pos[1] - 5 - math.sin(pygame.time.get_ticks() / 200) * 5,
                        )
                    ),
                )

    def draw_projectiles(self):
        for entity, (projectile_graphics, projectile_pos) in self.world.get_components(
            projectile_component.ProjectileGraphics,
            projectile_component.ProjectilePosition,
        ):
            screen.blit(
                projectile_graphics.current_img,
                self.camera.apply(projectile_pos.pos),
            )

    def draw_clouds(self):
        if random.random() < 0.022:
            self.particle_system.add(
                ImageParticle()
                .builder()
                .at(
                    pygame.Vector2(
                        # MAGIC NUMBERS - DON'T QUESTION
                        # Gist: Spawns clouds at appropriate pos outside of screen
                        common.WIDTH
                        + (self.camera.camera.x + common.WIDTH) * self.cloud_parallax
                        + random.randint(-300, 400),
                        self.camera.camera.y * self.cloud_parallax + random.randint(-75, 125),
                    )
                )
                .image(
                    image=utils.load_img(random.choice(self.cloud_paths)),
                    scale=random.uniform(0.6, 1.1),
                )
                .starting_vel(
                    # - 0.3 is for semi-guarentee no lagging
                    pygame.Vector2(
                        random.choice(self.wind_gusts) / random.uniform(13, 17) - 0.3, 0
                    )
                )
                .lifespan(frames=2000)
                .draw_when(when="pre_interactables")
                .parallax(parallax_val=self.cloud_parallax)
                .effect_fade(start_fade_frac=0.9)
                .build()
            )

    def draw_wind_particles(self):
        # Adds wind gust particles
        if random.random() < 0.19:
            if random.random() < 0.05:
                self.wind_gusts = [random.uniform(-15, -1.5) for _ in range(3)]
                self.random_wind_gust_idx = random.randrange(0, len(self.wind_gusts))

            self.particle_system.create_wind_particle(
                pygame.Vector2(
                    random.randint(self.camera.camera.x, self.camera.camera.x + common.WIDTH),
                    random.randint(self.camera.camera.y, self.camera.camera.y + common.HEIGHT),
                ),
                self.wind_gusts,
            )

    def animate_trees(self):
        for entity, (tile, tile_deco) in self.world.get_components(
            tile_component.Tile, tile_component.Decoration
        ):
            adj_rect = tile_deco.img.get_rect(midbottom=tile.rect.midbottom)

            self._draw_tree_layer(tile_deco.layers[-1], adj_rect, tile_deco.anim_offset)
            screen.blit(tile_deco.img, self.camera.apply(adj_rect))

            for i, layer in enumerate(tile_deco.layers[1::-1]):
                if i == 0:
                    screen.blit(layer, self.camera.apply(adj_rect))
                else:
                    self._draw_tree_layer(layer, adj_rect, tile_deco.anim_offset)

            if random.random() < 0.07:
                self.particle_system.create_wind_particle(
                    pygame.Vector2(
                        random.randint(tile.rect.x, tile.rect.x + tile.rect.width),
                        random.randint(tile.rect.y, tile.rect.y + tile.rect.height),
                    ),
                    self.wind_gusts,
                    movement_factor=1.5,
                )

    def process(self, event_list, dts) -> None:
        # Blits background
        screen.blit(self.level_state.placeholder_background, (0, 0))

        # No shake :( thinking
        self.camera.adjust_to(
            dts["dt"],
            self.world.component_for_entity(self.player, Position).pos,
        )

        self.particle_system.draw_pre_interactables()
        self.handle_pre_interactable_widgets(event_list, dts)
        screen.blit(self.interactable_map_surf, self.camera.apply((0, 0)))
        self.handle_post_interactable_widgets(event_list, dts)

        self.animate_trees()

        self.draw_mobs(dts)

        self.draw_world_items()

        self.draw_projectiles()

        self.particle_system.draw_pre_tilemap()
        self.handle_pre_tilemap_widgets(event_list, dts)
        screen.blit(self.normal_map_surf, self.camera.apply((0, 0)))

        self.particle_system.draw_pre_ui()
        self.handle_pre_ui_widgets(event_list, dts)
        self.level_state.ui.draw()
        self.particle_system.draw_post_ui()
        self.handle_post_ui_widgets(event_list, dts)

        self.draw_wind_particles()

        self.draw_clouds()

        # Cleanup widgets
        self._send_to_graphics_widgets.clear()

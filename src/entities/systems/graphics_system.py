"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

from __future__ import annotations

import math

from src import common, core, pygame, screen, utils
from src.common import TILE_HEIGHT, TILE_WIDTH
from src.entities.components import (ai_component, item_component,
                                     projectile_component, tile_component)
from src.entities.components.component import (Graphics, Inventory, Movement,
                                               Position)
from src.entities.systems.system import System


class GraphicsSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

        self.normal_map_surf, self.interactable_map_surf = self.tilemap.make_map()
        self.background = pygame.transform.scale(self.imgs["placeholder_background2"], common.RES).convert()

    #####################################################################
    # DRAWING FUNCTIONS: Very similar to ParticleSystem's draw handling #
    #####################################################################

    def handle_widgets_base(self, when: str):
        for widget, widget_when in self._send_to_graphics_widgets:
            if widget_when == when:
                widget.draw(self.camera)
                widget.update()

    def handle_pre_interactable_widgets(self):
        self.handle_widgets_base("pre_interactables")

    def handle_post_interactable_widgets(self):
        self.handle_widgets_base("post_interactables")

    def handle_pre_tilemap_widgets(self):
        self.handle_widgets_base("pre_tilemap")

    def handle_pre_ui_widgets(self):
        self.handle_widgets_base("pre_ui")

    def handle_post_ui_widgets(self):
        self.handle_widgets_base("post_ui")

    ####################
    # Helper functions #
    ####################

    def _draw_tree_layer(self, layer: pygame.Surface, adj_rect: pygame.Rect, anim_offset: float):
        screen.blit(
            pygame.transform.rotate(layer, math.sin(core.time.get_ticks() / 800) * 1.4),
            self.camera.apply(
                pygame.Vector2(adj_rect.topleft)
                + pygame.Vector2(
                    math.sin(core.time.get_ticks() / 600 + anim_offset) * 2,
                    math.sin(core.time.get_ticks() / 750 + anim_offset) * 1.5,
                )
                * (math.sin(core.time.get_ticks() / 650) * 1.6)
            ),
        )

    def _draw_mob_debug(self, entity: int, pos: Position):
        """Draws debug rects of the mobs"""
        info = pygame.Surface((180, 100), pygame.SRCALPHA)
        info.set_alpha(180)

        adj_pos = self.camera.apply(pos.rect)
        info_pos = adj_pos.copy()
        info_pos.width, info_pos.height = info.get_size()
        info_pos.bottom = adj_pos.top - 5
        info_pos.centerx = adj_pos.centerx

        pygame.draw.rect(info, (249, 204, 127), (0, 0, *info.get_size()), border_radius=5)
        pygame.draw.rect(info, (80, 46, 23), (0, 0, *info.get_size()), width=2, border_radius=5)
        pygame.draw.rect(
            screen,
            (255, 0, 0),
            adj_pos,
            width=1,
        )

        font = utils.load_font(15)
        lines = (
            f"Entity ID: {entity}",
            f"Coord pos: {pos.pos.xy}",
            f"Tile pos: {pos.tile_pos.xy}",
        )

        for i, line in enumerate(lines):
            info.blit(font.render(line, True, (0, 0, 0)), (10, i * 20 + 10))

        if self.world.has_component(entity, ai_component.EntityState):
            entity_state = self.world.component_for_entity(entity, ai_component.EntityState)
            info.blit(font.render(f"State: {type(entity_state.state).__name__}", True, (0, 0, 0)), (10, 70))

        screen.blit(info, info_pos)

    def _draw_mob(self, raw_dt: float, entity: int, graphics: Graphics, pos: Position):
        """Draws the actual mob sprite and animations"""

        if graphics.sprites is not None:
            if pos.direction == 1:
                screen.blit(graphics.sprites["right"], self.camera.apply(pos.pos))
            else:
                screen.blit(graphics.sprites["left"], self.camera.apply(pos.pos))
        elif graphics.animations is not None:
            movement = self.world.component_for_entity(entity, Movement)

            if movement.vel.x > 0 and graphics.animations.get("move_right"):
                graphics.animations["move_right"].play_anim(
                    self.camera.apply(pos.pos),
                    raw_dt,
                    graphics.animation_speeds["move"],
                )
            elif movement.vel.x < 0 and graphics.animations.get("move_left"):
                graphics.animations["move_left"].play_anim(
                    self.camera.apply(pos.pos),
                    raw_dt,
                    graphics.animation_speeds["move"],
                )

            elif pos.direction == 1 and graphics.animations.get("idle_right"):
                graphics.animations["idle_right"].play_anim(
                    self.camera.apply(pos.pos),
                    raw_dt,
                    graphics.animation_speeds["idle"],
                )
            elif pos.direction == -1 and graphics.animations.get("idle_left"):
                graphics.animations["idle_left"].play_anim(
                    self.camera.apply(pos.pos),
                    raw_dt,
                    graphics.animation_speeds["idle"],
                )

    def _draw_mob_item(self, entity: int, pos: Position):
        """Draws the mob's equipped item (if any)"""

        if self.world.has_component(entity, Inventory):
            inventory = self.world.component_for_entity(entity, Inventory)
            equipped_item = inventory[inventory.equipped_item_idx]

            if equipped_item is not None:
                item_graphics = self.world.component_for_entity(equipped_item, item_component.ItemGraphics)
                item_pos = self.world.component_for_entity(equipped_item, item_component.ItemPosition)

                x_offset = math.copysign(2, -pos.direction)
                if item_graphics.flip_on_dir:
                    if pos.direction == -1:
                        item_graphics.current_img = pygame.transform.flip(
                            item_graphics.current_img, flip_x=True, flip_y=False
                        )
                        x_offset = item_graphics.bound_size[0] + 8

                screen.blit(
                    item_graphics.current_img,
                    self.camera.apply((item_pos.pos[0] - x_offset, item_pos.pos[1] + 5)),
                )

                item_graphics.current_img = item_graphics.original_img

    def draw_mobs(self, raw_dt: float):
        """Draws all mobs appropriately"""
        for entity, (graphics, pos) in self.world.get_components(Graphics, Position):
            self._draw_mob(raw_dt, entity, graphics, pos)
            self._draw_mob_item(entity, pos)

    def draw_mobs_debug(self):
        for entity, pos in self.world.get_component(Position):
            if self.level.debug:
                self._draw_mob_debug(entity, pos)

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
                            item_pos.pos[1] - 5 - math.sin(core.time.get_ticks() / 200) * 5,
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

    def handle_blade_rotation(self, tile_grass: tile_component.GrassBlades, blade):
        player_rect = self.component_for_player(Position).rect
        player_grass_pos = (player_rect.centerx, player_rect.bottom)
        blade_pos = (tile_grass.tile_x * TILE_WIDTH + blade.x, tile_grass.tile_y * TILE_HEIGHT)

        if math.dist(blade_pos, player_grass_pos) < 45:
            h_dis = player_grass_pos[0] - blade_pos[0]
            angle_apply = math.copysign(30, -h_dis) + h_dis * 3.5
            blade.target_angle = max(min(blade.target_angle + angle_apply, 90), -90)
        else:
            blade.target_angle = -(math.sin(core.time.get_ticks() / 600) - blade.rotate_weight) * blade.rotate_angle

        blade.angle += (blade.target_angle - blade.angle) / 6

    def animate_grass(self):
        for entity, (tile, tile_grass) in self.world.get_components(tile_component.Tile, tile_component.GrassBlades):
            if not self.camera.visible(tile.rect):
                continue

            for blade in tile_grass.blades:
                self.handle_blade_rotation(tile_grass, blade)

                img_to_blit = pygame.transform.rotate(blade.img, blade.angle)
                img_to_blit.set_colorkey((0, 0, 0))

                screen.blit(
                    img_to_blit,
                    self.camera.apply(
                        (
                            tile_grass.tile_x * TILE_WIDTH  # Location
                            + blade.x  # X rel to location
                            - img_to_blit.get_width() // 2,  # Centering mechanism
                            tile_grass.tile_y * TILE_HEIGHT + 31 - img_to_blit.get_height() // 2,
                        )
                    ),
                )

    def animate_trees(self):
        for entity, (tile, tile_deco) in self.world.get_components(tile_component.Tile, tile_component.Decoration):
            adj_rect = tile_deco.img.get_rect(midbottom=tile.rect.midbottom)
            if not self.camera.visible(adj_rect):
                continue

            self._draw_tree_layer(tile_deco.layers[-1], adj_rect, tile_deco.anim_offset)
            screen.blit(tile_deco.img, self.camera.apply(adj_rect))

            for i, layer in enumerate(tile_deco.layers[1::-1]):
                if i == 0:
                    screen.blit(layer, self.camera.apply(adj_rect))
                else:
                    self._draw_tree_layer(layer, adj_rect, tile_deco.anim_offset)

    def process(self):
        # Blits background
        screen.blit(self.background, (0, 0))

        # No shake :( thinking
        self.camera.adjust_to(
            core.dt.dt,
            self.component_for_player(Position).pos,
        )

        self.particle_system.draw_pre_interactables()
        self.handle_pre_interactable_widgets()
        screen.blit(self.interactable_map_surf, self.camera.apply((0, 0)))
        self.handle_post_interactable_widgets()

        self.animate_trees()
        self.animate_grass()

        self.draw_mobs(core.dt.raw_dt)

        self.draw_world_items()

        self.draw_projectiles()

        self.particle_system.draw_pre_tilemap()
        self.handle_pre_tilemap_widgets()
        screen.blit(self.normal_map_surf, self.camera.apply((0, 0)))

        self.particle_system.draw_pre_ui()
        self.handle_pre_ui_widgets()
        self.ui.draw()
        self.particle_system.draw_post_ui()
        self.handle_post_ui_widgets()

        self.draw_mobs_debug()

        # Cleanup widgets
        self._send_to_graphics_widgets.clear()

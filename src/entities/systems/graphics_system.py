"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""

import math

import pytmx

from src import pygame, screen, utils
from src.entities.components import item_component, projectile_component
from src.entities.components.component import Flags, Graphics, Inventory, Movement, Position
from src.entities.systems.system import System


class GraphicsSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

        self.normal_map_surf, self.interactable_map_surf = self.tilemap.make_map()

    def handle_sent_widgets(self, event_list, dts):
        for widget in self._send_to_graphics_widgets:
            widget.draw(self.camera)
            widget.update(event_list, dts)

        self._send_to_graphics_widgets.clear()

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

    def process(self, event_list, dts) -> None:
        # Blits background
        screen.blit(self.level_state.placeholder_background, (0, 0))
        screen.blit(self.interactable_map_surf, self.camera.apply((0, 0)))

        # No shake :( thinking
        self.camera.adjust_to(
            dts["dt"],
            self.world.component_for_entity(self.player, Position).pos,
        )

        self.draw_mobs(dts)

        self.draw_world_items()

        self.draw_projectiles()

        screen.blit(self.normal_map_surf, self.camera.apply((0, 0)))

        self.handle_sent_widgets(event_list, dts)

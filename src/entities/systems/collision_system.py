"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the collision system, which handles entity-to-tile collision as well as
entity-to-player collision (soon)
"""
from __future__ import annotations

import pygame

from src import utils
from src.entities.components import item_component
from src.entities.components.component import (Flags, Graphics, Inventory,
                                               Movement, Position)
from src.entities.systems.system import System
from src.types import Dts, Events


class CollisionSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    @staticmethod
    def collide_with_tiles(
        rect: pygame.Rect, movement: Movement, neighboring_tile_rects: list[pygame.Rect], dt: float
    ):
        collision_types = {"top": False, "bottom": False, "right": False, "left": False}
        rect.x += round(movement.vel.x * dt)

        for neighboring_tile_rect in neighboring_tile_rects:
            if neighboring_tile_rect is not None and neighboring_tile_rect.colliderect(rect):
                if movement.vel.x > 0:
                    rect.right = neighboring_tile_rect.left
                    collision_types["right"] = True
                elif movement.vel.x < 0:
                    # print('OMAGOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO')
                    rect.left = neighboring_tile_rect.right
                    collision_types["left"] = True

        rect.y += round(movement.vel.y)

        for neighboring_tile_rect in neighboring_tile_rects:
            if neighboring_tile_rect is not None and neighboring_tile_rect.colliderect(rect):
                if movement.vel.y > 0:
                    movement.vel.y = 0
                    rect.bottom = neighboring_tile_rect.top
                    collision_types["bottom"] = True
                elif movement.vel.y < 0:
                    movement.vel.y = 0
                    rect.top = neighboring_tile_rect.bottom
                    collision_types["top"] = True
        return collision_types

    def process(self, event_list: Events, dts: Dts):
        # super().process(event_list)

        # Mob
        for entity, (flags, pos, movement, graphics) in self.world.get_components(Flags, Position, Movement, Graphics):
            pos.rect = pygame.Rect(*pos.pos, *graphics.size)
            neighboring_tile_rects = self.tilemap.get_unwalkable_rects(
                utils.get_neighboring_tile_entities(self.tilemap, 3, pos)
            )

            # Obvs, if it's gonna collide with player, player should be in it
            if flags.collide_with_player:
                neighboring_tile_rects.append(self.world.component_for_entity(self.player, Position).rect)

            # Player collides with collide_with_player entities
            if entity == self.player:
                # Still super inefficient
                for nested_entity, (nested_flags, nested_pos, *_) in self.world.get_components(
                    Flags, Position, Movement, Graphics
                ):
                    if nested_flags.collide_with_player and nested_pos.rect is not None:
                        neighboring_tile_rects.append(nested_pos.rect)

            # Apply gravity
            # Weird bug, can patch it up by capping movement y vel
            movement.vel.y += movement.gravity_acc.y
            if movement.vel.y > 170:
                movement.vel.y = 170
            pos.pos.y += movement.vel.y

            collisions = self.collide_with_tiles(pos.rect, movement, neighboring_tile_rects, dts["dt"])
            if collisions["bottom"]:
                pos.on_ground = True
                movement.vel.y = 0

            pos.pos.x = pos.rect.x
            pos.pos.y = pos.rect.y
            pos.tile_pos = utils.pixel_to_tile(pos.pos)

        # Item pickup
        for entity, (item, item_pos, item_graphics) in self.world.get_components(
            item_component.Item,
            item_component.ItemPosition,
            item_component.ItemGraphics,
        ):
            owner_pos = self.world.component_for_entity(self.player, Position)
            player_rect = owner_pos.rect
            player_inventory = self.world.component_for_entity(self.player, Inventory)
            item_pos.rect = pygame.Rect(*item_pos.pos, *item_graphics.bound_size)

            # Player collided with item
            if not item_pos.in_inventory and player_rect.colliderect(item_pos.rect):
                available_inventory_idx = player_inventory.get_available_idx()
                if available_inventory_idx is not None:
                    item.owner = self.player
                    item_pos.pos.x, item_pos.pos.y = item_pos.pos.x, item_pos.pos.y
                    item_pos.in_inventory = True

                    player_inventory.inventory[available_inventory_idx] = entity

                    self.particle_system.create_text_particle(owner_pos.pos, f"Acquired: {item.name}")
                else:
                    self.particle_system.create_text_particle(owner_pos.pos, "No more room in inventory!")

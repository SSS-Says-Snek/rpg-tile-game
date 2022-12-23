"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file defines the collision system, which handles entity-to-tile collision as well as
entity-to-player collision (soon)
"""
from __future__ import annotations

import pygame

from src import core, utils
from src.entities.components import item_component, tile_component
from src.entities.components.component import (Graphics, Inventory, Movement,
                                               NoCollidePlayer, Position)
from src.entities.systems.system import System


class CollisionSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    def collide_with_tiles(self, pos: Position, movement: Movement, neighboring_tile_rects: list[pygame.Rect]) -> bool:
        collide_bottom = False

        pos.pos.x += movement.vel.x * core.dt.dt
        pos.pos.x = min(max(pos.pos.x, 0), self.tilemap.width - pos.rect.width)
        pos.rect.x = round(pos.pos.x)

        for neighboring_tile_rect in neighboring_tile_rects:
            if neighboring_tile_rect.colliderect(pos.rect):
                if movement.vel.x > 0:
                    pos.rect.right = neighboring_tile_rect.left
                    pos.pos.x = pos.rect.x
                elif movement.vel.x < 0:
                    pos.rect.left = neighboring_tile_rect.right
                    pos.pos.x = pos.rect.x

        pos.pos.y += movement.vel.y * core.dt.dt
        pos.rect.y = round(pos.pos.y)

        for neighboring_tile_rect in neighboring_tile_rects:
            if neighboring_tile_rect.colliderect(pos.rect):
                if movement.vel.y > 0:
                    pos.rect.bottom = neighboring_tile_rect.top
                    pos.pos.y = pos.rect.y
                    collide_bottom = True
                elif movement.vel.y < 0:
                    pos.rect.top = neighboring_tile_rect.bottom
                    pos.pos.y = pos.rect.y
                    movement.vel.y = 0
        return collide_bottom

    @staticmethod
    def collide_with_ramps(pos: Position, ramps: list[tuple[pygame.Rect, tile_component.Type]]):
        collide_bottom = False

        for ramp_rect, ramp_type in ramps:
            if ramp_rect.colliderect(pos.rect):
                rel_x = pos.pos.x - ramp_rect.x

                if ramp_type == tile_component.Type.RAMP_UP:
                    pos_height = rel_x + pos.rect.width
                else:
                    pos_height = ramp_rect.height - rel_x
                pos_height = min(max(pos_height, 0), ramp_rect.height)

                actual_y = ramp_rect.y + ramp_rect.height - pos_height
                if pos.rect.bottom > actual_y:
                    pos.rect.bottom = actual_y
                    pos.pos.y = pos.rect.y
                    collide_bottom = True

        return collide_bottom

    def process(self):
        # Mob
        for entity, (pos, movement, graphics) in self.world.get_components(Position, Movement, Graphics):
            neighboring_tile_entities = self.tilemap.get_neighboring_tile_entities(3, pos)
            neighboring_tile_rects = self.tilemap.get_unwalkable_rects(neighboring_tile_entities)
            neighboring_ramps = self.tilemap.get_ramps(neighboring_tile_entities)

            # Obvs, if it's gonna collide with player, player should be in it
            collide_with_player = not self.world.has_component(entity, NoCollidePlayer)
            if entity != self.player and collide_with_player:
                neighboring_tile_rects.append(self.component_for_player(Position).rect)

            # Player collides with collide_with_player entities
            # Player can also go on ramps
            if entity == self.player:
                # Still super inefficient
                for nested_entity, nested_pos in self.world.get_component(Position):
                    collide_with_player = not self.world.has_component(nested_entity, NoCollidePlayer)
                    if nested_entity != self.player and collide_with_player:
                        neighboring_tile_rects.append(nested_pos.rect)

            collide_bottom_tiles = self.collide_with_tiles(pos, movement, neighboring_tile_rects)
            collide_bottom_ramps = self.collide_with_ramps(pos, neighboring_ramps)
            if collide_bottom_tiles or collide_bottom_ramps:
                pos.on_ground = True
                movement.vel.y = 0

            pos.tile_pos = utils.pixel_to_tile(pos.pos)

        # Item pickup
        for entity, (item, item_pos, item_graphics) in self.world.get_components(
            item_component.Item,
            item_component.ItemPosition,
            item_component.ItemGraphics,
        ):
            owner_pos = self.component_for_player(Position)
            player_inventory = self.component_for_player(Inventory)
            player_rect = owner_pos.rect

            # Player collided with item
            if not item_pos.in_inventory and player_rect.colliderect(item_pos.rect):
                available_inventory_idx = player_inventory.get_available_idx()
                if available_inventory_idx is not None:
                    item.owner = self.player
                    item_pos.pos.x, item_pos.pos.y = item_pos.pos.x, item_pos.pos.y
                    item_pos.in_inventory = True

                    player_inventory[available_inventory_idx] = entity

                    self.notify("player_get_item", entity)
                else:
                    self.particle_manager.create_text_particle(owner_pos.pos, "No more room in inventory!")

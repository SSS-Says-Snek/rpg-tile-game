"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek

This file contains various utilities for entity AI
"""


from __future__ import annotations

import math

from src.entities.components.component import Movement, Position
from src.tilemap import TileMap
from src.utils import enum_eq


class EntityState:
    """Contains states for actions for entities that have >1 state"""

    @enum_eq
    class Patrol:
        def __init__(self, patrol_speed: float):
            self.patrol_speed = patrol_speed

        def patrol(self, tilemap: TileMap, pos: Position, movement: Movement):
            movement.vel.x = self.patrol_speed * pos.direction

            tile_next_beneath = tilemap.get_tile(
                pos.tile_pos.x + math.copysign(1, movement.vel.x),
                pos.tile_pos.y + 1,
            )
            tile_next = tilemap.get_tile(pos.tile_pos.x + math.copysign(1, pos.direction), pos.tile_pos.y)

            if tile_next or not tile_next_beneath:
                if not (tile_next is not None and not tile_next.get("unwalkable")):
                    pos.direction *= -1

    @enum_eq
    class Flee:
        def __init__(self, flee_speed: float, flee_time: int):
            self.flee_speed = flee_speed
            self.flee_time = flee_time

            self.flee_start_time = 0

    @enum_eq
    class Follow:
        pass

    def __init__(self, available_states: list, starting_state: type):
        self.available_states = {type(state): state for state in available_states}
        self._state = self.available_states[starting_state]

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, enum):
        self._state = self.available_states[enum]


class FollowsEntityClose:
    def __init__(self, entity: int, follow_range: int):
        self.entity_followed = entity
        self.follow_range = follow_range


class BackAndForthMovement:
    def __init__(self):
        pass


class MeleeWeaponAttack:
    def __init__(self, attack_range: int):
        self.attack_range = attack_range

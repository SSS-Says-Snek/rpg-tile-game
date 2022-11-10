"""
This file is a part of the source code for rpg-tile-game
This project has been licensed under the MIT license.
Copyright (c) 2022-present SSS-Says-Snek
"""


from __future__ import annotations


class EntityState:
    """Contains states for actions for entities that have >1 state"""

    PATROL = 1
    FOLLOW = 2

    def __init__(self, default_state):
        self.state = default_state


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

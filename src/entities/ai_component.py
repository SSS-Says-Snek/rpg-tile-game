class FollowsEntityClose:
    def __init__(self, entity: int, follow_range: int):
        self.entity_followed = entity
        self.follow_range = follow_range


class MeleeWeaponAttack:
    def __init__(self, attack_range: int):
        self.attack_range = attack_range

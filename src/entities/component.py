__all__ = ["HasDialogue", "Tile", "Collidable", "Graphics", "Position", "Velocity"]

from src import utils


class HasDialogue:
    def __init__(self):
        pass


class Collidable:
    def __init__(self):
        pass


class Tile:
    def __init__(self, tile_width, tile_height):
        self.tile_width = tile_width
        self.tile_height = tile_height


class Graphics:
    def __init__(self, sprite):
        self.sprite = sprite
        self.size = self.sprite.get_size()


class Position:
    def __init__(self, pos):
        self.pos = pos
        self.tile_pos = utils.pixel_to_tile(pos)
        self.facing = None


class Velocity:
    def __init__(self, vx=0, vy=0):
        self.vx = vx
        self.vy = vy

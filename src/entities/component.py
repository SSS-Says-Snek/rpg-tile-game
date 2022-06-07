__all__ = ["Flags", "Tile", "Graphics", "Position", "Movement"]

from src import utils


class Flags:
    def __init__(self, has_dialogue=False, collidable=False, rotatable=False):
        self.has_dialogue = has_dialogue
        self.collidable = collidable
        self.rotatable = rotatable


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


class Movement:
    def __init__(self, speed, vx=0, vy=0, acc=0, rot=0):
        self.speed = speed
        self.vx = vx
        self.vy = vy

        self.acc = acc
        self.rot = rot

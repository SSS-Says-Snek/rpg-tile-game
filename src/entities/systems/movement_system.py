import esper

from src.entities.components.velocity import Velocity
from src.entities.components.position import Position

class MovementSystem(esper.Processor):
    def __init__(self, level_state):
        super().__init__()
        self.level_state = level_state

    def process(self):
        for entity, (vel, pos) in self.world.get_components(Velocity, Position):
            pos.pos[0] += vel.vx * self.level_state.game_class.dt
            pos.pos[1] += vel.vy * self.level_state.game_class.dt
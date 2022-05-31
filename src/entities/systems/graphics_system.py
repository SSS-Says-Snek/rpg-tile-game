import esper

from src import screen
from src.entities.components.graphics import Graphics
from src.entities.components.position import Position


class GraphicsSystem(esper.Processor):
    def __init__(self, level_state):
        super().__init__()
        self.level_state = level_state

    def process(self):
        for entity, (graphics, pos) in self.world.get_components(Graphics, Position):
            self.level_state.camera.adjust_to(pos.pos)
            screen.blit(graphics.sprite, self.level_state.camera.apply(pos.pos))
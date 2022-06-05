from src import screen
from src.entities.systems.system import System
from src.entities.component import Graphics, Position


class GraphicsSystem(System):
    def __init__(self, level_state):
        super().__init__(level_state)

    def process(self, event_list):
        # super().process(event_list)

        for entity, (graphics, pos) in self.world.get_components(Graphics, Position):
            self.level_state.camera.adjust_to(pos.pos)
            screen.blit(graphics.sprite, self.level_state.camera.apply(pos.pos))
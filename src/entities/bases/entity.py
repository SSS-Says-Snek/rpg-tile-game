import abc

class Entity(abc.ABC):
    def __init__(self, game_class, level_state):
        self.game_class = game_class
        self.level_state = level_state

    @abc.abstractmethod
    def draw(self, camera):
        pass

    @abc.abstractmethod
    def handle_event(self, event):
        pass

    def update(self):
        pass

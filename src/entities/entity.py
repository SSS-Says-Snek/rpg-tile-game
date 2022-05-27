import abc

class Entity(abc.ABC):
    def __init__(self, game_class, state):
        self.game_class = game_class
        self.state = state

    @abc.abstractmethod
    def draw(self, camera):
        pass

    @abc.abstractmethod
    def handle_event(self, event):
        pass

    def update(self):
        pass

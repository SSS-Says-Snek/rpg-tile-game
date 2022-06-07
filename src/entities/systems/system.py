import esper

class System(esper.Processor):
    def __init__(self, level_state):
        super().__init__()

        self.level_state = level_state
        self.player = self.level_state.player

    def process(self, event_list):
        # self.event_list = event_list
        pass

class UI:
    def __init__(self, camera):
        self.camera = camera
        self.widgets = []

    def draw(self):
        for widget in self.widgets:
            if self.camera is not None:
                widget.draw(self.camera)
            else:
                widget.draw()

    def add_widget(self, widget):
        self.widgets.append(widget)

    def remove_widget(self, widget):
        self.widgets.remove(widget)

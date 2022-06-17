class UI:
    def __init__(self, camera):
        self.current_widget_uuid = 0

        self.camera = camera
        self.world = None
        self.widgets = {}
        self.hud_widgets = {}

    def draw(self):
        for widget in self.widgets.copy().values():
            if self.camera is not None:
                widget.draw(self.camera)
            else:
                widget.draw()

    def add_widget(self, widget, hud=False, hud_name=None):
        widget.uuid = self.current_widget_uuid
        self.widgets[self.current_widget_uuid] = widget
        if hud and hud_name:
            self.hud_widgets[hud_name] = widget

        self.current_widget_uuid += 1
        return widget.uuid

    def remove_widget(self, uuid):
        del self.widgets[uuid]

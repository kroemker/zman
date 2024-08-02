from abc import abstractmethod


class BaseView:
    def __init__(self, name, config, visible=False):
        self.name = name
        self.config = config
        self.visible = visible

    def render(self):
        if self.visible:
            self.render_internal()

    @abstractmethod
    def render_internal(self):
        raise NotImplementedError

    @abstractmethod
    def update(self):
        raise NotImplementedError

    def show(self):
        self.visible = True
        self.update()

    def hide(self):
        self.visible = False

from abc import abstractmethod

import imgui

window_id = 0


class BaseWindow:
    def __init__(self, name, config, on_destroy=None):
        self.name = name + "###" + str(get_next_window_id())
        self.config = config
        self.on_destroy = on_destroy

    def render(self):
        _, opened = imgui.begin(self.name, True, imgui.WINDOW_ALWAYS_AUTO_RESIZE)
        if not opened:
            self.destroy()
        else:
            self.render_internal()
        imgui.end()

    def destroy(self):
        if self.on_destroy:
            self.on_destroy(self)

    @abstractmethod
    def render_internal(self):
        raise NotImplementedError


def get_next_window_id():
    global window_id
    window_id += 1
    return window_id

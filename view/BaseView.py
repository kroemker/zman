from abc import abstractmethod

import imgui


class BaseView:
    def __init__(self, name, config, visible=False):
        self.name = name
        self.config = config
        self.visible = visible

    def render(self):
        if self.visible:
            _, self.visible = imgui.begin(self.name, True, imgui.WINDOW_MENU_BAR)
            self.__render_menu()
            self.render_internal()
            imgui.end()

    def __render_menu(self):
        if imgui.begin_menu_bar():
            if imgui.begin_menu("Actions"):
                _, clicked = imgui.menu_item("Refresh")
                if clicked:
                    self.update()
                imgui.end_menu()
            imgui.end_menu_bar()

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

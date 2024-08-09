from abc import abstractmethod

import imgui

from BaseWindow import BaseWindow


class BaseView(BaseWindow):
    def __init__(self, name, config, visible=False, menu=True):
        super().__init__(name, config)
        self.visible = visible
        self.menu = menu

    def render(self):
        if self.visible:
            _, self.visible = imgui.begin(self.name, True, imgui.WINDOW_MENU_BAR if self.menu else 0)
            if self.menu:
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
    def update(self):
        raise NotImplementedError

    def show(self):
        self.visible = True
        self.update()

    def hide(self):
        self.visible = False

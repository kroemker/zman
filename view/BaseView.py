﻿from abc import abstractmethod

import imgui

from BaseWindow import BaseWindow


class BaseView(BaseWindow):
    def __init__(self, name, config, visible=False, menu=True):
        super().__init__(name, config)
        self.visible = visible
        self.menu = menu
        self.child_windows = []
        self.menu_actions = [{"name": "Refresh", "on_click": self.update}]

    def render(self):
        if self.visible:
            _, self.visible = imgui.begin(self.name, True, imgui.WINDOW_MENU_BAR if self.menu else 0)
            if self.menu:
                self.__render_menu()
            self.render_internal()
            imgui.end()
            for window in self.child_windows:
                window.render()

    def __render_menu(self):
        if imgui.begin_menu_bar():
            if imgui.begin_menu("Actions"):
                for action in self.menu_actions:
                    _, clicked = imgui.menu_item(action["name"])
                    if clicked:
                        action["on_click"]()
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

    def add_child_window(self, window):
        self.child_windows.append(window)

    def remove_child_window(self, window):
        self.child_windows.remove(window)

    def add_menu_action(self, name, on_click):
        self.menu_actions.append({"name": name, "on_click": on_click})

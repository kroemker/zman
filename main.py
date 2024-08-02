#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import sys

import OpenGL.GL as gl
import imgui
import pygame
from imgui.integrations.pygame import PygameRenderer

from config import Config
from view.ActorView import ActorView
from view.InventoryView import InventoryView
from view.SpecView import SpecView


class MainWindow:
    def __init__(self):
        pygame.init()
        size = 1024, 800
        pygame.display.set_mode(size, pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
        pygame.display.set_caption("ZMan")
        imgui.create_context()
        self.renderer = PygameRenderer()
        io = imgui.get_io()
        io.display_size = size
        self.show_custom_window = True
        self.config = Config("\\\\wsl.localhost\\Ubuntu\\home\\leo\\oot")
        self.views = [
            SpecView(self.config),
            ActorView(self.config),
            InventoryView(self.config),
        ]

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            self.renderer.process_event(event)
        self.renderer.process_inputs()

        imgui.new_frame()

        self.menu()

        self.render_views()

        imgui.show_test_window()

        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        self.renderer.render(imgui.get_draw_data())

        pygame.display.flip()

    def menu(self):
        if imgui.begin_main_menu_bar():
            if imgui.begin_menu("File", True):
                clicked_quit, selected_quit = imgui.menu_item("Quit", "Cmd+Q", False, True)
                if clicked_quit:
                    sys.exit(0)
                imgui.end_menu()
            if imgui.begin_menu("Views", True):
                for view in self.views:
                    clicked_view, selected_view = imgui.menu_item(view.name, "", False, True)
                    if clicked_view:
                        view.show()
                imgui.end_menu()
            imgui.end_main_menu_bar()

    def render_views(self):
        for view in self.views:
            view.render()


def main():
    window = MainWindow()
    while True:
        window.render()


if __name__ == "__main__":
    main()

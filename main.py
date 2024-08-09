#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import

import sys

import OpenGL.GL as gl
import imgui
import pygame
from imgui.integrations.pygame import PygameRenderer

from config import Config
from tools.CreateActorTool import CreateActorTool
from view.ActorView import ActorView
from view.ConfigView import ConfigView
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
            ConfigView(self.config),
            SpecView(self.config),
            ActorView(self.config),
            InventoryView(self.config),
        ]
        self.tools = [{
            "name": "Create Actor",
            "create": lambda: CreateActorTool(self.config, lambda window: self.windows.remove(window))
        }]
        self.windows = []
        self.windows.extend(self.views)

    def render(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit(0)
            self.renderer.process_event(event)
        self.renderer.process_inputs()

        imgui.new_frame()

        self.render_menu()

        self.render_windows()

        imgui.show_test_window()

        gl.glClearColor(0, 0, 0, 1)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        imgui.render()
        self.renderer.render(imgui.get_draw_data())

        pygame.display.flip()

    def render_menu(self):
        if imgui.begin_main_menu_bar():
            self.render_menu_item_section("View", self.views, lambda view: view.name, lambda view: view.show())
            self.render_menu_item_section("Tools", self.tools, lambda tool: tool["name"],
                                          lambda tool: self.windows.append(tool["create"]()))
            imgui.end_main_menu_bar()

    def render_menu_item_section(self, name, items, on_name, on_click):
        if imgui.begin_menu(name):
            for item in items:
                clicked_item, selected_item = imgui.menu_item(on_name(item), "", False, True)
                if clicked_item:
                    on_click(item)
            imgui.end_menu()

    def render_windows(self):
        for window in self.windows:
            window.render()


def main():
    window = MainWindow()
    while True:
        window.render()


if __name__ == "__main__":
    main()

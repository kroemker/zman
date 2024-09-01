import os

import imgui

from util.StringUtil import get_flags
from view.ActorEditWindow import ActorEditWindow
from view.BaseView import BaseView


class ActorView(BaseView):
    def __init__(self, config):
        super().__init__("Actors", config)
        self.actors = []
        self.show_by_descriptive_name = True
        self.name_filter = ""
        self.category_values = [category.name for category in self.config.actor_categories]
        self.category_values.append("All")
        self.category_filter = len(self.config.actor_categories)
        self.showEditWindow = False

    def render_internal(self):
        self.__render_menu()
        for actor in self.actors:
            list_name, tooltip_name = self.__get_actor_names(actor)
            if self.name_filter.lower() not in list_name.lower() and self.name_filter.lower() not in tooltip_name.lower():
                continue
            actor_category = self.config.get_cenum_by_constant(self.config.actor_categories, actor["category"])
            if (self.category_filter < len(self.config.actor_categories) and (
                    actor_category is None or
                    self.category_values[self.category_filter] != actor_category.name)):
                continue
            if imgui.tree_node(list_name, imgui.TREE_NODE_FRAMED):
                if tooltip_name != "" and imgui.is_item_hovered(imgui.HOVERED_ANY_WINDOW):
                    imgui.begin_tooltip()
                    imgui.text(tooltip_name)
                    imgui.end_tooltip()
                imgui.text("Variable: " + actor["variable"])
                imgui.text("Category: " + actor_category.name if actor_category is not None else "?")
                imgui.text("Flags: " + ", ".join(
                    [self.config.get_cenum_by_constant(self.config.actor_flags, flag).name for flag in actor["flags"]]))
                imgui.text("Object: " + actor["object"])
                if imgui.button("Edit"):
                    self.add_child_window(ActorEditWindow(self.config, actor, self.remove_child_window))
                imgui.tree_pop()

    def __render_menu(self):
        if imgui.begin_menu_bar():
            if imgui.begin_menu("Options"):
                _, self.show_by_descriptive_name = imgui.checkbox("Show by descriptive name",
                                                                  self.show_by_descriptive_name)
                _, self.name_filter = imgui.input_text("Name Filter", self.name_filter, 256)
                imgui.same_line()
                if imgui.button("Clear"):
                    self.name_filter = ""
                _, self.category_filter = imgui.combo("Category Filter", self.category_filter, self.category_values)
                imgui.end_menu()
            imgui.end_menu_bar()

    def update(self):
        self.actors = []
        for root, dirs, files in os.walk(self.config.oot_decomp_path + "/src/overlays/actors"):
            for directory in dirs:
                if directory == "ovl_player_actor":
                    c_file = root + "/" + directory + "/" + "z_player.c"
                else:
                    c_file = root + "/" + directory + "/" + directory.lower().replace("ovl_", "z_") + ".c"
                with open(c_file, "r", encoding="utf-8") as f:
                    content = f.read()
                actor = self.__parse_actor(c_file, directory, content)
                self.actors.append(actor)

    def __parse_actor(self, c_file, directory, content):
        actor = {}
        actor["c_file"] = c_file
        actor["name"] = directory
        actor["descriptive_name"] = self.__parse_descriptive_name(content)
        actor["variable"], actor["category"], actor["flags"], actor["object"] = self.parse_profile(directory,
                                                                                                   content)
        return actor

    def __parse_descriptive_name(self, content):
        if not content.startswith("/*"):
            return ""
        comment_lines = content[2:].split("*/")[0].strip().split("\n")
        for line in comment_lines:
            line = line.strip()[2:]
            if line.startswith("Description: "):
                return line[len("Description: "):].strip()
        return ""

    def parse_profile(self, name, content):
        start = content.find("ActorProfile ")
        end = content.find("};", start)
        if start == -1 or end == -1:
            print("No actor profile found for actor " + name)
            return ["", "", "", ""]
        lines = content[start:end].split("\n")
        profile = []
        i = 1
        while len(profile) < 4:
            line = lines[i].replace("/**/", "").replace(",", "").strip()
            i += 1
            if line.startswith("//"):
                continue
            profile.append(line)
        profile[2] = self.__parse_flags(content, profile[2])
        return profile

    def __parse_flags(self, content, flags):
        start = content.find("#define " + flags + " ") + len(flags) + len("#define  ")
        end = content.find("\n", start)
        if content == -1:
            return []
        return get_flags(content[start:end])

    def __get_actor_names(self, actor):
        if self.show_by_descriptive_name and actor["descriptive_name"] != "":
            return actor["descriptive_name"], actor["name"]
        else:
            return actor["name"], actor["descriptive_name"]

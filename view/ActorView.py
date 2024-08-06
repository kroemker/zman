import os

import imgui

from view.BaseView import BaseView


class ActorView(BaseView):
    def __init__(self, config):
        super().__init__("Actors", config)
        self.actors = []
        self.show_by_descriptive_name = True
        self.name_filter = ""
        self.category_mapping = {
            "ACTORCAT_SWITCH": "Switch",
            "ACTORCAT_BG": "Background",
            "ACTORCAT_PLAYER": "Player",
            "ACTORCAT_EXPLOSIVE": "Explosives",
            "ACTORCAT_NPC": "NPC",
            "ACTORCAT_ENEMY": "Enemy",
            "ACTORCAT_PROP": "Prop",
            "ACTORCAT_ITEMACTION": "Item/Action",
            "ACTORCAT_MISC": "Misc",
            "ACTORCAT_BOSS": "Boss",
            "ACTORCAT_DOOR": "Door",
            "ACTORCAT_CHEST": "Chest"
        }
        self.category_values = list(self.category_mapping.values())
        self.category_values.append("All")
        self.category_filter = len(self.category_mapping)

    def render_internal(self):
        self.__render_menu()
        for actor in self.actors:
            list_name, tooltip_name = self.__get_actor_names(actor)
            if self.name_filter.lower() not in list_name.lower() and self.name_filter.lower() not in tooltip_name.lower():
                continue
            if (self.category_filter < len(self.category_mapping) and (
                    actor["category"] not in self.category_mapping or
                    self.category_values[self.category_filter] != self.category_mapping[actor["category"]])):
                continue
            if imgui.tree_node(list_name, imgui.TREE_NODE_FRAMED):
                imgui.text("Variable: " + actor["variable"])
                imgui.text("Category: " + self.category_mapping[actor["category"]])
                imgui.text("Flags: " + str(actor["flags"]))
                imgui.text("Object: " + actor["object"])
                if tooltip_name != "" and imgui.is_item_hovered(imgui.HOVERED_ANY_WINDOW):
                    imgui.begin_tooltip()
                    imgui.text(tooltip_name)
                    imgui.end_tooltip()
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
        for root, dirs, files in os.walk(self.config.decomp_path + "/src/overlays/actors"):
            for directory in dirs:
                if directory == "ovl_player_actor":
                    c_file = root + "/" + directory + "/" + "z_player.c"
                else:
                    c_file = root + "/" + directory + "/" + directory.lower().replace("ovl_", "z_") + ".c"
                with open(c_file, "r", encoding="utf-8") as f:
                    content = f.read()
                actor = self.__parse_actor(directory, content)
                self.actors.append(actor)

    def __parse_actor(self, directory, content):
        actor = {}
        actor["name"] = directory
        actor["descriptive_name"] = self.__parse_descriptive_name(content)
        actor["variable"], actor["category"], actor["flags"], actor["object"] = self.__parse_init_vars(directory,
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

    def __parse_init_vars(self, name, content):
        start = content.find("ActorInit ")
        end = content.find("};", start)
        if start == -1 or end == -1:
            print("No actor init vars found for actor " + name)
            return ["", "", "", ""]
        lines = content[start:end].split("\n")
        init_vars = []
        i = 1
        while len(init_vars) < 4:
            line = lines[i].replace("/**/", "").replace(",", "").strip()
            i += 1
            if line.startswith("//"):
                continue
            init_vars.append(line)
        init_vars[2] = self.__parse_flags(content, init_vars[2])
        return init_vars

    def __parse_flags(self, content, flags):
        start = content.find("#define " + flags + " ") + len(flags) + len("#define  ")
        end = content.find("\n", start)
        if content == -1:
            return []
        flags = list(map(lambda x: x.strip(), content[start:end].strip("()").split("|")))
        if len(flags) == 1 and flags[0] == "0":
            return []
        return flags

    def __get_actor_names(self, actor):
        if self.show_by_descriptive_name and actor["descriptive_name"] != "":
            return actor["descriptive_name"], actor["name"]
        else:
            return actor["name"], actor["descriptive_name"]

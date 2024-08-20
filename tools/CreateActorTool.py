import os

import imgui

from BaseWindow import BaseWindow
from util.CEnumValue import CEnumValue
from util.ImguiUtil import add_tooltip


# Possible features:
# - init chain
# - Collider generator
# - Collision support
# - Damage Table
# - Dynapoly setup
# - NPC Message tree

class CreateActorTool(BaseWindow):
    def __init__(self, config, on_destroy):
        super().__init__("Create Actor", config, on_destroy=on_destroy)
        self.actor_name = ""
        self.description = ""
        self.allocation_types = [
            CEnumValue("ACTOROVL_ALLOC_NORMAL", "Normal", "The overlay is loaded and unloaded as needed."),
            CEnumValue("ACTOROVL_ALLOC_PERSISTENT", "Persistent", "The overlay is loaded persistently."),
            CEnumValue("ACTOROVL_ALLOC_ABSOLUTE", "Absolute",
                       "The overlay is loaded to a fixed memory region. Only one absolute overlay can be loaded at a "
                       "time."),
        ]
        self.allocation_type = 0
        self.prefer_overriding_unset_actors = True
        self.category = 0
        self.object_names, self.object_variables = self.config.parse_object_table()
        self.object_variable = 0
        self.actor_flags = {}
        self.actor_draw_enabled = True
        self.has_skeleton = False
        self.skeleton = 0
        self.possible_skeletons = []
        self.initial_animation = 0
        self.action_funcs = []
        self.possible_animations = []
        self.update_object_file_data()

    def render_internal(self):
        _, self.actor_name = imgui.input_text("Actor Name", self.actor_name, 256)
        add_tooltip("The name of the actor to create without any prefix, e.g. 'Obj_Bombiwa' or 'En_Test'.")
        _, self.description = imgui.input_text("Description", self.description, 256)
        add_tooltip("A short description of the actor.")

        imgui.separator()
        imgui.text("Overlay Settings")
        _, self.allocation_type = imgui.combo("Allocation Type", self.allocation_type,
                                              [allocation_type.name for allocation_type in self.allocation_types])
        add_tooltip(self.build_tooltip_from_cenum_list("Overlay allocation type", self.allocation_types))
        _, self.prefer_overriding_unset_actors = imgui.checkbox("Prefer Overriding Unset Actors",
                                                                self.prefer_overriding_unset_actors)
        add_tooltip(
            "If enabled, an entry in the actor table will be overridden if it is unset.\nThis leads to new actors being "
            "fragmented in the actor table,\nbut keeps the actor table the same size as long as there are enough "
            "unset slots.")

        imgui.separator()
        imgui.text("Profile")
        _, self.category = imgui.combo("Category", self.category,
                                       [category.name for category in self.config.actor_categories])
        add_tooltip(self.build_tooltip_from_cenum_list("Actor category", self.config.actor_categories))
        changed_object, self.object_variable = imgui.combo("Object", self.object_variable, self.object_variables)
        if changed_object:
            self.update_object_file_data()
        add_tooltip(
            "The object contains the actor's additional resources such as model, textures etc..\nIt is loaded when "
            "the actor is spawned unless it is already loaded.\nThis is always the case for OBJECT_GAMEPLAY_KEEP.\n"
            "OBJECT_GAMEPLAY_FIELD_KEEP and OBJECT_DANGEON_KEEP are automatically\nloaded if a overworld or dungeon "
            "scene is active respectively.")
        self.render_actor_flag_checkboxes()
        _, self.actor_draw_enabled = imgui.checkbox("Draw Enabled", self.actor_draw_enabled)
        add_tooltip("If disabled, the actor will not have a draw function (i.e. will not be drawn).")
        _, self.has_skeleton = imgui.checkbox("Has Skeleton", self.has_skeleton)
        add_tooltip("If enabled, the actor will have a skeleton and can be animated.")
        if self.has_skeleton:
            _, self.skeleton = imgui.combo("Skeleton", self.skeleton,
                                           [skel["name"] for skel in self.possible_skeletons])
            _, self.initial_animation = imgui.combo("Initial Animation", self.initial_animation,
                                                    self.possible_animations)
            add_tooltip("The initial animation to play when the actor is spawned.")

        imgui.separator()
        imgui.text("Action Functions")
        self.render_action_function_list()

        if imgui.button("Create") and self.is_valid():
            self.create_actor()
            self.destroy()
        if not self.is_valid():
            imgui.text_colored("Please fill out all required fields.", 1, 0, 0)

    def render_actor_flag_checkboxes(self):
        if imgui.tree_node("Actor Flags", imgui.TREE_NODE_FRAMED):
            for actor_flag in self.config.actor_flags:
                if actor_flag.constant not in self.actor_flags:
                    self.actor_flags[actor_flag.constant] = False
                _, self.actor_flags[actor_flag.constant] = imgui.checkbox(actor_flag.name,
                                                                          self.actor_flags[actor_flag.constant])
                add_tooltip(actor_flag.description)
            imgui.tree_pop()

    def render_action_function_list(self):
        i = 0
        for action_func in self.action_funcs:
            if i > 0:
                imgui.separator()
            _, action_func["name"] = imgui.input_text("Name##" + str(i), action_func["name"], 256)
            imgui.same_line(imgui.get_window_width() - 30)
            if imgui.button("X##" + str(i)):
                self.action_funcs.remove(action_func)
            _, action_func["animation"] = imgui.combo("Animation##" + str(i), action_func["animation"],
                                                      self.possible_animations)
            _, action_func["animation_speed"] = imgui.slider_float("Speed##" + str(i), action_func["animation_speed"],
                                                                   0, 3, "%.1f")
            imgui.same_line()
            _, action_func["animation_looped"] = imgui.checkbox("Looped##" + str(i), action_func["animation_looped"])
            i += 1

        if imgui.button("+"):
            self.action_funcs.append({"name": "", "animation": 0, "animation_looped": False, "animation_speed": 1.0})

    def build_tooltip_from_cenum_list(self, description, cenum_list):
        tooltip = description
        if len(cenum_list) > 0:
            tooltip += "\n\n"
            for value in cenum_list:
                tooltip += f"{value.name}: {value.description}\n"
        return tooltip

    def is_valid(self):
        return self.actor_name != ""

    def update_object_file_data(self):
        object_name = self.object_names[self.object_variable]
        self.possible_animations, self.possible_skeletons = self.config.parse_object_file(object_name)

    def create_actor(self):
        self.create_spec_entry()
        self.create_actor_variable()
        self.create_actor_file()
        print("Create actor " + self.actor_name)

    def create_spec_entry(self):
        with open(self.config.spec_path, "r") as f:
            spec_content = f.read()
        ovl_section_start = spec_content.find("beginseg\n    name \"ovl_title\"")
        if ovl_section_start == -1:
            raise Exception("Overlay section not found in spec file")
        spec_entry = f"beginseg\n" \
                     f"    name \"ovl_{self.actor_name}\"\n" \
                     f"    compress\n" \
                     f"    include \"$(BUILD_DIR)/src/overlays/actors/ovl_{self.actor_name}/z_{self.actor_name.lower()}.o\"\n" \
                     f"    include \"$(BUILD_DIR)/src/overlays/actors/ovl_{self.actor_name}/ovl_{self.actor_name}_reloc.o\"\n" \
                     f"endseg\n\n"
        spec_content = spec_content[:ovl_section_start] + spec_entry + spec_content[ovl_section_start:]
        with open(self.config.spec_path, "w") as f:
            f.write(spec_content)

    def create_actor_variable(self):
        with open(self.config.actor_table_path, "r") as f:
            actor_table_content = f.read()
        actor_table_entry = f"DEFINE_ACTOR({self.actor_name}, {self.get_actor_variable()}, " \
                            f"{self.allocation_types[self.allocation_type].constant}, \"{self.actor_name}\")"
        unset_actor_start = actor_table_content.find("DEFINE_ACTOR_UNSET(")
        if self.prefer_overriding_unset_actors and unset_actor_start != -1:
            unset_actor_end = actor_table_content.find(")", unset_actor_start) + 1
            actor_table_content = (actor_table_content[:unset_actor_start]
                                   + actor_table_entry
                                   + actor_table_content[unset_actor_end:])
        else:
            actor_table_content += actor_table_entry + "\n"
        with open(self.config.actor_table_path, "w") as f:
            f.write(actor_table_content)

    def create_actor_file(self):
        actor_file_dir = self.config.oot_decomp_path + f"/src/overlays/actors/ovl_{self.actor_name}"
        actor_file_path = actor_file_dir + f"/z_{self.actor_name.lower()}"
        os.makedirs(actor_file_dir, exist_ok=True)
        with open(actor_file_path + ".h", "w") as f:
            f.write(self.build_actor_h_file())
        with open(actor_file_path + ".c", "w") as f:
            f.write(self.build_actor_c_file())

    def build_actor_h_file(self):
        h_file = f"#ifndef _Z_{self.actor_name.upper()}_H_\n" \
                 f"#define _Z_{self.actor_name.upper()}_H_\n\n" \
                 f"#include <ultra64.h>\n" \
                 f"#include <global.h>\n\n" \
                 f"struct {self.actor_name_no_underscores()};\n\n" \
                 f"typedef void (*{self.actor_name_no_underscores()}ActionFunc)(struct {self.actor_name_no_underscores()}*, PlayState*);\n\n" \
                 f"typedef struct {self.actor_name_no_underscores()} {{\n" \
                 f"    Actor actor;\n"
        if self.has_skeleton:
            skeleton = self.possible_skeletons[self.skeleton]
            h_file += f"    SkelAnime skelAnime;\n" \
                      f"    Vec3s jointTable[{skeleton["limb_count"]}];\n" \
                      f"    Vec3s morphTable[{skeleton["limb_count"]}];\n"
        h_file += f"    {self.actor_name_no_underscores()}ActionFunc actionFunc;\n"
        h_file += f"}} {self.actor_name_no_underscores()};\n\n" \
                  f"#endif\n"
        return h_file

    def build_actor_c_file(self):
        actor_flags = " | ".join([flag for flag, enabled in self.actor_flags.items() if enabled])
        action_func_declarations = "\n".join([
            f"void {self.actor_name_no_underscores()}_Action_{action_func['name']}({self.actor_name_no_underscores()}* this, PlayState* play);"
            for action_func in self.action_funcs])
        actor_profile = f"ActorProfile {self.actor_name}_Profile = {{\n" \
                        f"    /**/ {self.get_actor_variable()},\n" \
                        f"    /**/ {self.config.actor_categories[self.category].constant},\n" \
                        f"    /**/ FLAGS,\n" \
                        f"    /**/ {self.object_variables[self.object_variable]},\n" \
                        f"    /**/ sizeof({self.actor_name_no_underscores()}),\n" \
                        f"    /**/ {self.actor_name_no_underscores()}_Init,\n" \
                        f"    /**/ {self.actor_name_no_underscores()}_Destroy,\n" \
                        f"    /**/ {self.actor_name_no_underscores()}_Update,\n"
        if self.actor_draw_enabled:
            actor_profile += f"    /**/ {self.actor_name_no_underscores()}_Draw,\n"
        else:
            actor_profile += f"    /**/ NULL,\n"
        actor_profile += f"}};\n\n"

        c_file = f"/*\n" \
                 f" * File: z_{self.actor_name.lower()}.c\n" \
                 f" * Overlay: ovl_{self.actor_name}\n" \
                 f" * Description: {self.description}\n" \
                 f" */\n\n" \
                 f"#include \"z_{self.actor_name.lower()}.h\"\n" \
                 f"#include \"assets/objects/{self.object_names[self.object_variable]}/{self.object_names[self.object_variable]}.h\"\n\n" \
                 f"#define FLAGS ({actor_flags})\n\n" \
                 f"void {self.actor_name_no_underscores()}_Init(Actor* thisx, PlayState* play);\n" \
                 f"void {self.actor_name_no_underscores()}_Destroy(Actor* thisx, PlayState* play);\n" \
                 f"void {self.actor_name_no_underscores()}_Update(Actor* thisx, PlayState* play);\n"
        if self.actor_draw_enabled:
            c_file += f"void {self.actor_name_no_underscores()}_Draw(Actor* thisx, PlayState* play);\n"
        c_file += "\n" + action_func_declarations + "\n\n" + actor_profile

        c_file += f"void {self.actor_name_no_underscores()}_SetupAction({self.actor_name_no_underscores()}* this, PlayState* play, {self.actor_name_no_underscores()}ActionFunc actionFunc) {{\n" \
                  f"    this->actionFunc = actionFunc;\n\n"
        if self.has_skeleton:
            i = 0
            for action_func in self.action_funcs:
                if i > 0:
                    c_file += "    else "
                else:
                    c_file += "    "
                c_file += f"if (this->actionFunc == {self.actor_name_no_underscores()}_Action_{action_func['name']}) {{\n" \
                          f"        Animation_Change(&this->skelAnime, &{self.possible_animations[action_func["animation"]]}, {action_func["animation_speed"]}f, 0.0f, Animation_GetLastFrame(&{self.possible_animations[action_func["animation"]]}), {"ANIMMODE_LOOP" if action_func["animation_looped"] else "ANIMMODE_ONCE_INTERP"}, 4.0f);\n" \
                          f"    }}\n"
                i += 1
        c_file += f"}}\n\n"

        for action_func in self.action_funcs:
            c_file += f"void {self.actor_name_no_underscores()}_Action_{action_func['name']}({self.actor_name_no_underscores()}* this, PlayState* play) {{\n" \
                      f"}}\n\n"

        c_file += f"void {self.actor_name_no_underscores()}_Init(Actor* thisx, PlayState* play) {{\n" \
                  f"    {self.actor_name_no_underscores()}* this = ({self.actor_name_no_underscores()}*)thisx;\n"
        if self.has_skeleton:
            skeleton = self.possible_skeletons[self.skeleton]
            c_file += "    SkelAnime_Init"
            if skeleton["flex"]:
                c_file += "Flex"
            c_file += f"(play, &this->skelAnime, &{skeleton["name"]}, &{self.possible_animations[self.initial_animation]}, this->jointTable, this->morphTable, {skeleton["limb_count"]});\n"
        c_file += f"}}\n\n" \
                  f"void {self.actor_name_no_underscores()}_Destroy(Actor* thisx, PlayState* play) {{\n" \
                  f"    {self.actor_name_no_underscores()}* this = ({self.actor_name_no_underscores()}*)thisx;\n" \
                  f"}}\n\n" \
                  f"void {self.actor_name_no_underscores()}_Update(Actor* thisx, PlayState* play) {{\n" \
                  f"    {self.actor_name_no_underscores()}* this = ({self.actor_name_no_underscores()}*)thisx;\n" \
                  f"}}\n\n"
        if self.actor_draw_enabled:
            c_file += f"void {self.actor_name_no_underscores()}_Draw(Actor* thisx, PlayState* play) {{\n" \
                      f"    {self.actor_name_no_underscores()}* this = ({self.actor_name_no_underscores()}*)thisx;\n" \
                      f"}}\n\n"

        return c_file

    def actor_name_no_underscores(self):
        return self.actor_name.replace("_", "")

    def get_actor_variable(self):
        return f"ACTOR_{self.actor_name.upper()}"

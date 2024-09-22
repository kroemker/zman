import os

import imgui

from BaseWindow import BaseWindow
from util.CEnumValue import CEnumValue
from util.ImguiUtil import add_tooltip
from util.MessageList import MessageList
from util.RenderUtil import render_cenum_combo
from util.SpecUtil import create_overlay_spec_entry, create_object_spec_entry
from util.StringUtil import tab


# Possible features:
# - init chain
# - Collider generator
# - Collision support
# - Damage Table
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
        self.prefer_overriding_unset_entries = True
        self.category = 0
        self.object_names, self.object_variables = self.config.parse_object_table()
        self.object_variable = 0
        self.new_object = False
        self.new_object_name = ""
        self.generate_object_files = False
        self.actor_flags = {}
        self.actor_draw_enabled = True
        self.has_skeleton = False
        self.skeleton = 0
        self.possible_skeletons = []
        self.initial_animation = 0
        self.action_funcs = []
        self.possible_animations = []
        self.update_object_file_data()
        self.is_dynapoly = False
        self.dynapoly_update_position = False
        self.dynapoly_update_y_rotation = False
        self.messages = MessageList()

    def render_internal(self):
        _, self.actor_name = imgui.input_text("Actor Name", self.actor_name, 256)
        add_tooltip("The name of the actor to create without any prefix, e.g. 'Obj_Bombiwa' or 'En_Test'.")
        _, self.description = imgui.input_text("Description", self.description, 256)
        add_tooltip("A short description of the actor.")

        imgui.separator()
        imgui.text("Overlay Settings")
        _, self.allocation_type = render_cenum_combo("Allocation Type", self.allocation_type, self.allocation_types)
        add_tooltip(self.build_tooltip_from_cenum_list("Overlay allocation type", self.allocation_types))
        _, self.prefer_overriding_unset_entries = imgui.checkbox("Prefer Overriding Unset Entries",
                                                                 self.prefer_overriding_unset_entries)
        add_tooltip(
            "If enabled, an entry in the actor table (and object table if required) will be overridden if it is unset.\n"
            "This leads to new actors being fragmented in the actor table,but keeps the actor table the same size as\n"
            "long as there are enough unset slots.")

        imgui.separator()
        imgui.text("Profile")
        _, self.category = render_cenum_combo("Category", self.category, self.config.actor_categories)
        add_tooltip(self.build_tooltip_from_cenum_list("Actor category", self.config.actor_categories))
        _, self.new_object = imgui.checkbox("Create new Object", self.new_object)
        if self.new_object:
            _, self.generate_object_files = imgui.checkbox("Generate Object Files", self.generate_object_files)
            _, self.new_object_name = imgui.input_text("Object Name", self.new_object_name, 256)
            add_tooltip("The name of the new object to create (should start with 'object_')")
        else:
            changed_object, self.object_variable = imgui.combo("Object", self.object_variable, self.object_variables)
            if changed_object:
                self.update_object_file_data()
        add_tooltip(
            "The object contains the actor's graphical resources such as model, textures etc..\nIt is loaded when "
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
        imgui.text("Collision")
        _, self.is_dynapoly = imgui.checkbox("Dynamic Collision", self.is_dynapoly)
        add_tooltip(
            "If enabled, the actor will have dynamic collision.\nUse this for actors that should move Link around or "
            "update Link's rotation.")
        if self.is_dynapoly:
            _, self.dynapoly_update_position = imgui.checkbox("Update Position", self.dynapoly_update_position)
            _, self.dynapoly_update_y_rotation = imgui.checkbox("Update Y Rotation", self.dynapoly_update_y_rotation)
        imgui.separator()
        imgui.text("Action Functions")
        self.render_action_function_list()

        if imgui.button("Create") and self.is_valid():
            self.create_actor()
            self.destroy()
        self.messages.render()

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
            if self.has_skeleton:
                _, action_func["animation"] = imgui.combo("Animation##" + str(i), action_func["animation"],
                                                          self.possible_animations)
                _, action_func["animation_speed"] = imgui.slider_float("Speed##" + str(i),
                                                                       action_func["animation_speed"],
                                                                       0, 3, "%.1f")
                imgui.same_line()
                _, action_func["animation_looped"] = imgui.checkbox("Looped##" + str(i),
                                                                    action_func["animation_looped"])
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
        self.messages.clear()
        if self.actor_name == "":
            self.messages.add_message("Actor name is empty", MessageList.Error)
        if self.description == "":
            self.messages.add_message("Description is empty", MessageList.Warning)
        if self.new_object and self.new_object_name == "":
            self.messages.add_message("Object name is empty", MessageList.Error)
        if self.is_dynapoly and not self.dynapoly_update_position and not self.dynapoly_update_y_rotation:
            self.messages.add_message("Dynamic collision must update position and/or y rotation", MessageList.Error)
        return not self.messages.has_errors()

    def update_object_file_data(self):
        object_name = self.object_names[self.object_variable]
        self.possible_animations, self.possible_skeletons = self.config.parse_object_file(object_name)

    def create_actor(self):
        create_overlay_spec_entry(self.config, self.actor_name)
        if self.new_object:
            create_object_spec_entry(self.config, self.new_object_name)
            self.create_object_variable()
            if self.generate_object_files:
                self.create_object_files()
        self.create_actor_variable()
        self.create_actor_file()
        print("Create actor " + self.actor_name)

    def create_object_variable(self):
        with open(self.config.object_table_path, "r") as f:
            object_table_content = f.read()
        object_table_entry = f"DEFINE_OBJECT({self.new_object_name}, {self.new_object_name.upper()})"
        unset_object_start = object_table_content.find("DEFINE_OBJECT_UNSET(OBJECT_UNSET")
        if self.prefer_overriding_unset_entries and unset_object_start != -1:
            unset_object_end = object_table_content.find(")", unset_object_start) + 1
            object_table_content = (object_table_content[:unset_object_start]
                                    + object_table_entry
                                    + object_table_content[unset_object_end:])
        else:
            object_table_content += object_table_entry + "\n"
        with open(self.config.object_table_path, "w") as f:
            f.write(object_table_content)

    def create_object_files(self):
        object_file_dir = self.config.mod_assets_object_path + f"/{self.new_object_name}"
        object_file_path = object_file_dir + f"/{self.new_object_name}"
        os.makedirs(object_file_dir, exist_ok=True)
        with open(object_file_path + ".h", "w") as f:
            f.write(self.build_object_h_file(object_file_dir))
        with open(object_file_path + ".c", "w") as f:
            f.write(self.build_object_c_file(object_file_dir))

    def build_object_h_file(self, object_file_dir):
        h_files = [f for f in os.listdir(object_file_dir) if f.endswith(".h") and f != f"{self.new_object_name}.h"]
        h_file = f"#ifndef _Z_{self.new_object_name.upper()}_H_\n" \
                 f"#define _Z_{self.new_object_name.upper()}_H_\n\n"

        for h_file_name in h_files:
            h_file += f"#include \"{h_file_name}\"\n"

        h_file += "\n#endif\n"
        return h_file

    def build_object_c_file(self, object_file_dir):
        c_files = [f for f in os.listdir(object_file_dir) if f.endswith(".c") and f != f"{self.new_object_name}.c"]
        c_file = ""

        for c_file_name in c_files:
            c_file += f"#include \"{c_file_name}\"\n"

        return c_file

    def create_actor_variable(self):
        with open(self.config.actor_table_path, "r") as f:
            actor_table_content = f.read()
        actor_table_entry = f"DEFINE_ACTOR({self.actor_name}, {self.get_actor_variable()}, " \
                            f"{self.allocation_types[self.allocation_type].constant}, \"{self.actor_name}\")"
        unset_actor_start = actor_table_content.find("DEFINE_ACTOR_UNSET(")
        if self.prefer_overriding_unset_entries and unset_actor_start != -1:
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
                 f"typedef struct {self.actor_name_no_underscores()} {{\n"
        if self.is_dynapoly:
            h_file += tab(1) + f"DynaPolyActor dyna;\n"
        else:
            h_file += tab(1) + f"Actor actor;\n"
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
                        f"    /**/ {self.get_object_variable()},\n" \
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
                 f"#include \"z_{self.actor_name.lower()}.h\"\n"
        if self.new_object:
            c_file += f"#include \"assets/objects/{self.new_object_name}/{self.new_object_name}.h\"\n\n"
        else:
            c_file += f"#include \"assets/objects/{self.object_names[self.object_variable]}/{self.object_names[self.object_variable]}.h\"\n\n"
        c_file += f"#define FLAGS ({actor_flags})\n\n" \
                  f"void {self.actor_name_no_underscores()}_Init(Actor* thisx, PlayState* play);\n" \
                  f"void {self.actor_name_no_underscores()}_Destroy(Actor* thisx, PlayState* play);\n" \
                  f"void {self.actor_name_no_underscores()}_Update(Actor* thisx, PlayState* play);\n"
        if self.actor_draw_enabled:
            c_file += f"void {self.actor_name_no_underscores()}_Draw(Actor* thisx, PlayState* play);\n"
        c_file += "\n" + action_func_declarations + "\n\n" + actor_profile

        # Setup action function
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

        # Action functions
        for action_func in self.action_funcs:
            c_file += f"void {self.actor_name_no_underscores()}_Action_{action_func['name']}({self.actor_name_no_underscores()}* this, PlayState* play) {{\n" \
                      f"}}\n\n"

        # Init function
        c_file += f"void {self.actor_name_no_underscores()}_Init(Actor* thisx, PlayState* play) {{\n" \
                  f"    {self.actor_name_no_underscores()}* this = ({self.actor_name_no_underscores()}*)thisx;\n"
        if self.is_dynapoly:
            dynapoly_flags = []
            if self.dynapoly_update_position:
                dynapoly_flags.append("DYNA_TRANSFORM_POS")
            if self.dynapoly_update_y_rotation:
                dynapoly_flags.append("DYNA_TRANSFORM_ROT_Y")
            c_file += tab(1) + f"CollisionHeader* colHeader = NULL;\n\n"
            c_file += tab(1) + f"DynaPolyActor_Init(&this->dyna, {" | ".join(dynapoly_flags)});\n"
            c_file += tab(1) + f"CollisionHeader_GetVirtual(&{self.get_collision_header_name()}, &colHeader);\n"
            c_file += (tab(1)
                       + f"this->dyna.bgId = DynaPoly_SetBgActor(play, &play->colCtx.dyna, &this->dyna.actor, "
                         f"colHeader);\n")
        if self.has_skeleton:
            skeleton = self.possible_skeletons[self.skeleton]
            c_file += "    SkelAnime_Init"
            if skeleton["flex"]:
                c_file += "Flex"
            c_file += f"(play, &this->skelAnime, &{skeleton["name"]}, &{self.possible_animations[self.initial_animation]}, this->jointTable, this->morphTable, {skeleton["limb_count"]});\n"
        if len(self.action_funcs) > 0:
            c_file += "\n" + tab(
                1) + f"{self.actor_name_no_underscores()}_SetupAction(this, play, {self.actor_name_no_underscores()}_Action_{self.action_funcs[0]["name"]});\n"
        c_file += f"}}\n\n"

        # Destroy function
        c_file += f"void {self.actor_name_no_underscores()}_Destroy(Actor* thisx, PlayState* play) {{\n" \
                  f"    {self.actor_name_no_underscores()}* this = ({self.actor_name_no_underscores()}*)thisx;\n"
        if self.is_dynapoly:
            c_file += tab(1) + f"DynaPoly_DeleteBgActor(play, &play->colCtx.dyna, this->dyna.bgId);\n"
        c_file += f"}}\n\n"

        # Update function
        c_file += f"void {self.actor_name_no_underscores()}_Update(Actor* thisx, PlayState* play) {{\n" \
                  f"    {self.actor_name_no_underscores()}* this = ({self.actor_name_no_underscores()}*)thisx;\n\n" \
                  f"    this->actionFunc(this, play);\n" \
                  f"}}\n\n"

        # Draw function
        if self.actor_draw_enabled:
            c_file += f"void {self.actor_name_no_underscores()}_Draw(Actor* thisx, PlayState* play) {{\n" \
                      f"    {self.actor_name_no_underscores()}* this = ({self.actor_name_no_underscores()}*)thisx;\n" \
                      f"}}\n\n"

        return c_file

    def actor_name_no_underscores(self):
        return self.actor_name.replace("_", "")

    def get_actor_variable(self):
        return f"ACTOR_{self.actor_name.upper()}"

    def get_object_variable(self):
        return self.object_variables[self.object_variable] if not self.new_object else f"{self.new_object_name.upper()}"

    def get_collision_header_name(self):
        return self.new_object_name + "_collisionHeader" if self.new_object else "<INSERT_COLLISION_HEADER_VAR_HERE>"

import imgui

from BaseWindow import BaseWindow
from util.ImguiUtil import add_tooltip
from util.MessageList import MessageList
from util.SpecUtil import spec_entry_exists, create_overlay_spec_entry, \
    create_object_spec_entry, create_scene_spec_entry, create_room_spec_entry


class CreateSpecEntriesWindow(BaseWindow):
    def __init__(self, config, on_destroy):
        super().__init__("Create spec entries", config, on_destroy)
        self.spec_entry_type = 0
        self.spec_entry_types = ["Scene", "Room", "Overlay", "Object"]
        self.spec_name = ""
        self.sub_folder = 0
        self.sub_folders = ["", "dungeons", "overworld", "indoors", "shops", "misc", "test_levels"]
        self.number_of_rooms = 1
        self.messages = MessageList()

    def render_internal(self):
        _, self.spec_entry_type = imgui.combo("Entry type", self.spec_entry_type, self.spec_entry_types)
        _, self.spec_name = imgui.input_text("Name", self.spec_name)
        add_tooltip(
            "Name of the thing the spec entry will be created for, without prefixes (e.g. 'ovl_') and\n"
            "suffixes (e.g. '_scene' or '_room').")
        if self.spec_entry_type == 0 or self.spec_entry_type == 1:
            _, self.sub_folder = imgui.combo("Sub folder", self.sub_folder, self.sub_folders)
            add_tooltip("Sub folder inside the scenes directory. Leave this empty for custom scenes.")
            if self.spec_entry_type == 1:
                _, self.number_of_rooms = imgui.slider_int("Number of rooms", self.number_of_rooms, 1, 32)
                add_tooltip("Total number of rooms of the scene. If there are already room entries for the scene,\n"
                            "only the remaining entries will be added.")
        if imgui.button("Create spec entries"):
            self.update_spec_entries()
        self.messages.render()

    def update_spec_entries(self):
        self.messages.clear()
        if self.spec_entry_type == 0:
            entry_name = self.spec_name + "_scene"
            if spec_entry_exists(self.config, entry_name):
                self.messages.add_message(
                    "A spec entry for scene " + entry_name + " already exists. No new entry will be created.",
                    MessageList.Warning)
            else:
                create_scene_spec_entry(self.config, entry_name, self.sub_folders[self.sub_folder])
                self.messages.add_message("Scene entry created!", MessageList.Success)
        elif self.spec_entry_type == 1:
            created = 0
            if not spec_entry_exists(self.config, self.spec_name + "_scene"):
                self.messages.add_message(
                    "Unable to create room entry because no scene entry exists for " + self.spec_name,
                    MessageList.Error)
            else:
                for i in range(0, self.number_of_rooms):
                    entry_name = self.spec_name + "_room_" + str(i)
                    if spec_entry_exists(self.config, entry_name):
                        self.messages.add_message(
                            "A spec entry for room " + entry_name + " already exists.", MessageList.Info)
                    else:
                        create_room_spec_entry(self.config, entry_name)
                        created += 1
                self.messages.add_message(str(created) + " room entries created!",
                                          MessageList.Success if created > 0 else MessageList.Warning)
        elif self.spec_entry_type == 2:
            entry_name = "ovl_ " + self.spec_name
            if spec_entry_exists(self.config, entry_name):
                self.messages.add_message(
                    "A spec entry for overlay " + entry_name + " already exists. No new entry will be created.",
                    MessageList.Warning)
            else:
                create_overlay_spec_entry(self.config, entry_name)
                self.messages.add_message("Overlay entry created!", MessageList.Success)
        elif self.spec_entry_type == 3:
            entry_name = "object_ " + self.spec_name
            if spec_entry_exists(self.config, entry_name):
                self.messages.add_message(
                    "A spec entry for object " + entry_name + " already exists. No new entry will be created.",
                    MessageList.Warning)
            else:
                create_object_spec_entry(self.config, entry_name)
                self.messages.add_message("Object entry created!", MessageList.Success)
        self.config.set_file_reload_required()

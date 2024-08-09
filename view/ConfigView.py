import re

import imgui

from patch.AdultCrawlspaceEntryPatch import AdultCrawlspaceEntryPatch
from patch.DrawDPadIconPatch import DrawDPadIconPatch
from util.StringUtil import replace_line, insert_block_before_line, remove_block_from_line_to_line
from view.BaseView import BaseView


class ConfigView(BaseView):
    def __init__(self, config):
        super().__init__("Configuration", config)
        self.saved = False
        self.copy_rom = False
        self.rom_copy_dir = ""
        self.compilers = ["ido", "gcc"]
        self.compiler = 0
        self.override_region = False
        self.regions = ["US", "JP", "EU"]
        self.region = 0
        self.disable_matching_check = False
        self.map_select_default_scene = 0
        self.scenes = []
        self.patches = [
            AdultCrawlspaceEntryPatch(self.config),
            DrawDPadIconPatch(self.config),
        ]
        self.patch_info = [{"enabled": False, "applied": False} for _ in self.patches]

    def update(self):
        self.update_makefile_options()
        self.update_scenes()
        self.update_file_select_options()
        self.update_patch_info()
        self.saved = False

    def update_makefile_options(self):
        with open(self.config.makefile_path, "r", encoding="utf-8") as f:
            makefile_content = f.read()
        for line in makefile_content.split("\n"):
            if line.startswith("COMPILER "):
                self.compiler = self.compilers.index(line.split("=")[1].strip())
            if line.startswith("REGION "):
                self.region = self.regions.index(line.split("=")[1].strip())
                self.override_region = True
            if line.startswith("COMPARE "):
                self.disable_matching_check = line.split("=")[1].strip() == "0"
            if line.startswith("\tcp $(ROM) "):
                self.copy_rom = True
                self.rom_copy_dir = line.split(" ")[2]

    def update_file_select_options(self):
        with open(self.config.z_select_path, "r", encoding="utf-8") as f:
            content = f.read()
        init_start = content.find("void MapSelect_Init")
        for line in content[init_start:].split("\n"):
            match = re.search(r"this->topDisplayedScene = (\d+);", line)
            if match:
                self.map_select_default_scene = int(match.group(1))
                break

    def update_patch_info(self):
        for i in range(len(self.patches)):
            self.patch_info[i]["enabled"] = self.patches[i].is_patch_applied()
            self.patch_info[i]["applied"] = self.patch_info[i]["enabled"]

    def render_internal(self):
        if imgui.begin_tab_bar("ConfigTabBar"):
            if imgui.begin_tab_item("Paths").selected:
                oot_path_changed, self.config.oot_decomp_path = imgui.input_text("OoT Decomp Path",
                                                                                 self.config.oot_decomp_path, 256)
                if oot_path_changed:
                    self.update()
                _, self.config.mm_decomp_path = imgui.input_text("MM Decomp Path", self.config.mm_decomp_path, 256)
                _, self.copy_rom = imgui.checkbox("Copy ROM to directory after building", self.copy_rom)
                if self.copy_rom:
                    _, self.rom_copy_dir = imgui.input_text("ROM Copy Directory", self.rom_copy_dir, 256)
                imgui.end_tab_item()
            if imgui.begin_tab_item("Build").selected:
                _, self.compiler = imgui.combo("Compiler", self.compiler, self.compilers)
                _, self.override_region = imgui.checkbox("Override Region", self.override_region)
                if self.override_region:
                    _, self.region = imgui.combo("Region", self.region, self.regions)
                _, self.disable_matching_check = imgui.checkbox("Disable Matching check", self.disable_matching_check)
                imgui.end_tab_item()
            if imgui.begin_tab_item("Gameplay").selected:
                _, self.map_select_default_scene = imgui.combo("Default Scene for Map Select",
                                                               self.map_select_default_scene, self.scenes)
                imgui.end_tab_item()
            if imgui.begin_tab_item("Patches").selected:
                for i in range(len(self.patches)):
                    _, self.patch_info[i]["enabled"] = (
                        imgui.checkbox(self.patches[i].name, self.patch_info[i]["enabled"]))
                imgui.end_tab_item()
            imgui.end_tab_bar()
            imgui.separator()
            if imgui.button("Save configuration"):
                self.save_config()
                self.saved = True
            if self.saved:
                imgui.text_colored("Configuration saved!", 0, 1, 0)

    def update_scenes(self):
        self.scenes = []
        with open(self.config.scene_table_path, "r", encoding="utf-8") as f:
            content = f.read()
        for match in re.finditer(r"/\* \w+ \*/ DEFINE_SCENE\((\w+), (\w+), (\w+), (\w)+, (\d+), (\d+)\)", content):
            self.scenes.append(match.group(3)[len("SCENE_"):])

    def save_config(self):
        self.save_makefile()
        self.save_file_select()
        self.apply_patches()

    def save_makefile(self):
        with open(self.config.makefile_path, "r", encoding="utf-8") as f:
            makefile_content = f.read()
        makefile_content = replace_line(makefile_content, "COMPARE ",
                                        "COMPARE ?= " + ("0" if self.disable_matching_check else "1"))
        makefile_content = replace_line(makefile_content, "NON_MATCHING ",
                                        "NON_MATCHING ?= " + (
                                            "1" if self.disable_matching_check else "0"))
        makefile_content = replace_line(makefile_content, "COMPILER ",
                                        "COMPILER ?= " + self.compilers[self.compiler])
        makefile_content = replace_line(makefile_content, "REGION ", "REGION ?= " + self.regions[
            self.region] if self.override_region else "# REGION ?= ")

        makefile_content = replace_line(makefile_content, "all:",
                                        "all: rom compress copy" if self.copy_rom else "all: rom compress")

        copy_block_exists = makefile_content.find("\ncopy:") != -1
        if self.copy_rom and not copy_block_exists:
            makefile_content = insert_block_before_line(makefile_content, "clean:",
                                                        "copy:\n\tcp $(ROM) " + self.rom_copy_dir)
        elif not self.copy_rom and copy_block_exists:
            makefile_content = remove_block_from_line_to_line(makefile_content, "copy:", "clean:")

        with open(self.config.makefile_path, "w", encoding="utf-8") as f:
            f.write(makefile_content)

    def save_file_select(self):
        with open(self.config.z_select_path, "r", encoding="utf-8") as f:
            content = f.read()
        init_start = content.find("void MapSelect_Init")
        content = replace_line(content, "    this->topDisplayedScene = ",
                               "    this->topDisplayedScene = " + str(self.map_select_default_scene) + ";",
                               search_from=init_start)
        content = replace_line(content, "    this->currentScene = ",
                               "    this->currentScene = " + str(self.map_select_default_scene) + ";",
                               search_from=init_start)
        with open(self.config.z_select_path, "w", encoding="utf-8") as f:
            f.write(content)

    def apply_patches(self):
        for i in range(len(self.patches)):
            if self.patch_info[i]["enabled"] != self.patch_info[i]["applied"]:
                if self.patch_info[i]["enabled"]:
                    self.patches[i].apply()
                    self.patch_info[i]["applied"] = True
                else:
                    self.patches[i].revert()

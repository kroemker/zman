import imgui

from view.BaseView import BaseView


class ConfigView(BaseView):
    def __init__(self, config):
        super().__init__("Configuration", config)
        self.copy_rom = False
        self.rom_copy_dir = ""
        self.compilers = ["ido", "gcc"]
        self.compiler = 0
        self.override_region = False
        self.regions = ["US", "JP", "EU"]
        self.region = 0
        self.disable_matching_check = False
        self.makefile_updated = False

    def update(self):
        with open(self.config.oot_decomp_path + "/Makefile", "r", encoding="utf-8") as f:
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
            if imgui.begin_tab_item("Makefile").selected:
                _, self.compiler = imgui.combo("Compiler", self.compiler, self.compilers)
                _, self.override_region = imgui.checkbox("Override Region", self.override_region)
                if self.override_region:
                    _, self.region = imgui.combo("Region", self.region, self.regions)
                _, self.disable_matching_check = imgui.checkbox("Disable Matching check", self.disable_matching_check)
                imgui.end_tab_item()
            if imgui.begin_tab_item("Patches").selected:
                imgui.text("TODO")
                imgui.end_tab_item()
            imgui.end_tab_bar()
            imgui.separator()
            if imgui.button("Save configuration"):
                self.save_config()
                self.makefile_updated = True
            if self.makefile_updated:
                imgui.text_colored("Configuration saved!", 0, 1, 0)

    def save_config(self):
        with open(self.config.oot_decomp_path + "/Makefile", "r", encoding="utf-8") as f:
            makefile_content = f.read()
        makefile_content = self.replace_line(makefile_content, "COMPARE ",
                                             "COMPARE ?= " + ("0" if self.disable_matching_check else "1"))
        makefile_content = self.replace_line(makefile_content, "NON_MATCHING ",
                                             "NON_MATCHING ?= " + (
                                                 "1" if self.disable_matching_check else "0"))
        makefile_content = self.replace_line(makefile_content, "COMPILER ",
                                             "COMPILER ?= " + self.compilers[self.compiler])
        makefile_content = self.replace_line(makefile_content, "REGION ", "REGION ?= " + self.regions[
            self.region] if self.override_region else "# REGION ?= ")

        makefile_content = self.replace_line(makefile_content, "all:",
                                             "all: rom compress copy" if self.copy_rom else "all: rom compress")

        copy_block_exists = makefile_content.find("\ncopy:") != -1
        if self.copy_rom and not copy_block_exists:
            makefile_content = self.insert_block_before_line(makefile_content, "clean:",
                                                             "copy:\n\tcp $(ROM) " + self.rom_copy_dir)
        elif not self.copy_rom and copy_block_exists:
            makefile_content = self.remove_block_from_line_to_line(makefile_content, "copy:", "clean:")

        with open(self.config.oot_decomp_path + "/Makefile", "w", encoding="utf-8") as f:
            f.write(makefile_content)

    def replace_line(self, content, line_start, new_line):
        start = content.find("\n" + line_start) + 1
        if start == 0:
            start = content.find("\n# " + line_start) + 1
        if start == 0:
            raise Exception("Could not find '" + line_start.strip() + "'!")
        end = content.find("\n", start)
        return content[:start] + new_line + content[end:]

    def insert_block_before_line(self, content, line_start, block):
        start = content.find("\n" + line_start) + 1
        if start == 0:
            raise Exception("Could not find '" + line_start.strip() + "'!")
        return content[:start] + block + "\n\n" + content[start:]

    def remove_block_from_line_to_line(self, content, from_line_start, to_line_start):
        start = content.find("\n" + from_line_start) + 1
        if start == 0:
            raise Exception("Could not find '" + from_line_start.strip() + "'!")
        end = content.find("\n" + to_line_start, start) + 1
        if end == 0:
            raise Exception("Could not find '" + to_line_start.strip() + "'!")
        return content[:start] + content[end:]

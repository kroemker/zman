from util.StringUtil import tab

SPEC_OVL_SECTION = "beginseg\n    name \"ovl_title\""
SPEC_OBJECT_SECTION = "beginseg\n    name \"object_box\""
SPEC_SCENE_SECTION = "beginseg\n    name \"ydan_scene\""


def spec_name_option(name):
    return f"name \"{name}\""


def spec_compress_option():
    return "compress"


def spec_include_option(path):
    return f"include \"{path}\""


def spec_number_option(number):
    return f"number {number}"


def spec_rom_align_option(alignment):
    return f"romalign {alignment}"


def create_spec_entry(config, options, section, insert_after_section=False):
    with open(config.spec_path, "r") as f:
        spec_content = f.read()
    section_start = spec_content.find(section)
    if section_start == -1:
        raise Exception("Target section not found in spec file")
    spec_entry = f"beginseg\n"
    for option in options:
        spec_entry += tab(1) + option + "\n"
    spec_entry += f"endseg"
    if insert_after_section:
        section_end = spec_content.find("endseg", section_start)
        if section_end == -1:
            raise Exception("End of target section not found in spec file")
        section_end += len("endseg")
        spec_content = spec_content[:section_end] + "\n\n" + spec_entry + spec_content[section_end:]
    else:
        spec_content = spec_content[:section_start] + spec_entry + "\n\n" + spec_content[section_start:]
    with open(config.spec_path, "w") as f:
        f.write(spec_content)


def create_overlay_spec_entry(config, actor_name):
    options = [
        spec_name_option(f"ovl_{actor_name}"),
        spec_compress_option(),
        spec_include_option(f"$(BUILD_DIR)/src/overlays/actors/ovl_{actor_name}/z_{actor_name.lower()}.o"),
        spec_include_option(f"$(BUILD_DIR)/src/overlays/actors/ovl_{actor_name}/ovl_{actor_name}_reloc.o")
    ]
    create_spec_entry(config, options, SPEC_OVL_SECTION)


def create_object_spec_entry(config, object_name, segment_number=6):
    options = [
        spec_name_option(f"{object_name}"),
        spec_compress_option(),
        spec_rom_align_option("0x1000"),
        spec_include_option(f"$(BUILD_DIR)/assets/objects/{object_name.lower()}/{object_name.lower()}.o"),
        spec_number_option(segment_number)
    ]
    create_spec_entry(config, options, SPEC_OBJECT_SECTION)


def create_scene_spec_entry(config, name, sub_folder=""):
    folder = name[:name.index("_scene")]
    options = [
        spec_name_option(f"{name}"),
        spec_compress_option(),
        spec_rom_align_option("0x1000"),
        spec_include_option(
            f"$(BUILD_DIR)/assets/scenes/{sub_folder + "/" if sub_folder != "" else ""}{folder.lower()}/{name.lower()}.o"),
        spec_number_option(2)
    ]
    create_spec_entry(config, options, SPEC_SCENE_SECTION)


def create_room_spec_entry(config, name, sub_folder=""):
    folder = name[:name.index("_room")]
    base_name = folder + "_room_"
    room_number = int(name[name.index("_room_") + 6:])
    i = room_number - 1
    while i >= 0:
        if spec_entry_exists(config, base_name + str(i)):
            break
        i -= 1
    if i < 0:
        room_section = build_spec_section_search_string(folder + "_scene")
    else:
        room_section = build_spec_section_search_string(base_name + str(i))
    options = [
        spec_name_option(f"{name}"),
        spec_compress_option(),
        spec_rom_align_option("0x1000"),
        spec_include_option(
            f"$(BUILD_DIR)/assets/scenes/{sub_folder + "/" if sub_folder != "" else ""}{folder.lower()}/{name.lower()}.o"),
        spec_number_option(3)
    ]
    create_spec_entry(config, options, room_section, True)


def spec_entry_exists(config, name):
    return f"beginseg\n    name \"{name}\"" in config.read_file_memoized(config.spec_path)


def build_spec_section_search_string(name):
    return f"beginseg\n    name \"{name}\""

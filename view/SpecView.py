from functools import reduce

import imgui

from view.BaseView import BaseView


class SpecView(BaseView):
    def __init__(self, config):
        super().__init__("Spec", config)
        self.segments = {}
        self.selected_segment = None
        self.spec_filter = ""

    def render_internal(self):
        imgui.begin("Spec", True)
        imgui.text("Filter")
        imgui.same_line()
        _, self.spec_filter = imgui.input_text("", self.spec_filter, 256)
        self.__render_segment(self.segments)
        imgui.separator()
        if self.selected_segment:
            imgui.begin_child("Selected Segment", 0, 0, True)
            imgui.text(self.selected_segment["code"])
            imgui.end_child()
        imgui.end()

    def __render_segment(self, segment):
        for key in sorted(segment.keys(), key=lambda x: "name" in segment[x]):
            if not self.__contains_filter(segment[key]):
                continue
            if "name" in segment[key]:
                if imgui.tree_node(key, imgui.TREE_NODE_LEAF):
                    if imgui.is_item_clicked(0):
                        self.selected_segment = segment[key]
                    imgui.tree_pop()
            else:
                if imgui.tree_node(key, imgui.TREE_NODE_SELECTED):
                    self.__render_segment(segment[key])
                    imgui.tree_pop()

    def __contains_filter(self, segment):
        if self.spec_filter == "":
            return True
        if "name" in segment:
            return self.spec_filter.lower() in segment["name"].lower()
        for key in segment.keys():
            if self.__contains_filter(segment[key]):
                return True

    def update(self):
        with open(self.config.decomp_path + "/spec", "r") as f:
            spec_content = f.read()
        segments = spec_content.split("beginseg")
        for segment in segments:
            if segment.strip().startswith("/*"):
                continue
            parsed_segment = self.__parse_segment(segment)
            self.__add_segment(parsed_segment)

    def __add_segment(self, segment):
        self.__add_segment_to_group(segment["groups"][0], segment["groups"][1:], self.segments, segment)

    def __add_segment_to_group(self, group, remaining_groups, parent_group, segment):
        if group not in parent_group:
            parent_group[group] = {}
        if len(remaining_groups) == 0:
            parent_group[group][segment["name"]] = segment
        else:
            self.__add_segment_to_group(remaining_groups[0], remaining_groups[1:], parent_group[group], segment)

    def __parse_segment(self, seg):
        segment = {"name": "", "groups": []}
        for line in seg.split("\n"):
            options = line.strip().split(" ", 1)
            if len(options) != 2:
                continue
            if options[0] == "name":
                segment["name"] = options[1].strip("\"")
            elif options[0] == "include":
                segment["groups"] = self.__parse_groups_from_include_path(options[1].strip("\""))
                break
        segment["code"] = reduce(lambda acc, val: acc + "\n" + val,
                                 map(lambda x: x.strip(), seg[:seg.find("endseg")].split("\n")))
        return segment

    def __parse_groups_from_include_path(self, include_path):
        groups = include_path.replace("$(BUILD_DIR)/", "").title().split("/")
        return groups[:-2] if len(groups) > 2 else groups[:-1]

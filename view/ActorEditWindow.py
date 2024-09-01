import re

import imgui

from BaseWindow import BaseWindow
from util.RenderUtil import render_cenum_combo
from util.StringUtil import get_flags, get_struct_content, parse_c_float


class ActorEditWindow(BaseWindow):
    def __init__(self, config, actor, on_destroy=None):
        super().__init__("Edit Actor: " + actor["descriptive_name"], config, on_destroy)
        self.actor = actor
        with open(self.actor["c_file"], "r", encoding="utf-8") as f:
            self.content = f.read()
        self.colliders = []
        self.parse_actor_data()

    def parse_actor_data(self):
        for match in re.finditer(r"static (Collider\w*Init) (\w+) = \{([\s\w{,|}\.]*)};", self.content, re.MULTILINE):
            collider = {"name": match.group(2), "start": match.start(), "end": match.end(), "type": match.group(1)}
            struct, _ = get_struct_content(match.group(3))
            if match.group(1) == "ColliderJntSphInit":
                collider["init"] = self.parse_collider_init(struct[0])
                collider["count"] = int(struct[1])
            elif match.group(1) == "ColliderQuadInit":
                collider["init"] = self.parse_collider_init(struct[0])
                collider["elem"] = self.parse_collider_elem(struct[1])
                collider["quad_dim"] = self.parse_collider_quad_dim(struct[2])
            elif match.group(1) == "ColliderCylinderInit":
                collider["init"] = self.parse_collider_init(struct[0])
                collider["elem"] = self.parse_collider_elem(struct[1])
                collider["cyl_dim"] = self.parse_collider_cylinder_dim(struct[2])

            self.colliders.append(collider)

    def parse_collider_init(self, definition):
        collider_init = {"type": self.config.get_cenum_index_by_constant(self.config.collider_types, definition[0])}

        flags = get_flags(definition[1])
        collider_init["at_on"] = "AT_ON" in flags
        collider_init["at_types"] = self.build_flag_set(self.config.at_flags, flags)

        flags = get_flags(definition[2])
        collider_init["ac_on"] = "AC_ON" in flags
        collider_init["ac_types"] = self.build_flag_set(self.config.ac_flags, flags)

        flags = get_flags(definition[3])
        collider_init["oc1_types"] = self.build_flag_set(self.config.oc1_flags, flags)

        flags = get_flags(definition[4])
        collider_init["oc2_types"] = self.build_flag_set(self.config.oc2_flags, flags)

        collider_init["shape"] = self.config.get_cenum_index_by_constant(self.config.collider_shapes, definition[5])
        return collider_init

    def parse_collider_elem(self, definition):
        collider_elem = {"elem_type": definition[0],
                         "at_effect": int(definition[1][1], 0),
                         "at_attack": int(definition[1][2], 0),
                         "ac_effect": int(definition[2][1], 0),
                         "ac_defense": int(definition[2][2], 0)}

        constants = self.config.get_constants_from_flag_string(self.config.damage_types, definition[1][0])
        collider_elem["at_damage_types"] = self.build_flag_set(self.config.damage_types, constants)

        constants = self.config.get_constants_from_flag_string(self.config.damage_types, definition[2][0])
        collider_elem["ac_damage_types"] = self.build_flag_set(self.config.damage_types, constants)

        flags = get_flags(definition[3])
        collider_elem["at_elem_on"] = "ATELEM_ON" in flags
        collider_elem["at_elem_types"] = self.build_flag_set(self.config.at_elem_flags, flags)
        flags = get_flags(definition[4])
        collider_elem["ac_elem_on"] = "ACELEM_ON" in flags
        collider_elem["ac_elem_types"] = self.build_flag_set(self.config.ac_elem_flags, flags)
        flags = get_flags(definition[5])
        collider_elem["oc_elem_on"] = "OCELEM_ON" in flags
        collider_elem["oc_elem_types"] = self.build_flag_set(self.config.oc_elem_flags, flags)
        return collider_elem

    def parse_collider_quad_dim(self, definition):
        return [
            [parse_c_float(definition[0][0][0]),
             parse_c_float(definition[0][0][1]),
             parse_c_float(definition[0][0][2])],
            [parse_c_float(definition[0][1][0]),
             parse_c_float(definition[0][1][1]),
             parse_c_float(definition[0][1][2])],
            [parse_c_float(definition[0][2][0]),
             parse_c_float(definition[0][2][1]),
             parse_c_float(definition[0][2][2])],
            [parse_c_float(definition[0][3][0]),
             parse_c_float(definition[0][3][1]),
             parse_c_float(definition[0][3][2])]
        ]

    def parse_collider_cylinder_dim(self, definition):
        return {
            "radius": int(definition[0]),
            "height": int(definition[1]),
            "y_shift": int(definition[2]),
            "position": [int(definition[3][0]), int(definition[3][1]), int(definition[3][2])]
        }

    def render_internal(self):
        imgui.text("Actor: " + self.actor["name"])
        imgui.text("Descriptive Name: " + self.actor["descriptive_name"])
        imgui.separator()
        for collider in self.colliders:
            imgui.text("Collider: " + collider["name"])
            imgui.text("Type: " + collider["type"][len("Collider"):-len("Init")])
            if collider["type"] == "ColliderJntSphInit":
                imgui.text("Count: " + str(collider["count"]))
                self.render_collider_init(collider["name"], collider["init"])
            elif collider["type"] == "ColliderQuadInit":
                self.render_collider_init(collider["name"], collider["init"])
                self.render_collider_elem(collider["name"], collider["elem"])
                self.render_collider_quad_dim(collider["name"], collider["quad_dim"])
            elif collider["type"] == "ColliderCylinderInit":
                self.render_collider_init(collider["name"], collider["init"])
                self.render_collider_elem(collider["name"], collider["elem"])
                self.render_collider_cylinder_dim(collider["name"], collider["cyl_dim"])
            imgui.separator()

    def render_collider_init(self, name, collider_init):
        _, collider_init["type"] = render_cenum_combo("Collision Type##" + name, collider_init["type"],
                                                      self.config.collider_types)
        _, collider_init["shape"] = render_cenum_combo("Shape##" + name, collider_init["shape"],
                                                       self.config.collider_shapes)
        _, collider_init["at_on"] = imgui.checkbox("AT##" + name, collider_init["at_on"])
        if collider_init["at_on"]:
            self.render_flag_set("AT Flags##" + name, self.config.at_flags, collider_init["at_types"])
        _, collider_init["ac_on"] = imgui.checkbox("AC##" + name, collider_init["ac_on"])
        if collider_init["ac_on"]:
            self.render_flag_set("AC Flags##" + name, self.config.ac_flags, collider_init["ac_types"])
        self.render_flag_set("OC1 Flags##" + name, self.config.oc1_flags, collider_init["oc1_types"])
        self.render_flag_set("OC2 Flags##" + name, self.config.oc2_flags, collider_init["oc2_types"])

    def render_collider_elem(self, name, collider_elem):
        _, collider_elem["elem_type"] = imgui.input_text("Element Type##" + name, collider_elem["elem_type"], 256)
        imgui.text("AT")
        self.render_flag_set("AT Damage Flags##" + name, self.config.damage_types, collider_elem["at_damage_types"])
        _, collider_elem["at_effect"] = render_cenum_combo("AT Effect##" + name, collider_elem["at_effect"],
                                                           self.config.damage_effects)
        _, collider_elem["at_attack"] = imgui.input_int("AT Attack##" + name, collider_elem["at_attack"])
        imgui.text("AC")
        self.render_flag_set("AC Damage Flags##" + name, self.config.damage_types, collider_elem["ac_damage_types"])
        _, collider_elem["ac_effect"] = render_cenum_combo("AC Effect##" + name, collider_elem["ac_effect"],
                                                           self.config.damage_effects)
        _, collider_elem["ac_defense"] = imgui.input_int("AC Defense##" + name, collider_elem["ac_defense"])

        _, collider_elem["at_elem_on"] = imgui.checkbox("AT Elem##" + name, collider_elem["at_elem_on"])
        if collider_elem["at_elem_on"]:
            self.render_flag_set("AT Element Flags##" + name, self.config.at_elem_flags, collider_elem["at_elem_types"])
        _, collider_elem["ac_elem_on"] = imgui.checkbox("AC Elem##" + name, collider_elem["ac_elem_on"])
        if collider_elem["ac_elem_on"]:
            self.render_flag_set("AC Element Flags##" + name, self.config.ac_elem_flags, collider_elem["ac_elem_types"])
        _, collider_elem["oc_elem_on"] = imgui.checkbox("OC Elem##" + name, collider_elem["oc_elem_on"])
        if collider_elem["oc_elem_on"]:
            self.render_flag_set("OC Element Flags##" + name, self.config.oc_elem_flags, collider_elem["oc_elem_types"])

    def render_collider_quad_dim(self, name, quad_dim):
        for i in range(4):
            imgui.text("Point " + str(i + 1))
            _, quad_dim[i][0] = imgui.input_float("X##" + name + str(i), quad_dim[i][0])
            _, quad_dim[i][1] = imgui.input_float("Y##" + name + str(i), quad_dim[i][1])
            _, quad_dim[i][2] = imgui.input_float("Z##" + name + str(i), quad_dim[i][2])

    def render_collider_cylinder_dim(self, name, cyl_dim):
        _, cyl_dim["radius"] = imgui.input_int("Radius##" + name, cyl_dim["radius"])
        _, cyl_dim["height"] = imgui.input_int("Height##" + name, cyl_dim["height"])
        _, cyl_dim["y_shift"] = imgui.input_int("Y Shift##" + name, cyl_dim["y_shift"])
        imgui.text("Position")
        _, cyl_dim["position"][0] = imgui.input_int("X##" + name, cyl_dim["position"][0])
        _, cyl_dim["position"][1] = imgui.input_int("Y##" + name, cyl_dim["position"][1])
        _, cyl_dim["position"][2] = imgui.input_int("Z##" + name, cyl_dim["position"][2])

    def render_flag_set(self, title, possible_flags, flags):
        i = 0
        if imgui.tree_node(title, imgui.TREE_NODE_FRAMED):
            for flag in possible_flags:
                _, flags[flag.constant] = imgui.checkbox(flag.name, flags[flag.constant])
                i += 1
            imgui.tree_pop()

    def build_flag_set(self, possible_flags_cenum, flag_constants):
        flags = {}
        for flag in possible_flags_cenum:
            flags[flag.constant] = flag.constant in flag_constants
        return flags

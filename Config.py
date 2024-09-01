import re

from util.CEnumValue import CEnumValue


class Config:
    def __init__(self, oot_decomp_path):
        self.oot_decomp_path = oot_decomp_path
        self.mm_decomp_path = ""
        self.spec_path = oot_decomp_path + "/spec"
        self.makefile_path = oot_decomp_path + "/Makefile"
        self.sys_cfb_path = oot_decomp_path + "/src/code/sys_cfb.c"
        self.actor_table_path = oot_decomp_path + "/include/tables/actor_table.h"
        self.scene_table_path = oot_decomp_path + "/include/tables/scene_table.h"
        self.entrance_table_path = oot_decomp_path + "/include/tables/entrance_table.h"
        self.object_table_path = oot_decomp_path + "/include/tables/object_table.h"
        self.objects_base_path = oot_decomp_path + f"/extracted/gc-eu-mq-dbg/assets/objects"
        self.z_select_path = oot_decomp_path + "/src/overlays/gamestates/ovl_select/z_select.c"
        self.z_player_path = oot_decomp_path + "/src/overlays/actors/ovl_player_actor/z_player.c"
        self.z_parameter_path = oot_decomp_path + "/src/code/z_parameter.c"
        self.z_play_path = oot_decomp_path + "/src/code/z_play.c"
        self.z_scene_path = oot_decomp_path + "/src/code/z_scene.c"
        self.z_title_path = oot_decomp_path + "/src/overlays/gamestates/ovl_title/z_title.c"
        self.z_opening_path = oot_decomp_path + "/src/overlays/gamestates/ovl_opening/z_opening.c"
        self.z_std_dma_path = oot_decomp_path + "/src/boot/z_std_dma.c"
        self.actor_categories = [
            CEnumValue("ACTORCAT_PLAYER", "Player", "Only player."),
            CEnumValue("ACTORCAT_EXPLOSIVE", "Explosives", "Bombchus, Bombs, etc."),
            CEnumValue("ACTORCAT_NPC", "NPC", "All kinds of NPCs."),
            CEnumValue("ACTORCAT_ENEMY", "Enemy", "All kinds of enemies except bosses."),
            CEnumValue("ACTORCAT_PROP", "Prop", "Props like rocks, trees, etc."),
            CEnumValue("ACTORCAT_ITEMACTION", "Item/Action", "Items and action actors like boomerang, hookshot, etc."),
            CEnumValue("ACTORCAT_MISC", "Misc", "Everything else."),
            CEnumValue("ACTORCAT_BOSS", "Boss", "Bosses, triggers boss music?"),
            CEnumValue("ACTORCAT_DOOR", "Door", "Doors"),
            CEnumValue("ACTORCAT_CHEST", "Chest", "Chests"),
        ]
        self.actor_flags = [
            CEnumValue("ACTOR_FLAG_0", "Targetable", "Navi will fly over the actor and it can be Z targeted"),
            CEnumValue("ACTOR_FLAG_2", "Unfriendly",
                       "Changes targeting behavior for unfriendly actors (sound, Link's stance)"),
            CEnumValue("ACTOR_FLAG_3", "Friendly",
                       "Opposite of the unfriendly flag. Flag is not checked against."),
            CEnumValue("ACTOR_FLAG_4", "No Update Culling",
                       "Actor will keep updating even if outside of the uncull zone."),
            CEnumValue("ACTOR_FLAG_5", "No Draw Culling",
                       "Actor will keep drawing even if outside of the uncull zone."),
            CEnumValue("ACTOR_FLAG_6", "In Uncull Zone", "Actor is currently in the uncull zone."),
            CEnumValue("ACTOR_FLAG_REACT_TO_LENS", "React to Lens", "Hidden or revealed by Lens of Truth."),
            CEnumValue("ACTOR_FLAG_TALK", "Talk Requested",
                       "Player has requested to talk to the actor; Player uses this flag differently than every other actor."),
            CEnumValue("ACTOR_FLAG_9", "Hook Can Carry", "Brings the actor back to Player if hookshoted."),
            CEnumValue("ACTOR_FLAG_10", "Hook Bring Player",
                       "Brings Player to the actor if hookshoted."),
            CEnumValue("ACTOR_FLAG_ENKUSA_CUT", "Enkusa Cut", "Grass actor has been cut."),
            CEnumValue("ACTOR_FLAG_IGNORE_QUAKE", "Ignore Quake", "Actor will not shake when a quake occurs."),
            CEnumValue("ACTOR_FLAG_13", "Hook Attached", "Hookshot has attached to the actor."),
            CEnumValue("ACTOR_FLAG_14", "Arrow Can Carry",
                       "When an arrow hits the actor it will attach to the actor and carry it."),
            CEnumValue("ACTOR_FLAG_15", "Arrow Is Carrying",
                       "An arrow is currently carrying this actor."),
            CEnumValue("ACTOR_FLAG_16", "Immediate Talk",
                       "Forces Player to talk when in range. Needs to be unset manually to avoid infinite talking."),
            CEnumValue("ACTOR_FLAG_17", "Heavy Block",
                       "Changes actor carrying behavior specifically for the golden gauntlets block actor."),
            CEnumValue("ACTOR_FLAG_18", "Check With Navi",
                       "Navi can be used to trigger dialogue when targeting the actor."),
            CEnumValue("ACTOR_FLAG_19", "SFX At Position",
                       "Play sound from sfx field at the actor's position."),
            CEnumValue("ACTOR_FLAG_20", "SFX Centered 2", "Same as ACTOR_FLAG_SFX_CENTERED, unused."),
            CEnumValue("ACTOR_FLAG_21", "SFX Centered",
                       "Play sound from sfx field at the center of the screen."),
            CEnumValue("ACTOR_FLAG_IGNORE_POINT_LIGHTS", "Ignore Point Lights",
                       "Ignores point lights but not directional lights (such as environment lights)."),
            CEnumValue("ACTOR_FLAG_23", "Always Throw", "Player throws held actor even if standing still."),
            CEnumValue("ACTOR_FLAG_24", "Play Bodyhit SFX",
                       "When actor hits Player's body, a thump sfx plays."),
            CEnumValue("ACTOR_FLAG_25", "Ocarina No Freeze",
                       "Actor doesnt freeze when Player has ocarina out or is using a warp song."),
            CEnumValue("ACTOR_FLAG_26", "Can Hold Switch", "Actor can press and hold down switches."),
            CEnumValue("ACTOR_FLAG_27", "Cant Lock On",
                       "Prevents locking on with Z targeting an actor even if Navi is floating over it."),
            CEnumValue("ACTOR_FLAG_28", "SFX Timer",
                       "Actor sfx field is used as timer state instead of an sfx id")
        ]
        self.collider_types = [
            CEnumValue("COLTYPE_HIT0", "Hit 0", "Blue blood, white hitmark"),
            CEnumValue("COLTYPE_HIT1", "Hit 1", "No blood, dust hitmark"),
            CEnumValue("COLTYPE_HIT2", "Hit 2", "Green blood, dust hitmark"),
            CEnumValue("COLTYPE_HIT3", "Hit 3", "No blood, white hitmark"),
            CEnumValue("COLTYPE_HIT4", "Hit 4", "Water burst, no hitmark"),
            CEnumValue("COLTYPE_HIT5", "Hit 5", "No blood, red hitmark"),
            CEnumValue("COLTYPE_HIT6", "Hit 6", "Green blood, white hitmark"),
            CEnumValue("COLTYPE_HIT7", "Hit 7", "Red blood, white hitmark"),
            CEnumValue("COLTYPE_HIT8", "Hit 8", "Blue blood, red hitmark"),
            CEnumValue("COLTYPE_METAL", "Metal", "Metal"),
            CEnumValue("COLTYPE_NONE", "None", "None"),
            CEnumValue("COLTYPE_WOOD", "Wood", "Wood"),
            CEnumValue("COLTYPE_HARD", "Hard", "Hard"),
            CEnumValue("COLTYPE_TREE", "Tree", "Tree"),
        ]
        self.at_flags = [
            CEnumValue("AT_TYPE_PLAYER", "Player", "Has player-aligned damage"),
            CEnumValue("AT_TYPE_ENEMY", "Enemy", "Has enemy-aligned damage"),
            CEnumValue("AT_TYPE_OTHER", "Other", "Has non-aligned damage"),
            CEnumValue("AT_SELF", "Self", "Can have AT collisions with colliders attached to the same actor"),
        ]
        self.ac_flags = [
            CEnumValue("AC_TYPE_PLAYER", "Player", "Takes player-aligned damage"),
            CEnumValue("AC_TYPE_ENEMY", "Enemy", "Takes enemy-aligned damage"),
            CEnumValue("AC_TYPE_OTHER", "Other", "Takes non-aligned damage"),
            CEnumValue("AC_NO_DAMAGE", "No Damage", "Collider does not take damage"),
        ]
        self.oc1_flags = [
            CEnumValue("OC1_NO_PUSH", "No Push", "Does not push other colliders away during OC collisions"),
            CEnumValue("OC1_TYPE_PLAYER", "Player", "Can have OC collisions with OC type player"),
            CEnumValue("OC1_TYPE_1", "Type 1", "Can have OC collisions with OC type 1"),
            CEnumValue("OC1_TYPE_2", "Type 2", "Can have OC collisions with OC type 2"),
        ]
        self.oc2_flags = [
            CEnumValue("OC2_UNK1", "Unknown 1",
                       "Prevents OC collisions with OC2_UNK2. Some horses and toki_sword have it."),
            CEnumValue("OC2_UNK2", "Unknown 2", "Prevents OC collisions with OC2_UNK1. Nothing has it."),
            CEnumValue("OC2_TYPE_PLAYER", "Player", "Has OC type player"),
            CEnumValue("OC2_TYPE_1", "Type 1", "Has OC type 1"),
            CEnumValue("OC2_TYPE_2", "Type 2", "Has OC type 2"),
        ]
        self.collider_shapes = [
            CEnumValue("COLSHAPE_JNTSPH", "Joint Sphere", "Jointed sphere"),
            CEnumValue("COLSHAPE_CYLINDER", "Cylinder", "Cylinder"),
            CEnumValue("COLSHAPE_TRIS", "Tris", "Triangles"),
            CEnumValue("COLSHAPE_QUAD", "Quad", "Quad"),
        ]
        self.at_elem_flags = [
            CEnumValue("ATELEM_NEAREST", "Nearest",
                       "For COLSHAPE_QUAD colliders, only collide with the closest AC element"),
            CEnumValue("ATELEM_SFX_NORMAL", "Normal SFX", "Hit sound effect based on AC collider's type"),
            CEnumValue("ATELEM_SFX_HARD", "Hard SFX", "Always uses hard deflection sound"),
            CEnumValue("ATELEM_SFX_WOOD", "Wood SFX", "Always uses wood deflection sound"),
            CEnumValue("ATELEM_SFX_NONE", "No SFX", "No hit sound effect"),
            CEnumValue("ATELEM_AT_HITMARK", "Hitmark", "Draw hitmarks for every AT collision"),
            CEnumValue("ATELEM_UNK7", "Unknown", " Unknown purpose. Used by some enemy quads"),
        ]
        self.ac_elem_flags = [
            CEnumValue("ACELEM_HOOKABLE", "Hookable", "Can be hooked if actor has hookability flags set."),
            CEnumValue("ACELEM_NO_AT_INFO", "No AT Info", "Does not give its info to the AT collider that hit it."),
            CEnumValue("ACELEM_NO_DAMAGE", "No Damage", "Does not take damage."),
            CEnumValue("ACELEM_NO_SWORD_SFX", "No Sword SFX",
                       "Does not have a sound effect when hit by player-attached AT colliders."),
            CEnumValue("ACELEM_NO_HITMARK", "No Hitmark", "Skips hit effects."),
        ]
        self.oc_elem_flags = [
            CEnumValue("OCELEM_UNK3", "Unknown 3",
                       "Unknown purpose. Used by Dead Hand element 0 and Dodongo element 5"),
        ]
        self.damage_types = [
            CEnumValue("DMG_DEKU_NUT", "Deku Nut", "Deku Nut"),
            CEnumValue("DMG_DEKU_STICK", "Deku Stick", "Deku Stick"),
            CEnumValue("DMG_SLINGSHOT", "Slingshot", "Slingshot"),
            CEnumValue("DMG_EXPLOSIVE", "Explosive", "Explosive"),
            CEnumValue("DMG_BOOMERANG", "Boomerang", "Boomerang"),
            CEnumValue("DMG_ARROW_NORMAL", "Arrow Normal", "Arrow Normal"),
            CEnumValue("DMG_HAMMER_SWING", "Hammer Swing", "Hammer Swing"),
            CEnumValue("DMG_HOOKSHOT", "Hookshot", "Hookshot"),
            CEnumValue("DMG_SLASH_KOKIRI", "Slash Kokiri", "Slash Kokiri"),
            CEnumValue("DMG_SLASH_MASTER", "Slash Master", "Slash Master"),
            CEnumValue("DMG_SLASH_GIANT", "Slash Giant", "Slash Giant"),
            CEnumValue("DMG_ARROW_FIRE", "Arrow Fire", "Arrow Fire"),
            CEnumValue("DMG_ARROW_ICE", "Arrow Ice", "Arrow Ice"),
            CEnumValue("DMG_ARROW_LIGHT", "Arrow Light", "Arrow Light"),
            CEnumValue("DMG_ARROW_UNK1", "Arrow Unk1", "Arrow Unk1"),
            CEnumValue("DMG_ARROW_UNK2", "Arrow Unk2", "Arrow Unk2"),
            CEnumValue("DMG_ARROW_UNK3", "Arrow Unk3", "Arrow Unk3"),
            CEnumValue("DMG_MAGIC_FIRE", "Magic Fire", "Magic Fire"),
            CEnumValue("DMG_MAGIC_ICE", "Magic Ice", "Magic Ice"),
            CEnumValue("DMG_MAGIC_LIGHT", "Magic Light", "Magic Light"),
            CEnumValue("DMG_SHIELD", "Shield", "Shield"),
            CEnumValue("DMG_MIR_RAY", "Mirror Ray", "Mirror Ray"),
            CEnumValue("DMG_SPIN_KOKIRI", "Spin Kokiri", "Spin Kokiri"),
            CEnumValue("DMG_SPIN_GIANT", "Spin Giant", "Spin Giant"),
            CEnumValue("DMG_SPIN_MASTER", "Spin Master", "Spin Master"),
            CEnumValue("DMG_JUMP_KOKIRI", "Jump Kokiri", "Jump Kokiri"),
            CEnumValue("DMG_JUMP_GIANT", "Jump Giant", "Jump Giant"),
            CEnumValue("DMG_JUMP_MASTER", "Jump Master", "Jump Master"),
            CEnumValue("DMG_UNKNOWN_1", "Unknown 1", "Unknown 1"),
            CEnumValue("DMG_UNBLOCKABLE", "Unblockable", "Unblockable"),
            CEnumValue("DMG_HAMMER_JUMP", "Hammer Jump", "Hammer Jump"),
            CEnumValue("DMG_UNKNOWN_2", "Unknown 2", "Unknown 2"),
        ]
        self.damage_effects = [
            CEnumValue("0", "None", "No damage effect"),
            CEnumValue("1", "Fire", "Fire damage effect"),
            CEnumValue("2", "Ice", "Ice damage effect"),
            CEnumValue("3", "Electric", "Electric damage effect"),
        ]

    def get_cenum_index_by_constant(self, cenum, constant):
        for i in range(len(cenum)):
            if cenum[i].constant == constant:
                return i
        return None

    def get_cenum_by_constant(self, cenum, constant):
        for val in cenum:
            if val.constant == constant:
                return val
        return None

    def get_constants_from_flag_string(self, cenum, flags_string):
        result = []
        flags_int = int(flags_string, 0)
        for i in range(len(cenum)):
            if flags_int & (1 << i):
                result.append(cenum[i].constant)
        return result

    def parse_object_table(self):
        object_names = []
        object_variables = []
        with open(self.object_table_path, "r", encoding="utf-8") as f:
            content = f.read()
        for line in content.split("\n"):
            match = re.search(r"\/\* \w* \*\/ DEFINE_OBJECT\((\w*),\s*(\w*)\)", line)
            if match:
                object_names.append(match.group(1))
                object_variables.append(match.group(2))
        return object_names, object_variables

    def parse_object_file(self, object_name):
        animation_headers = []
        skeleton_headers = []
        with open(self.objects_base_path + f"/{object_name}/{object_name}.h", "r", encoding="utf-8") as f:
            content = f.read()
        for match in re.finditer(r"extern AnimationHeader (\w*);", content):
            animation_headers.append(match.group(1))
        for match in re.finditer(r"extern (Flex)*SkeletonHeader (\w*);", content):
            skeleton_headers.append({"name": match.group(2), "flex": match.group(1) == "Flex", "limb_count": 0})

        with open(self.objects_base_path + f"/{object_name}/{object_name}.c", "r", encoding="utf-8") as f:
            content = f.read()
        for skel in skeleton_headers:
            if skel["flex"]:
                match = re.search(
                    r"FlexSkeletonHeader\s+" + re.escape(skel["name"]) + r"\s*=\s*{\s*{\s*(\w+)",
                    content, re.MULTILINE)
            else:
                match = re.search(r"SkeletonHeader\s+" + re.escape(skel["name"]) + r"\s*=\s*{\s*(\w+)",
                                  content, re.MULTILINE)
            if match:
                start = content.find(f"{match.group(1)}[]")
                end = content.find("};", start)
                skel["limb_count"] = content[start:end].count("&") + 1
            else:
                raise Exception(f"No skeleton found for {object_name} {skel['name']}")

        return animation_headers, skeleton_headers

    def parse_entrance_table(self):
        with open(self.entrance_table_path, "r") as f:
            content = f.read()
        entrances = []
        for line in content.split("\n"):
            for match in re.finditer(r"/\* \w+ \*/ DEFINE_ENTRANCE\((\w+), (\w+), (\d+), (\w+), (\w+), (\w+), (\w+)\)",
                                     line):
                entrances.append({
                    "entrance": match.group(1),
                    "scene": match.group(2),
                    "spawn_number": int(match.group(3)),
                    "continue_bgm": match.group(4) == "true",
                    "display_title_card": match.group(5) == "true",
                    "enter_transition": match.group(6),
                    "exit_transition": match.group(7),
                })
        return entrances

    def get_entrances_for_scene(self, scene):
        entrances = self.parse_entrance_table()
        return [entrance for entrance in entrances if entrance["scene"] == scene]

    def get_scene_for_entrance(self, entrance_name):
        entrances = self.parse_entrance_table()
        for entrance in entrances:
            if entrance["entrance"] == entrance_name:
                return entrance["scene"]

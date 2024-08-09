from util.CEnumValue import CEnumValue


class Config:
    def __init__(self, oot_decomp_path):
        self.oot_decomp_path = oot_decomp_path
        self.mm_decomp_path = ""
        self.spec_path = oot_decomp_path + "/spec"
        self.makefile_path = oot_decomp_path + "/Makefile"
        self.actor_table_path = oot_decomp_path + "/include/tables/actor_table.h"
        self.scene_table_path = oot_decomp_path + "/include/tables/scene_table.h"
        self.object_table_path = oot_decomp_path + "/include/tables/object_table.h"
        self.objects_base_path = oot_decomp_path + f"/extracted/gc-eu-mq-dbg/assets/objects"
        self.z_select_path = oot_decomp_path + "/src/overlays/gamestates/ovl_select/z_select.c"
        self.z_player_path = oot_decomp_path + "/src/overlays/actors/ovl_player_actor/z_player.c"
        self.z_parameter_path = oot_decomp_path + "/src/code/z_parameter.c"
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

    def get_cenum_by_constant(self, cenum, constant):
        for val in cenum:
            if val.constant == constant:
                return val
        return None

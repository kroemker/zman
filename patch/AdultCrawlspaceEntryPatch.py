from patch.Patch import Patch
from util.StringUtil import remove_in_line


class AdultCrawlspaceEntryPatch(Patch):
    FUNCTION_START = "s32 Player_TryEnteringCrawlspace"
    IF_START = "    if ("
    PATCH_STRING = "!LINK_IS_ADULT && "

    def __init__(self, config):
        super().__init__(config, "Adult Crawlspace Entry")

    def apply(self):
        with open(self.config.z_player_path, "r", encoding="utf-8") as f:
            content = f.read()
        start = content.find(self.FUNCTION_START)
        if start == -1:
            raise Exception("Could not find " + self.FUNCTION_START)
        content = remove_in_line(content, self.IF_START, self.PATCH_STRING)
        with open(self.config.z_player_path, "w", encoding="utf-8") as f:
            f.write(content)

    def is_patch_applied(self):
        with open(self.config.z_player_path, "r", encoding="utf-8") as f:
            content = f.read()
        start = content.find(self.FUNCTION_START)
        if start == -1:
            raise Exception("Could not find " + self.FUNCTION_START)
        return content.find(self.IF_START, start) != content.find(self.IF_START + self.PATCH_STRING, start)

    def revert(self):
        with open(self.config.z_player_path, "r", encoding="utf-8") as f:
            content = f.read()
        start = content.find(self.FUNCTION_START)
        if start == -1:
            raise Exception("Could not find " + self.FUNCTION_START)
        if_start = content.find(self.IF_START, start)
        if if_start == -1:
            raise Exception("Could not find " + self.IF_START)
        insert_position = if_start + len(self.IF_START)
        content = content[:insert_position] + self.PATCH_STRING + content[insert_position:]
        with open(self.config.z_player_path, "w", encoding="utf-8") as f:
            f.write(content)

from patch.Patch import Patch


class FindReplacePatch(Patch):
    def __init__(self, config, name, file_path, find, replace):
        super().__init__(config, name)
        self.file_path = file_path
        self.find = find
        self.replace = replace

    def apply(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace(self.find, self.replace)
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(content)

    def is_patch_applied(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            content = f.read()
        return self.replace in content

    def revert(self):
        with open(self.file_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace(self.replace, self.find)
        with open(self.file_path, "w", encoding="utf-8") as f:
            f.write(content)

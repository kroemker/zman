from patch.Patch import Patch


class RestoreN64LogoPatch(Patch):
    FIXED_CALC = """void ConsoleLogo_Calc(ConsoleLogoState* this) {
    if (this->coverAlpha == 0 && this->visibleDuration != 0) {
        this->unk_1D4--;
        this->visibleDuration--;
        if (this->unk_1D4 == 0) {
            this->unk_1D4 = 400;
        }
    } else {
        this->coverAlpha += this->addAlpha;
        if (this->coverAlpha <= 0) {
            this->coverAlpha = 0;
            this->addAlpha = 3;
        } else if (this->coverAlpha >= 255) {
            this->coverAlpha = 255;
            this->exit = true;
        }
    }
    this->uls = this->ult & 0x7F;
    this->ult++;
}"""
    OLD_CALC = """void ConsoleLogo_Calc(ConsoleLogoState* this) {
    this->exit = true;
}"""

    def __init__(self, config):
        super().__init__(config, "Restore N64 Logo")

    def apply(self):
        with open(self.config.z_title_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace(self.OLD_CALC, self.FIXED_CALC)
        with open(self.config.z_title_path, "w", encoding="utf-8") as f:
            f.write(content)

    def is_patch_applied(self):
        with open(self.config.z_title_path, "r", encoding="utf-8") as f:
            content = f.read()
        return self.FIXED_CALC in content

    def revert(self):
        with open(self.config.z_title_path, "r", encoding="utf-8") as f:
            content = f.read()
        content = content.replace(self.FIXED_CALC, self.OLD_CALC)
        with open(self.config.z_title_path, "w", encoding="utf-8") as f:
            f.write(content)

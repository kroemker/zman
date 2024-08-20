from patch.FindReplacePatch import FindReplacePatch


class RestoreN64LogoPatch(FindReplacePatch):
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
        super().__init__(config, "Restore N64 Logo", config.z_title_path, self.OLD_CALC, self.FIXED_CALC)

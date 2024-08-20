from patch.FindReplacePatch import FindReplacePatch


class SkipDmaTablePrintPatch(FindReplacePatch):
    FIND = """PRINTF("dma_rom_ad[]\\n");

#if OOT_DEBUG"""
    REPLACE = """PRINTF("dma_rom_ad[]\\n");

#if 0"""

    def __init__(self, config):
        super().__init__(config, "Skip DMA Table Print", config.z_std_dma_path, self.FIND, self.REPLACE)

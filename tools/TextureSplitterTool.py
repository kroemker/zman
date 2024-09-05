import imageio.v3 as iio
import imgui

from BaseWindow import BaseWindow
from util.MessageList import MessageList


class TextureSplitterTool(BaseWindow):
    def __init__(self, config, on_destroy):
        super().__init__("Texture Splitter", config, on_destroy)
        self.texture_file = ""
        self.output_folder = ""
        self.texture_name = ""
        self.size_x = 32
        self.size_y = 32
        self.messages = MessageList()

    def render_internal(self):
        _, self.texture_file = imgui.input_text("Texture file path", self.texture_file, 256)
        _, self.output_folder = imgui.input_text("Output folder", self.output_folder, 256)
        _, self.texture_name = imgui.input_text("Texture name", self.texture_name, 256)
        _, self.size_x = imgui.input_int("Size X", self.size_x)
        _, self.size_y = imgui.input_int("Size Y", self.size_y)
        if imgui.button("Split Textures"):
            self.split_textures()
        self.messages.render()

    def split_textures(self):
        self.messages.clear()
        if self.texture_file == "":
            self.messages.add_message("Texture file not set", MessageList.Error)
        if self.output_folder == "":
            self.messages.add_message("Output folder not set", MessageList.Error)
        if self.texture_name == "":
            self.messages.add_message("Texture name not set", MessageList.Error)
        if self.messages.has_errors():
            return

        try:
            image = iio.imread(self.texture_file)
        except Exception as e:
            self.messages.add_message("Error loading image: " + str(e), MessageList.Error)
            return
        if image is None:
            self.messages.add_message("Error loading image", MessageList.Error)
            return
        if image.shape[0] % self.size_y != 0 or image.shape[1] % self.size_x != 0:
            self.messages.add_message("Image dimensions are not divisible by size", MessageList.Error)
            return
        for i in range(0, image.shape[0], self.size_y):
            for j in range(0, image.shape[1], self.size_x):
                iio.imwrite(self.output_folder + "/" + self.texture_name + "_" + str(i) + "_" + str(j) + ".png",
                            image[i:i + self.size_y, j:j + self.size_x])
        self.messages.add_message("Textures split successfully", MessageList.Success)

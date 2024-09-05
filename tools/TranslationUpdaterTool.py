import glob
import re

import imgui

from BaseWindow import BaseWindow
from util.ImguiUtil import add_tooltip
from util.StringUtil import get_file_name_from_path, concat_and_replace_duplicate_substring


class TranslationUpdaterTool(BaseWindow):
    WINDOW_WIDTH = 400
    CJK_RANGES = [
        {"from": ord(u"\u3300"), "to": ord(u"\u33ff")},  # compatibility ideographs
        {"from": ord(u"\ufe30"), "to": ord(u"\ufe4f")},  # compatibility ideographs
        {"from": ord(u"\uf900"), "to": ord(u"\ufaff")},  # compatibility ideographs
        {"from": ord(u"\U0002F800"), "to": ord(u"\U0002fa1f")},  # compatibility ideographs
        {"from": ord(u"\u3000"), "to": ord(u"\u303f")},  # Some japanese?
        {'from': ord(u'\u3040'), 'to': ord(u'\u309f')},  # Japanese Hiragana
        {"from": ord(u"\u30a0"), "to": ord(u"\u30ff")},  # Japanese Katakana
        {"from": ord(u"\u2e80"), "to": ord(u"\u2eff")},  # cjk radicals supplement
        {"from": ord(u"\u4e00"), "to": ord(u"\u9fff")},
        {"from": ord(u"\u3400"), "to": ord(u"\u4dbf")},
        {"from": ord(u"\U00020000"), "to": ord(u"\U0002a6df")},
        {"from": ord(u"\U0002a700"), "to": ord(u"\U0002b73f")},
        {"from": ord(u"\U0002b740"), "to": ord(u"\U0002b81f")},
        {"from": ord(u"\U0002b820"), "to": ord(u"\U0002ceaf")}  # included as of Unicode 8.0
    ]

    def __init__(self, config, on_destroy):
        super().__init__("Translation Updater", config, on_destroy)
        self.run_search = None
        self.search_index = None
        self.translatable_entries = None
        self.reset_search()
        self.search_files = glob.glob(self.config.oot_decomp_path + "/**/*.c", recursive=True)
        self.applied = 0

    def render_internal(self):
        if self.run_search:
            current_file = get_file_name_from_path(self.search_files[self.search_index])
            imgui.progress_bar(self.search_index / len(self.search_files), (self.WINDOW_WIDTH, 20), current_file)
            self.search()
        if imgui.button("Search", self.WINDOW_WIDTH):
            self.reset_search()
            self.run_search = True
        if not self.run_search and len(self.translatable_entries) > 0 and imgui.button("Apply all", self.WINDOW_WIDTH):
            self.apply_translations()
            self.reset_search()
        imgui.separator()
        if self.applied > 0:
            imgui.text_colored("Applied " + str(self.applied) + " translations", 0.0, 1.0, 0.0)
        if not self.run_search and len(self.translatable_entries) > 0:
            imgui.text("Found " + str(len(self.translatable_entries)) + " files with translatable entries")
        for key in self.translatable_entries.keys():
            entries = self.translatable_entries[key]
            imgui.text_colored(str(len(entries)), 0.0, 1.0, 1.0)
            imgui.same_line()
            imgui.text_colored(get_file_name_from_path(key), 1.0, 1.0, 0.0)
            add_tooltip("\n\n".join(["Original:\n" + entry[3] + "\nReplacement:\n" + entry[4] for entry in entries]))

    def apply_translations(self):
        self.applied = 0
        for c_file in self.translatable_entries.keys():
            with open(c_file, "r", encoding="utf-8") as f:
                content = f.read()
            for entry in sorted(self.translatable_entries[c_file], key=lambda x: x[1], reverse=True):
                content = content[:entry[1]] + entry[4] + content[entry[2]:]
            with open(c_file, "w", encoding="utf-8") as f:
                f.write(content)
            self.applied += len(self.translatable_entries[c_file])

    def reset_search(self):
        self.translatable_entries = {}
        self.search_index = 0
        self.run_search = False

    def search(self):
        self.__search_in_file(self.search_files[self.search_index])
        self.search_index += 1
        if self.search_index >= len(self.search_files):
            self.run_search = False

    def __search_in_file(self, c_file):
        with open(c_file, "r", encoding="utf-8") as f:
            content = f.read()
        # Translation above PRINT function
        for match in re.finditer(
                r"//\s*\"(.*)\"\s*(\w*PRINTF|osSyncPrintf)\((\s*.*\s*)\"(.*)\"",
                content, re.UNICODE | re.MULTILINE):
            replacement = match.group(1).replace("\"", "")
            function = match.group(2)
            color_format = match.group(3)
            text = match.group(4)
            self.add_translatable_entry(c_file, content, function, color_format, match.start(), match.end(),
                                        replacement, text)

        # Translation at the end of line
        for match in re.finditer(r"(\w*PRINTF|osSyncPrintf)\((\s*.*\s*)\"(.*)\".*//\s*\"(.*)\"", content, re.UNICODE):
            function = match.group(1)
            color_format = match.group(2)
            text = match.group(3)
            replacement = match.group(4).replace("\"", "")
            self.add_translatable_entry(c_file, content, function, color_format, match.start(), match.end(3) + 1,
                                        replacement, text)

    def add_translatable_entry(self, c_file, content, function, color_format, start, end, replacement, text):
        cjk_substring_start, cjk_substring_end = self.get_cjk_substring(text)
        if cjk_substring_start >= 0:
            replaced_text = concat_and_replace_duplicate_substring(text[:cjk_substring_start], replacement)
            replaced_text = concat_and_replace_duplicate_substring(replaced_text, text[cjk_substring_end:])
            result = function + "(" + color_format + "\"" + replaced_text + "\""
            entry = (c_file, start, end, content[start:end], result)
            if c_file not in self.translatable_entries:
                self.translatable_entries[c_file] = [entry]
            else:
                self.translatable_entries[c_file].append(entry)

    def get_cjk_substring(self, text):
        start = -1
        end = -1
        for i in range(len(text)):
            if self.is_cjk(text[i]):
                if start == -1:
                    start = i
                end = i
        return start, end + 1

    def is_cjk(self, char):
        return any([r["from"] <= ord(char) <= r["to"] for r in self.CJK_RANGES])

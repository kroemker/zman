def replace_line(content, line_start, new_line, search_from=0):
    start = content.find("\n" + line_start, search_from) + 1

    if start == 0:
        start = content.find("\n# " + line_start) + 1
    if start == 0:
        raise Exception("Unable to find '" + line_start.strip() + "'!")
    end = content.find("\n", start)
    return content[:start] + new_line + content[end:]


def insert_block_before_line(content, line_start, block, search_from=0):
    start = content.find("\n" + line_start, search_from) + 1
    if start == 0:
        raise Exception("Unable to find '" + line_start.strip() + "'!")
    return content[:start] + block + "\n\n" + content[start:]


def remove_block_from_line_to_line(content, from_line_start, to_line_start):
    start = content.find("\n" + from_line_start) + 1
    if start == 0:
        raise Exception("Unable to find '" + from_line_start.strip() + "'!")
    end = content.find("\n" + to_line_start, start) + 1
    if end == 0:
        raise Exception("Unable to find '" + to_line_start.strip() + "'!")
    return content[:start] + content[end:]


def remove_in_line(content, line_start, string_to_remove):
    start = content.find("\n" + line_start) + 1
    if start == 0:
        raise Exception("Unable to find '" + line_start.strip() + "'!")
    string_start = content.find(string_to_remove, start)
    if string_start == -1:
        raise Exception("Unable to find '" + string_to_remove.strip() + "'!")
    return content[:string_start] + content[string_start + len(string_to_remove):]


def get_file_name_from_path(path):
    return path[max(path.rfind("\\"), path.rfind("/")) + 1:]


def concat_and_replace_duplicate_substring(first, second):
    for i in range(len(first), 0, -1):
        if second.startswith(first[-i:]):
            return first + second[i:]
    return first + second


def get_flags(flags_string):
    flags = list(map(lambda x: x.strip(), flags_string.strip("()").split("|")))
    if len(flags) == 1 and flags[0] == "0":
        return []
    return flags


def get_struct_content(struct_content_string):
    struct = []
    field_start = 0
    i = 0
    while i < len(struct_content_string):
        char = struct_content_string[i]
        if char == ",":
            field = struct_content_string[field_start:i].strip()
            if field != "":
                struct.append(field)
            field_start = i + 1
        elif char == "{":
            inner_struct, index = get_struct_content(struct_content_string[i + 1:])
            struct.append(inner_struct)
            i += index + 1
            field_start = i + 1
        elif char == "}":
            field = struct_content_string[field_start:i].strip()
            if field != "":
                struct.append(field)
            return struct, i
        i += 1
    return struct, i


def parse_c_float(string) -> float:
    return float(string.strip("f"))


def formatHex(number, digits):
    return "0x" + format(number, "0" + str(digits) + "X")


def tab(num):
    return "    " * num

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

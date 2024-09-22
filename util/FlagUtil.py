from util.StringUtil import formatHex


def build_flag_set(possible_flags_cenum, flag_constants):
    flags = {}
    for flag in possible_flags_cenum:
        flags[flag.constant] = flag.constant in flag_constants
    return flags


def build_flag_constant_list(possible_flags, flags):
    return [flag.constant for flag in possible_flags if flags[flag.constant]]


def build_flag_string(possible_flags, flags):
    return " | ".join(build_flag_constant_list(possible_flags, flags))


def build_flag_hex_string(possible_flags, flags):
    number = 0
    for i in range(len(possible_flags)):
        if flags[possible_flags[i].constant]:
            number |= 1 << i
    return formatHex(number, 8 if len(possible_flags) > 8 else 2)

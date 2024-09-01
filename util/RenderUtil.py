import imgui


def render_cenum_combo(label, index, cenum):
    return imgui.combo(label, index, [cenum.name for cenum in cenum])

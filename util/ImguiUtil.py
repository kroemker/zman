import imgui


def add_tooltip(text):
    if imgui.is_item_hovered(imgui.HOVERED_ANY_WINDOW):
        imgui.begin_tooltip()
        imgui.text(text)
        imgui.end_tooltip()

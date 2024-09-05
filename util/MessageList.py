import imgui


class MessageList:
    Warning = 0
    Error = 1
    Info = 2
    Success = 3

    def __init__(self):
        self.messages = []

    def add_message(self, message, message_type):
        self.messages.append((message_type, message))

    def clear(self):
        self.messages.clear()

    def has_errors(self):
        for message in self.messages:
            if message[0] == self.Error:
                return True
        return False

    def render(self):
        for message in self.messages:
            if message[0] == self.Warning:
                imgui.text_colored(message[1], 1.0, 1.0, 0.0)
            elif message[0] == self.Error:
                imgui.text_colored(message[1], 1.0, 0.0, 0.0)
            elif message[0] == self.Info:
                imgui.text_colored(message[1], 0.0, 1.0, 1.0)
            elif message[0] == self.Success:
                imgui.text_colored(message[1], 0.0, 1.0, 0.0)
            else:
                imgui.text(message[1])

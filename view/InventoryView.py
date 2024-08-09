from view.BaseView import BaseView


class InventoryView(BaseView):
    def __init__(self, config):
        super().__init__("Inventory", config)

    def render_internal(self):
        pass

    def update(self):
        pass

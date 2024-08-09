from abc import abstractmethod


class Patch:
    def __init__(self, config, name):
        self.config = config
        self.name = name

    @abstractmethod
    def apply(self):
        raise NotImplementedError

    @abstractmethod
    def is_patch_applied(self):
        raise NotImplementedError

    @abstractmethod
    def revert(self):
        raise NotImplementedError

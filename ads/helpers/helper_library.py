from ads.helpers.string_helper import StringHelper


class HelperLibrary:
    """Combined library of all the helper classes"""

    _global_instance = None

    def __init__(self):
        self._string_helper = StringHelper()

    @classmethod
    def global_instance(cls):
        if cls._global_instance is None:
            cls._global_instance = cls()
        return cls._global_instance


    @property
    def string(self) -> StringHelper:
        return self._string_helper
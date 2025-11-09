from ads.helpers.enum_helper import EnumHelper
from ads.helpers.filesystem_helper import FileSystemHelper
from ads.helpers.string_helper import StringHelper


class HelperLibrary:
    """Combined library of all the helper classes"""

    _global_instance = None

    def __init__(self):
        self._string_helper = StringHelper()
        self._enum_helper = EnumHelper()
        self._filesystem_helper = FileSystemHelper()

    @classmethod
    def global_instance(cls):
        if cls._global_instance is None:
            cls._global_instance = cls()
        return cls._global_instance


    @property
    def string(self) -> StringHelper:
        return self._string_helper

    @property
    def enum(self) -> EnumHelper:
        return self._enum_helper

    @property
    def filesystem(self) -> FileSystemHelper:
        return self._filesystem_helper
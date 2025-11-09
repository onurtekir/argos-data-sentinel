from typing import Optional


class EnumHelper:

    def get_value(self, enum_value, default_value: Optional[str] = None):
        return getattr(enum_value, "value", str(default_value or str(enum_value)))
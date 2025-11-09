from typing import Any, Dict, Optional

import jinja2


class StringHelper:
    """String utilities, including Jinja2 rendering."""

    @staticmethod
    def render_jinja_template(value: str,
                              params: Optional[Dict[str, Any]],
                              keep_undefined_as_is: Optional[bool] = False) -> str:
        """
        Renders a Jinja-templated string using provided parameters.

        Example:
            value = "SELECT * FROM {{ table }}"
            params = {"table": "my_table"}
        """

        env = jinja2.Environment(undefined=jinja2.DebugUndefined if keep_undefined_as_is else jinja2.StrictUndefined)
        template = env.from_string(value)
        return template.render(params or {})

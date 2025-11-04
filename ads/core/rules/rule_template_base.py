from typing import Optional, Dict, Any, ClassVar, List

from pydantic import Field, BaseModel, ConfigDict

from ads.core.base import AdsBase
from ads.core.rules.exceptions import RuleParameterError
from ads.helpers.helper_library import HelperLibrary


class RuleTemplateBase(BaseModel, AdsBase):
    """
    Base class for all rule templates.
    All custom rule templates must inherit from this.
    """

    model_config = ConfigDict(extra='ignore')

    # Class level constants
    name: ClassVar[str]
    description: ClassVar[str]
    sql_template: ClassVar[str]

    # Optional: Instance level defaults
    params: Optional[Dict[str, Any]] = Field(default_factory=dict,
                                             description="Default parameters for the rule template.")
    required_params: ClassVar[List[str]] = []

    def render(self, helpers: HelperLibrary, extra_params: Optional[Dict[str, Any]]) -> str:
        """Renders the SQL with given parameters."""
        combined_params = {**(self.params or {}), **(extra_params or {})}
        self._validate_required_params(params=combined_params)
        rendered_sql = helpers.string.render_jinja_template(
            value=self.sql_template,
            params=combined_params,
            keep_undefined_as_is=True
        )

        # region Fail-safe validation in final SQL script to check unresolved Jinja variables
        if "{{" in rendered_sql or "}}" in rendered_sql:
            raise RuleParameterError(rule_name=self.name, missing_params=["unresolved Jinja variables"])
        # endregion

        return rendered_sql

    def _validate_required_params(self, params: Dict[str, Any]) -> None:
        """Checks that all required parameters are present and non-None."""
        missing_params = [p for p in getattr(self, "required_params", []) if not params.get(p)]
        if missing_params:
            raise RuleParameterError(rule_name=getattr(self, "name", "unknown"),
                                     missing_params=missing_params)

    def __repr__(self):
        return f"<RuleTemplate name='{self.name}' required={self.required_params}>"
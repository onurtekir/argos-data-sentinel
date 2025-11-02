from typing import List


class RuleParameterError(ValueError):
    """Raised when a required rule parameter is missing or invalid."""

    def __init__(self, rule_name: str, missing_params: List[str]):
        msg = f"Rule '{rule_name}' missing required parameter(s): {', '.join(missing_params)}"
        super().__init__(msg)
        self.rule_name = rule_name
        self.missing_params = missing_params
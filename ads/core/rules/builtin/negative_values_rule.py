from typing import ClassVar, List

from ads.core.rules.rule_template_base import RuleTemplateBase


class NegativeValuesRule(RuleTemplateBase):
    """
    Ensures that numeric columns do not contain negative values.
    """

    name: ClassVar[str] = "negative_values"
    description: ClassVar[str] = "Counts negative values in a numeric column."
    sql_template: ClassVar[str] = """
SELECT 
    '{{ check_name }}' AS check_name,
    COUNTIF({{ column_name }} < 0) AS value
FROM
    cte_{{ suite_name }}_base
    """
    required_params: ClassVar[List[str]] = ["column_name"]
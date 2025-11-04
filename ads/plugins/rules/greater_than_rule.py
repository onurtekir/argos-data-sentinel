from typing import ClassVar, List

from ads.core.rules.rule_template_base import RuleTemplateBase


class GreaterThan(RuleTemplateBase):
    """
    Ensures that a column only contains values greater than the lower limit value.
    """

    name: ClassVar[str] = "greater_than"
    description: ClassVar[str] = "Counts values greater than the lower limit value."
    sql_template: ClassVar[str] = """
SELECT 
    '{{ check_name }}' AS check_name,
    COUNTIF({{ column_name }} > ({{ lower_limit_value }})) AS value
FROM
    cte_{{ suite_name }}_base
    """
    required_params: ClassVar[List[str]] = ["column_name", "lower_limit_value"]
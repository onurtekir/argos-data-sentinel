from typing import List, ClassVar

from ads.core.rules.rule_template_base import RuleTemplateBase


class ValueRangeRule(RuleTemplateBase):
    """
    Counts how many rows have column values outside a specified range.
    """

    name: ClassVar[str] = "value_range"
    description: ClassVar[str] = "Checks if numeric values fall within a specified range."
    sql_template: ClassVar[str] = """
SELECT
    '{{ check_name }}' AS check_name,
    COUNTIF({{ column_name }} < {{ lower_bound }} OR {{ column_name }} > {{ upper_bound }}) AS value
FROM
    cte_{{ suite_name }}_base
    """
    required_params: ClassVar[List[str]] = ["column_name", "lower_bound", "upper_bound"]
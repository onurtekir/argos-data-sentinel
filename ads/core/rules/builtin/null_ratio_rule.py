from typing import ClassVar, List

from ads.core.rules.rule_base import RuleTemplateBase


class NullRatioRule(RuleTemplateBase):
    """
    Calculates the ratio of NULL values in a column (0–1).
    """

    name: ClassVar[str] = "null_ratio"
    description: ClassVar[str] = "Computes ratio of NULL values to total records."
    sql_template: ClassVar[str] = """
SELECT 
    '{{ check_name }}' AS check_name,
    SAFE_DIVIDE(COUNTIF({{ column_name }} IS NULL), COUNT(*)) AS value
FROM
    cte_{{ suite_name }}_base
    """
    required_params: ClassVar[List[str]] = ["column_name"]
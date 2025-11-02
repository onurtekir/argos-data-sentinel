from typing import ClassVar, List

from ads.core.rules.rule_base import RuleTemplateBase


class NotNullRule(RuleTemplateBase):
    """
    Counts the number of NULL values in a column.
    A result of 0 means the column is fully populated (PASS).
    """

    name: ClassVar[str] = "not_null"
    description: ClassVar[str] = "Counts NULL values in a specific column"
    sql_template: ClassVar[str] = """
SELECT
    '{{ check_name }}' AS check_name,
    COUNTIF({{ column_name }} IS NULL) AS value
FROM cte_{{ suite_name }}_base
    """
    required_params: ClassVar[List[str]] = ["column_name"]
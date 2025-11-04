from typing import ClassVar, List

from ads.core.rules.rule_template_base import RuleTemplateBase


class UniqueRule(RuleTemplateBase):
    """
    Ensures that all values in a column are unique.
    """

    name: ClassVar[str] = "unique"
    description: ClassVar[str] = "Counts duplicate values in a column."
    sql_template: ClassVar[str] = """
SELECT 
    '{{ check_name }}' AS check_name,
    COUNT(*) - COUNT(DISTINCT {{ column_name }}) AS value
FROM
    cte_{{ suite_name }}_base
    """
    required_params: ClassVar[List[str]] = ["column_name"]
from typing import ClassVar, List

from ads.core.rules.rule_template_base import RuleTemplateBase


class ConstantColumnRule(RuleTemplateBase):
    """
    Checks whether a column contains only one distinct value.
    """

    name: ClassVar[str] = "constant_column"
    description: ClassVar[str] = "Counts extra distinct values beyond the first."
    sql_template: ClassVar[str] = """
SELECT 
    '{{ check_name }}' AS check_name,
    COUNT(DISTINCT {{ column_name }}) -1 AS value
FROM
    cte_{{ suite_name }}_base
    """
    required_params: ClassVar[List[str]] = ["column_name"]
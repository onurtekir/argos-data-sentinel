from typing import ClassVar, List

from ads.core.rules.rule_template_base import RuleTemplateBase


class RowCountRule(RuleTemplateBase):
    """
    Measures total number of rows in the dataset.
    """

    name: ClassVar[str] = "row_count"
    description: ClassVar[str] = "Counts total rows in the dataset."
    sql_template: ClassVar[str] = """
SELECT
    '{{ check_name }}' AS check_name,
    COUNT(*) AS value
FROM
    cte_{{ suite_name }}_base    
    """
    required_params: ClassVar[List[str]] = []
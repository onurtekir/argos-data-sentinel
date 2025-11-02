from typing import ClassVar, List

from ads.core.rules.rule_base import RuleTemplateBase


class DuplicateRowsRule(RuleTemplateBase):
    """
    Detects duplicate records based on a combination of key columns.
    """

    name: ClassVar[str] = "duplicate_rows"
    description: ClassVar[str] = "Counts duplicate rows based on specified key columns."
    sql_template: ClassVar[str] = """
SELECT 
    '{{ check_name }}' AS check_name,
    COUNT(*) - COUNT(DISTINCT CONCAT({{ column_names | join(', ') }})) AS value
FROM
    cte_{{ suite_name }}_base
    """
    required_params: ClassVar[List[str]] = ["check_name", "suite_name", "column_names"]
from typing import ClassVar, List

from ads.core.rules.rule_template_base import RuleTemplateBase


class ReferentialIntegrityRule(RuleTemplateBase):
    """
    Verifies foreign key integrity between two tables.
    """

    name: ClassVar[str] = "referential_integrity"
    description: ClassVar[str] = "Counts rows where column value not found in reference table"
    sql_template: ClassVar[str] = """
SELECT 
    '{{ check_name }}' AS check_name,
    COUNTIF(
        NOT EXISTS(
            SELECT 1 FROM `{{ reference_table }}` r
            WHERE r.{{ reference_column }} = b.{{ column_name }}
        )
    ) AS value
FROM cte_{{ suite_name }}_base AS b
    """
    required_params: ClassVar[List[str]] = ["column_name", "reference_table", "reference_column"]
from typing import ClassVar, List

from ads.core.rules.rule_template_base import RuleTemplateBase


class AcceptedValuesRule(RuleTemplateBase):
    """
    Ensures that a column only contains values from a predefined set.
    """

    name: ClassVar[str] = "accepted_values"
    description: ClassVar[str] = "Counts values not in the accepted list."
    sql_template: ClassVar[str] = """
SELECT 
    '{{ check_name }}' AS check_name,
    COUNTIF({{ column_name }} NOT IN ({{ accepted_values | join(', ') }})) AS value
FROM
    cte_{{ suite_name }}_base
    """
    required_params: ClassVar[List[str]] = ["column_name", "accepted_values"]
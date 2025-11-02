from typing import ClassVar, List

from ads.core.rules.rule_base import RuleTemplateBase


class RegexMatchRule(RuleTemplateBase):
    """
    Validates that values in a column match a regular expression pattern.
    """

    name: ClassVar[str] = "regex_match"
    description: ClassVar[str] = "Counts values not matching regex pattern."
    sql_template: ClassVar[str] = """
SELECT 
    '{{ check_name }}' AS check_name,
    COUNTIF(REGEXP_CONTAINS({{ column_name }}, r'{{ regex_pattern }}') = FALSE) AS value
FROM
    cte_{{ suite_name }}_base
    """
    required_params: ClassVar[List[str]] = ["column_name", "regex_pattern"]
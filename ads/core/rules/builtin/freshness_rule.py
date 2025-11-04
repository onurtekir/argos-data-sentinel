from enum import Enum
from typing import ClassVar, List

from ads.core.rules.rule_template_base import RuleTemplateBase


class FreshnessGranularity(Enum):
    MICROSECOND = "MICROSECOND"
    MILLISECOND = "MILLISECOND"
    SECOND = "SECOND"
    MINUTE = "MINUTE"
    HOUR = "HOUR"
    DAY = "DAY"

class FreshnessRule(RuleTemplateBase):
    """
    Measures the freshness of data based on a timestamp column.
    """

    name: ClassVar[str] = "freshness"
    description: ClassVar[str] = "Calculates (MICROSECOND, MILLISECOND, SECOND, MINUTE, HOUR, DAY) since most recent record."
    sql_template: ClassVar[str] = """
SELECT 
    '{{ check_name }}' AS check_name,
    TIMESTAMP_DIFF(CURRENT_TIMESTAMP(), MAX({{ column_name }}), {{ granularity }}) AS value
FROM
    cte_{{ suite_name }}_base  
    """
    required_params: ClassVar[List[str]] = ["column_name", "granularity"]
import importlib
import inspect
import pkgutil
import re
from types import ModuleType
from typing import List, Any, Dict, Type

import regex
from torch.nn.functional import bilinear

from ads.core.rules.builtin.accepted_values_rule import AcceptedValuesRule
from ads.core.rules.builtin.constant_colum_rule import ConstantColumnRule
from ads.core.rules.builtin.duplicate_rows_rule import DuplicateRowsRule
from ads.core.rules.builtin.freshness_rule import FreshnessRule, FreshnessGranularity
from ads.core.rules.builtin.negative_values_rule import NegativeValuesRule
from ads.core.rules.builtin.not_null_rule import NotNullRule
from ads.core.rules.builtin.null_ratio_rule import NullRatioRule
from ads.core.rules.builtin.referential_integrity_rule import ReferentialIntegrityRule
from ads.core.rules.builtin.regex_match_rule import RegexMatchRule
from ads.core.rules.builtin.row_count_rule import RowCountRule
from ads.core.rules.builtin.unique_rule import UniqueRule
from ads.core.rules.builtin.value_range_rule import ValueRangeRule
from ads.core.rules.rule_base import RuleTemplateBase


class CoreRulesetRegistry:
    """Registry for all built-in rule templates."""
    
    @property
    def not_null(self) -> NotNullRule:
        return NotNullRule()

    @property
    def unique(self) -> UniqueRule:
        return UniqueRule()

    @property
    def row_count(self) -> RowCountRule:
        return RowCountRule()

    @property
    def negative_values(self) -> NegativeValuesRule:
        return NegativeValuesRule()

    @property
    def constant_column(self) -> ConstantColumnRule:
        return ConstantColumnRule()

    @property
    def null_ratio(self) -> NullRatioRule:
        return NullRatioRule()

    def regex_match(self, regex_pattern: re.Pattern[str]) -> RegexMatchRule:
        return RegexMatchRule(params={"regex_pattern": regex_pattern})

    def duplicated_rows(self, column_names: List[str]) -> DuplicateRowsRule:
        return DuplicateRowsRule(params={"column_names": column_names})

    def freshness(self, granularity: FreshnessGranularity = FreshnessGranularity.HOUR) -> FreshnessRule:
        return FreshnessRule(params={"granularity": granularity.value})

    def referential_integrity(self, reference_table: str, reference_column: str) -> ReferentialIntegrityRule:
        return ReferentialIntegrityRule(
            params={"reference_table": reference_table, "reference_column": reference_column}
        )

    def accepted_values(self, accepted_values: List[Any]) -> AcceptedValuesRule:
        return AcceptedValuesRule(params={"accepted_values": accepted_values})

    def value_range(self, lower_bound: float, upper_bound: float) -> ValueRangeRule:
        return ValueRangeRule(params={"upper_bound": upper_bound, "lower_bound": lower_bound})

core_ruleset = CoreRulesetRegistry()
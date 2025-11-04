from ads.core.base import AdsBase
from ads.core.rules.core_ruleset_registry import CoreRulesetRegistry
from ads.core.rules.plugin_ruleset_registry import PluginRulesetRegistry
from ads.core.rules.rule_template_base import RuleTemplateBase


class RulesetRegistry(AdsBase):
    """Unified registry for Core Ruleset and Plugin Ruleset(s)"""

    def __init__(self):
        self._core = CoreRulesetRegistry()
        self._plugins = PluginRulesetRegistry()

    @property
    def core(self) -> CoreRulesetRegistry:
        return self._core

    @property
    def plugins(self) -> PluginRulesetRegistry:
        return self._plugins

    def get(self, rule_name: str) -> RuleTemplateBase:
        if hasattr(self._core, rule_name):
            return getattr(self._core, rule_name)
        if rule_name in self._plugins:
            return self._plugins.get(name=rule_name)
        raise KeyError(f"Rule '{rule_name}' not found in core or plugin registry")



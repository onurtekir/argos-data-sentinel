import importlib
import inspect
import pkgutil
from types import ModuleType
from typing import List, Any, Dict, Type

from ads.core.base import AdsBase
from ads.core.rules.rule_template_base import RuleTemplateBase


class PluginRulesetRegistry(AdsBase):
    """
    Dynamic registry for all plugin rule templates.

    Automatically discovers and loads rule classes defined under
    ads.plugins.rules.*, registering them by their `name` attribute.

    Example:
        plugin_rules = PluginRulesetRegistry()
        plugin_rule = plugin_rules.get("not_null")
        plugin_rule.render(helpers, {"column_name": "customer_id"})
    """

    def __init__(self):
        self._rules = {}
        self._load_builtin_rules()

    def _load_builtin_rules(self) -> None:
        """Dynamically import and register all rule classes under plugins/rules/"""
        import ads.plugins.rules as plugin_pkg

        for module_info in pkgutil.iter_modules(plugin_pkg.__path__, plugin_pkg.__name__ + "."):
            module = importlib.import_module(module_info.name)
            self._register_rules_from_module(module)

    def _register_rules_from_module(self, module: ModuleType) -> None:
        """Find and register all RuleTemplateBase subclasses in the given module."""
        for _, obj in inspect.getmembers(module, inspect.isclass):
            if issubclass(obj, RuleTemplateBase) and obj is not RuleTemplateBase:
                rule_name = getattr(obj, "name", obj.__name__).lower()
                self._rules[rule_name] = obj

    def get(self, name: str, **params: Any) -> RuleTemplateBase:
        """Returns an instance of the given rule, optionally initialized with parameters."""
        rule_cls = self._rules.get(name.lower())
        if not rule_cls:
            raise KeyError(f"Rule '{name}' not found in registry")
        instance = rule_cls()
        if params:
            instance.params.update(params)

        return instance

    def list(self) -> Dict[str, Type[RuleTemplateBase]]:
        """Returns a dictionary of all available rule names and their classes."""
        return dict(self._rules)

    def __getitem__(self, name: str) -> RuleTemplateBase:
        """Shortcut for ruleset['not_null'] access."""
        return self.get(name)

    def __repr__(self):
        rule_names = ", ".join(sorted(self._rules.keys()))
        return f"<PluginRulesetRegistry rules=[{rule_names}]>"

plugin_ruleset = PluginRulesetRegistry()
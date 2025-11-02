from ads.core.rules.ruleset_registry import RulesetRegistry


def test_core_rule_loading():

    registry = RulesetRegistry()
    not_null_rule = registry.core.not_null
    print(f"Rule '{not_null_rule.name}' loaded with the required parameters {', '.join(not_null_rule.required_params)}")


def test_plugin_rule_loading():
    registry = RulesetRegistry()
    greater_than_rule = registry.plugins.get("greater_than")
    print(f"Rule '{greater_than_rule.name}' loaded with the required parameters {', '.join(greater_than_rule.required_params)}")

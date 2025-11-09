import json

from ads.core.enums import DataSourceType, Severity, CheckStatus, ResultExportType, SuiteRunStatus
from ads.core.models import ResultsMetadata, DataSource, Check, Threshold, Suite
from ads.core.rules.ruleset_registry import RulesetRegistry
from ads.core.runner.sentinel_runner import SentinelRunner


class MockExecutor:
    """Simulates a BigQuery executor for unit testing."""

    def __init__(self, *_, **__):
        self._called = False

    def execute(self, *_, **__):
        self._called = True
        metadata = ResultsMetadata(status="SUCCESS", duration_ms=1234.5, job_id="bq_mock_job_1")
        rows = [
            {"check_name": "customer_id_null_check", "value": 0.0},
            {"check_name": "positive_revenue_check", "value": 1.2},
        ]
        return metadata, rows

def test_end_to_end_json_export(monkeypatch, tmp_path):

    # region Prepare the suite
    data_source = DataSource(
        type=DataSourceType.QUERY,
        query="SELECT * FROM temp_table",
        description="This is the suite for testing END-to-END JSON exporter"
    )

    ruleset_registry = RulesetRegistry()

    checks = [
        Check(
            name="customer_id_null_check",
            threshold=Threshold(value=0.7),
            description="NULL check for column 'customer_id'",
            rule_template=ruleset_registry.core.not_null,
            severity=Severity.CRITICAL,
            column_name="customer_id"
        ),
        Check(
            name="positive_revenue_check",
            description="All the revenue values should be position",
            severity=Severity.CRITICAL,
            rule_template=ruleset_registry.core.negative_values,
            column_name="revenue"
        )
    ]

    suite = Suite(name="Sales_Quality_Suite",
                  checks=checks,
                  data_source=data_source)
    # endregion

    # region Patch Executor with mock
    from ads.core.runner import sentinel_runner
    monkeypatch.setattr(sentinel_runner, "Executor", MockExecutor)
    # endregion

    # region Run full pipeline
    runner = SentinelRunner(project_id="dummy")
    metadata, results = runner.run_suite(suite)

    assert metadata.status == SuiteRunStatus.SUCCESS
    assert len(results) == 2
    print(results)
    assert results[0].status == CheckStatus.FAIL
    assert results[1].status == CheckStatus.PASS

    # endregion

    # region Export results
    output_path = tmp_path / "end_to_end.json"
    runner.export_results(results=results,
                          metadata=metadata,
                          export_type=ResultExportType.JSON,
                          destination=str(output_path))
    # endregion

    # region Validate output content
    assert output_path.exists(), "JSON export file was not created"

    content = json.loads(output_path.read_text())
    assert "metadata" in content
    assert content["metadata"]["status"] == "SUCCESS"

    exported_results = content["results"]
    assert len(exported_results) == 2
    assert exported_results[0]["check_name"] == "customer_id_null_check"
    assert exported_results[1]["check_name"] == "positive_revenue_check"
    # endregion

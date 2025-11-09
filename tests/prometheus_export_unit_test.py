from ads.core.enums import SuiteRunStatus, CheckStatus, Severity
from ads.core.exporters.prometheus_exporter import PrometheusExporter
from ads.core.models import ResultsMetadata, Result


def test_prometheus_file_export(tmp_path):
    exporter = PrometheusExporter()
    output_path = tmp_path / "metrics.prom"

    metadata = ResultsMetadata(
        suite_name="sales_suite",
        status=SuiteRunStatus.SUCCESS
    )

    results = [
        Result(check_name="null_check", status=CheckStatus.PASS, severity=Severity.INFO, value=0),
        Result(check_name="unique_check", status=CheckStatus.FAIL, severity=Severity.CRITICAL, value=5),
    ]

    exporter.export(metadata=metadata, results=results, destination=output_path)

    content = output_path.read_text()
    assert "sales_suite" in content
    assert "ads_check_value" in content
    assert "null_check" in content
    assert "unique_check" in content
    assert "FAIL" in content

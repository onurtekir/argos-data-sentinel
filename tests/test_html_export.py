from ads.core.exporters.html_exporter import HtmlExporter
from ads.core.models import ResultsMetadata, Result
from ads.core.enums import SuiteRunStatus, CheckStatus, Severity


def test_html_exporter(tmp_path):
    exporter = HtmlExporter()
    metadata = ResultsMetadata(
        job_id="job_001",
        suite_name="sales_suite",
        suite_description="Test HTML export for Argos Data Sentinel",
        status=SuiteRunStatus.SUCCESS
    )
    results = [
        Result(check_name="null_check", status=CheckStatus.PASS, severity=Severity.INFO, value=0.0, message="No nulls found"),
        Result(check_name="unique_check", status=CheckStatus.FAIL, severity=Severity.CRITICAL, value=12, message="Duplicates found")
    ]

    html_file = tmp_path / "test_report.html"
    path = exporter.export(metadata=metadata, results=results, destination=html_file,
                           config={"custom_message": "This is a test HTML export"})
    assert html_file.exists()
    content = html_file.read_text()
    assert "sales_suite" in content
    assert "Suite Run Metadata" in content
    assert "Suite Results" in content
    assert "This is a test HTML export" in content

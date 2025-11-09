from ads.core.enums import ResultExportType
from ads.core.exporters.csv_exporter import CsvExporter
from ads.core.exporters.exporter_base import ExporterBase
from ads.core.exporters.json_exporter import JsonExporter
from ads.core.exporters.prometheus_exporter import PrometheusExporter
from ads.core.exporters.sqlite_exporter import SQLiteExporter


class ExporterRegistry:
    """Registry for available exporters."""

    def __init__(self):
        self._exporters = {
            ResultExportType.JSON: JsonExporter(),
            ResultExportType.SQLITE: SQLiteExporter(),
            ResultExportType.PROMETHEUS: PrometheusExporter(),
            ResultExportType.CSV: CsvExporter()
        }

    def get(self, export_type: ResultExportType) -> ExporterBase:
        if export_type not in self._exporters:
            raise ValueError(f"No available exporter found for type '{export_type.name}'")
        return self._exporters[export_type]
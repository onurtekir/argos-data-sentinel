import csv
from pathlib import Path
from typing import List, Optional, Dict, Any

from ads.core.exporters.exporter_base import ExporterBase
from ads.core.models import ResultsMetadata, Result


class CsvExporter(ExporterBase):
    """
    Exports suite run metadata and results into two CSV files:

        <suite_name>_run.csv      - single row with execution metadata
        <suite_name>_results.csv  - one row per check result
    """


    def _sanitize_name(self, name: str) -> str:
        """Converts arbitrary suite names into filesystem-safe names."""
        return "".join(c if c.isalnum() or c in "-._" else "_" for c in name)

    def export(self,
               metadata: ResultsMetadata,
               results: List[Result],
               destination: Optional[str] = None,
               config: Optional[Dict[Any, Any]] = None) -> Optional[str]:
        """
        Args:
            metadata: Suite-level execution metadata
            results: List of Result objects
            destination:
                - If directory path: files are created inside it.
                - If None: uses current working directory.
            config: reserved for future options (e.g. custom filenames)
        Returns:
            The directory path where CSV files are written (as string).
        """

        # region Resolve target directory and create parent directories if needed
        base_dir = Path(destination) if destination else Path(".")
        self.helpers.filesystem.create_parent_directories(path=base_dir)
        # endregion

        # region Generate CSV file names
        suite_name = self._sanitize_name(metadata.suite_name)
        runs_csv_file = base_dir / f"{suite_name}_run.csv"
        results_csv_file = base_dir / f"{suite_name}_results.csv"
        # endregion

        # region Get columns and rows delimiter from config
        column_delimiter = (config or {}).get("column_delimiter", ",")
        row_delimiter = (config or {}).get("row_delimiter", "\n")
        # endregion

        # region Prepare and write run payload
        run_payload = metadata.model_dump(mode="json")
        run_payload.setdefault("error_count", len(metadata.errors or []))
        run_columns = [
            "job_id",
            "suite_name",
            "suite_description",
            "status",
            "started_at",
            "ended_at",
            "duration_ms",
            "bytes_processed",
            "cache_hit",
            "validate_first",
            "validate_only",
            "error_count",
            "extra",
        ]

        # Add dynamic columns
        for key in run_payload.keys():
            if key not in run_columns:
                run_columns.append(key)

        # Run columns to run CSV file
        with runs_csv_file.open("w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f,
                                    fieldnames=run_columns,
                                    delimiter=column_delimiter,
                                    lineterminator=row_delimiter)
            writer.writeheader()
            writer.writerow(run_payload)
        # endregion

        # region Prepare and write results payloads
        results_rows = []
        for r in results:
            data = r.model_dump(mode="json")
            row = {
                "check_name": data.get("check_name"),
                "check_description": data.get("check_description"),
                "check_params": data.get("check_params"),
                "status": data.get("status"),
                "severity": data.get("severity"),
                "value": data.get("value"),
                "threshold_lower": data.get("threshold_lower"),
                "threshold_upper": data.get("threshold_upper"),
                "message": data.get("message")
            }

            # Include dynamic fields
            for key, value in data.items():
                if key not in row:
                    row[key] = value
            results_rows.append(row)

        if results_rows:
            # region Write result rows
            result_columns = list(results_rows[0].keys())
            with results_csv_file.open("w", encoding="utf-8", newline="") as f:
                writer = csv.DictWriter(f,
                                       fieldnames=result_columns,
                                       delimiter=column_delimiter,
                                       lineterminator=row_delimiter)
                writer.writeheader()
                writer.writerows(results_rows)
            # endregion
        else:
            # region Write empty row
            with results_csv_file.open("w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    [
                        "check_name",
                        "check_description",
                        "check_params",
                        "status",
                        "severity",
                        "value",
                        "threshold_lower",
                        "threshold_upper",
                        "message",
                    ])
            # endregion

        # endregion

        self.logger.info(
            "CSV export completed → run='%s', results='%s'",
            runs_csv_file.resolve(),
            results_csv_file.resolve()
        )

        return str(base_dir.resolve())
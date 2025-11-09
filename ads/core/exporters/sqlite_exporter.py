import json
import sqlite3
from multiprocessing.reduction import send_handle
from pathlib import Path
from typing import List, Optional, Dict, Any

from pydantic.v1.json import custom_pydantic_encoder

from ads.core.exporters.exporter_base import ExporterBase
from ads.core.models import ResultsMetadata, Result


class SQLiteExporter(ExporterBase):
    """
    Persists suite execution metadata and results into a local SQLite database.

    The exporter automatically initializes schema if the database file does not exist.
    """

    def _ensure_database(self, db_path: Path, runs_table: str, results_table: str) -> None:
        """Initializes database and creates schema if not present."""
        try:
            # region Load ADS Runs SQL query
            sql_ads_runs = self._load_sql_template(
                sql_path=Path("templates/sqlite_exporter/table__ads_runs.sql"),
                params={"ads_runs_table_name": runs_table}
            )
            # endregion

            # region Load ADS Results SQL query
            sql_ads_results = self._load_sql_template(
                sql_path=Path("templates/sqlite_exporter/table__ads_results.sql"),
                params={"ads_results_table_name": results_table}
            )
            # endregion

            # region Auto create missing parent directories
            self.helpers.filesystem.create_parent_directories(path=db_path.parent)
            # endregion

            # region Create/Check database and tables
            with sqlite3.connect(db_path) as conn:
                cursor = conn.cursor()
                cursor.executescript(sql_ads_runs)
                cursor.executescript(sql_ads_results)
                conn.commit()
            # endregion
        except Exception as e:
            self.logger.error(f"Failed to initialize SQLite DB: {e}")
            raise

    def _load_sql_template(self, sql_path: Path, params: Dict[str, Any]) -> str:
        """Loads SQL template and apply Jinja templates."""
        with open("templates/sqlite_exporter/table__ads_results.sql", "r") as f:
            return self.helpers.string.render_jinja_template(
            value=f.read(),
            params=params,
            keep_undefined_as_is=False
        )

    def export(self,
               metadata: ResultsMetadata,
               results: List[Result],
               destination: Optional[str] = None,
               config: Optional[Dict[Any, Any]] = None) -> Optional[str]:
        """
        Writes the metadata and all results into the SQLite database.

        Args:
            metadata: suite-level execution metadata
            results: list of Result objects
            destination: optional custom DB file path
            config: optional configuration parameters
        """

        runs_table_name = (config or {}).get("runs_table_name", "ads_runs")
        results_table_name = (config or {}).get("results_table_name", "ads_results")

        db_file = Path(destination or "ads_database.db")

        # region Ensure database and tables first
        self._ensure_database(db_path=db_file,
                              runs_table=runs_table_name,
                              results_table=results_table_name)
        # endregion

        with sqlite3.connect(db_file) as conn:
            cursor = conn.cursor()
            conn.execute("BEGIN")

            # region Insert suite run metadata
            cursor.execute(f"""
            INSERT INTO {runs_table_name} (
                job_id, 
                suite_name, 
                suite_description,
                status,
                started_at,
                ended_at,
                duration_ms,
                bytes_processed,
                cache_hit,
                validate_first,
                validate_only,
                error_count,
                extra
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,(
                metadata.job_id,
                metadata.suite_name,
                metadata.suite_description,
                self.helpers.enum.get_value(metadata.status.value),
                metadata.started_at,
                metadata.ended_at,
                metadata.duration_ms,
                metadata.bytes_processed,
                metadata.cache_hit,
                metadata.validate_first,
                metadata.validate_only,
                len(metadata.errors or []),
                json.dumps(metadata.extra or {})
            ))

            run_id = cursor.lastrowid
            # endregion

            # region Insert ADS results
            for r in results:
                cursor.execute(f"""
                INSERT INTO {results_table_name} (
                    run_id,
                    check_name,
                    check_description,
                    check_params,
                    status,
                    severity,
                    value,
                    threshold_lower,
                    threshold_upper,
                    message
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,(
                    run_id,
                    r.check_name,
                    r.check_description,
                    json.dumps(r.check_params or {}),
                    self.helpers.enum.get_value(r.status.value),
                    self.helpers.enum.get_value(r.severity),
                    r.value,
                    r.threshold_lower,
                    r.threshold_upper,
                    r.message
                ))
            # endregion

            conn.commit()

        self.logger.info(f"SQLite export completed successfully → '{db_file.resolve()}'")

        return str(db_file.resolve())

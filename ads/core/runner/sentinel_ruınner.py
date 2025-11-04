import time
from typing import Optional, List, Dict, Any, Tuple

from ads.core.base import AdsBase
from ads.core.engine.executor import Executor
from ads.core.engine.result_parser import ResultParser
from ads.core.engine.sql_builder import SQLBuilder
from ads.core.enums import ResultExportType, CheckStatus, Severity
from ads.core.models import Suite, Result, ResultsMetadata
from ads.helpers.helper_library import HelperLibrary


class SentinelRunner(AdsBase):
    """
    Central orchestrator for executing Data Quality Suites within Argos Data Sentinel.

    Responsibilities:
        - Compile Suite definitions into executable SQL (via SQLBuilder)
        - Optionally perform a dry-run to validate query correctness
        - Execute SQL against BigQuery using Executor
        - Parse raw query output into structured Result objects (via ResultParser)
        - Optionally export or persist results (e.g., JSON, SQLite, Prometheus)
    """

    def __init__(self,
                 project_id: str,
                 location: Optional[str] = None):
        self._helpers = HelperLibrary()
        self._project_id = project_id
        self._location = location
        self._executor = Executor(project_id=project_id,
                                  helpers=self._helpers,
                                  location=location)
        self._result_parser = ResultParser()

    @property
    def project_id(self) -> str:
        return self._project_id

    @property
    def helpers(self) -> HelperLibrary:
        return self._helpers

    @property
    def location(self) -> Optional[str]:
        return self._location

    def run_suite(self,
                  suite: Suite,
                  validate_first: Optional[bool] = True,
                  validate_only: Optional[bool] = False,
                  flatten_results: Optional[bool] = False,
                  extra: Optional[Dict[str, Any]] = None) -> Tuple[ResultsMetadata, List[Result]]:
        """
        Compiles and executes all checks within a Suite.

        Steps:
            1. Build unified SQL (SQLBuilder)
            2. Dry-run to validate
            3. Execute full query
            4. Parse results into structured Result objects
        """

        # region Prepare the SQL and execute
        builder = SQLBuilder(suite=suite, helpers=self.helpers)
        sql_query = builder.build()

        metadata, rows = self._executor.execute(
            sql_query=sql_query,
            flatten_results=flatten_results,
            validate_first=validate_first,
            validate_only=validate_only,
            extra=extra
        )
        # endregion

        # region Parse results
        results = self._result_parser.parse(rows=rows)
        # endregion

        return metadata, results


    def run_check(self, suite: Suite, check_name: str) -> Optional[Result]:
        """
        Executes a single check from within the suite (for debugging or development).

        Typically used when iterating on rule definitions or testing new checks.
        """
        raise NotImplementedError("To be implemented later")

    def export_results(self,
                       results: List[Result],
                       export_format: Optional[ResultExportType] = ResultExportType.JSON,
                       destination: Optional[str] = None) -> None:
        """
        Exports a list of Result objects to the specified format.

        Supported formats (MVP):
            - JSON (default)
            - SQLite (planned)
            - Prometheus (planned)
        """
        raise NotImplementedError("Exporting logic will be added later")

    def __repr__(self):
        return f"<SentinelRunner project='{self.project_id}' location='{self.location}'"
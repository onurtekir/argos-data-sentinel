import time
from typing import Optional, Tuple, List, Dict, Any

from google.cloud import bigquery

from ads.core.base import AdsBase
from ads.core.enums import SuiteRunStatus
from ads.core.models import ResultsMetadata, Suite
from ads.helpers.helper_library import HelperLibrary


class Executor(AdsBase):
    """
    Responsible for executing a compiled BigQuery SQL statement and
    returning raw results and execution metadata.

    The Executor isolates all interactions with BigQuery so that the
    rest of the engine remains backend-agnostic.

    Steps:
        1. Connect to BigQuery using Application Default Credentials.
        2. Submit and monitor a query job.
        3. Collect metrics (duration, bytes processed, cache hit, job id).
        4. Return the raw results as a list of dictionaries.

    Example:
        executor = Executor(project_id="my_project")
        rows, metrics = executor.execute(compiled_sql)
    """

    def __init__(self,
                 project_id: str,
                 helpers: HelperLibrary,
                 location: Optional[str] = None):
        """Initializes a BigQuery client and basic execution settings"""
        self._project_id = project_id
        self._location = location
        self._helpers = helpers
        self._client: Optional[bigquery.Client] = None

    # region Properties
    @property
    def helpers(self) -> HelperLibrary:
        return self._helpers

    @property
    def project_id(self) -> str:
        return self._project_id

    @property
    def location(self) -> Optional[str]:
        return self._location
    # endregion

    def _connect(self) -> bigquery.Client:
        """Creates and caches a BigQuery client"""
        if not self._client:
            self._client = bigquery.Client(project=self.project_id, location=self.location)
        return self._client

    def execute(self,
                suite: Suite,
                sql_query: str,
                flatten_results: Optional[bool] = False,
                validate_first: Optional[bool] = True,
                validate_only: Optional[bool] = False,
                extra: Optional[Dict[str, Any]] = None) -> Tuple[ResultsMetadata, List[Dict[str, Any]]]:
        """
        Executes the given SQL statement in BigQuery

        Returns:
            - rows: List of result rows (as dicts)
            - metadata: Dict wit execution info (job_id, duration, bytes_processed, etc.)
        """

        # region Initialize connection and prepare base metadata
        client = self._connect()
        metadata: ResultsMetadata = ResultsMetadata(
            suite_name=suite.name,
            suite_description=suite.description,
            validate_first=validate_first,
            validate_only=validate_only,
            started_at=time.time(),
            extra=extra
        )
        # endregion

        # region Prepare and execute dry_run
        if validate_only or validate_first:
            try:
                dry_job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
                dry_job = client.query(query=sql_query, job_config=dry_job_config)
                metadata.job_id = dry_job.job_id
                metadata.bytes_processed = dry_job.total_bytes_processed
                metadata.cache_hit = dry_job.cache_hit
                metadata.status = SuiteRunStatus.VALIDATION_SUCCESS
            except Exception as e:
                metadata.status = SuiteRunStatus.VALIDATION_FAILED
                metadata.errors = [str(e)]
                return metadata, []

            if validate_only:
                return metadata, []
        # endregion

        # region Execute Query
        job_config = bigquery.QueryJobConfig
        rows: List[Dict[str, Any]] = []
        try:

            # region Execute actual query and return results
            job = client.query(query=sql_query, job_config=job_config)
            result = job.result()

            metadata.job_id = job.job_id
            metadata.bytes_processed = job.total_bytes_processed
            metadata.cache_hit = job.cache_hit
            metadata.status = SuiteRunStatus.SUCCESS

            rows = self._to_dict_rows(result=result, flatten=flatten_results)
            # endregion

        except Exception as e:

            # region Get errors if exist
            errors = []
            try:
                errors = [err["message"] for err in (job.errors or [])]
            except Exception:
                pass
            # endregion

            # region Update metadata and return result
            metadata.job_id = getattr(job, "job_id", None)
            metadata.status = SuiteRunStatus.FAILED
            metadata.errors = [str(e) + errors]
            # endregion

        finally:
            metadata.ended_at = time.time()
            metadata.duration_ms = round((metadata.ended_at - metadata.started_at) * 1000, 2)
            return metadata, rows
        # endregion

    def _flatten_rows(self,
                      data: Dict[str, Any],
                      parent_key: Optional[str] = "",
                      seperator: Optional[str] = ".") -> Dict[str, Any]:
        """
        Recursively flattens a nested dictionary (and lists) into a flat dict.

        Examples:
            Input:
                {"a": {"b": {"c": 1}}, "d": [10, 20]}
            Output:
                {"a.b.c": 1, "d[0]": 10, "d[1]": 20}
        """

        items = []

        for key, value in data.items():
            flatten_key = f"{parent_key}{seperator}{key}" if parent_key else key

            if isinstance(value, dict):
                items.extend(self._flatten_rows(data=value,
                                                parent_key=key,
                                                seperator=seperator))
            elif isinstance(value, list):
                for idx, val in enumerate(value):
                    if isinstance(val, dict):
                        items.extend(self._flatten_rows(data=val,
                                                        parent_key=f"{flatten_key}[{idx}]",
                                                        seperator=seperator))
                    else:
                        items.append((f"{flatten_key}[{idx}]", val))

            else:
                items.append((flatten_key, value))

        return dict(items)

    def _to_dict_rows(self,
                      result: bigquery.table.RowIterator,
                      flatten: Optional[bool] = False) -> List[Dict[str, Any]]:
        """Converts BigQuery RowIterator to list of dictionaries"""
        rows = []
        for row in result:
            row_dict = dict(row.items())
            if flatten:
                row_dict = self._flatten_rows(data=row_dict)
            rows.append(row_dict)
        return rows
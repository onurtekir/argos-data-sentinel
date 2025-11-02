import time
from typing import Optional, Tuple, List, Dict, Any

from google.cloud import bigquery

from ads.helpers.helper_library import HelperLibrary


class Executor:
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
                sql_query: str,
                flatten_results: Optional[bool] = False,
                dry_run_first: Optional[bool] = True,
                dry_run_only: Optional[bool] = False) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
        """
        Executes the given SQL statement in BigQuery

        Returns:
            - rows: List of result rows (as dicts)
            - metadata: Dict wit execution info (job_id, duration, bytes_processed, etc.)
        """

        # region Initialize connection and prepare base metadata
        client = self._connect()
        metadata: Dict[str, Any] = {
            "job_id": None,
            "duration_ms": None,
            "bytes_processed": None,
            "cache_hit": None,
            "dry_run": dry_run_only,
            "status": "UNKNOWN",
            "errors": [],
        }
        # endregion

        # region Prepare and execute dry_run
        if dry_run_only or dry_run_first:
            try:
                dry_job_config = bigquery.QueryJobConfig(dry_run=True, use_query_cache=False)
                dry_job = client.query(query=sql_query, job_config=dry_job_config)
                metadata.update({
                    "job_id": dry_job.job_id,
                    "bytes_processed": dry_job.total_bytes_processed,
                    "cache_hit": dry_job.cache_hit,
                    "status": "DRY_RUN_SUCCESS"
                })
            except Exception as e:
                metadata.update({
                    "status": "DRY_RUN_FAILED",
                    "errors": [str(e)]
                })
                return [], metadata

            if dry_run_only:
                return [], metadata
        # endregion

        # region Execute Query
        job_config = bigquery.QueryJobConfig
        start_time = time.time()
        try:

            # region Execute actual query and return results
            job = client.query(query=sql_query, job_config=job_config)
            result = job.result()
            end_time = time.time()
            duration_ms = round((end_time - start_time) * 1000, 2)

            metadata.update({
                "job_id": job.job_id,
                "start_time": start_time,
                "end_time": end_time,
                "duration_ms": duration_ms,
                "bytes_processed": getattr(job, "total_bytes_processed", None),
                "cache_hit": getattr(job, "cache_hit", None),
                "status": "SUCCESS"
            })

            rows = self._to_dict_rows(result=result, flatten=flatten_results)
            return rows, metadata
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
            metadata.update({
                "job_id": getattr(job, "job_id", None),
                "start_time": start_time,
                "end_time": time.time(),
                "status": "FAILED",
                "errors": [str(e)] + errors
            })
            return [], metadata
            # endregion

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
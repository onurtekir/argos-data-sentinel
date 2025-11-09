import logging

from ads.core.base import AdsBase

logger = logging.getLogger(__name__)


from typing import Any, Dict, List, Optional
from ads.core.models import Suite, Result, CheckStatus, Check, Threshold


class ResultParser(AdsBase):
    """
    Parses raw BigQuery query results into structured Result objects.

    Steps:
        1. Iterate through each row returned by the Executor.
        2. Match the check name with its definition in the Suite.
        3. Determine the check status (PASS / FAIL / ERROR) based on thresholds.
        4. Create and return a list of Result objects with computed fields.

    Example:
        parser = ResultParser()
        results = parser.parse(rows, suite)
    """

    def parse(self, suite: Suite, rows: List[Dict[str, Any]]) -> List[Result]:
        """Main entry point: converts raw rows into Result objects."""
        parsed_results: List[Result] = []

        for row in rows:
            check_name = row["check_name"]
            check = self._get_check_by_name(suite=suite, check_name=check_name)

            if not check:
                self.logger.warning(f"ResultParser: No check found for '{check_name}' in suite '{suite.name}'")
                continue

            value = self._extract_value(row)
            threshold: Threshold = check.threshold or Threshold()

            if value is None:
                status = CheckStatus.ERROR
                message = "Check value is invalid!"
            else:
                is_passed = threshold.is_within(value)
                status = CheckStatus.PASS if is_passed else CheckStatus.FAIL
                message = self._build_message(check_name=check_name, value=value, threshold=threshold, status=status)

            result = Result(
                check_name=check_name,
                status=status,
                message=message,
                value=value,
                threshold_lower=threshold.lower,
                threshold_upper=threshold.upper,
                severity=check.severity,
            )

            parsed_results.append(result)

        return parsed_results

    def _build_message(self, check_name: str, value: float, threshold: Threshold, status: CheckStatus) -> str:
        return (f"{check_name}: value {value} within {threshold.describe()}"
                if status == CheckStatus.PASS
                else f"{check_name}: value {value} outside {threshold.describe()}")

    def _extract_value(self, row: Dict[str, Any]) -> Optional[float]:
        """Extracts the primary numeric value (violations, ratio, etc.)."""
        for key in ["check_value", "value", "metric_value", "ratio", "count", "row_count"]:
            if key in row:
                return float(row[key])
        return None

    def _get_check_by_name(self, suite: Suite, check_name: str) -> Optional[Check]:
        """Helper to fetch the matching Check definition from a Suite"""
        for check in suite.checks:
            if check.name == check_name:
                return check
        return None

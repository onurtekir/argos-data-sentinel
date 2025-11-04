from datetime import datetime
from enum import Enum
from typing import Optional, Literal, List, Dict, Any
from pydantic import BaseModel, Field

from ads.core.enums import DataSourceType, Severity, CheckStatus, SuiteRunStatus
from ads.core.rules.rule_template_base import RuleTemplateBase

# region DataSource
class DataSource(BaseModel):
    """
    Represents a single source of data used for validation within the suite.

    A DataSource can be either:
        - a reference to a physical table (type="TABLE"), or
        - a custom SQL query (type="QUERY")

    All checks defined under the same Suite share the same DataSource.
    When type="QUERY", this query becomes the base CTE (Common Table Expression)
    that other checks will reference as 'base' in their SQL definitions

    Examples:
        Table source:
            type = "TABLE"
            table = "argos-data-sentinel.revenue.weekly_revenue"

        Query source:
            type = "QUERY"
            query = "SELECT year, week_number, customer_id, revenue FROM argos-data-sentinel.revenue.weekly_revenue"
    """
    type: DataSourceType = Field(DataSourceType.TABLE, description="Source type: TABLE or QUERY")
    table: Optional[str] = Field(None, description="Fully qualified table name if type=DataSourceType.TABLE")
    query: Optional[str] = Field(None, description="SQL query text if type=DataSourceType.QUERY")
    description: Optional[str] = Field(None, description="Optional description of context of the data source")
# endregion

# region RuleTemplate
class RuleTemplate(BaseModel):
    """
    Represents a reusable SQL logic template for data quality checks.

    Each RuleTemplate defines a SQL fragment (usually parameterized)
    that can be instantiated by multiple Check objects using different parameters.

    Example:
        RuleTemplate(
            name="not_null",
            sql_template=\"\"\"
                SELECT '{check_name}' AS check_name,
                       COUNTIF({column} IS NULL) AS violations
                FROM base
            \"\"\"
        )
    """
    name: str = Field(..., description="Unique name of the RuleTemplate")
    sql_template: str = Field(..., description="SQL template of the RuleTemplate")
    description: Optional[str] = Field(None, description="Optional human-readable description of the RuleTemplate")
# endregion

# region Threshold
class Threshold(BaseModel):
    """
    Represents numeric boundaries for evaluating check results.

    Supports:
        - Single limit (threshold = 5)
        - Range limit (lower = 3, upper = 10)

    Rules:
        - If only `value` is set → lower = upper = value
        - If both lower and upper are set → comparison is range-based
    """
    lower: Optional[float] = Field(None, description="Lower limit of the threshold")
    upper: Optional[float] = Field(None, description="Upper limit of the threshold")

    def __init__(self,
                 value: Optional[float] = None,
                 lower: Optional[float] = None,
                 upper: Optional[float] = None):
        super().__init__(lower=lower, upper=upper)
        if value is not None:
            self.lower = value
            self.upper = value

    def is_within(self, val: float) -> bool:
        """Returns True if value is within threshold bounds."""
        if self.lower is None and self.upper is None:  # Threshold not defined, always True
            return True
        if self.lower is not None and val < self.lower:
            return False
        if self.upper is not None and val > self.upper:
            return False
        return True

    def describe(self) -> str:
        """Readable text for debugging or reporting."""
        if self.lower == self.upper:
            return f"threshold = {self.lower}"
        return f"range [{self.lower or '-∞'}, {self.upper or '+∞'}]"
# endregion

# region Check
class Check(BaseModel):
    """
    Represents a single validation rule or test applied on the Suite's DataSource.

    Each Check defines its logic as a SQL snippet or CTE body that references
    the base DataSource as `base`. When the Suite is executed, all Checks are
    compiled together into a single SQL statement (one CTE per Check ).

    The results of each Check must include at least:
        - a check name (identifier)
        - a measure of the violations or pass/fail condition

    Examples:
          Check(name="no_null_customer_id",
                sql="SELECT 'no_null_customer_id' AS check_name, COUNTIF(customer_id IS NULL) AS violations FROM base",
                severity=Severity.ERROR)
    """
    name: str = Field(..., description="Unique name of the check")
    description: Optional[str] = Field(None, description="Optional human-readable description")
    rule_template: Optional[RuleTemplateBase] = Field(None, description="Name of the RuleTemplate this check references")
    column_name: Optional[str] = Field(None, description="Name of the column the check applies to")
    params: Optional[Dict[str, Any]] = Field(None, description="Parameter substitutions for the rule template")
    severity: Severity = Field(Severity.ERROR, description="Severity level of this check")
    threshold: Optional[Threshold] = Field(None, description="Threshold boundries for this check")
# endregion

# region Suite
class Suite(BaseModel):
    """
    Represents a logical group of data quality checks that run on the same DataSource

    A Suite defines:
        - which DataSource (table or query) it operates on
        - the collection of Checks that should be executed
        - optional metadata like domains, owner, or schedule tags.

    Each Check in the Suite compiles into a CTE (Common Tables Expression)
    that references the base DataSource query. The engine then builds
    a unified SQL statement combining all check CTEs and executes it in BigQuery

    Example:
        Suite: "revenue_quality_suite"
        DataSource: revenue_query
        Checks: [null_check, positive_revenue_check, volume_check]
    """
    name: str = Field(..., description="Unique name of the suite")
    domain: Optional[str] = Field(None, description="Optional business domain or area")
    owner: Optional[str] = Field(None, description="Optional owner of team responsible for this suite")
    data_source: DataSource = Field(..., description="The shared data source for all checks şn this suite")
    params: Optional[Dict[str, Any]] = Field(None, description="Parameter substitutions for the suite")
    checks: List[Check] = Field(default_factory=list, description="List of checks belonging to this suite")
    tags: Optional[Dict[Any, Any]] = Field(None, description="Optional key-value tags for metadata or filtering")
# endregion

# region Result
class Result(BaseModel):
    """
    Represents the execution outcome of a single Check after the suite is run.

    Each Result is derived from one row in the unified query output that the
    BigQuery engine returns after executing all checks within a Suite.

    A Result typically includes:
        - the check name
        - pass/fail status
        - numeric metrics (e.g., count of violations, ratio)
        - execution timestamps

    Results are later passed to exporters (JSON, Prometheus, SQLite, etc.)
    for persistence or monitoring.
    """
    check_name: str = Field(..., description="The name of the check that produced this result")
    status: CheckStatus = Field(CheckStatus.ERROR, description="CheckStatus of this result")
    severity: Severity = Field(Severity.WARN, description="Severity level of this result")
    message: Optional[str] = Field(None, description="Optional descriptive message or context")
    value: Optional[float] = Field(None, description="Numeric value evaluated for threshold comparison")
    threshold_lower: Optional[float] = Field(None, description="Lower boundary of threshold")
    threshold_upper: Optional[float] = Field(None, description="Upper boundary of threshold")
# endregion

# region ResultsMetadata
class ResultsMetadata(BaseModel):
    """
    Represents metadata for a full Suite execution.

    Captures information about:
        - timing
        - BigQuery job statistics
        - dry-run validation
        - execution status and errors
    """
    job_id: Optional[str] = Field(None, description="BigQuery job ID")
    started_at: Optional[float] = Field(None, description="Query start timestamp (EPOCH seconds)")
    ended_at: Optional[float] = Field(None, description="Query end timestamp (EPOCH seconds)")
    duration_ms: Optional[float] = Field(None, description="Total duration in milliseconds")
    bytes_processed: Optional[int] = Field(None, description="Total bytes processed by BigQuery job")
    cache_hit: Optional[bool] = Field(None, description="BigQuery result cache was used, or not")
    validate_first: Optional[bool] = Field(None, description="Validate script before execution, or not")
    validate_only: Optional[bool] = Field(None, description="ONLY validate script, or not")
    status: Optional[SuiteRunStatus] = Field(
        SuiteRunStatus.UNKNOWN,
        description=f"Suite execution status ({', '.join([status.name for status in SuiteRunStatus])})"
    )
    errors: Optional[List[str]] = Field(default_factory=list, description="List of error messages, if any")
    extra: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional custom metadata fields")

# endregion
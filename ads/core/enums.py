from enum import Enum


# region CheckStatus
class CheckStatus(Enum):
    """
    Enumeration representing the status of a check.

    CheckStatus indicates that the check passed, failed or with error.

    Statuses:
        - PASS:    Check passed
        - FAIL:    Check failed
        - ERROR:   Check exited with error

    Example:
        >>> CheckStatus.PASS
        <CheckStatus.PASS: 'PASS'>
    """
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"

    @property
    def is_fail(self) -> bool:
        return self in (CheckStatus.FAIL, CheckStatus.ERROR)
# endregion

# region SuiteRunStatus
class SuiteRunStatus(Enum):
    UNKNOWN = "UNKNOWN"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    VALIDATION_SUCCESS = "VALIDATION_SUCCESS"
    VALIDATION_FAILED = "VALIDATION_FAILED"
# endregion

# region Severity
class Severity(Enum):
    """
    Enumeration representing the severity level of a data quality check.

    Severity indicates how critical a failed check is and determines
    what type of action or alert should be triggered when it fails.

    Levels:
        - INFO:    Informational only; used for reporting or logging.
        - WARN:    Minor issue; should alert but does not block execution.
        - ERROR:   Significant issue; may block downstream jobs or raise alerts.
        - CRITICAL: Severe issue requiring immediate attention or manual intervention.

    Example:
        >>> Severity.ERROR
        <Severity.ERROR: 'ERROR'>
    """
    INFO = "INFO"
    WARN = "WARN"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
# endregion

# region DataSourceType
class DataSourceType(Enum):
    """
    Enumeration representing the type of data source.

    DataSourceType indicates that the type of data source ("table", "query").

    Statuses:
        - TABLE:   Table (<project>.<dataset>.<table>)
        - QUERY:   SQL query

    Example:
        >>> DataSourceType.QUERY
        <DataSourceType.QUERY: 'QUERY'>
    """
    TABLE = "TABLE"
    QUERY = "QUERY"
# endregion

# region ResultExportType
class ResultExportType(Enum):
    JSON = "JSON"
    CSV = "CSV"
    SQLITE = "SQLITE"
    PROMETHEUS = "PROMETHEUS"
# endregion

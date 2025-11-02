import sys
from pathlib import Path
from pprint import pprint

from ads.core.rules.core_ruleset_registry import core_ruleset

# Add project's root path
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))


from ads.core.engine.result_parser import ResultParser
from ads.core.engine.sql_builder import SQLBuilder
from ads.core.models import DataSource, DataSourceType, Check, Severity, Threshold, Suite, RuleTemplate
from ads.helpers.helper_library import HelperLibrary


def test_ads_end_to_end_simulation():

    # region Setup Helpers and DataSource
    helpers = HelperLibrary()

    data_source = DataSource(
        type=DataSourceType.QUERY,
        query="SELECT * FROM mock_revenue.mock_table"
    )
    # endregion

    #region Define Checks
    check_row_count = Check(
        name="row_count_check",
        description="Row count should be at least 100",
        rule_template=core_ruleset.row_count,
        params={},
        severity=Severity.ERROR,
        threshold=Threshold(lower=100)
    )

    check_ratio = Check(
        name="revenue_ratio_check",
        description="Revenue ratio must be between 0.9 and 1.1",
        rule_template=core_ruleset.accepted_values(accepted_values=["'Onur'", "'Tekir'", "'Nasılsın'"]),
        params={},
        severity=Severity.ERROR,
        threshold=Threshold(lower=0.9, upper=1.1),
        column_name="revenue"
    )
    # endregion

    # region Create Suite
    suite = Suite(
        name="revenue_suite",
        data_source=data_source,
        checks=[check_row_count, check_ratio],
        params={"ymd": "2025-11-02"}
    )
    # endregion

    # region Build SQL
    builder = SQLBuilder(suite=suite, helpers=helpers)
    sql = builder.build()
    print("Generated SQL: ")
    print(sql)
    # endregion

    # region Mock executor output
    rows = [
        {"check_name": "row_count_check", "value": 150},
        {"check_name": "revenue_ratio_check", "value": 1.25}
    ]
    # endregion

    # region Parse Results
    parser = ResultParser(suite=suite)
    results = parser.parse(rows=rows)
    print("Final Results:")
    for r in results:
        print("Result Object")
        pprint(r)
        print(f"[{r.status.value}] {r.check_name} → {r.message}")
    # endregion
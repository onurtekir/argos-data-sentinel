from typing import List


from ads.core.models import Suite, Check, DataSourceType
from ads.helpers.helper_library import HelperLibrary


class SQLBuilder:
    """
    Responsible for generating a unified BigQuery SQL statement
    that combines all checks defined within a Suite.

    This class transforms a Suite object into a single executable SQL query.
    It builds:
      - a base CTE from the suite's DataSource,
      - a CTE per Check (referencing the base query as 'base'),
      - and a final UNION ALL that merges all check results.

    Example output:
        WITH base AS (...),
             check_nulls AS (...),
             check_positive_revenue AS (...)
        SELECT * FROM check_nulls
        UNION ALL
        SELECT * FROM check_positive_revenue
    """

    def __init__(self, suite: Suite, helpers: HelperLibrary):
        self._suite = suite
        self._helpers = helpers

    @property
    def suite(self) -> Suite:
        return self._suite

    @property
    def helpers(self) -> HelperLibrary:
        return self._helpers

    def build(self) -> str:
        """Main entrypoint: builds and returns the full SQL string."""

        # region Prepare SQL body
        base_sql_block = self._build_base_cte()
        check_cte_blocks = [self._build_check_cte(check) for check in self.suite.checks]
        raw_sql_body = self._combine_cte_blocks(base_cte=base_sql_block, check_ctes=check_cte_blocks)
        sql_body = self.helpers.string.render_jinja_template(value=raw_sql_body,
                                                             params=self.suite.params,
                                                             keep_undefined_as_is=False)
        # endregion

        # region Union all checks
        check_unions = "\nUNION ALL\n".join(
            f"SELECT * FROM cte_{check.name}" for check in self.suite.checks
        )
        # endregion

        return f"{sql_body}\n{check_unions}"


    def _build_base_cte(self) -> str:
        """Returns SQL for the base CTE depending on DataSource type (TABLE, QUERY)"""
        if self.suite.data_source.type == DataSourceType.TABLE:
            sql_body = (f"-- Base CTE (Data Source Type > TABLE)\n"
                        f"WITH cte_{self.suite.name}_base AS ( SELECT * FROM `{self.suite.data_source.table}` )")
        else:
            sql_body = (f"-- Base CTE (Data Source Type > QUERY)\n"
                        f"WITH cte_{self.suite.name}_base AS (\n {self.suite.data_source.query} \n)")

        # Apply Jinja templates
        sql_body = self.helpers.string.render_jinja_template(value=sql_body,
                                                             params=self.suite.params or {},
                                                             keep_undefined_as_is=False)
        return sql_body

    def _build_check_cte(self, check: Check) -> str:
        """Wraps a single Check's SQL snippet into a CTE with alias 'check_<name>'"""

        if not check.rule_template:
            raise ValueError(f"Check '{check.name}' has no associated rule template")
        sql_body = check.rule_template.render(
            helpers=self.helpers,
            extra_params={
                **check.params,
                "check_name": check.name,
                "suite_name": self.suite.name,
                "column_name": check.column_name
            }
        )
        check_description = f"[{check.description}]" if check.description else ""
        return (f"\n-- Check CTE - {check.name} {check_description}\n"
                f"cte_{check.name} AS ({sql_body})")

    def _combine_cte_blocks(self, base_cte: str, check_ctes: List[str]) -> str:
        """Joins base CTE + all check CTEs + final UNION ALL into one SQL string"""
        sql_body_items = [base_cte]
        sql_body_items.extend(check_ctes)
        return ", ".join(sql_body_items)
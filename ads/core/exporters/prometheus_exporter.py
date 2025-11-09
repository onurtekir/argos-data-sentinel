import re
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

import requests

from ads.core.exporters.exporter_base import ExporterBase
from ads.core.models import ResultsMetadata, Result


class PrometheusExporter(ExporterBase):
    """
    Exports suite results as Prometheus-compatible metrics.

    Supports:
      - Writing metrics to a `.prom` file (text-based)
      - Pushing metrics to a Prometheus Pushgateway

    Metric format:
        ads_check_value{suite="suite_name", check="check_name", severity="CRITICAL"} 12.3
    """

    METRIC_PREFIX = "ads"


    def export(self, metadata: ResultsMetadata, results: List[Result], destination: Optional[str] = None,
               config: Optional[Dict[Any, Any]] = None) -> Optional[str]:
        """
        Exports results to a Prometheus text file or Pushgateway.

        Args:
            metadata: Suite-level metadata
            results: List of Result objects
            destination: Path to `.prom` file (optional)
            config: dict with optional keys:
                - "pushgateway_url": str (e.g., "http://localhost:9091")
                - "job_name": str
                - "labels": dict of extra labels
        """

        lines = []
        suite_name = getattr(metadata, "suite_name", "unknown_suite")
        timestamp = int(time.time())

        for r in results:

            # region Prepare and append metric line
            metric_name = self._sanitize_metric_name(f"{self.METRIC_PREFIX}_check_value")

            labels = {
                "suite": suite_name,
                "check": r.check_name,
                "status": self.helpers.enum.get_value(r.status),
                "severity": self.helpers.enum.get_value(r.severity)
            }

            # region Merge with user specific labels
            user_specific_labels = (config or {}).get("labels", {})
            labels.update(user_specific_labels)
            # endregion

            label_str = ",".join(f'{k}={v}' for k, v in labels.items())
            value = r.value or 0

            lines.append(f"{metric_name}{{{label_str}}} {value} {timestamp}")
            # endregion

        metrics_text = "\n".join(lines)

        # region PushGateway
        if (config or {}).get("pushgateway_url"):

            push_url = config.get("pushgateway_url").rstrip("/")
            job_name = config.get("job_name", suite_name)
            full_url = f"{push_url}/metrics/job/{job_name}"
            try:
                response = requests.post(full_url, data=metrics_text, timeout=5)
                if response.status_code != 202:
                    self.logger.warning(f"Pushgateway returned {response.status_code}: {response.text}")
                else:
                    self.logger.info(f"Pushed {len(results)} metrics to Pushgateway → {full_url}")
                return full_url
            except Exception as e:
                self.logger.error(f"Failed to push metrics to PushGateway: {e}")
                return None
        # endregion

        output_path = Path(destination or f"{suite_name}.prom")
        self.helpers.filesystem.create_parent_directories(path=output_path.parent)
        output_path.write_text(metrics_text)
        self.logger.info(f"Prometheus metrics written → {output_path.resolve()}")

        return str(output_path.resolve())

    @staticmethod
    def _sanitize_metric_name(name: str) -> str:
        """Ensures Prometheus-compatible metric name."""
        return re.sub(r"[^a-zA-Z0-9_:]", "_", name)

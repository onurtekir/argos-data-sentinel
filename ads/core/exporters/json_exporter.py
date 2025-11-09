import json
from pathlib import Path
from typing import List, Optional, Any

from ads.core.exporters.exporter_base import ExporterBase
from ads.core.models import ResultsMetadata, Result


class JsonExporter(ExporterBase):
    """
    Writes execution results and metadata to a JSON file.

    If no destination is provided, defaults to `ads_results.json`
    in the current working directory.
    """

    def export(self,
               metadata: ResultsMetadata,
               results: List[Result],
               destination: Optional[str] = None,
               config: Optional[Any, Any] = None) -> Optional[str]:
        output_path = Path(destination or "ads_results.json")

        payload = dict(
            metadata=metadata.model_dump(mode="json"),
            results=[r.model_dump(mode="json") for r in results]
        )

        self.helpers.filesystem.create_parent_directories(path=output_path.parent)

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=5, ensure_ascii=False)

        self.logger.info(f"Results exported to '{output_path.resolve()}'")

        return str(output_path.resolve())


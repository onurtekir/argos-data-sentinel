import base64
import datetime
import re
from pathlib import Path
from tokenize import endpats
from typing import List, Optional, Dict, Any

import requests

from ads.core.exporters.exporter_base import ExporterBase
from ads.core.models import ResultsMetadata, Result


class HtmlExporter(ExporterBase):
    """
    Exports suite run results into a styled HTML report.

    Uses a Jinja2 template (html_template.html) under:
        ads/core/exporters/templates/html_exporter/

    The report includes:
      - Suite name, description, custom message
      - Metadata summary
      - Results table
      - Optional custom logo (logo.png in template directory)
    """

    TEMPLATE_DIR = Path(__file__).parent / "templates" / "html_exporter"
    TEMPLATE_FILE = "html_template.html"

    def _get_logo_base64(self, logo_path: str) -> str:
        """
        Convert a logo from a URL or file path into a Base64-encoded string.

        Args:
            logo_path: URL or local file path of the image

        Returns:
            Base64-encoded string of the image
        """
        is_url = re.match(r"^http?://", logo_path, re.IGNORECASE)

        try:
            if is_url:
                response = requests.get(logo_path)
                response.raise_for_status()
                image_data = response.content
            else:
                if not self.helpers.filesystem.file_exists(path=Path(logo_path)):
                    raise FileNotFoundError(f"File not found: {logo_path}")
                with open(logo_path, "rb") as f:
                    image_data = f.read()
            return base64.b64encode(image_data).decode("utf-8")
        except Exception as e:
            raise RuntimeError(f"Failed to process image: {e}")

    def export(self,
               metadata: ResultsMetadata,
               results: List[Result],
               destination: Optional[str] = None,
               config: Optional[Dict[Any, Any]] = None) -> Optional[str]:
        """
        Renders HTML report and writes to a file

        Args:
            metadata: suite-level execution metadata
            results: List of Result objects
            destination: Optional output HTML path
            config:
                - template_base_dir: HTML template directory
                - custom_message: str
                - custom_logo_path or URL: str (overwrite default logo)
        Returns:
            Rendered HTML content
        """

        # region Load and render template HTML and prepare logo embedding
        template_directory = (config or {}).get("template_base_dir", self.TEMPLATE_DIR)
        html_filename = template_directory / "html_template.html"
        logo_filename = template_directory / "logo.png"
        custom_logo_path = (config or {}).get("custom_logo_path", None)

        if not self.helpers.filesystem.file_exists(path=html_filename):
            self.logger.error(f"HTML template file '{html_filename.resolve()}' not found")
            raise

        logo_base64 = None
        if custom_logo_path:
            logo_base64 = self._get_logo_base64(logo_path=str(custom_logo_path))
        elif self.helpers.filesystem.file_exists(path=logo_filename):
            logo_base64 = self._get_logo_base64(logo_path=str(logo_filename.resolve()))

        html_content = None
        with open(html_filename, "r", encoding="utf-8") as f:
            html_content = self.helpers.string.render_jinja_template(
                value=f.read(),
                params=dict(
                    suite_name=metadata.suite_name,
                    suite_description=metadata.suite_description,
                    metadata=metadata.model_dump(mode="json"),
                    results=results,
                    logo_base64=logo_base64,
                    custom_message=(config or {}).get("custom_message", None),
                    generation_time=datetime.datetime.now(datetime.UTC).strftime("%d.%m.%Y %H:%M:%S UTC")
                ),
                keep_undefined_as_is=False
            )
        # endregion

        # region Export HTML if destination path defined
        if destination:
            output_path = Path(destination)
            self.helpers.filesystem.create_parent_directories(path=output_path.parent)
            output_path.write_text(data=html_content, encoding="utf-8")
            self.logger.info(f"HTML report generated: {output_path.resolve()}")
        # endregion

        return html_content

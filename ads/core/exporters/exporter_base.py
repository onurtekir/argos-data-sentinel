from abc import abstractmethod, ABC
from typing import List, Optional, Dict, Any

from ads.core.base import AdsBase
from ads.core.models import ResultsMetadata, Result


class ExporterBase(AdsBase, ABC):
    """
    Abstract base class for all exporters in Argos Data Sentinel.

    Exporters handle persistence or transmission of execution results,
    such as writing to files, databases, or metrics systems.
    """

    @abstractmethod
    def export(self,
               metadata: ResultsMetadata,
               results: List[Result],
               destination: Optional[str] = None,
               config: Optional[Dict[Any, Any]] = None) -> Optional[str]:
        """Export results and metadata to a target destination."""
        pass
    
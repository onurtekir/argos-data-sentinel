from typing import List

from ads.core.base import AdsBase
from ads.core.models import ResultsMetadata, Result


class ExporterBase(AdsBase):
    def export(self, metadata: ResultsMetadata, results: List[Result]) -> None:
        raise NotImplementedError
    
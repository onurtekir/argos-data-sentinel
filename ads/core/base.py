import logging
from abc import ABC

from ads.helpers.helper_library import HelperLibrary


class AdsBase(ABC):
    """
    Base class for all core Argos Data Sentinel components.

    Provides:
        - preconfigured module-aware logger via `self.logger`
        - potential future hooks (timing, telemetry, etc.)
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = logging.getLogger(self.__class__.__module__)
        self._helpers = HelperLibrary()

    @property
    def logger(self) -> logging.Logger:
        return self._logger

    @property
    def helpers(self) -> HelperLibrary:
        return self._helpers

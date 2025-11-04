import logging
from abc import ABC


class AdsBase(ABC):
    """
    Base class for all core Argos Data Sentinel components.

    Provides:
        - preconfigured module-aware logger via `self.logger`
        - potential future hooks (timing, telemetry, etc.)
    """

    def __repr__(self, *args, **kwargs):
        self._logger = logging.getLogger(self.__class__.__module__)
        super().__init__(*args, **kwargs)

    @property
    def logger(self) -> logging.Logger:
        return self._logger

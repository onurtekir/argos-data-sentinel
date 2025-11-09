import logging
import os
from typing import Optional


def setup_logging(level: Optional[str] = None):
    env_log_level = os.getenv("ADS_LOG_LEVEL", "").upper()
    if env_log_level:
        log_level = getattr(logging, env_log_level, logging.INFO)
    else:
        if level:
            log_level = getattr(logging, level, logging.INFO)
        else:
            log_level = logging.INFO

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # region Silence third-party logging libraries
    logging.getLogger("google").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.ERROR)
    # endregion
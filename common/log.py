from __future__ import annotations

import logging
import sys

from pythonjsonlogger import jsonlogger

from common.constants import APPLICATION_NAME


def setup_logging(log_level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(APPLICATION_NAME)
    logger.setLevel(log_level)
    handler = logging.StreamHandler(sys.stdout)
    formatter = jsonlogger.JsonFormatter(
        "%(created)s %(levelname)s %(name)s %(message)s %(pathname)s %(lineno)s %(exc_text)s",
        json_default=str,
    )
    handler.setFormatter(formatter)
    handler.setLevel(log_level)
    logger.addHandler(handler)
    return logger

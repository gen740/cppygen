import os
import sys
from logging import CRITICAL, ERROR, WARNING, Logger

import colorlog


def create_default_formatter() -> colorlog.ColoredFormatter:
    """Create a default formatter of log messages.

    This function is not supposed to be directly accessed by library users.
    """
    return colorlog.ColoredFormatter(
        "%(log_color)s%(message)s",
        no_color=False if _color_supported() else True,
    )


def _color_supported() -> bool:
    """Detection of color support."""
    # NO_COLOR environment variable:
    if os.environ.get("NO_COLOR", None):
        return False

    if not hasattr(sys.stderr, "isatty") or not sys.stderr.isatty():
        return False
    else:
        return True


def get_logger(name: str) -> Logger:
    handler = colorlog.StreamHandler()
    handler.setFormatter(create_default_formatter())
    logger = colorlog.getLogger(name)
    logger.addHandler(handler)
    return logger


__all__ = ["ERROR", "CRITICAL", "WARNING"]

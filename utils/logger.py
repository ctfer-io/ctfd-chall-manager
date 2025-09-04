"""
This module contains the logger configuration for the plugin
"""

import logging
import sys
import os


def configure_logger(name: str) -> logging.Logger:
    """
    Configures a logger with a specified name and log level.

    :param name: The name of the logger, typically the module's __name__.
    :return: Configured logger instance.
    """
    logger = logging.getLogger(name)

    level = os.getenv("LOG_LEVEL")
    if level is None or level not in logging.getLevelNamesMapping().keys():
        level = "INFO"

    logger.setLevel(logging.getLevelNamesMapping()[level])

    # Check if the logger already has handlers to prevent adding multiple handlers
    if not logger.hasHandlers():
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)

        # Formatter
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
        console_handler.setFormatter(formatter)

        # Add handler to logger
        logger.addHandler(console_handler)

    logger.debug("logger %s initiate with level %s", name, level)

    return logger

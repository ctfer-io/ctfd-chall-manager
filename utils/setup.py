"""
This module configure the CTFd-chall-manager default settings.
"""

import os
from urllib.parse import urlparse

from CTFd.plugins.ctfd_chall_manager.utils.logger import configure_logger
from CTFd.utils import set_config

# Configure logger for this module
logger = configure_logger(__name__)


def setup_default_configs():
    """
    This function check if environment variable is used or not.
    Configure default value is not.
    """
    logger.debug("configure plugin")

    default_cm_api_url = "http://localhost:8080"
    default_cm_api_timeout = 600  # 10* 60 = 600s => 10m

    default_cm_mana_total = 0

    # Load varenv
    cm_api_url = os.getenv("PLUGIN_SETTINGS_CM_API_URL", default_cm_api_url)

    # Validate cm_api_url
    parsed_url = urlparse(cm_api_url)
    if parsed_url.scheme not in ["http"]:
        logger.warning(
            "invalid PLUGIN_SETTINGS_CM_API_URL, got %s,falling back to default.",
            cm_api_url,
        )
        cm_api_url = default_cm_api_url

    logger.debug("configuring chall-manager_api_url to %s", cm_api_url)

    # Load env
    cm_api_timeout = os.getenv(
        "PLUGIN_SETTINGS_CM_API_TIMEOUT",
        str(default_cm_api_timeout),  # default value must be str
    )
    try:
        cm_api_timeout = int(cm_api_timeout)  # try to trigger an execption
    except TypeError:
        logger.warning(
            "invalid PLUGIN_SETTINGS_CM_API_TIMEOUT, got %s. Falling back to default.",
            cm_api_timeout,
        )
        cm_api_timeout = default_cm_api_timeout  # default value

    # Validate cm_mana_total
    if not cm_api_timeout > 0:
        logger.warning(
            "invalid PLUGIN_SETTINGS_CM_API_TIMEOUT, got %s. Falling back to default.",
            cm_api_timeout,
        )
        cm_api_timeout = default_cm_api_timeout  # default value

    logger.debug("configuring chall-manager_api_timeout to %s", cm_api_timeout)

    # Load env
    cm_mana_total = os.getenv(
        "PLUGIN_SETTINGS_CM_MANA_TOTAL",
        str(default_cm_mana_total),  # default value must be str
    )
    try:
        cm_mana_total = int(cm_mana_total)  # try to trigger an execption
    except TypeError:
        logger.warning(
            "invalid PLUGIN_SETTINGS_CM_MANA_TOTAL, got %s. Falling back to default.",
            cm_mana_total,
        )
        cm_mana_total = default_cm_mana_total  # default value

    # Validate cm_mana_total
    if not cm_mana_total >= 0:
        logger.warning(
            "invalid PLUGIN_SETTINGS_CM_MANA_TOTAL, got %s. Falling back to default.",
            cm_mana_total,
        )
        cm_mana_total = default_cm_mana_total  # default value

    logger.debug("configuring chall-manager_mana_total to %s", cm_mana_total)

    # Set configuration on CTFd
    for key, val in {
        "setup": "true",
        "chall-manager_api_url": cm_api_url,
        "chall-manager_api_timeout": cm_api_timeout,
        "chall-manager_mana_total": cm_mana_total,
    }.items():
        set_config("chall-manager:" + key, val)

    logger.info("plugin configured successfully")

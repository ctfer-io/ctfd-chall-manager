from CTFd.utils import set_config # type: ignore
import os
from urllib.parse import urlparse
from .logger import configure_logger

# Configure logger for this module
logger = configure_logger(__name__)


def setup_default_configs():
    logger.debug("configure plugin")

    default_cm_api_url = "http://localhost:8080/api/v1"
    default_cm_mana_total = 0

    # Load varenv
    cm_api_url = os.getenv("PLUGIN_SETTINGS_CM_API_URL", default_cm_api_url)

    # Validate cm_api_url
    parsed_url = urlparse(cm_api_url)
    if not (parsed_url.scheme in ['http', 'https'] and parsed_url.path == '/api/v1'):
        logger.warning(f"Invalid PLUGIN_SETTINGS_CM_API_URL, got {cm_api_url}. Falling back to default.")
        cm_api_url = default_cm_api_url

    logger.debug(f"configuring chall-manager_api_url to {cm_api_url}")

    # Load env
    cm_mana_total = os.getenv("PLUGIN_SETTINGS_CM_MANA_TOTAL", default_cm_mana_total)
    try:        
        cm_mana_total = int(cm_mana_total) # try to trigger an execption
    except:
        logger.warning(f"Invalid PLUGIN_SETTINGS_CM_MANA_TOTAL, got {cm_mana_total}. Falling back to default.")
        cm_mana_total = default_cm_mana_total # default value

    # Validate cm_mana_total
    if not cm_mana_total >= 0:
        logger.warning(f"Invalid PLUGIN_SETTINGS_CM_MANA_TOTAL, got {cm_mana_total}. Falling back to default.")
        cm_mana_total = default_cm_mana_total # default value

    logger.debug(f"configuring chall-manager_mana_total to {cm_mana_total}")

    # Set configuration on CTFd
    for key, val in {
        'setup': 'true',
        'chall-manager_api_url': cm_api_url,
        'chall-manager_mana_total': cm_mana_total
    }.items():
        set_config('chall-manager:' + key, val)

    logger.info("plugin configured successfully")
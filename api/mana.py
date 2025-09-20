"""
This module describes the UserMana API endpoint of the plugin:
Route: /api/v1/plugins/ctfd-chall-manager/mana
"""

from CTFd.plugins.ctfd_chall_manager.utils.chall_manager_error import (
    ChallManagerException,
)
from CTFd.plugins.ctfd_chall_manager.utils.helpers import calculate_mana_used
from CTFd.plugins.ctfd_chall_manager.utils.logger import configure_logger
from CTFd.plugins.ctfd_chall_manager.utils.mana_lock import load_or_store
from CTFd.utils import get_config
from CTFd.utils import user as current_user
from CTFd.utils.config import is_teams_mode
from CTFd.utils.decorators import authed_only
from flask_restx import Resource

# Configure logger for this module
logger = configure_logger(__name__)


# region UserMana
class UserMana(Resource):
    """
    UserMana class handle R operation on /mana.
    """

    @staticmethod
    @authed_only
    def get():
        """
        Retrieve the actual mana used by the sourceId.
        If CTFd is in Team mode, the mana_used will be amound all players of a team.
        """
        mana_total = int(get_config("chall-manager:chall-manager_mana_total"))

        # If mana disabled, return 0 immediatly
        if mana_total == 0:
            return {
                "success": True,
                "data": {
                    "used": 0,
                    "total": 0,
                },
            }, 200

        user_id = int(current_user.get_current_user().id)
        source_id = user_id
        if is_teams_mode():
            source_id = int(current_user.get_current_user().team_id)
            # If user has no team
            if not source_id:
                logger.info(
                    "user %s has no team, abort",
                    user_id,
                )
                return {"success": False, "data": {"message": "unauthorized"}}, 403

        try:
            lock = load_or_store(str(source_id))
            logger.debug("get /mana acquire the player lock for %s", source_id)
            lock.player_lock()

            mana = calculate_mana_used(source_id)
            logger.debug("retrieved mana for source_id: %s, mana: %s", source_id, mana)
        except ChallManagerException as e:
            logger.error(
                "error while calculating the mana for source_id %s: %s", source_id, e
            )
            return {"success": False, "message": "internal server error"}, 500

        finally:
            logger.debug("get /mana release the player lock for %s", source_id)
            lock.player_unlock()

        return {
            "success": True,
            "data": {
                "used": mana,
                "total": mana_total,
            },
        }, 200

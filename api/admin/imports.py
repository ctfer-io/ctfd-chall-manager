"""
This module describes the AdminImport API endpoints of the plugin:
Route: /api/v1/plugins/ctfd-chall-manager/admin/import.
"""

from CTFd.api.v1.helpers.request import validate_args
from CTFd.plugins.ctfd_chall_manager.models import (
    DynamicIaCChallenge,
    prepare_chall_manager_payload,
    prepare_ctfdcm_database,
)
from CTFd.plugins.ctfd_chall_manager.utils.chall_manager_error import (
    ChallManagerException,
)
from CTFd.plugins.ctfd_chall_manager.utils.challenge_store import (
    create_challenge,
)
from CTFd.plugins.ctfd_chall_manager.utils.logger import configure_logger
from CTFd.utils.decorators import admins_only
from flask import request
from flask_restx import Resource, abort

# Configure logger for this module
logger = configure_logger(__name__)


# region AdminImport
# Resource to import challenge on chall-manager
class AdminImport(Resource):
    """
    AdminImport is an admin API endpoint for creating challenges in chall-manager.
    It can be used after importing a CTFd database or for disaster recovery on chall-manager.
    """

    @staticmethod
    @admins_only
    @validate_args({"challengeId": (int)}, location="json")
    def post(json_args):
        """
        Trigger an import
        """
        challenge_id = json_args.pop("challengeId", None)
        logger.info("trying to import challenge %d", challenge_id)

        if not challenge_id:
            abort(400, "missing argument challenge_id", success=False)

        # retrieve challenge information on CTFd
        challenge = DynamicIaCChallenge.query.filter_by(id=challenge_id).first()
        challenge_dict = {k: v for k, v in challenge.__dict__.items()}
        logger.debug("challenge %d infos : %s", challenge_id, challenge_dict)

        data = prepare_ctfdcm_database(challenge_dict)
        params = prepare_chall_manager_payload(data)
        try:
            # recreate challenge on chall-manager
            create_challenge(challenge_id, **params)
            logger.info("challenge %d import successfully", challenge_id)
        except ChallManagerException as e:
            logger.error("error while communicating with CM: %s", e)
            return {
                "success": False,
                "message": e.message,
            }, e.http_code

        return {"success": True}, 200

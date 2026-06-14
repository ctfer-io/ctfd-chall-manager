"""
This module describes the AdminInstance API endpoints of the plugin:
Route: /api/v1/plugins/ctfd-chall-manager/admin/instance.
"""

from CTFd.api.v1.helpers.request import validate_args
from CTFd.plugins.ctfd_chall_manager.utils.chall_manager_error import (
    ChallManagerException,
)
from CTFd.plugins.ctfd_chall_manager.utils.helpers import retrieve_all_ids
from CTFd.plugins.ctfd_chall_manager.utils.instance_manager import (
    create_instance,
    delete_instance,
    get_instance,
    update_instance,
)
from CTFd.plugins.ctfd_chall_manager.utils.lock import load_or_store
from CTFd.plugins.ctfd_chall_manager.utils.logger import configure_logger
from CTFd.utils import user as current_user
from CTFd.utils.decorators import admins_only
from flask_restx import Resource, abort

# Configure logger for this module
logger = configure_logger(__name__)


# region AdminInstance
# Resource to monitor all instances
class AdminInstance(Resource):
    """
    AdminInstance class handles CRUD operation for /admin/instance API endpoint.
    This class bypasses the mana verification and admin can create or destroy instances for Users.
    Required to be authenticated with an admin capable account.
    """

    @staticmethod
    @admins_only
    @validate_args(
        {
            "sourceId": (int, None),
            "challengeId": (int, None),
        },
        location="query"
    )
    def get(query_args):
        """
        Retrieve instance infos for the sourceId and challengeId provided.
        The returned value contains all informations given by Chall-Manager API (flag included).
        """

        admin_id = current_user.get_current_user()
        challenge_id = query_args.pop("challengeId", None)
        source_id = query_args.pop("sourceId", None)

        if None in (challenge_id, source_id):
            return {
                "success": False,
                "message": "missing challengeId or sourceId",
            }, 400

        logger.info(
            "admin %s get instance info for challenge_id: %s, source_id: %s",
            admin_id,
            challenge_id,
            source_id,
        )

        try:
            logger.debug(
                "getting instance for challenge_id: %s, source_id: %s",
                challenge_id,
                source_id,
            )

            result = get_instance(challenge_id, source_id)
            logger.info("instance retrieved successfully: %s", result)
        except ChallManagerException as e:
            logger.error("error while communicating with CM: %s", e)
            return {
                "success": False,
                "message": e.message,
            }, e.http_code

        return {"success": True, "data": result}, 200

    @staticmethod
    @admins_only
    @validate_args(
        {
            "challengeId": (int, None),
            "sourceId": (int, None),
        },
        location="json",
    )
    def post(json_args):
        """
        Create instance for the sourceId and challengeId provided.
        This function will create a coupon, but bypass mana checks and
        deploy instance in all cases.
        The returned value contains all informations given by Chall-Manager API (flag included).
        """
        admin_id = current_user.get_current_user()
        challenge_id = json_args.pop("challengeId", None)
        source_id = json_args.pop("sourceId", None)

        if None in (challenge_id, source_id):
            abort(404, "missing challengeId or sourceId")

        logger.info(
            "admin %s request instance creation for challenge_id: %s, source_id: %s",
            admin_id,
            challenge_id,
            source_id,
        )

        try:
            lock = load_or_store(f"{source_id}")
            lock.lock()

            result = create_instance(challenge_id, source_id)
            logger.info(
                "instance for challenge_id: %s, source_id: %s created successfully",
                challenge_id,
                source_id,
            )

        except ChallManagerException as e:
            if e.http_code == 409:
                logger.warning(
                    "instance for challenge_id: %s, source_id: %s already exists, ignoring",
                    challenge_id,
                    source_id,
                )
                return {
                    "success": False,
                    "data": {
                        "message": "instance already exist",
                    },
                }, 200

            logger.error(
                "error while creating instance for challenge_id: %s, source_id: %s",
                challenge_id,
                source_id,
            )
            return {
                "success": False,
                "message": e.message,
            }, e.http_code

        finally:
            logger.debug("unlock %s", lock)
            lock.unlock()

        return {"success": True, "data": result}, 200

    @staticmethod
    @admins_only
    @validate_args(
        {
            "challengeId": (int, None),
            "sourceId": (int, None),
        },
        location="json",
    )
    def patch(json_args):
        """
        Renew instance for the sourceId and challengeId provided.
        The returned value contains all informations given by Chall-Manager API (flag included).
        """

        admin_id = current_user.get_current_user()
        challenge_id = json_args.pop("challengeId", None)
        source_id = json_args.pop("sourceId", None)

        if None in (challenge_id, source_id):
            abort(404, "missing challengeId or sourceId")

        logger.info(
            "admin %s request instance update for challenge_id: %s, source_id: %s",
            admin_id,
            challenge_id,
            source_id,
        )

        try:
            logger.debug(
                "updating instance for challenge_id: %s, source_id: %s",
                challenge_id,
                source_id,
            )

            result = update_instance(challenge_id, source_id)
            logger.info(
                "instance for challenge_id: %s, source_id: %s updated successfully",
                challenge_id,
                source_id,
            )
        except ChallManagerException as e:
            logger.error("error while updating instance: %s", e)
            return {
                "success": False,
                "message": e.message,
            }, e.http_code

        return {"success": True, "data": result}, 200

    @staticmethod
    @admins_only
    @validate_args(
        {
            "challengeId": (int, None),
            "sourceId": (int, None),
        },
        location="json",
    )
    def delete(json_args):
        """
        Destroy instance for the sourceId and challengeId provided.
        This function will delete the associated coupon.
        """
        admin_id = current_user.get_current_user()
        challenge_id = json_args.pop("challengeId", None)
        source_id = json_args.pop("sourceId", None)

        if None in (challenge_id, source_id):
            abort(404, "missing challengeId or sourceId")

        logger.info(
            "admin %s request instance delete for challenge_id: %s, source_id: %s",
            admin_id,
            challenge_id,
            source_id,
        )

        try:
            lock = load_or_store(f"{source_id}")
            lock.lock()

            logger.debug(
                "deleting instance for challenge_id: %s, source_id: %s",
                challenge_id,
                source_id,
            )
            result = delete_instance(challenge_id, source_id)
            logger.info(
                "instance for challenge_id: %s, source_id: %s delete successfully",
                challenge_id,
                source_id,
            )

        except ChallManagerException as e:
            logger.error("error while deleting instance: %s", e)
            return {
                "success": False,
                "message": e.message,
            }, e.http_code

        finally:
            logger.debug("unlock %s", lock)
            lock.unlock()

        return {"success": True, "data": result}, 200

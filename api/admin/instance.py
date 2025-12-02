"""
This module describes the AdminInstance API endpoints of the plugin:
Route: /api/v1/plugins/ctfd-chall-manager/admin/instance.
"""

from CTFd.plugins.ctfd_chall_manager.utils.chall_manager_error import (
    ChallManagerException,
    build_error_payload,
)
from CTFd.plugins.ctfd_chall_manager.utils.helpers import retrieve_all_ids
from CTFd.plugins.ctfd_chall_manager.utils.instance_manager import (
    create_instance,
    delete_instance,
    get_instance,
    update_instance,
)
from CTFd.plugins.ctfd_chall_manager.utils.logger import configure_logger
from CTFd.plugins.ctfd_chall_manager.utils.mana_lock import load_or_store
from CTFd.utils.decorators import admins_only
from flask_restx import Resource

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
    def get():
        """
        Retrieve instance infos for the sourceId and challengeId provided.
        The returned value contains all informations given by Chall-Manager API (flag included).
        """
        admin_id = 0
        challenge_id = 0
        source_id = 0

        try:
            result = retrieve_all_ids(admin=True)
            admin_id = result["admin_id"]
            challenge_id = result["challenge_id"]
            source_id = result["source_id"]
        except ValueError:
            return {
                "success": False,
                "data": {
                    "message": "missing challengeId or sourceId",
                },
            }, 400

        # admin_id and challenge_id must be updated by retrieve_all_ids()
        # source_id can be 0 (shared)
        if admin_id == 0 or challenge_id == 0:
            return {
                "success": False,
                "data": {
                    "message": "internal server error: cannot load challenge_id or admin_id",
                },
            }, 500

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
            error_data, status = build_error_payload(e)
            return {
                "success": False,
                "data": error_data,
            }, status

        return {"success": True, "data": result}, 200

    @staticmethod
    @admins_only
    def post():
        """
        Create instance for the sourceId and challengeId provided.
        This function will create a coupon, but bypass mana checks and
        deploy instance in all cases.
        The returned value contains all informations given by Chall-Manager API (flag included).
        """
        admin_id = 0
        challenge_id = 0
        source_id = 0

        try:
            result = retrieve_all_ids(admin=True)
            admin_id = result["admin_id"]
            challenge_id = result["challenge_id"]
            source_id = result["source_id"]
        except ValueError:
            return {
                "success": False,
                "data": {
                    "message": "missing challengeId or sourceId",
                },
            }, 400

        # admin_id and challenge_id must be updated by retrieve_all_ids()
        # source_id can be 0 (shared)
        if admin_id == 0 or challenge_id == 0:
            return {
                "success": False,
                "data": {
                    "message": "internal server error: cannot load challenge_id or admin_id",
                },
            }, 500

        logger.info(
            "admin %s request instance creation for challenge_id: %s, source_id: %s",
            admin_id,
            challenge_id,
            source_id,
        )

        try:
            lock = load_or_store(f"{source_id}")
            lock.admin_lock()

            result = create_instance(challenge_id, source_id)
            logger.info(
                "instance for challenge_id: %s, source_id: %s created successfully",
                challenge_id,
                source_id,
            )

        except ChallManagerException as e:
            if "already exist" in e.message:
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
                }, e.http_status

            logger.error(
                "error while creating instance for challenge_id: %s, source_id: %s: %s",
                challenge_id,
                source_id,
                e,
            )
            error_data, status = build_error_payload(e)
            return {
                "success": False,
                "data": error_data,
            }, status

        finally:
            logger.debug("admin_unlock %s", lock)
            lock.admin_unlock()

        return {"success": True, "data": result}, 200

    @staticmethod
    @admins_only
    def patch():
        """
        Renew instance for the sourceId and challengeId provided.
        The returned value contains all informations given by Chall-Manager API (flag included).
        """

        # mandatory
        admin_id = 0
        challenge_id = 0
        source_id = 0

        try:
            result = retrieve_all_ids(admin=True)
            admin_id = result["admin_id"]
            challenge_id = result["challenge_id"]
            source_id = result["source_id"]
        except ValueError:
            return {
                "success": False,
                "data": {
                    "message": "missing challengeId or sourceId",
                },
            }, 400

        # admin_id and challenge_id must be updated by retrieve_all_ids()
        # source_id can be 0 (shared)
        if admin_id == 0 or challenge_id == 0:
            return {
                "success": False,
                "data": {
                    "message": "internal server error: cannot load challenge_id or admin_id",
                },
            }, 500

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
            error_data, status = build_error_payload(e)
            return {
                "success": False,
                "data": error_data,
            }, status

        return {"success": True, "data": result}, 200

    @staticmethod
    @admins_only
    def delete():
        """
        Destroy instance for the sourceId and challengeId provided.
        This function will delete the associated coupon.
        """
        # mandatory
        admin_id = 0
        challenge_id = 0
        source_id = 0

        try:
            result = retrieve_all_ids(admin=True)
            admin_id = result["admin_id"]
            challenge_id = result["challenge_id"]
            source_id = result["source_id"]
        except ValueError:
            return {
                "success": False,
                "data": {
                    "message": "missing challengeId or sourceId",
                },
            }, 400

        # admin_id and challenge_id must be updated by retrieve_all_ids()
        # source_id can be 0 (shared)
        if admin_id == 0 or challenge_id == 0:
            return {
                "success": False,
                "data": {
                    "message": "internal server error: cannot load challenge_id or admin_id",
                },
            }, 500

        logger.info(
            "admin %s request instance delete for challenge_id: %s, source_id: %s",
            admin_id,
            challenge_id,
            source_id,
        )

        try:
            lock = load_or_store(f"{source_id}")
            lock.admin_lock()

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
            error_data, status = build_error_payload(e)
            return {
                "success": False,
                "data": error_data,
            }, status

        finally:
            logger.debug("admin_unlock %s", lock)
            lock.admin_unlock()

        return {"success": True, "data": result}, 200

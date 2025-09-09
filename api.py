"""
This module describes the 3 API endpoints of the plugin:
    - AdminInstance: /api/v1/plugins/ctfd-chall-manager/admin/instance
    - UserInstance: /api/v1/plugins/ctfd-chall-manager/instance
    - UserMana: /api/v1/plugins/ctfd-chall-manager/mana
"""

import json

from CTFd.plugins.ctfd_chall_manager.decorators import challenge_visible
from CTFd.plugins.ctfd_chall_manager.models import DynamicIaCChallenge
from CTFd.plugins.ctfd_chall_manager.utils.chall_manager_error import (
    ChallManagerException,
)
from CTFd.plugins.ctfd_chall_manager.utils.instance_manager import (
    create_instance,
    delete_instance,
    get_instance,
    update_instance,
)
from CTFd.plugins.ctfd_chall_manager.utils.logger import configure_logger
from CTFd.plugins.ctfd_chall_manager.utils.mana_coupon import (
    create_coupon,
    delete_coupon,
    get_source_mana,
)
from CTFd.plugins.ctfd_chall_manager.utils.mana_lock import load_or_store
from CTFd.utils import get_config
from CTFd.utils import user as current_user
from CTFd.utils.config import is_teams_mode
from CTFd.utils.decorators import admins_only, authed_only
from flask import request
from flask_restx import Namespace, Resource

# Configure logger for this module
logger = configure_logger(__name__)

admin_namespace = Namespace("ctfd-chall-manager-admin")
user_namespace = Namespace("ctfd-chall-manager-user")


@admin_namespace.errorhandler
@user_namespace.errorhandler
def handle_default(err):
    """
    Handler for namespaces error
    """
    logger.error("Unexpected error: %s", err)
    return {"success": False, "message": "Unexpected things happened"}, 500


# region AdminInstance
# Resource to monitor all instances
@admin_namespace.route("/instance")
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

            r = get_instance(challenge_id, source_id)
            logger.info("instance retrieved successfully: %s", json.loads(r.text))
        except ChallManagerException as e:
            logger.error("error while communicating with CM: %s", e)
            return {
                "success": False,
                "data": {
                    "message": f"error while communicating with CM : {e}",
                },
            }, 500

        return {"success": True, "data": json.loads(r.text)}, 200

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

        cm_mana_total = get_config("chall-manager:chall-manager_mana_total")

        try:
            lock = load_or_store(f"{source_id}")
            lock.admin_lock()

            if cm_mana_total > 0:
                create_coupon(challenge_id, source_id)
                logger.info(
                    "coupon created for challenge_id: %s, source_id: %s",
                    challenge_id,
                    source_id,
                )

            logger.debug(
                "creating instance for challenge_id: %s, source_id: %s",
                challenge_id,
                source_id,
            )

            r = create_instance(challenge_id, source_id)
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
                }, 200

            logger.error(
                "error while creating instance for challenge_id: %s, source_id: %s",
                challenge_id,
                source_id,
            )
            if cm_mana_total > 0:
                delete_coupon(challenge_id, source_id)
                logger.info(
                    "coupon deleted for challenge_id: %s, source_id: %s",
                    challenge_id,
                    source_id,
                )
            return {
                "success": False,
                "data": {
                    "message": e.message,
                },
            }, 500

        finally:
            logger.debug("admin_unlock %s", lock)
            lock.admin_unlock()

        return {"success": True, "data": json.loads(r.text)}, 200

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

            r = update_instance(challenge_id, source_id)
            logger.info(
                "instance for challenge_id: %s, source_id: %s updated successfully",
                challenge_id,
                source_id,
            )
        except ChallManagerException as e:
            logger.error("error while updating instance: %s", e)
            return {
                "success": False,
                "data": {
                    "message": f"error while communicating with CM : {e}",
                },
            }, 500

        return {"success": True, "data": json.loads(r.text)}, 200

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

        cm_mana_total = get_config("chall-manager:chall-manager_mana_total")

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
            r = delete_instance(challenge_id, source_id)
            logger.info(
                "instance for challenge_id: %s, source_id: %s delete successfully",
                challenge_id,
                source_id,
            )

            if cm_mana_total > 0:
                delete_coupon(challenge_id, source_id)
                logger.info(
                    "coupon deleted for challenge_id: %s, source_id: %s",
                    challenge_id,
                    source_id,
                )

        except ChallManagerException as e:
            logger.error("error while deleting instance: %s", e)
            return {
                "success": False,
                "data": {
                    "message": f"error while communicating with CM : {e}",
                },
            }, 500

        finally:
            logger.debug("admin_unlock %s", lock)
            lock.admin_unlock()

        return {"success": True, "data": json.loads(r.text)}, 200


# region UserInstance
# Resource to permit user to manage their instance
@user_namespace.route("/instance")
class UserInstance(Resource):
    """
    UserInstance class handle CRUD operation for /instance API endpoint.
    To use methods, you need to be authenticated with user capable permission on CTFd.
    The sourceId cannot be defined as long as the current will be retrieve from flask session.
    If CTFd is configured as Team mode, the sourceId will be replaced by
    the team_id of the current user.
    """

    @staticmethod
    @authed_only
    @challenge_visible
    def get():
        """
        Retrieve instance informations of challengeId provided on Chall-Manager.
        """
        # mandatory
        challenge_id = request.args.get("challengeId")

        # check userMode of CTFd
        user = current_user.get_current_user()
        if user is None:
            logger.info()
            return {"success": False, "data": {"message": "unauthorized"}}, 403

        user_id = user.id
        source_id = user_id
        logger.info("user %s request GET on challenge %s", source_id, challenge_id)

        if is_teams_mode():
            source_id = user.team_id
            # If user has no team
            if not source_id:
                logger.info("user %s has no team, abort", user_id)
                return {"success": False, "data": {"message": "unauthorized"}}, 403

        if not challenge_id or not source_id:
            logger.warning("Missing argument: challenge_id or source_id")
            return {
                "success": False,
                "data": {
                    "message": "Missing argument : challenge_id or source_id",
                },
            }, 403

        # if challenge is shared
        challenge = DynamicIaCChallenge.query.filter_by(id=challenge_id).first()
        if challenge.shared:
            source_id = 0

        try:
            logger.debug(
                "getting instance for challenge_id: %s, source_id: %s",
                challenge_id,
                source_id,
            )
            r = get_instance(challenge_id, source_id)
            logger.info("instance retrieved successfully : %s", json.loads(r.text))
        except ChallManagerException as e:
            logger.error("error while getting instance: {e}")
            return {
                "success": False,
                "data": {
                    "message": f"Error while communicating with CM : {e}",
                },
            }, 500

        # return only necessary values
        data = {}
        result = json.loads(r.text)
        for k in ["connectionInfo", "until", "since"]:
            if k in result.keys():
                data[k] = result[k]

        return {"success": True, "data": data}, 200

    @staticmethod
    @authed_only
    @challenge_visible
    def post():  # pylint: disable=too-many-return-statements,too-many-branches
        """
        Create an instance of challengeId provided on Chall-Manager.
        This method requires user to be authenticated and has suffisant mana to perform creation.
        """
        data = request.get_json()
        challenge_id = data.get("challengeId")

        user = current_user.get_current_user()
        if user is None:
            return {"success": False, "data": {"message": "unauthorized"}}, 403

        user_id = int(user.id)
        source_id = user_id
        logger.info(
            "user %s request instance creation of challenge %s", source_id, challenge_id
        )
        # check userMode of CTFd
        if is_teams_mode():
            source_id = user.team_id
            # If user has no team
            if not source_id:
                logger.info("user %s has no team, abort", user_id)
                return {"success": False, "data": {"message": "unauthorized"}}, 403

        # retrieve all instance deployed by chall-manager
        cm_mana_total = get_config("chall-manager:chall-manager_mana_total")
        challenge = DynamicIaCChallenge.query.filter_by(id=challenge_id).first()
        if challenge.shared:
            logger.warning(
                "unauthorized attempt to create sharing instance challenge_id: %s, source_id: %s",
                challenge_id,
                source_id,
            )
            return {"success": False, "data": {"message": "unauthorized"}}, 403

        # check if source_id can launch the instance
        try:
            lock = load_or_store(str(source_id))
            logger.debug("post /instance acquire the player lock for %s", source_id)
            lock.player_lock()

            if cm_mana_total > 0:
                challenge = DynamicIaCChallenge.query.filter_by(id=challenge_id).first()

                # check current mana
                source_mana = get_source_mana(int(source_id))

                if source_mana + challenge.mana_cost > cm_mana_total:
                    logger.warning(
                        "source_id %s does not have the necessary mana", source_id
                    )
                    return (
                        {
                            "success": False,
                            "data": {
                                "message": "You or your team used up all your mana. \
                                You must recover mana by destroying instances \
                                of other challenges to continue.",
                            },
                        },
                        403,
                    )

            logger.debug(
                "creating instance for challenge_id: %s, source_id: %s",
                challenge_id,
                source_id,
            )
            r = create_instance(challenge_id, source_id)
            logger.info(
                "instance for challenge_id: %s, source_id: %s created successfully",
                challenge_id,
                source_id,
            )

            # create a new coupon
            if cm_mana_total > 0:
                logger.debug(
                    "creating coupon for challenge_id: %s, source_id: %s",
                    challenge_id,
                    source_id,
                )
                create_coupon(challenge_id, source_id)
                logger.info(
                    "coupon for challenge_id: %s, source_id: %s created successfully",
                    challenge_id,
                    source_id,
                )

        except ChallManagerException as e:
            if "already exist" in e.message:
                return {
                    "success": False,
                    "data": {
                        "message": "instance already exist",
                    },
                }, 200
            return {
                "success": False,
                "data": {
                    "message": f"error from Chall-Manager API: {e.message}",
                },
            }, 500

        finally:
            logger.debug("post /instance release the player lock for %s", source_id)
            lock.player_unlock()

        # return only necessary values
        data = {}
        result = json.loads(r.text)
        for k in ["connectionInfo", "until", "since"]:
            if k in result.keys():
                data[k] = result[k]

        return {"success": True, "data": data}, 200

    @staticmethod
    @authed_only
    @challenge_visible
    def patch():  # pylint: disable=too-many-return-statements
        """
        Renew instance on Chall-Manager.
        If the challengeId provided
        """
        # mandatory
        data = request.get_json()
        challenge_id = data.get("challengeId")

        user = current_user.get_current_user()
        if user is None:
            return {"success": False, "data": {"message": "unauthorized"}}, 403

        user_id = int(user.id)
        source_id = user_id
        logger.info(
            "user %s request instance renew of challenge %s", source_id, challenge_id
        )
        # check userMode of CTFd
        if is_teams_mode():
            source_id = user.team_id
            # If user has no team
            if not source_id:
                logger.info("user %s has no team, abort", user_id)
                return {"success": False, "data": {"message": "unauthorized"}}, 403

        challenge = DynamicIaCChallenge.query.filter_by(id=challenge_id).first()
        if challenge.shared:
            logger.warning(
                "unauthorized attempt to patch sharing instance challenge_id: %s, source_id: %s",
                challenge_id,
                source_id,
            )
            return {"success": False, "data": {"message": "unauthorized"}}, 403

        if not challenge.timeout:
            logger.warning(
                "unauthorized attempt to patch non timeout instance challenge_id:%s, source_id: %s",
                challenge_id,
                source_id,
            )
            return {"success": False, "data": {"message": "unauthorized"}}, 403

        if not challenge_id or not source_id:
            logger.warning("Missing argument: challenge_id or source_id")
            return {
                "success": False,
                "data": {
                    "message": "Missing argument : challenge_id or source_id",
                },
            }, 400

        try:
            logger.debug(
                "updating instance for challenge_id: %s, source_id: %s",
                challenge_id,
                source_id,
            )
            r = update_instance(challenge_id, source_id)
            logger.info(
                "instance for challenge_id: %s, source_id: %s updated successfully",
                challenge_id,
                source_id,
            )
        except ChallManagerException as e:
            return {
                "success": False,
                "data": {
                    "message": f"error from Chall-Manager API: {e.message}",
                },
            }, 500

        msg = "Your instance has been renewed !"
        a = json.loads(r.text)

        if challenge.until and challenge.timeout:
            if challenge.until == a["until"]:
                msg = (
                    "You have renewed your instance, but it can't be renewed anymore !"
                )

        return {"success": True, "data": {"message": msg}}, 200

    @staticmethod
    @authed_only
    @challenge_visible
    def delete():
        """
        Delete instance of the challengeId provided
        """
        data = request.get_json()
        challenge_id = data.get("challengeId")

        user = current_user.get_current_user()
        if user is None:
            return {"success": False, "data": {"message": "unauthorized"}}, 403

        user_id = int(user.id)
        source_id = user_id
        logger.info(
            "user %s request instance delete of challenge %s", user_id, challenge_id
        )
        # check userMode of CTFd
        if is_teams_mode():
            source_id = user.team_id
            # If user has no team
            if not source_id:
                logger.info("user %s has no team, abort", user_id)
                return {"success": False, "data": {"message": "unauthorized"}}, 403

        cm_mana_total = get_config("chall-manager:chall-manager_mana_total")
        challenge = DynamicIaCChallenge.query.filter_by(id=challenge_id).first()
        if challenge.shared:
            logger.warning(
                "unauthorized attempt to delete shared instance, challenge_id: %s, source_id: %s",
                challenge_id,
                source_id,
            )
            return {"success": False, "data": {"message": "unauthorized"}}, 403

        try:
            lock = load_or_store(f"{source_id}")
            logger.debug("delete /instance acquire the player lock for %s", source_id)
            lock.player_lock()

            logger.debug(
                "deleting instance for challenge_id: %s, source_id: %s",
                challenge_id,
                source_id,
            )
            delete_instance(challenge_id, source_id)
            logger.info(
                "instance for challenge_id: %s, source_id: %s deleted successfully",
                challenge_id,
                source_id,
            )

            if cm_mana_total > 0:
                logger.debug(
                    "deleting coupon for challenge_id: %s, source_id: %s",
                    challenge_id,
                    source_id,
                )
                delete_coupon(challenge_id, source_id)
                logger.info(
                    "coupon deleted for challenge_id: %s, source_id: %s",
                    challenge_id,
                    source_id,
                )

        except ChallManagerException as e:
            logger.error("error while deleting instance: %s", e)
            return {
                "success": False,
                "data": {
                    "message": f"error while communicating with CM : {e}",
                },
            }, 500

        finally:
            logger.debug("delete /instance release the player lock for %s", source_id)
            lock.player_unlock()

        return {"success": True, "data": {}}, 200


# region UserMana
@user_namespace.route("/mana")
class UserMana(Resource):
    """
    UserMana class handle R operation on /mana.
    When the Player use /mana, all coupons will be updated or deleted regarding the
    actual informations on Chall-Manager.
    """

    @staticmethod
    @authed_only
    def get():
        """
        Retrieve the actual mana used by the sourceId.
        All existing coupons without actual instances will be destroyed.
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

            mana = get_source_mana(source_id)
            logger.debug("retrieved mana for source_id: %s, mana: %s", source_id, mana)
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


def retrieve_all_ids(admin=False) -> dict[str, int] | ValueError:
    """
    This function return all ids for AdminInstance calls.

    return: dict of {"user_id", "team_id", "source_id", "challenge_id"}
    """
    team_id = 0
    admin_id = 0

    user = current_user.get_current_user()
    user_id = int(user.id)

    if admin:
        admin_id = user_id

    # If GET
    challenge_id = request.args.get("challengeId")
    source_id = request.args.get("sourceId")

    if challenge_id is None or source_id is None:  # If POST/PATCH/DELETE
        data = request.get_json()
        challenge_id = data.get("challengeId")
        source_id = data.get("sourceId")

    if challenge_id is None or source_id is None:
        raise ValueError("missing challengeId or sourceId")

    challenge_id = int(challenge_id)
    source_id = int(source_id)

    if not admin:
        source_id = user_id
        if is_teams_mode():
            team_id = user.team_id
            if team_id is not None:
                source_id = int(team_id)

    return {
        "admin_id": admin_id,
        "user_id": user_id,
        "team_id": team_id,
        "source_id": source_id,
        "challenge_id": challenge_id,
    }

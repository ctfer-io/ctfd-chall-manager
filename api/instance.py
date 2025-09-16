"""
This module describes the UserInstance API endpoint of the plugin:
Route: /api/v1/plugins/ctfd-chall-manager/instance.
"""

import json

from CTFd.plugins.ctfd_chall_manager.models import DynamicIaCChallenge
from CTFd.plugins.ctfd_chall_manager.utils.chall_manager_error import (
    ChallManagerException,
)
from CTFd.plugins.ctfd_chall_manager.utils.decorators import challenge_visible
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
from CTFd.utils.decorators import authed_only
from flask import request
from flask_restx import Resource

# Configure logger for this module
logger = configure_logger(__name__)


# region UserInstance
# Resource to permit user to manage their instance
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

import json

from flask import request
from flask_restx import Namespace, Resource, abort

from CTFd.utils import get_config  # type: ignore
from CTFd.utils import user as current_user  # type: ignore
from CTFd.utils.decorators import admins_only, authed_only  # type: ignore

from .models import DynamicIaCChallenge

from .utils.instance_manager import create_instance, delete_instance, get_instance, update_instance
from .utils.mana_coupon import create_coupon, delete_coupon, get_source_mana
from .utils.logger import configure_logger
from .utils.mana_lock import load_or_store
from .utils.chall_manager_error import ChallManagerException
from .decorators import challenge_visible


# Configure logger for this module
logger = configure_logger(__name__)

admin_namespace = Namespace("ctfd-chall-manager-admin")
user_namespace = Namespace("ctfd-chall-manager-user")


@admin_namespace.errorhandler
@user_namespace.errorhandler
def handle_default(err):
    logger.error(f"Unexpected error: {err}")
    return {
        'success': False,
        'message': 'Unexpected things happened'
    }, 500


# region AdminInstance
# Resource to monitor all instances
@admin_namespace.route('/instance')
class AdminInstance(Resource):
    @staticmethod
    @admins_only
    def get():
        # retrieve all instances deployed by chall-manager
        challengeId = request.args.get("challengeId")
        sourceId = request.args.get("sourceId")

        adminId = str(current_user.get_current_user().id)
        logger.info(f"Admin {adminId} get instance info for challengeId: {challengeId}, sourceId: {sourceId}")

        try:
            logger.debug(f"Getting instance for challengeId: {challengeId}, sourceId: {sourceId}")
            r = get_instance(challengeId, sourceId)
            logger.info(f"Instance retrieved successfully. {json.loads(r.text)}")
        except Exception as e:
            logger.error(f"Error while communicating with CM: {e}")
            return {'success': False, 'data': {
                'message': f"Error while communicating with CM : {e}",
            }}

        return {'success': True, 'data': json.loads(r.text)}
    
    @staticmethod
    @admins_only
    def post():
        data = request.get_json()
        # mandatory
        challengeId = data.get("challengeId")
        sourceId = data.get("sourceId")

        adminId = str(current_user.get_current_user().id)
        logger.info(f"Admin {adminId} request instance creation for challengeId: {challengeId}, sourceId: {sourceId}")

        cm_mana_total = get_config("chall-manager:chall-manager_mana_total")

        try:
            lock = load_or_store(f"{sourceId}")
            lock.admin_lock()

            if cm_mana_total > 0:
                create_coupon(challengeId, sourceId)
                logger.info(f"Coupon created for challengeId: {challengeId}, sourceId: {sourceId}")

            logger.debug(f"Creating instance for challengeId: {challengeId}, sourceId: {sourceId}")
            r = create_instance(challengeId, sourceId)
            logger.info(f"Instance for challengeId: {challengeId}, sourceId: {sourceId} created successfully.")

        except ChallManagerException as e:
            if "already exist" in e.message:
                return {'success': False, 'data': {
                    'message': f"instance already exist",
                }}
            return {'success': False, 'data': {
                    'message': f"{e.message}",
                }}

        except Exception as e:
            logger.error(f"Error while creating instance: {e}")
            if cm_mana_total > 0:
                delete_coupon(challengeId, sourceId)
                logger.info(f"Coupon deleted for challengeId: {challengeId}, sourceId: {sourceId}")
            return {'success': False, 'data': {
                'message': f"Error while communicating with CM : {e}",
            }}

        finally:
            logger.debug(f"admin_unlock {lock}")
            lock.admin_unlock()

        return {'success': True, 'data': json.loads(r.text)}

    @staticmethod
    @admins_only
    def patch():
        # mandatory
        data = request.get_json()
        challengeId = data.get("challengeId")
        sourceId = data.get("sourceId")

        adminId = str(current_user.get_current_user().id)
        logger.info(f"Admin {adminId} request instance update for challengeId: {challengeId}, sourceId: {sourceId}")

        try:
            logger.debug(f"Updating instance for challengeId: {challengeId}, sourceId: {sourceId}")
            r = update_instance(challengeId, sourceId)
            logger.info(f"Instance for challengeId: {challengeId}, sourceId: {sourceId} updated successfully.")
        except Exception as e:
            logger.error(f"Error while updating instance: {e}")
            return {'success': False, 'data': {
                'message': f"Error while communicating with CM : {e}",
            }}

        return {'success': True, 'data': json.loads(r.text)}

    @staticmethod
    @admins_only
    def delete():
        # mandatory
        data = request.get_json()
        challengeId = data.get("challengeId")
        sourceId = data.get("sourceId")

        cm_mana_total = get_config("chall-manager:chall-manager_mana_total")

        adminId = str(current_user.get_current_user().id)
        logger.info(f"Admin {adminId} request instance delete for challengeId: {challengeId}, sourceId: {sourceId}")

        try:
            lock = load_or_store(f"{sourceId}")
            lock.admin_lock()

            logger.debug(f"Deleting instance for challengeId: {challengeId}, sourceId: {sourceId}")
            r = delete_instance(challengeId, sourceId)
            logger.info(f"Instance for challengeId: {challengeId}, sourceId: {sourceId} delete successfully.")

            if cm_mana_total > 0:
                delete_coupon(challengeId, sourceId)
                logger.info(f"Coupon deleted for challengeId: {challengeId}, sourceId: {sourceId}")

        except Exception as e:
            logger.error(f"Error while deleting instance: {e}")
            return {'success': False, 'data': {
                'message': f"Error while communicating with CM : {e}",
            }}

        finally:
            logger.debug(f"admin_unlock {lock}")
            lock.admin_unlock()

        return {'success': True, 'data': json.loads(r.text)}


# region UserInstance
# Resource to permit user to manage their instance
@user_namespace.route("/instance")
class UserInstance(Resource):
    @staticmethod
    @authed_only
    @challenge_visible
    def get():
        # mandatory     
        challengeId = request.args.get("challengeId")

        # check userMode of CTFd
        sourceId = str(current_user.get_current_user().id)
        logger.info(f"user {sourceId} request GET on challenge {challengeId}")

        if get_config("user_mode") == "teams":
            sourceId = str(current_user.get_current_user().team_id)        

        if not challengeId or not sourceId:
            logger.warning("Missing argument: challengeId or sourceId")
            return {'success': False, 'data': {
                'message': "Missing argument : challengeId or sourceId",
            }}

        # if challenge is shared
        challenge = DynamicIaCChallenge.query.filter_by(id=challengeId).first()
        if challenge.shared:
            sourceId = 0

        try:
            logger.debug(f"Getting instance for challengeId: {challengeId}, sourceId: {sourceId}")
            r = get_instance(challengeId, sourceId)
            logger.info(f"Instance retrieved successfully. {json.loads(r.text)}")
        except Exception as e:
            logger.error(f"Error while getting instance: {e}")
            return {'success': False, 'data': {
                'message': f"Error while communicating with CM : {e}",
            }}

        # return only necessary values
        data = {}
        result = json.loads(r.text)
        if 'connectionInfo' in result.keys():
            data['connectionInfo'] = result['connectionInfo']

        if 'until' in result.keys():
            data['until'] = result['until']

        if 'since' in result.keys():
            data['since'] = result['since']

        return {'success': True, 'data': data}

    @staticmethod
    @authed_only
    @challenge_visible
    def post(): 
        # retrieve all instance deployed by chall-manager
        cm_mana_total = get_config("chall-manager:chall-manager_mana_total")

        data = request.get_json()
        # mandatory
        challengeId = data.get("challengeId")

        # check userMode of CTFd
        sourceId = str(current_user.get_current_user().id)
        logger.info(f"user {sourceId} request instance creation of challenge {challengeId}")
        if get_config("user_mode") == "teams":
            sourceId = str(current_user.get_current_user().team_id)

        challenge = DynamicIaCChallenge.query.filter_by(id=challengeId).first()
        if challenge.shared:
            logger.warning(f"Unauthorized attempt to create sharing instance challengeId: {challengeId}, sourceId: {sourceId}")
            return {'success': False, 'data': {
                'message': "Unauthorized"
            }} 
        
        # check if sourceId can launch the instance

        try:
            lock = load_or_store(f"{sourceId}")
            lock.player_lock()

            if cm_mana_total > 0:
                challenge = DynamicIaCChallenge.query.filter_by(id=challengeId).first()

                # check current mana
                source_mana = get_source_mana(int(sourceId))

                if source_mana + challenge.mana_cost > cm_mana_total:
                    logger.warning(f"sourceId {sourceId} does not have the necessary mana")
                    return {'success': False, 'data': {
                        'message': "You or your team used up all your mana. You must recover mana by destroying instances of other challenges to continue.",
                    }}

            logger.debug(f"Creating instance for challengeId: {challengeId}, sourceId: {sourceId}")
            r = create_instance(challengeId, sourceId)
            logger.info(f"Instance for challengeId: {challengeId}, sourceId: {sourceId} created successfully")

            # create a new coupon
            if cm_mana_total > 0:
                logger.debug(f"Creating coupon for challengeId: {challengeId}, sourceId: {sourceId}")
                create_coupon(challengeId, sourceId)
                logger.info(f"Coupon for challengeId: {challengeId}, sourceId: {sourceId} created successfully")

        except ChallManagerException as e:
            if "already exist" in e.message:
                return {'success': False, 'data': {
                    'message': f"instance already exist",
                }}
            return {'success': False, 'data': {
                'message': f"{e.message}",
            }}

        except Exception as e:
            logger.error(f"Error while creating instance: {e}")
            return {'success': False, 'data': {
                'message': f"Error while communicating with CM : {e}",
            }}

        finally:
            lock.player_unlock()

        # return only necessary values
        data = {}
        result = json.loads(r.text)
        if 'connectionInfo' in result.keys():
            data['connectionInfo'] = result['connectionInfo']

        if 'until' in result.keys():
            data['until'] = result['until']

        if 'since' in result.keys():
            data['since'] = result['since']

        return {'success': True, 'data': data}

    @staticmethod
    @authed_only
    @challenge_visible
    def patch():
        # mandatory
        data = request.get_json()
        challengeId = data.get("challengeId")

        # check userMode of CTFd
        sourceId = str(current_user.get_current_user().id)
        logger.info(f"user {sourceId} request instance update of challenge {challengeId}")
        if get_config("user_mode") == "teams":
            sourceId = str(current_user.get_current_user().team_id)

        challenge = DynamicIaCChallenge.query.filter_by(id=challengeId).first()
        if challenge.shared:
            logger.warning(f"Unauthorized attempt to patch sharing instance challengeId: {challengeId}, sourceId: {sourceId}")
            return {'success': False, 'data': {
                'message': "Unauthorized"
            }} 

        if not challengeId or not sourceId:
            logger.warning("Missing argument: challengeId or sourceId")
            return {'success': False, 'data': {
                'message': "Missing argument : challengeId or sourceId",
            }}

        try:
            logger.debug(f"Updating instance for challengeId: {challengeId}, sourceId: {sourceId}")
            r = update_instance(challengeId, sourceId)
            logger.info(f"Instance for challengeId: {challengeId}, sourceId: {sourceId} updated successfully.")
        except ChallManagerException as e:
            return {'success': False, 'data': {
                'message': f"{e.message}",
            }}

        except Exception as e:
            logger.error(f"Error while updating instance: {e}")
            return {'success': False, 'data': {
                'message': f"Error while communicating with CM : {e}",
            }}


        msg = "Your instance has been renewed !"
        a = json.loads(r.text)

        if challenge.until and challenge.timeout:
            if challenge.until  == a["until"]:
                msg = "You have renewed your instance, but it can't be renewed anymore !"

        return {'success': True, 'data': {
            'message': msg
        }}

    @staticmethod
    @authed_only
    @challenge_visible
    def delete():
        # retrieve all instances deployed by chall-manager
        cm_mana_total = get_config("chall-manager:chall-manager_mana_total")

        data = request.get_json()
        challengeId = data.get("challengeId")

        # check userMode of CTFd
        sourceId = str(current_user.get_current_user().id)
        logger.info(f"user {sourceId} requests instance destroy of challenge {challengeId}")
        if get_config("user_mode") == "teams":
            sourceId = str(current_user.get_current_user().team_id)

        challenge = DynamicIaCChallenge.query.filter_by(id=challengeId).first()
        if challenge.shared:
            logger.warning(f"Unauthorized attempt to delete shared instance, challengeId: {challengeId}, sourceId: {sourceId}")
            return {'success': False, 'data': {
                'message': "Unauthorized"
            }}

        try:
            lock = load_or_store(f"{sourceId}")
            lock.player_lock()

            logger.debug(f"Deleting instance for challengeId: {challengeId}, sourceId: {sourceId}")
            r = delete_instance(challengeId, sourceId)
            logger.info(f"Instance for challengeId: {challengeId}, sourceId: {sourceId} deleted successfully.")
        except Exception as e:
            logger.error(f"Error while deleting instance: {e}")
            return {'success': False, 'data': {
                'message': f"Error while communicating with CM : {e}",
            }}

        finally:
            logger.debug(f"/mana release the {sourceId}_r lock")
            lock.player_unlock()

        if cm_mana_total > 0:
            logger.debug(f"Deleting coupon for challengeId: {challengeId}, sourceId: {sourceId}")
            delete_coupon(challengeId, sourceId)
            logger.info(f"Coupon deleted for challengeId: {challengeId}, sourceId: {sourceId}")

        return {'success': True, 'data': {}}


# region UserMana
@user_namespace.route("/mana")
class UserMana(Resource):
    @staticmethod
    @authed_only
    def get():
        sourceId = str(current_user.get_current_user().id)
        if get_config("user_mode") == "teams":
            sourceId = str(current_user.get_current_user().team_id)

        try:
            lock = load_or_store(f"{sourceId}")
            lock.player_lock()

            mana = get_source_mana(sourceId)
            logger.debug(f"Retrieved mana for sourceId: {sourceId}, mana: {mana}")
        finally:
            lock.player_unlock()

        return {'success': True, 'data': {
            'used': f"{mana}",
            'total': f"{get_config('chall-manager:chall-manager_mana_total')}",
        }}


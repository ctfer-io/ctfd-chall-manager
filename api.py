import json

from flask import request
from flask_restx import Namespace, Resource, abort

from CTFd.utils import get_config # type: ignore
from CTFd.utils import user as current_user # type: ignore
from CTFd.utils.decorators import admins_only, authed_only # type: ignore

from .models import DynamicIaCChallenge

from .utils.instance_manager import create_instance, delete_instance, get_instance, update_instance
from .utils.mana_coupon import create_coupon, delete_coupon, get_source_mana

admin_namespace = Namespace("ctfd-chall-manager-admin")
user_namespace = Namespace("ctfd-chall-manager-user")


@admin_namespace.errorhandler
@user_namespace.errorhandler
def handle_default(err):
    return {
        'success': False,
        'message': 'Unexpected things happened'
    }, 500

# region AdminInstance
# Ressource to monitor all instances
@admin_namespace.route('/instance')
class AdminInstance(Resource):
    @staticmethod
    @admins_only
    def get():
        # retrieve all instance deployed by chall-manager
        challengeId = request.args.get("challengeId")
        sourceId = request.args.get("sourceId")

        try:
            r = get_instance(challengeId, sourceId)
        except Exception as e:
            return {'success': False, 'data':{
                    'message': f"Error while communicating with CM : {e}",
            }}
        
        return {'success': True, 'data':{
                'message': json.loads(r.text),
        }}
    
    @staticmethod
    @admins_only
    def post():
        ## mandatory
        challengeId = request.args.get("challengeId") 
        sourceId = request.args.get("sourceId")

        cm_mana_total = get_config("chall-manager:chall-manager_mana_total")

        if cm_mana_total > 0:
            create_coupon(challengeId, sourceId)

        try:
            r = create_instance(challengeId, sourceId)
        except Exception as e:
            if cm_mana_total > 0:
                delete_coupon(challengeId, sourceId)
            return {'success': False, 'data':{
                    'message': f"Error while communicating with CM : {e}",
            }}
        
        return {'success': True, 'data':{
                'message': json.loads(r.text),
        }}

    @staticmethod
    @admins_only
    def patch():
        ## mandatory
        challengeId = request.args.get("challengeId") 
        sourceId = request.args.get("sourceId")

        try:
            r = update_instance(challengeId, sourceId)
        except Exception as e:
            return {'success': False, 'data':{
                    'message': f"Error while communicating with CM : {e}",
            }}
        
        return {'success': True, 'data':{
                'message': json.loads(r.text),
        }}


    @staticmethod
    @admins_only
    def delete():
        ## mandatory
        challengeId = request.args.get("challengeId") 
        sourceId = request.args.get("sourceId")

        cm_mana_total = get_config("chall-manager:chall-manager_mana_total")

        try:
            r = delete_instance(challengeId, sourceId)
        except Exception as e:
            return {'success': False, 'data':{
                    'message': f"Error while communicating with CM : {e}",
            }}      
        
        
        if cm_mana_total > 0:        
            delete_coupon(challengeId, sourceId)
        
        return {'success': True, 'data':{
                'message': json.loads(r.text),
        }}


# region UserInstance
# Resource to permit user to manager their instance 
@user_namespace.route("/instance")
class UserInstance(Resource):
    @staticmethod
    @authed_only
    # @challenge_visible
    # trigger while GET http://localhost:4000/api/v1/plugins/ctfd-chall-manager/instance?challengeId=1
    def get():
        # retrieve all instance deployed by chall-manager
        
        ## mandatory
        challengeId = request.args.get("challengeId")
        
        # check userMode of CTFd
        sourceId = str(current_user.get_current_user().id)
        if get_config("user_mode") == "teams":
            sourceId = str(current_user.get_current_user().team_id)

        if not challengeId or not sourceId:
            return {'success': False, 'data':{
                    'message': "Missing argument : challengeId or sourceId",
            }} 
        
        # if challenge is global scope
        challenge = DynamicIaCChallenge.query.filter_by(id=challengeId).first()
        if challenge.scope_global:
            sourceId = 0

        try:
            r = get_instance(challengeId, sourceId)
        except Exception as e:
            return {'success': False, 'data':{
                    'message': f"Error while communicating with CM : {e}",
            }}
        
        ## return only necessary values
        data = {}
        result = json.loads(r.text)
        if 'connectionInfo' in result.keys():
            data['connectionInfo'] = result['connectionInfo']
        
        if 'until' in result.keys():
            data['until'] = result['until'] 
        
        
        return {'success': True, 'data':{
                'message': data,
        }}

    @staticmethod
    @authed_only
    # @challenge_visible
    # @frequency_limited
    def post():
        # retrieve all instance deployed by chall-manager
        cm_mana_total = get_config("chall-manager:chall-manager_mana_total")
       
        data = request.get_json()  
        ## mandatory
        challengeId = data.get("challengeId") 

        # if challenge is global scope
        challenge = DynamicIaCChallenge.query.filter_by(id=challengeId).first()
        if challenge.scope_global:
            return {'success': False, 'data':{
                    'message': "Unauthorized"
                }}
        
        # check userMode of CTFd
        sourceId = str(current_user.get_current_user().id)
        if get_config("user_mode") == "teams":
            sourceId = str(current_user.get_current_user().team_id)
        
        # check if sourceId can launch the instance 
        if cm_mana_total > 0:
            # retrieve challenge mana_cost
            challenge = DynamicIaCChallenge.query.filter_by(id=data.get("challengeId")).first()   

            # check current mana
            mana_source = get_source_mana(int(sourceId))

            if mana_source + challenge.mana_cost > cm_mana_total:
                print("sourceId does not have the necessary mana") # TODO use logging
                return {'success': False, 'data':{
                        'message': "You or your team used up all your mana. You must recover mana by destroying instances of other challenges to continue.",
                }}

            # create a new coupon 
            create_coupon(data.get("challengeId"), sourceId)

        try:
            r = create_instance(challengeId, sourceId)
        except Exception as e:
            if cm_mana_total > 0:
                delete_coupon(challengeId, sourceId)
            return {'success': False, 'data':{
                    'message': f"Error while communicating with CM : {e}",
            }}

        
        ## return only necessary values
        data = {}
        result = json.loads(r.text)
        if 'connectionInfo' in result.keys():
            data['connectionInfo'] = result['connectionInfo']
        
        if 'until' in result.keys():
            data['until'] = result['until'] 
        
        
        return {'success': True, 'data':{
                'message': data,
        }}

    @staticmethod
    @authed_only
    # @challenge_visible
    # @frequency_limited
    def patch():
        ## mandatory
        challengeId = request.args.get("challengeId") 

        challenge = DynamicIaCChallenge.query.filter_by(id=challengeId).first()
        if challenge.scope_global:
            return {'success': False, 'data':{
                    'message': "Unauthorized"
                }}

        
        # check userMode of CTFd
        sourceId = str(current_user.get_current_user().id)
        if get_config("user_mode") == "teams":
            sourceId = str(current_user.get_current_user().team_id)

        if not challengeId or not sourceId:
            return {'success': False, 'data':{
                    'message': "Missing argument : challengeId or sourceId",
            }} 

        try:
            r = update_instance(challengeId, sourceId)
        except Exception as e:
            return {'success': False, 'data':{
                    'message': f"Error while communicating with CM : {e}",
            }}
        
        return {'success': True, 'data':{
                'message': f"{r}",
        }}


    @staticmethod
    @authed_only
    # @frequency_limited
    # @challenge_visible
    def delete():
        # retrieve all instance deployed by chall-manager
        cm_mana_total = get_config("chall-manager:chall-manager_mana_total")  
        
        challengeId = request.args.get("challengeId")   

        challenge = DynamicIaCChallenge.query.filter_by(id=challengeId).first()
        if challenge.scope_global:
            return {'success': False, 'data':{
                    'message': "Unauthorized"
                }}
        

        # check userMode of CTFd
        sourceId = str(current_user.get_current_user().id)
        if get_config("user_mode") == "teams":
            sourceId = str(current_user.get_current_user().team_id)        

        try:
            r = delete_instance(challengeId, sourceId)
        except Exception as e:
            return {'success': False, 'data':{
                    'message': f"Error while communicating with CM : {e}",
            }}
        
        if cm_mana_total > 0:
            delete_coupon(challengeId, sourceId)
        
        return {'success': True, 'data':{
                'message': json.loads(r.text),
        }}



# region UserMana
@user_namespace.route("/mana")
class UserMana(Resource):
    @staticmethod
    @authed_only
    def get():
        sourceId = str(current_user.get_current_user().id)
        if get_config("user_mode") == "teams":
            sourceId = str(current_user.get_current_user().team_id)
        
        mana = get_source_mana(sourceId)

        return {'success': True, 'data':{
                'sourceId': f"{sourceId}",
                'mana': f"{mana}",
                'remaining': f"{get_config('chall-manager:chall-manager_mana_total')-mana}",
        }} 
    

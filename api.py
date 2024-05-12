from datetime import datetime

import requests
import json
import os
import base64

from flask import request
from flask_restx import Namespace, Resource, abort

from CTFd.utils import get_config
from CTFd.utils import user as current_user
from CTFd.utils.decorators import admins_only, authed_only
from CTFd.models import Files, db, Challenges

# from .decorators import challenge_visible, frequency_limited
# from .utils.control import ControlUtil
# from .utils.db import DBContainer
# from .utils.routers import Router

admin_namespace = Namespace("ctfd-chall-manager-admin")
user_namespace = Namespace("ctfd-chall-manager-user")


@admin_namespace.errorhandler
@user_namespace.errorhandler
def handle_default(err):
    return {
        'success': False,
        'message': 'Unexpected things happened'
    }, 500

# Ressource to monitor all instances
@admin_namespace.route('/instance')
class AdminInstance(Resource):
    @staticmethod
    @admins_only
    def get():
        # retrieve all instance deployed by chall-manager
        cm_api_url = get_config("chall-manager:chall-manager_api_url")

        challengeId = request.args.get("challengeId")
        sourceId = request.args.get("sourceId")

        if challengeId and sourceId: 
            url = f"{cm_api_url}/instance/{challengeId}/{sourceId}"
        else:
            url = f"{cm_api_url}/challenge"

        try:        
            r = requests.get(url)
        except requests.exceptions.RequestException as e :
            return {'success': False, 'data':{
                    'message': f"An error occured while Plugins communication with Challmanager API : {e}",
            }}      

        # print(r.text)     

        return {'success': True, 'data': {
            'message': json.loads(r.text),
        }}

    @staticmethod
    @admins_only
    def patch():
        # retrieve all instance deployed by chall-manager
        cm_api_url = get_config("chall-manager:chall-manager_api_url")

        ## mandatory
        challengeId = request.args.get("challengeId") 
        sourceId = request.args.get("sourceId")

        if not challengeId or not sourceId:
            return {'success': False, 'data':{
                    'message': "Missing argument : challengeId or sourceId",
            }} 

        # TODO check user inputs

        url = f"{cm_api_url}/instance/{challengeId}/{sourceId}"

        try:        
            r = requests.patch(url)
        except requests.exceptions.RequestException as e :
            return {'success': False, 'data':{
                    'message': f"An error occured while Plugins communication with Challmanager API : {e}",
            }}       
            

        return {'success': True, 'data': {
            'message': json.loads(r.text),
        }}


    @staticmethod
    @admins_only
    def delete():
        # retrieve all instance deployed by chall-manager
        cm_api_url = get_config("chall-manager:chall-manager_api_url")

        ## mandatory
        challengeId = request.args.get("challengeId") 
        sourceId = request.args.get("sourceId")

        if not challengeId or not sourceId:
            return {'success': False, 'data':{
                    'message': "Missing argument : challengeId or sourceId",
            }} 

        # TODO check user inputs

        url = f"{cm_api_url}/instance/{challengeId}/{sourceId}"

        try:        
            r = requests.delete(url)
        except requests.exceptions.RequestException as e :
            return {'success': False, 'data':{
                    'message': f"An error occured while Plugins communication with Challmanager API : {e}",
            }}       
            

        return {'success': True, 'data': {
            'message': json.loads(r.text),
        }}


# Rsource to permit user to manager their instance 
@user_namespace.route("/instance")
class UserInstance(Resource):
    @staticmethod
    @authed_only
    # @challenge_visible
    # trigger while GET http://localhost:4000/api/v1/plugins/ctfd-chall-manager/instance?challengeId=1
    def get():
        # retrieve all instance deployed by chall-manager
        cm_api_url = get_config("chall-manager:chall-manager_api_url")
        
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

        # TODO check user inputs

        url = f"{cm_api_url}/instance/{challengeId}/{sourceId}"
        
        headers = {
            "Content-type": "application/json"
        }

        try:        
            r = requests.get(url, headers=headers)
        except requests.exceptions.RequestException as e :
            return {'success': False, 'data':{
                    'message': f"An error occured while Plugins communication with Challmanager API : {e}",
            }}       
            

        return {'success': True, 'data': {
            'message': json.loads(r.text),
        }}

    @staticmethod
    @authed_only
    # @challenge_visible
    # @frequency_limited
    def post():
        # retrieve all instance deployed by chall-manager
        cm_api_url = get_config("chall-manager:chall-manager_api_url")

        # check if Content-type is application/json
        if not request.is_json:
            return {'success': False, 'data':{
                    'message': "Content-type must be application/json",
            }}

        # retrieve infos provided by js
        data = request.get_json()
        payload = {}

        ## mandatory
        challengeId = data.get("challengeId") 
        
        # check userMode of CTFd
        sourceId = str(current_user.get_current_user().id)
        if get_config("user_mode") == "teams":
            sourceId = str(current_user.get_current_user().team_id)

        if not challengeId or not sourceId:
            return {'success': False, 'data':{
                    'message': "Missing argument : challengeId or sourceId",
            }} 

        # TODO check user inputs

        url = f"{cm_api_url}/instance"

        payload["challengeId"] = challengeId
        payload["sourceId"] = sourceId
        
        headers = {
            "Content-type": "application/json"
        }

        print(payload)

        try:        
            r = requests.post(url, data = json.dumps(payload), headers=headers)
        except requests.exceptions.RequestException as e :
            return {'success': False, 'data':{
                    'message': f"An error occured while Plugins communication with Challmanager API : {e}",
            }}       
            

        return {'success': True, 'data': {
            'message': json.loads(r.text),
        }}

    @staticmethod
    @authed_only
    # @challenge_visible
    # @frequency_limited
    def patch():
        # retrieve all instance deployed by chall-manager
        cm_api_url = get_config("chall-manager:chall-manager_api_url")

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

        # TODO check user inputs

        url = f"{cm_api_url}/instance/{challengeId}/{sourceId}"
        
        headers = {
            "Content-type": "application/json"
        }

        try:        
            r = requests.patch(url, headers=headers)
        except requests.exceptions.RequestException as e :
            return {'success': False, 'data':{
                    'message': f"An error occured while Plugins communication with Challmanager API : {e}",
            }}       
            

        return {'success': True, 'data': {
            'message': json.loads(r.text),
        }}


    @staticmethod
    @authed_only
    # @frequency_limited
    # @challenge_visible
    def delete():
        # retrieve all instance deployed by chall-manager
        cm_api_url = get_config("chall-manager:chall-manager_api_url")
       
        # check userMode of CTFd
        sourceId = str(current_user.get_current_user().id)
        if get_config("user_mode") == "teams":
            sourceId = str(current_user.get_current_user().team_id)

        ## mandatory
        challengeId = request.args.get("challengeId") 
        

        if not challengeId or not sourceId:
            return {'success': False, 'data':{
                    'message': "Missing argument : challengeId or sourceId",
            }} 

        # TODO check user inputs

        url = f"{cm_api_url}/instance/{challengeId}/{sourceId}"
        
        headers = {
            "Content-type": "application/json"
        }

        try:        
            r = requests.delete(url, headers=headers)
        except requests.exceptions.RequestException as e :
            return {'success': False, 'data':{
                    'message': f"An error occured while Plugins communication with Challmanager API : {e}",
            }}       
            

        return {'success': True, 'data': {
            'message': json.loads(r.text),
        }}



# Resource to permit admin to link scenario to challenges they create
@admin_namespace.route('/scenario')
class AdminScenario(Resource):
    
    @staticmethod
    @admins_only    
    def get():
        # retrieve chall-manager api url
        cm_api_url = get_config("chall-manager:chall-manager_api_url")

        # if challengeId is provided
        challengeId = request.args.get("challengeId")
        if challengeId:
            try: 
                int(challengeId)
            except:
                return {'success': False, 'data':{
                        'message': "Invalid synthax error: challengeId must be an integer",
                }}   

            url = f"{cm_api_url}/challenge/{challengeId}"
        else:
            url = f"{cm_api_url}/challenge"

        try:        
            r = requests.get(url)
        except requests.exceptions.RequestException as e :
            return {'success': False, 'data':{
                    'message': f"An error occured while Plugins communication with Challmanager API : {e}",
            }}        

        return {'success': True, 'data': {
                'message': json.loads(r.text),
        }}

    @staticmethod
    @admins_only
    # method to create scenario into chall-manager api. 
    # this is triggered while challenge creation
    def post():
        # retrieve chall-manager api url
        cm_api_url = get_config("chall-manager:chall-manager_api_url")

        # check if Content-type is application/json
        if not request.is_json:
            return {'success': False, 'data':{
                    'message': "Content-type must be application/json",
            }}          

        # retrieve infos provided by js
        data = request.get_json()
        payload = {}

        ## mandatory
        challengeId = data.get("challengeId") 
        scenarioId = data.get("scenarioId")
        
        if not challengeId or not scenarioId:
            return {'success': False, 'data':{
                    'message': "challengeId or scenarioId are missing",
            }} 
        
        # check if challengeId is an integer
        try: 
            int(challengeId)
            payload["id"] = challengeId
        except:
            return {'success': False, 'data':{
                    'message': "challengeId must be an integer",
            }} 
        
        # link the scenario with the challenge
        challenge = Challenges.query.filter_by(id=int(challengeId)).first()
        scenario = Files.query.filter_by(id=int(scenarioId)).first()

        challenge.scenario_id = scenarioId
        db.session.commit()


        # get base64 file located at full_scenario_location and send it to Chall-Manager
        # ex: b07afae94edec5d8a74c8d7b590feb63/deploy.zip
        full_scenario_location = os.path.join(os.getcwd(), "CTFd", "uploads", scenario.location)
        try: 
            with open(full_scenario_location, "rb") as f:  
                # TODO add hash checksum          
                encoded_string = base64.b64encode(f.read())
                payload["scenario"] = encoded_string.decode("utf-8")
        except:
            return {'success': False, 'data':{
                    'message': f"Error : file {full_scenario_location} cannot be founded on the server",
            }} 


        # get until or timeout of challengeId 
        until = challenge.until
        timeout = challenge.timeout

        # raise an error, or take until > timeout ?
        if until and timeout:
            return {'success': False, 'data':{
                    'message': "only one parameter must be provided: until or timeout",
            }} 

        # if until is not a date
        if until:
            try:
                datetime.fromisoformat(until)
                payload["until"] = f"{until}"
            except Exception as e:
                return {'success': False, 'data':{
                        'message': f"until invalid format with {until}: {e}",
                }} 

        if timeout:            
            try: 
                int(timeout)
            except Exception as e:
                return {'success': False, 'data':{
                        'message': f"timeout invalid format, must be XXXs, where XXX is digits, got {timeout}: {e}",
                }} 
        
            payload["timeout"] = f"{timeout}s" 
    
        # craft request
        headers = {
            "Content-Type": "application/json"
        }        

        # do request
        try:        
            r = requests.post(f"{cm_api_url}/challenge", data = json.dumps(payload), headers=headers)
        except requests.exceptions.RequestException as e :
            return {'success': False, 'data':{
                    'message': f"An error occured while Plugins communication with Challmanager API : {e}",
            }}      

        # TODO check if hash is valid

        return {'success': True, 'data': {
                'message': json.loads(r.text),
        }}

    @staticmethod
    @admins_only
    # method to edit params of a scenario
    # this is triggered while scenario is update by admins
    def patch():
        # retrieve chall-manager api url
        cm_api_url = get_config("chall-manager:chall-manager_api_url")

        # check if Content-type is application/json
        if not request.is_json:
            return {'success': False, 'data':{
                    'message': "Content-type must be application/json",
            }}

        # retrieve infos provided by js
        data = request.get_json()
        payload = {}

        # if challengeId is provided in parameters ?
        challengeId = request.args.get("challengeId")

        if not challengeId:
            return {'success': False, 'data': {
                'message': "Error: challengeId must be set ",
            }} 

        try: 
            int(challengeId)
        except:
            return {'success': False, 'data': {
                    'message': "Invalid Synthax Error: challengeId must be an integer",
            }} 

        challenge = Challenges.query.filter_by(id=int(challengeId)).first()

        # handle parameters provided
        if "scenarioId" in data.keys():
            # TODO delete previous
            prev_scenarioId = challenge.scenario_id
            #current_scenario = Files.query.filter_by(id=int(current_scenarioId)).first()
            print("previous = ", prev_scenarioId)

            # send new scenario to CM
            new_scenario = Files.query.filter_by(id=int(data["scenarioId"])).first()

            print("new_scenario = ", new_scenario)
       
            full_scenario_location = os.path.join(os.getcwd(), "CTFd", "uploads", new_scenario.location)
            try: 
                with open(full_scenario_location, "rb") as f:  
                    # TODO add hash checksum          
                    encoded_string = base64.b64encode(f.read())
                    payload["scenario"] = encoded_string.decode("utf-8")
                    
                    # TODO maybe replace this only if CM accept this archive ?
                    # replace by new scenario provided
                    challenge.scenario_id = data["scenarioId"]
                    db.session.commit()

            except Exception as e:
                return {'success': False, 'data':{
                        'message': f"Error : while open the file {full_scenario_location}, got {e}",
                }} 

        # get cm-mode 
        mode = challenge.mode

        # TODO check 
        if mode == "until":
            try:
                datetime.fromisoformat(challenge.until)
                payload["until"] = f"{challenge.until}"
            except Exception as e:
                return {'success': False, 'data':{
                        'message': f"until invalid format, got {challenge.until}: {e}",
                }} 

        elif mode == "timeout":            
            try: 
                int(challenge.timeout)
                payload["timeout"] = f"{challenge.timeout}s" 
            except Exception as e:
                return {'success': False, 'data':{
                        'message': f"timeout invalid format, must be XXXs, where XXX is digits, got {challenge.timeout}: {e}",
                }} 
        else:
            return {'success': False, 'data':{
                        'message': f"Unsupported mode , got {mode}",
                }} 
   
 
        # craft request
        headers = {
            "Content-Type": "application/json"
        }  

        url = f"{cm_api_url}/challenge/{challengeId}"  

        # print(payload)    

        # do request
        try:        
            r = requests.patch(url, data = json.dumps(payload), headers=headers)
        except requests.exceptions.RequestException as e :
            return {'success': False, 'data':{
                    'message': f"An error occured while Plugins communication with Challmanager API : {e}",
            }}    
        return {'success': True, 'data': {
                'message': json.loads(r.text),
        }}
        
    @staticmethod
    @admins_only
    # method to DELETE scenario
    # this is triggered while scenario is DELETE by admins
    def delete():
        # retrieve chall-manager api url
        cm_api_url = get_config("chall-manager:chall-manager_api_url")

        # check if Content-type is application/json
        if not request.is_json:
            return {'success': False, 'data':{
                    'message': "Content-type must be application/json",
            }}

        # retrieve infos provided by js
        data = request.get_json()
        payload = {}

        # if challengeId is provided in parameters ?
        challengeId = request.args.get("challengeId")

        if not challengeId:
            return {'success': False, 'data': {
                'message': "Error: challengeId must be set ",
            }} 

        try: 
            int(challengeId)
        except:
            return {'success': False, 'data': {
                    'message': "Invalid Synthax Error: challengeId must be an integer",
            }} 

        # craft request
        headers = {
            "Content-Type": "application/json"
        }  

        url = f"{cm_api_url}/challenge/{challengeId}"      

        # do request
        try:        
            r = requests.delete(url, data = json.dumps(payload), headers=headers)
        except requests.exceptions.RequestException as e :
            return {'success': False, 'data':{
                    'message': f"An error occured while Plugins communication with Challmanager API : {e}",
            }}    
        return {'success': True, 'data': {
                'message': json.loads(r.text),
        }}
        
    

        
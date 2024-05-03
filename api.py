from datetime import datetime

import requests
import json
import os
import base64
import datetime

from flask import request
from flask_restx import Namespace, Resource, abort

from CTFd.utils import get_config
from CTFd.utils import user as current_user
from CTFd.utils.decorators import admins_only, authed_only

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
        sourceId = data.get("sourceId")

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
        sourceId = data.get("sourceId")

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
    #@challenge_visible
    # trigger while GET http://localhost:4000/api/v1/plugins/ctfd-chall-manager/instance?user_id=1&challengeId=1
    def get():
        # retrieve all instance deployed by chall-manager
        cm_api_url = get_config("chall-manager:chall-manager_api_url")

        # check if Content-type is application/json
        if not request.is_json:
            return {'success': False, 'data':{
                    'message': "Content-type must be application/json",
            }}

        # retrieve infos provided by js
        data = request.get_json()
        
        ## mandatory
        challengeId = data.get("challengeId") 
        sourceId = str(current_user.get_current_user().id)

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
    #@challenge_visible
    #@frequency_limited
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
        sourceId = str(current_user.get_current_user().id)

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
    #@challenge_visible
    #@frequency_limited
    def patch():
        # retrieve all instance deployed by chall-manager
        cm_api_url = get_config("chall-manager:chall-manager_api_url")

        # check if Content-type is application/json
        if not request.is_json:
            return {'success': False, 'data':{
                    'message': "Content-type must be application/json",
            }}

        # retrieve infos provided by js
        data = request.get_json()
        
        ## mandatory
        challengeId = data.get("challengeId") 
        sourceId = str(current_user.get_current_user().id)

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
    #@frequency_limited
    def delete():
        # retrieve all instance deployed by chall-manager
        cm_api_url = get_config("chall-manager:chall-manager_api_url")

        # check if Content-type is application/json
        if not request.is_json:
            return {'success': False, 'data':{
                    'message': "Content-type must be application/json",
            }}

        # retrieve infos provided by js
        data = request.get_json()
        
        ## mandatory
        challengeId = data.get("challengeId") 
        sourceId = str(current_user.get_current_user().id)

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
        scenario_location = data.get("scenario_location")
        if not challengeId or not scenario_location:
            return {'success': False, 'data':{
                    'message': "challengeId or scenario_location are missing",
            }} 
        
        # check if challengeId is an integer
        try: 
            int(challengeId)
            payload["id"] = challengeId
        except:
            return {'success': False, 'data':{
                    'message': "challengeId must be an integer",
            }} 
        
        # get base64 file located at full_scenario_location
        # ex: b07afae94edec5d8a74c8d7b590feb63/deploy.zip
        full_scenario_location = os.path.join(os.getcwd(), "CTFd", "uploads", scenario_location)
        with open(full_scenario_location, "rb") as f:  
            # TODO add hash checksum          
            encoded_string = base64.b64encode(f.read())
            payload["scenario"] = encoded_string.decode("utf-8")


        ## optionnal
        until = data.get("until")
        timeout = data.get("timeout")

        # raise an error, or take until > timeout ?
        if until and timeout:
            return {'success': False, 'data':{
                    'message': "only one parameter must be provided: until or timeout",
            }} 

        # if until is not a date
        if until:
            try:
                datetime.datetime.strptime(until, '%Y-%m-%dT%H:%M')
                payload["until"] = f"{until}:00.000Z"
            except:
                return {'success': False, 'data':{
                        'message': "until invalid format, must be YYYY-MM-DDTHH:MM",
                }} 

        if timeout:
            # if timeout is not protobuf compliant
            if timeout[-1] != "s":
                return {'success': False, 'data':{
                        'message': "timeout invalid format, must be XXXs, where XXX is digits",
                }} 

            try: 
                int(timeout[0:len(timeout)-1])
            except:
                return {'success': False, 'data':{
                        'message': "timeout invalid format, must be XXXs, where XXX is digits",
                }} 
        
            payload["timeout"] = timeout 
    
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

        # craft request
        headers = {
            "Content-Type": "application/json"
        }  

        url = f"{cm_api_url}/challenge/{challengeId}"      

        # do request
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
        
    

        
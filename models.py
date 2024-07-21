from flask import Blueprint, request, current_app

from CTFd.models import ( # type: ignore
    Flags,
    Files,
    db,
)
from CTFd.plugins.challenges import BaseChallenge # type: ignore 
from CTFd.plugins.flags import FlagException, get_flag_class # type: ignore
from CTFd.utils import user as current_user # type: ignore
from CTFd.utils import get_config # type: ignore

from CTFd.plugins.dynamic_challenges import DynamicChallenge, DynamicValueChallenge # type: ignore
from .utils.challenge_store import create_challenge, delete_challenge, get_challenge, update_challenge
from .utils.instance_manager import delete_instance, get_instance

import os
import base64
import json


class DynamicIaCChallenge(DynamicChallenge):
    __mapper_args__ = {"polymorphic_identity": "dynamic_iac"}
    id = db.Column(
        db.Integer, db.ForeignKey("dynamic_challenge.id", ondelete="CASCADE"), primary_key=True
    )
    mana_cost = db.Column(db.Integer, default=0)
    until = db.Column(db.Text) # date
    timeout = db.Column(db.Text) # duration
    scope_global = db.Column(db.Boolean, default=False)

    scenario_id = db.Column(
        db.Integer, db.ForeignKey("files.id")
    )

    def __init__(self, *args, **kwargs):
        super(DynamicIaCChallenge, self).__init__(**kwargs)
        self.value = kwargs["initial"]


class DynamicIaCValueChallenge(BaseChallenge):
    id = "dynamic_iac"  # Unique identifier used to register challenges
    name = "dynamic_iac"  # Name of a challenge type
    templates = {  # Handlebars templates used for each aspect of challenge editing & viewing
        "create": "/plugins/ctfd-chall-manager/assets/create.html",
        "update": "/plugins/ctfd-chall-manager/assets/update.html",
        "view": "/plugins/ctfd-chall-manager/assets/view.html",
    }

    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/ctfd-chall-manager/assets/create.js",
        "update": "/plugins/ctfd-chall-manager/assets/update.js",
        "view": "/plugins/ctfd-chall-manager/assets/view.js",
    }
    # Route at which files are accessible. This must be registered using register_plugin_assets_directory()
    route = "/plugins/ctfd-chall-manager/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        "ctfd-chall-manager",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    challenge_model = DynamicIaCChallenge

    @classmethod
    def create(cls, request):
        """
        This method is used to process the challenge creation request.

        :param request:
        :return:
        """
        data = request.form or request.get_json()        
        if "scope_global" in data.keys():
            data["scope_global"] = data["scope_global"] == 'true' # convert string to boolean

        challenge = cls.challenge_model(**data)
        db.session.add(challenge)
        db.session.commit()


        # create challenge on chall-manager       
        ## retrieve file based on scenario id provided by user
        scenario = Files.query.filter_by(id=int(data['scenario_id'])).first()
        
        ## retrieve content of scenario_id to send at CM
        full_scenario_location = os.path.join(current_app.config.get("UPLOAD_FOLDER"), scenario.location)
        try: 
            with open(full_scenario_location, "rb") as f:         
                encoded_string = base64.b64encode(f.read())
                content = encoded_string.decode("utf-8")                
        except Exception as e:
            print(f"Plugin: An exception occured while open file {int(data['scenario_id'])}: {e}")  # TODO use logging

        # check optionnal configuration for dynamic_iac 
        # init optionnal configuration   
        optionnal = {}     
        if data['timeout'] != "":
            optionnal['timeout'] = f"{data['timeout']}s" # 500 -> 500s proto standard

        if data['until'] != "":
            optionnal['until'] = f"{data['until']}"


        # handle challenge creation on chall-manager
        try: 
            print(f"plugins debug len of content = {len(content)}")  # TODO use logging
            print(f"plugins debug content of optionnal = {optionnal}")  # TODO use logging
            create_challenge(int(challenge.id), content, optionnal)
        except Exception as e:
            print(f"Plugin: An exception occured while scending challenge {challenge.id} at CM: {e}")   # TODO use logging 
            print("debug: deleting challenge on CTFd due to an issue while creating it on CM")  # TODO use logging
            cls.delete(challenge)   
            return 

        # return CTFd Challenge if no error
        return challenge


    @classmethod
    def read(cls, challenge):
        """
        This method is in used to access the data of a challenge in a format processable by the front end.

        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        challenge = DynamicIaCChallenge.query.filter_by(id=challenge.id).first()
        data = {
            "id": challenge.id,
            "name": challenge.name,
            "value": challenge.value,
            "initial": challenge.initial,
            "decay": challenge.decay,
            "minimum": challenge.minimum,
            "function": challenge.function,
            "description": challenge.description,
            "connection_info": challenge.connection_info,
            "next_id": challenge.next_id,
            "category": challenge.category,
            "state": challenge.state,
            "max_attempts": challenge.max_attempts,
            "type": challenge.type,
            "mana_cost": challenge.mana_cost, # plugins specific
            "until": challenge.until, # plugins specific
            "timeout": challenge.timeout, # plugins specific
            "type_data": {
                "id": cls.id,
                "name": cls.name,
                "templates": cls.templates,
                "scripts": cls.scripts,
            },
        }
        return data

    @classmethod
    def update(cls, challenge, request):
        """
        This method is used to update the information associated with a challenge. This should be kept strictly to the
        Challenges table and any child tables.

        :param challenge:
        :param request:
        :return:
        """
        data = request.form or request.get_json()

        # Change Scope
        if "scope_global" in data.keys():
            data["scope_global"] = data["scope_global"] == 'true' # convert string to boolean
            
            try:
                r = get_challenge(challenge.id)
            except Exception as e:
                print(f"Error while patching the challenge : {e}")  # TODO use logging
                return
            
            instances = json.loads(r.text)["instances"]

            if data["scope_global"]: # if true
                for i in instances: 
                    if i['sourceId'] == 0:
                        continue
                    try:
                        delete_instance(challenge.id, i['sourceId'])
                    except Exception as e:
                        print(f"try to delete challenge {challenge.id} for source {i['sourceId']}, but do not exist before. SKIP")  # TODO use logging
                
            
            else:
                try:
                    delete_instance(challenge.id, 0)
                except Exception as e:
                    print(f"try to delete challenge {challenge.id} for source 0, but do not exist before. SKIP")  # TODO use logging
                

        # Workaround
        if "state" in data.keys() and len(data.keys()) == 1:
            setattr(challenge, "state", data["state"])
            return DynamicValueChallenge.calculate_value(challenge)

        # Patch Challenge on CTFd
        if "until" not in data.keys():
            setattr(challenge, "until", "")

        if "timeout" not in data.keys():
            setattr(challenge, "timeout", "")        
        
        # don't touch this
        for attr, value in data.items():
            # We need to set these to floats so that the next operations don't operate on strings
            if attr in ("initial", "minimum", "decay"):
                value = float(value)
            setattr(challenge, attr, value)

        # Patch Challenge on CM WIP
        optionnal = {}  
        if "timeout" in data.keys():
            optionnal['timeout'] = f"{data['timeout']}s" # 500 -> 500s proto standard

        if "until" in data.keys():
            optionnal['until'] = f"{data['until']}"
        
        if "updateStrategy" in data.keys():
            optionnal["updateStrategy"] = data["updateStrategy"]

        if "scenario_id" in data.keys():
            # retrieve file based on scenario id provided by user
            scenario = Files.query.filter_by(id=int(data['scenario_id'])).first()
        
            ## retrieve content of scenario_id to send at CM
            full_scenario_location = os.path.join(current_app.config.get("UPLOAD_FOLDER"), scenario.location)
            try: 
                with open(full_scenario_location, "rb") as f:         
                    encoded_string = base64.b64encode(f.read())
                    content = encoded_string.decode("utf-8")     
                    optionnal["scenario"] = content           
            except Exception as e:
                print(f"Plugin: An exception occured while open file {int(challenge['scenario_id'])}: {e}")  # TODO use logging

        # send updates to CM
        try: 
            update_challenge(challenge.id, optionnal)
        except Exception as e:
            print(f"Error while patching the challenge : {e}")  # TODO use logging


        return DynamicValueChallenge.calculate_value(challenge)

    @classmethod
    def delete(cls, challenge):
        """
        This method is used to delete the resources used by a challenge.

        :param challenge:
        :return:
        """
        
        # check if challenge exists on CM
        try: 
            get_challenge(challenge.id)
        except:
            print("ignore challenge")  # TODO use logging
        else:
            delete_challenge(challenge.id) # FIXME handle proprely exception of challenge not found in CM

        # then delete it on CTFd 
        super().delete(challenge)

    
    @classmethod
    def attempt(cls, challenge, request):
        """
        This method is used to check whether a given input is right or wrong. It does not make any changes and should
        return a boolean for correctness and a string to be shown to the user. It is also in charge of parsing the
        user's input from the request itself.

        :param challenge: The Challenge object from the database
        :param request: The request the user submitted
        :return: (boolean, string)
        """
        data = request.form or request.get_json()
        submission = data["submission"].strip() # user input

        # check userMode of CTFd
        sourceId = str(current_user.get_current_user().id)
        if get_config("user_mode") == "teams":
            sourceId = str(current_user.get_current_user().team_id)

        # CM Plugins extention
        if challenge.scope_global:
            sourceId = 0

        try:
            result = get_instance(challenge.id, sourceId)      
        except Exception as e:
            return False, f"Error occured, contact admins ! {e}"       
        
        # If the instance no longer exists
        if result.status_code != 200:
            return False, "Expired"
        
        data =  json.loads(result.text)

        # If the instance provided its flag
        if 'flag' in data.keys():
            cm_flag = data['flag']

            # if the flag is OK
            if len(cm_flag) == len(submission):
                result = 0
                for x, y in zip(cm_flag, submission):
                    result |= ord(x) ^ ord(y)            
                if result == 0:
                    return True, "Correct"

        # CTFd behavior
        flags = Flags.query.filter_by(challenge_id=challenge.id).all()
        for flag in flags:
            try:
                if get_flag_class(flag.type).compare(flag, submission):
                    return True, "Correct"
            except FlagException as e:
                return False, str(e)
        return False, "Incorrect"
    
    @classmethod
    def solve(cls, user, team, challenge, request):
        super().solve(user, team, challenge, request)

        DynamicValueChallenge.calculate_value(challenge)





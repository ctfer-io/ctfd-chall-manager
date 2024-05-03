from flask import Blueprint

from CTFd.models import Challenges, db
from CTFd.plugins import register_plugin_assets_directory
from CTFd.plugins.challenges import CHALLENGE_CLASSES, BaseChallenge
from CTFd.plugins.dynamic_challenges.decay import DECAY_FUNCTIONS, logarithmic
from CTFd.plugins.migrations import upgrade

from CTFd.plugins.dynamic_challenges import DynamicChallenge, DynamicValueChallenge

import requests


class DynamicIaCChallenge(DynamicChallenge):
    __mapper_args__ = {"polymorphic_identity": "dynamic_iac"}
    id = db.Column(
        db.Integer, db.ForeignKey("dynamic_challenge.id", ondelete="CASCADE"), primary_key=True
    )
    mana_cost = db.Column(db.Integer, default=0)

    # FIXME wrong type 
    until = db.Column(db.Text, default=0) # date
    timeout = db.Column(db.Text, default=0) # duration
    scenario = db.Column(db.Text, default=0) # file / base64 / blob ?

    def __init__(self, *args, **kwargs):
        super(DynamicIaCChallenge, self).__init__(**kwargs)
        # print("this is executed when dynamic_iac is created")
        # print(self._sa_instance_state)
        # print(vars(self))
        # requests.post(f"http://localhost:4000/api/v1/plugins/ctfd-chall-manager/admin/scenario?challenge_id={self.id}&scenario={self.scenario}")
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

        for attr, value in data.items():
            # We need to set these to floats so that the next operations don't operate on strings
            if attr in ("initial", "minimum", "decay"):
                value = float(value)
            setattr(challenge, attr, value)

        return DynamicValueChallenge.calculate_value(challenge)



    @classmethod
    def solve(cls, user, team, challenge, request):
        super().solve(user, team, challenge, request)

        DynamicValueChallenge.calculate_value(challenge)


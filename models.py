# pylint: disable=no-member
"""
This module contains DynamicIac models and CRUD methods.
The DynamicIaC type of challenge inherits from CTFd built-in Dynamic challenges

"""

import json

# CTFd imports
from CTFd.exceptions.challenges import (
    ChallengeCreateException,
    ChallengeUpdateException,
)
from CTFd.models import Flags, db
from CTFd.plugins.challenges import ChallengeResponse
from CTFd.plugins.challenges.logic import (
    challenge_attempt_all,
    challenge_attempt_any,
    challenge_attempt_team,
)
from CTFd.plugins.ctfd_chall_manager.utils.chall_manager_error import (
    ChallManagerException,
    ChallManagerPluginException,
)
from CTFd.plugins.ctfd_chall_manager.utils.challenge_store import (
    create_challenge,
    delete_challenge,
    get_challenge,
    update_challenge,
)
from CTFd.plugins.ctfd_chall_manager.utils.instance_manager import (
    delete_instance,
    get_instance,
)
from CTFd.plugins.ctfd_chall_manager.utils.logger import configure_logger
from CTFd.plugins.dynamic_challenges import DynamicChallenge, DynamicValueChallenge
from CTFd.utils import user as current_user
from CTFd.utils.config import is_teams_mode
from flask import Blueprint

logger = configure_logger(__name__)


class DynamicIaCChallenge(DynamicChallenge):
    """
    DynamicIaCChallenge defines the columns of the dynamic_iac challenge type.
    """

    __mapper_args__ = {"polymorphic_identity": "dynamic_iac"}
    id = db.Column(
        db.Integer,
        db.ForeignKey("dynamic_challenge.id", ondelete="CASCADE"),
        primary_key=True,
    )
    mana_cost = db.Column(db.Integer, default=0)
    until = db.Column(db.Text)  # date
    timeout = db.Column(db.Integer)
    shared = db.Column(db.Boolean, default=False)
    destroy_on_flag = db.Column(db.Boolean, default=False)
    additional = db.Column(db.JSON, default={})

    # Pooler feature
    min = db.Column(db.Integer, default=0)
    max = db.Column(db.Integer, default=0)

    scenario = db.Column(db.Text, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.value = kwargs["initial"]

    def __str__(self):
        return f"DynamicIaCChallenge(id={self.id}, \
            mana_cost={self.mana_cost}, \
            until={self.until}, \
            timeout={self.timeout}, \
            shared={self.shared}, \
            destroy_on_flag={self.destroy_on_flag})"


class DynamicIaCValueChallenge(DynamicValueChallenge):
    """
    DynamicIaCValueChallenge defines the function CRUD of a dynamic_iac challenge type.
    """

    id = "dynamic_iac"  # Unique identifier used to register challenges
    name = "dynamic_iac"  # Name of a challenge type
    templates = (
        {  # Handlebars templates used for each aspect of challenge editing & viewing
            "create": "/plugins/ctfd_chall_manager/assets/create.html",
            "update": "/plugins/ctfd_chall_manager/assets/update.html",
            "view": "/plugins/ctfd_chall_manager/assets/view.html",
        }
    )

    scripts = {  # Scripts that are loaded when a template is loaded
        "create": "/plugins/ctfd_chall_manager/assets/create.js",
        "update": "/plugins/ctfd_chall_manager/assets/update.js",
        "view": "/plugins/ctfd_chall_manager/assets/view.js",
    }
    # Route at which files are accessible.
    # This must be registered using register_plugin_assets_directory()
    route = "/plugins/ctfd_chall_manager/assets/"
    # Blueprint used to access the static_folder directory.
    blueprint = Blueprint(
        "ctfd_chall_manager",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    challenge_model = DynamicIaCChallenge

    @classmethod
    def create(cls, request):  # pylint: disable=too-many-branches,too-many-statements
        """
        This method is used to process the challenge creation request.

        :param request:
        :return:
        """
        logger.debug("creating challenge on CTFd")
        data = request.form or request.get_json()

        try:
            data = prepare_ctfd_database(data)
        except ChallManagerPluginException as e:
            raise ChallengeCreateException from e

        challenge = cls.challenge_model(**data)
        db.session.add(challenge)
        db.session.commit()

        logger.info("challenge %s created successfully on CTFd", challenge.id)

        # init params configuration
        params = prepare_chall_manager_payload(data)

        # handle challenge creation on chall-manager
        try:
            logger.debug("creating challenge %s on CM", challenge.id)
            create_challenge(int(challenge.id), **params)
            logger.info("challenge %s created successfully on CM", challenge.id)
        except ChallManagerException as e:
            logger.error(
                "an exception occurred while sending challenge %s to CM: %s",
                challenge.id,
                e,
            )
            logger.debug(
                "deleting challenge on CTFd due to an issue while creating it on CM"
            )
            cls.delete(challenge)
            logger.info("challenge %s deleted sucessfully", challenge.id)
            raise ChallengeCreateException(e.message) from e

        # return CTFd Challenge if no error
        return challenge

    @classmethod
    def read(cls, challenge):
        """
        This method is used to access the data of a challenge
        in a format processable by the front end.

        :param challenge:
        :return: Challenge object, data dictionary to be returned to the user
        """
        challenge = DynamicIaCChallenge.query.filter_by(id=challenge.id).first()
        data = super().read(challenge)
        data.update(
            {
                "mana_cost": challenge.mana_cost,
                "until": challenge.until,
                "timeout": challenge.timeout,
                "shared": challenge.shared,
                "destroy_on_flag": challenge.destroy_on_flag,
                "scenario": challenge.scenario,
                "additional": (
                    challenge.additional if current_user.is_admin() else {}
                ),  # do not display additional for all user, can contains secrets
                "min": challenge.min,
                "max": challenge.max,
            }
        )

        return data

    @classmethod
    def update(
        cls, challenge, request
    ):  # pylint: disable=too-many-branches,too-many-statements
        """
        This method is used to update the information associated with a challenge.
        This should be kept strictly to the Challenges table and any child tables.

        :param challenge:
        :param request:
        :return:
        """
        data = request.form or request.get_json()

        # Workaround
        if "state" in data.keys() and len(data.keys()) == 1:
            setattr(challenge, "state", data["state"])
            return super().calculate_value(challenge)

        try:
            data = prepare_ctfd_database(data)
        except ChallManagerPluginException as e:
            raise ChallengeUpdateException from e

        # update on database
        for attr, value in data.items():
            # We need to set these to floats so that the next operations don't operate on strings
            if attr in ("initial", "minimum", "decay"):
                value = float(value)
            setattr(challenge, attr, value)  # update on database

        # Patch Challenge on Chall-Manager API
        params = prepare_chall_manager_payload(data)

        # send updates to CM
        try:
            update_challenge(challenge.id, **params)
        except ChallManagerException as e:
            logger.error("error while patching the challenge: %s", e)
            raise ChallengeUpdateException(e.message) from e

        return super().calculate_value(challenge)

    @classmethod
    def delete(cls, challenge):
        """
        This method is used to delete the resources used by a challenge.

        :param challenge:raise
        :return:
        """

        # check if challenge exists on CM
        try:
            get_challenge(challenge.id)
        except ChallManagerException as e:
            logger.info(
                "ignoring challenge %s as it does not exist on CM: %s", challenge.id, e
            )
        else:
            try:
                logger.debug("deleting challenge %s on CM", challenge.id)
                delete_challenge(challenge.id)
                logger.info("challenge %s on CM delete successfully", challenge.id)
            except ChallManagerException as e:
                logger.error(
                    "failed to delete challenge %s from CM: %s", challenge.id, e
                )

        # then delete it on CTFd
        logger.debug("deleting challenge %s on CTFd", challenge.id)
        super().delete(challenge)
        logger.info("challenge %s on CTFd deleted successfully", challenge.id)

    @classmethod
    def attempt(
        cls, challenge, request
    ):  # pylint: disable=too-many-locals,too-many-branches,too-many-statements
        """
        This method is used to check whether a given input is right or wrong.
        It does not make any changes and should return a boolean for correctness
        and a string to be shown to the user. It is also in charge of parsing the
        user's input from the request itself.

        :param challenge: The Challenge object from the database
        :param request: The request the user submitted
        :return: (boolean, string)
        """
        data = request.form or request.get_json()
        submission = data["submission"].strip()  # user input

        # retrieve source_id
        user_id = int(current_user.get_current_user().id)
        source_id = user_id
        if is_teams_mode():
            team_id = int(current_user.get_current_user().team_id)
            source_id = team_id
        if challenge.shared:
            source_id = 0

        logger.info(
            "submission of user %s as source %s for challenge %s : %s",
            user_id,
            source_id,
            challenge.id,
            submission,
        )

        # checks that the instance is alive
        try:
            data = get_instance(challenge.id, source_id)
        except ChallManagerException as e:
            logger.error("error occurred while getting instance: %s", e)
            if e.http_code == 404:
                logger.debug(
                    "instance for source_id %s and challenge_id %s no longer exists",
                    source_id,
                    challenge.id,
                )
                logger.info(
                    "invalid submission due to expired instance for challenge %s source %s",
                    challenge.id,
                    source_id,
                )
                return ChallengeResponse(
                    status="incorrect",
                    message="Expired (the instance must be running to submit)",
                )

            return ChallengeResponse(
                status="incorrect", message="Error occurred, contact admins!"
            )

        flags = Flags.query.filter_by(challenge_id=challenge.id).all()
        logger.debug("check if flags is provided by CM")

        # Chall-Manager feature since v0.6.0
        if "flags" in data.keys():
            cm_flags = list(data["flags"])
            logger.debug(
                "flags provided by CM for challenge %s source %s: %s",
                challenge.id,
                source_id,
                cm_flags,
            )

            for idx, flag in enumerate(cm_flags):
                # the flag id from CM will be -1, -2, ...
                # in fact, we just want to avoid collision with existing CTFd Flag id here
                generated_id = int(-(idx + 1))

                # create Flags object to ease compare method
                # this object is NOT stored in database.
                ctfd_cm_flag = Flags(
                    challenge_id=challenge.id,
                    type="static",
                    content=flag,
                    id=generated_id,
                )
                flags.append(ctfd_cm_flag)

        # CTFd behavior
        # https://github.com/CTFd/CTFd/blob/3.8.0/CTFd/plugins/challenges/__init__.py#L131
        if challenge.logic == "all":
            return challenge_attempt_all(submission, challenge, flags)
        if challenge.logic == "team":
            return challenge_attempt_team(submission, challenge, flags)

        return challenge_attempt_any(submission, challenge, flags)

    @classmethod
    def solve(cls, user, team, challenge, request):
        super().solve(user, team, challenge, request)

        # retrieve source_id
        user_id = int(current_user.get_current_user().id)
        source_id = user_id
        if is_teams_mode():
            team_id = int(current_user.get_current_user().team_id)
            source_id = team_id
        if challenge.shared:
            source_id = 0

        if challenge.destroy_on_flag:
            logger.info(
                "challenge %s solved, destroy instance for source %s",
                challenge.id,
                source_id,
            )
            try:
                delete_instance(challenge.id, source_id)
            except ChallManagerException as e:
                logger.warning(
                    "failed to delete challenge %s for source %s, \
                    instance may not exist got %s",
                    challenge.id,
                    source_id,
                    e,
                )


def convert_to_boolean(value):
    """
    Check if the value is a string and convert it to boolean
    if it matches "true" or "false" (case-insensitive)
    """
    if isinstance(value, str):
        value_lower = value.strip().lower()
        if value_lower == "true":
            return True
        return False
    # If the value is already a boolean or doesn't match a boolean string, return it as is
    return value


def prepare_ctfd_database(data) -> dict | ChallManagerPluginException:
    """
    Lint form attributes for the challenge creation.
    Fallbacks to the same default values as the database
    to prevent inconsistencies with chall-manager API.
    """

    defaults = {
        # integer
        "mana_cost": 0,
        "min": 0,
        "max": 0,
        # boolean
        "shared": False,
        "destroy_on_flag": False,
        # other
        "additional": {},
        "until": None,
        "timeout": None,
    }
    # Integer
    for k in ["min", "max", "mana_cost"]:
        if k in data.keys():
            try:
                data[k] = int(data[k]) if data[k] != "" else defaults[k]
            except ValueError as e:
                logger.error("%s cannot be convert into int, got %s", k, data[k])
                raise ChallManagerPluginException(
                    f"{k} cannot be convert into int, got {data[k]}"
                ) from e

    # Boolean
    for k in ["shared", "destroy_on_flag"]:
        if k in data.keys():
            data[k] = convert_to_boolean(data[k]) if data[k] != "" else defaults[k]

    # Other
    for k in ["until", "timeout"]:
        if k in data.keys():
            data[k] = data[k] if data[k] != "" else defaults[k]

    # convert string into dict in CTFd
    if "additional" in data.keys():
        if isinstance(data["additional"], str):
            try:
                # Attempt to parse the string as JSON
                data["additional"] = json.loads(data["additional"])
            except json.JSONDecodeError as e:
                logger.error(
                    "error while decoding additional configuration, found %s : %s",
                    data["additional"],
                    e,
                )
                raise ChallManagerPluginException(
                    f"error while decoding additional configuration, \
                    found {data['additional']}"
                ) from e
        elif not isinstance(data["additional"], dict):
            logger.error(
                "error while decoding additional configuration, found %s : %s",
                data["additional"],
                e,
            )
            raise ChallManagerPluginException(
                f"error while decoding additional configuration,\
                found {data['additional']}"
            ) from e

    return data


def prepare_chall_manager_payload(data) -> dict:
    """
    Build chall-manager API payload with timeout specific protobuf format
    """
    payload = {}
    for key in list(data.keys()):
        if key in ["additional", "until", "scenario", "min", "max", "updateStrategy"]:
            payload[key] = data[key]

    # timeout is protobuf format, store as integer in database
    if "timeout" in data.keys():
        payload["timeout"] = f"{data['timeout']}s"
        if data["timeout"] in (None, ""):
            payload["timeout"] = None

    return payload

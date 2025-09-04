# pylint: disable=no-member
"""
This module contains DynamicIac models and CRUD methods.
The DynamicIaC type of challenge herits from CTFd built-in Dynamic challenges

"""

import json

from flask import Blueprint

# CTFd imports
from CTFd.exceptions.challenges import (
    ChallengeCreateException,
    ChallengeUpdateException,
)
from CTFd.models import (
    Flags,
    db,
)
from CTFd.plugins.flags import FlagException, get_flag_class
from CTFd.utils import user as current_user
from CTFd.utils.config import is_teams_mode
from CTFd.plugins.dynamic_challenges import DynamicChallenge, DynamicValueChallenge

# Plugins specific imports
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

logger = configure_logger(__name__)


class DynamicIaCChallenge(DynamicChallenge):
    """
    DynamicIaCChallenge defines the colums of the dynamic_iac challenge type.
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
    additional = db.Column(db.JSON)

    # Pooler feature
    min = db.Column(db.Integer, default=0)
    max = db.Column(db.Integer, default=0)

    scenario = db.Column(db.Text)

    def __init__(self, *args, **kwargs):
        super(DynamicIaCChallenge, self).__init__(**kwargs)
        self.value = kwargs["initial"]

    def __str__(self):
        return f"DynamicIaCChallenge(id={self.id}, mana_cost={self.mana_cost}, until={self.until}, timeout={self.timeout}, shared={self.shared}, destroy_on_flag={self.destroy_on_flag})"


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
    def create(cls, request):
        """
        This method is used to process the challenge creation request.

        :param request:
        :return:
        """
        logger.debug("creating challenge on CTFd")
        data = request.form or request.get_json()

        # lint the plugin attributes by removing empty values
        for key in list(data.keys()):  # use list(data.keys()) to prevent RuntimeError
            if (
                key
                in [
                    "mana_cost",
                    "until",
                    "timeout",
                    "shared",
                    "destroy_on_flag",
                    "scenario",
                    "min",
                    "max",
                ]
                and data[key] == ""
            ):
                data.pop(key)

        # convert string value to boolean
        if "shared" in data.keys():
            data["shared"] = convert_to_boolean(data["shared"])

        if "destroy_on_flag" in data.keys():
            data["destroy_on_flag"] = convert_to_boolean(data["destroy_on_flag"])

        if "scenario" not in data.keys():
            logger.error("missing mandatory value in challenge creation")
            raise ChallengeCreateException(
                "missing mandatory value in challenge creation"
            )

        if "min" in data.keys():
            try:
                data["min"] = int(data["min"])
            except ValueError as e:
                logger.error("min cannot be convert into int, got %s", data["min"])
                raise ChallengeCreateException(
                    f"min cannot be convert into int, got {data['min']}"
                ) from e

        if "max" in data.keys():
            try:
                data["max"] = int(data["max"])
            except ValueError as e:
                logger.error("max cannot be convert into int, got %s", data["max"])
                raise ChallengeCreateException(
                    f"max cannot be convert into int, got {data['max']}"
                ) from e

        # convert string into dict in CTFd
        if "additional" in data.keys():
            if isinstance(data["additional"], str):
                try:
                    # Attempt to parse the string as JSON
                    data["additional"] = json.loads(data["additional"])
                except json.JSONDecodeError as e:
                    logger.error(
                        "error while decoding additional configuration, found %s: %s",
                        data["additional"],
                        e,
                    )
                    raise ChallengeCreateException(
                        f"error while decoding additional configuration, found {data['additional']}"
                    ) from e
            elif not isinstance(data["additional"], dict):
                raise ChallengeCreateException(
                    f"error while decoding additional configuration, found {data['additional']}"
                )

        challenge = cls.challenge_model(**data)
        db.session.add(challenge)
        db.session.commit()

        logger.info("challenge %s created successfully on CTFd", challenge.id)

        # check params configuration for dynamic_iac
        # init params configuration
        params = {
            "scenario": challenge.scenario,
        }
        if "timeout" in data.keys():
            if data["timeout"] is None:
                params["timeout"] = (
                    None  # must explicitely define it as we append a "s" elseway
                )
            else:
                params["timeout"] = f"{data['timeout']}s"  # 500 -> 500s proto standard

        if "until" in data.keys():
            if data["until"] is None:
                params["until"] = None
            else:
                params["until"] = f"{data['until']}"

        if "min" in data.keys():
            try:
                params["min"] = int(data["min"])
            except ValueError:
                logger.warning("min cannot be convert into int, got %s", data["min"])

        if "max" in data.keys():
            try:
                params["max"] = int(data["max"])
            except ValueError:
                logger.warning("min cannot be convert into int, got %s", data["max"])

        if "additional" in data.keys():
            logger.debug(
                "retrieving additional configuration for challenge %s : %s",
                challenge.id,
                data["additional"],
            )
            params["additional"] = data["additional"]

        # handle challenge creation on chall-manager
        try:
            logger.debug("creating challenge %s on CM", challenge.id)
            create_challenge(int(challenge.id), params)
            logger.info("challenge %s created successfully on CM", challenge.id)
        except Exception as e:
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
            raise ChallengeCreateException(
                f"an exception occurred while sending challenge {challenge.id} to CM: {e}"
            ) from e

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
    def update(cls, challenge, request):
        """
        This method is used to update the information associated with a challenge.
        This should be kept strictly to the Challenges table and any child tables.

        :param challenge:
        :param request:
        :return:
        """
        data = request.form or request.get_json()

        # lint the plugin attributes by removing empty values
        for key in list(data.keys()):  # use list(data.keys()) to prevent RuntimeError
            if (
                key
                in [
                    "mana_cost",
                    "until",
                    "timeout",
                    "shared",
                    "destroy_on_flag",
                    "scenario",
                    "min",
                    "max",
                ]
                and data[key] == ""
            ):
                data.pop(key)

        if "shared" in data.keys():
            data["shared"] = convert_to_boolean(data["shared"])

        # Update the destroy on flag boolean
        if "destroy_on_flag" in data.keys():
            data["destroy_on_flag"] = convert_to_boolean(data["destroy_on_flag"])

        # Workaround
        if "state" in data.keys() and len(data.keys()) == 1:
            setattr(challenge, "state", data["state"])
            return super().calculate_value(challenge)

        # Patch Challenge on CTFd
        params = {}
        if "until" not in data.keys():
            params["until"] = None
            setattr(challenge, "until", None)

        if "timeout" not in data.keys():
            params["timeout"] = None
            setattr(challenge, "timeout", None)

        # convert string into dict in CTFd
        if "additional" in data.keys():
            if isinstance(data["additional"], str):
                try:
                    # Attempt to parse the string as JSON
                    data["additional"] = json.loads(data["additional"])
                except json.JSONDecodeError as e:
                    logger.error(
                        f"An exception occurred while decoding additional configuration, found {data['additional']} : {e}"
                    )
                    raise ChallengeUpdateException(
                        f"An exception occurred while decoding additional configuration, found {data['additional']} : {e}"
                    )
            elif not isinstance(data["additional"], dict):
                raise ChallengeUpdateException(
                    f"An exception occurred while decoding additional configuration, found {data['additional']}"
                )

        # don't touch this
        for attr, value in data.items():
            # We need to set these to floats so that the next operations don't operate on strings
            if attr in ("initial", "minimum", "decay"):
                value = float(value)
            setattr(challenge, attr, value)

        # Patch Challenge on CM
        if "timeout" in data.keys():
            if data["timeout"] is None:
                params["timeout"] = (
                    None  # must explicitely define it as we append a "s" elseway
                )
            else:
                params["timeout"] = f"{data['timeout']}s"  # 500 -> 500s proto standard

        if "until" in data.keys():
            if data["until"] is None:
                params["until"] = None
            else:
                params["until"] = f"{data['until']}"

        if "additional" in data.keys():
            logger.debug(
                "retrieving additional configuration for challenge %s : %s",
                challenge.id,
                data["additional"],
            )
            params["additional"] = data["additional"]

        if "updateStrategy" in data.keys():
            params["updateStrategy"] = data["updateStrategy"]

        if "scenario" in data.keys():
            params["scenario"] = data["scenario"]

        if "min" in data.keys():
            params["min"] = data["min"]

        if "max" in data.keys():
            params["max"] = data["max"]

        # send updates to CM
        try:
            update_challenge(challenge.id, params)
        except Exception as e:
            logger.error("error while patching the challenge: %s", e)
            raise ChallengeUpdateException("error while patching the challenge") from e

        return super().calculate_value(challenge)

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
        except Exception as e:
            logger.info(
                "ignoring challenge %s as it does not exist on CM: %s", challenge.id, e
            )
        else:
            try:
                logger.debug("deleting challenge %s on CM", challenge.id)
                delete_challenge(challenge.id)
                logger.info("challenge %s on CM delete successfully", challenge.id)
            except Exception as e:
                logger.error(
                    "failed to delete challenge %s from CM: %s", challenge.id, e
                )

        # then delete it on CTFd
        logger.debug("deleting challenge %s on CTFd", challenge.id)
        super().delete(challenge)
        logger.info("challenge %s on CTFd deleted successfully", challenge.id)

    @classmethod
    def attempt(cls, challenge, request):
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

        # check userMode of CTFd
        user_id = int(current_user.get_current_user().id)
        source_id = user_id
        if is_teams_mode():
            team_id = int(current_user.get_current_user().team_id)
            source_id = team_id

        # CM Plugins extension
        if challenge.shared:
            source_id = 0

        logger.info(
            "submission of user %s as source %s for challenge %s : %s",
            user_id,
            source_id,
            challenge.id,
            submission,
        )

        try:
            result = get_instance(challenge.id, source_id)
        except Exception as e:
            logger.error("error occurred while getting instance: %s", e)
            return False, "error occurred, contact admins!"

        data = json.loads(result.text)

        # If the instance no longer exists
        if data["since"] == "":
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
            return False, "Expired (the instance must be running to submit)"

        logger.debug("check if flag is provided by CM")
        # If the instance provided its flag
        if "flag" in data.keys():
            cm_flag = data["flag"]
            logger.debug(
                "flag provided by CM for challenge %s source %s: %s",
                challenge.id,
                source_id,
                cm_flag,
            )

            # if the flag is OK
            if len(cm_flag) == len(submission):
                result = 0
                for x, y in zip(cm_flag, submission):
                    result |= ord(x) ^ ord(y)
                if result == 0:
                    logger.info(
                        "valid submission for CM flag: challenge %s source %s",
                        challenge.id,
                        source_id,
                    )

                    msg = "Correct"

                    if challenge.destroy_on_flag:
                        logger.info("destroy the instance")
                        try:
                            delete_instance(challenge.id, source_id)
                            msg = "Correct, your instance has been destroyed"
                        except Exception:
                            logger.warning(
                                "failed to delete challenge %s for source %s, instance may not exist",
                                challenge.id,
                                source_id,
                            )

                    return True, msg

            logger.info(
                "invalid submission for CM flag: challenge %s source %s",
                challenge.id,
                source_id,
            )

        # CTFd behavior
        logger.debug(
            "try the CTFd flag for challenge_id %s and source_id %s",
            challenge.id,
            source_id,
        )
        flags = Flags.query.filter_by(challenge_id=challenge.id).all()
        for flag in flags:
            try:
                if get_flag_class(flag.type).compare(flag, submission):
                    logger.info(
                        "valid submission for CTFd flag: challenge %s source_id %s",
                        challenge.id,
                        source_id,
                    )

                    msg = "Correct"

                    if challenge.destroy_on_flag:
                        logger.info("destroy the instance")
                        try:
                            delete_instance(challenge.id, source_id)
                            msg = "Correct, your instance has been destroyed"
                        except Exception:
                            logger.warning(
                                "failed to delete challenge %s for source %s, instance may not exist",
                                challenge.id,
                                source_id,
                            )

                    return True, msg
            except FlagException as e:
                logger.error("FlagException: %s", e)
                return False, str(e)
        logger.info(
            "invalid submission for CTFd flag: challenge %s source %s",
            challenge.id,
            source_id,
        )
        return False, "Incorrect"


def convert_to_boolean(value):
    """
    Check if the value is a string and convert it to boolean
    if it matches "true" or "false" (case-insensitive)
    """
    if isinstance(value, str):
        value_lower = value.strip().lower()
        if value_lower == "true":
            return True
        elif value_lower == "false":
            return False
    # If the value is already a boolean or doesn't match a boolean string, return it as is
    return value

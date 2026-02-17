# pylint: disable=no-member
"""
module for dynamic infrastructure-as-code (iac) challenge models and crud methods.
inherits from ctfd's built-in dynamic challenges.
"""

import json
from flask import Blueprint
from CTFd.models import Flags, db
from CTFd.plugins.challenges import ChallengeResponse
from CTFd.plugins.challenges.logic import (
    challenge_attempt_all,
    challenge_attempt_any,
    challenge_attempt_team,
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
from CTFd.exceptions.challenges import (
    ChallengeCreateException,
    ChallengeUpdateException,
)
from CTFd.plugins.ctfd_chall_manager.utils.chall_manager_error import (
    ChallManagerException,
    InternalPluginException,
)

logger = configure_logger(__name__)


# --- models ---
class DynamicIaCChallenge(DynamicChallenge):
    """defines the columns specific to the dynamic_iac challenge type."""

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
    min = db.Column(db.Integer, default=0)
    max = db.Column(db.Integer, default=0)
    scenario = db.Column(db.Text, nullable=False)

    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)
        self.value = kwargs["initial"]

    def __str__(self):
        return (
            f"dynamiciacchallenge(id={self.id}, mana_cost={self.mana_cost}, "
            f"until={self.until}, timeout={self.timeout}, shared={self.shared}, "
            f"destroy_on_flag={self.destroy_on_flag})"
        )


# --- crud ---
class DynamicIaCValueChallenge(DynamicValueChallenge):
    """handles crud operations for the dynamic_iac challenge type."""

    id = "dynamic_iac"
    name = "dynamic_iac"
    templates = {
        "create": "/plugins/ctfd_chall_manager/assets/create.html",
        "update": "/plugins/ctfd_chall_manager/assets/update.html",
        "view": "/plugins/ctfd_chall_manager/assets/view.html",
    }
    scripts = {
        "create": "/plugins/ctfd_chall_manager/assets/create.js",
        "update": "/plugins/ctfd_chall_manager/assets/update.js",
        "view": "/plugins/ctfd_chall_manager/assets/view.js",
    }
    route = "/plugins/ctfd_chall_manager/assets/"
    blueprint = Blueprint(
        "ctfd_chall_manager",
        __name__,
        template_folder="templates",
        static_folder="assets",
    )
    challenge_model = DynamicIaCChallenge

    @classmethod
    def _convert_booleans(cls, data, keys: list) -> InternalPluginException:
        """converts values to booleans for specified keys."""
        for key in keys:
            if key in data:
                if isinstance(data[key], str):
                    data[key] = data[key].strip().lower() == "true"
                try:
                    data[key] = bool(data[key])
                except (TypeError, ValueError) as e:
                    raise InternalPluginException from e

    @classmethod
    def _convert_integers(cls, data, keys: list) -> InternalPluginException:
        """converts values to integers for specified keys."""
        for key in keys:
            if key in data:
                try:
                    data[key] = int(data[key])
                except Exception as e:
                    raise InternalPluginException from e

    @classmethod
    def _convert_json(cls, data, keys: list) -> InternalPluginException:
        """converts a value to json for the specified key."""
        for key in keys:
            if key in data:
                if isinstance(data[key], str):
                    try:
                        return json.loads(data[key])
                    except json.JSONDecodeError as e:
                        logger.error("failed to decode json: %s", e)
                        raise InternalPluginException(
                            f"failed to decode json: {data[key]}"
                        ) from e
                if not isinstance(data[key], dict):
                    raise InternalPluginException(
                        f"expected dict or json string, got {data[key]}"
                    )

                # if already dict, do nothing

    @classmethod
    def _prepare_cm_params(cls, data, keys, timeout_key=None):
        """prepares parameters for the chall-manager api."""
        params = {}
        for key in keys:
            if key in data:
                params[key] = data[key]
        if timeout_key and timeout_key in data and data[timeout_key] is not None:
            params[timeout_key] = f"{data[timeout_key]}s"
        return params

    @classmethod
    def create(cls, request):
        """creates a dynamic_iac challenge."""
        logger.debug("creating challenge on ctfd")
        data = request.form or request.get_json()

        cls._convert_booleans(data, ["shared", "destroy_on_flag"])
        cls._convert_json(data, "additional")
        cls._convert_integers(data, ["min", "max", "mana_cost", "timeout"])

        if "scenario" not in data:
            logger.error("missing mandatory 'scenario' in challenge creation")
            raise ChallengeCreateException("missing mandatory 'scenario'")

        # create challenge in database
        challenge = cls.challenge_model(**data)
        db.session.add(challenge)
        db.session.commit()
        logger.info("challenge %s created on ctfd", challenge.id)

        # prepare parameters for chall-manager
        params = cls._prepare_cm_params(
            data,
            keys=[
                "additional",
                "until",
                "timeout",
                "scenario",
                "min",
                "max",
            ],
            timeout_key="timeout",
        )
        params["scenario"] = challenge.scenario

        # create challenge on chall-manager
        try:
            logger.debug("creating challenge %s on cm", challenge.id)
            create_challenge(int(challenge.id), **params)
            logger.info("challenge %s created on cm", challenge.id)
        except (ValueError, ChallManagerException) as e:
            logger.error("failed to create challenge %s on cm: %s", challenge.id, e)
            cls.delete(challenge)
            raise ChallengeCreateException(
                f"failed to create challenge on cm: {e}"
            ) from e

        return challenge

    @classmethod
    def read(cls, challenge):
        """reads challenge data for the frontend."""
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
                "additional": challenge.additional if current_user.is_admin() else {},
                "min": challenge.min,
                "max": challenge.max,
            }
        )
        return data

    @classmethod
    def update(cls, challenge, request):
        """updates a dynamic_iac challenge."""
        data = request.form or request.get_json()

        # convert data
        cls._convert_booleans(data, ["shared", "destroy_on_flag"])
        cls._convert_json(data, "additional")
        cls._convert_integers(data, ["min", "max", "mana_cost", "timeout"])

        # special case: only updating state
        if "state" in data and len(data) == 1:
            setattr(challenge, "state", data["state"])
            return super().calculate_value(challenge)

        # update challenge attributes in database
        for attr, value in data.items():
            if attr in ("initial", "minimum", "decay"):
                value = float(value)
            setattr(challenge, attr, value)

        # prepare parameters for chall-manager
        params = cls._prepare_cm_params(
            data,
            keys=[
                "additional",
                "until",
                "timeout",
                "scenario",
                "min",
                "max",
                "updateStrategy",
            ],
            timeout_key="timeout",
        )

        # update challenge on chall-manager
        try:
            update_challenge(challenge.id, **params)
        except Exception as e:
            logger.error("failed to update challenge %s on cm: %s", challenge.id, e)
            raise ChallengeUpdateException(
                f"failed to update challenge on cm: {e}"
            ) from e

        return super().calculate_value(challenge)

    @classmethod
    def delete(cls, challenge):
        """deletes a dynamic_iac challenge."""
        try:
            get_challenge(challenge.id)
        except ChallManagerException:
            logger.info("challenge %s does not exist on cm, skipping", challenge.id)
        else:
            try:
                delete_challenge(challenge.id)
                logger.info("challenge %s deleted from cm", challenge.id)
            except ChallManagerException as e:
                logger.error(
                    "failed to delete challenge %s from cm: %s", challenge.id, e
                )

        super().delete(challenge)
        logger.info("challenge %s deleted from ctfd", challenge.id)

    @classmethod
    def attempt(cls, challenge, request):
        """checks if a submission is correct."""
        data = request.form or request.get_json()
        submission = data["submission"].strip()

        # get source_id
        user_id = int(current_user.get_current_user().id)
        source_id = user_id
        if is_teams_mode():
            source_id = int(current_user.get_current_user().team_id)
        if challenge.shared:
            source_id = 0

        logger.info(
            "submission for challenge %s by user %s (source %s): %s",
            challenge.id,
            user_id,
            source_id,
            submission,
        )

        # check if instance exists
        try:
            instance = get_instance(challenge.id, source_id)
        except ChallManagerException as e:
            logger.error("failed to get instance: %s", e)
            return ChallengeResponse(
                status="incorrect",
                message="error occurred, contact admins!",
            )

        if instance["since"] is None:
            logger.info(
                "instance for challenge %s (source %s) is expired",
                challenge.id,
                source_id,
            )
            return ChallengeResponse(
                status="incorrect",
                message="expired (the instance must be running to submit)",
            )

        # get flags
        flags = Flags.query.filter_by(challenge_id=challenge.id).all()
        if "flags" in instance:
            for idx, flag in enumerate(instance["flags"]):
                flags.append(
                    Flags(
                        challenge_id=challenge.id,
                        type="static",
                        content=flag,
                        id=-(idx + 1),
                    )
                )

        # check flags logic
        if challenge.logic == "all":
            return challenge_attempt_all(submission, challenge, flags)
        if challenge.logic == "team":
            return challenge_attempt_team(submission, challenge, flags)
        return challenge_attempt_any(submission, challenge, flags)

    @classmethod
    def solve(cls, user, team, challenge, request):
        """handles the solving of a challenge."""
        super().solve(user, team, challenge, request)

        # get source_id
        user_id = int(current_user.get_current_user().id)
        source_id = user_id
        if is_teams_mode():
            source_id = int(current_user.get_current_user().team_id)
        if challenge.shared:
            source_id = 0

        if challenge.destroy_on_flag:
            logger.info(
                "deleting instance for challenge %s (source %s)",
                challenge.id,
                source_id,
            )
            try:
                delete_instance(challenge.id, source_id)
            except ChallManagerException as e:
                logger.warning("failed to delete instance: %s", e)


# --- utility functions ---
def convert_to_boolean(value):
    """converts a value to boolean if possible."""
    if isinstance(value, str):
        return value.strip().lower() == "true"
    return bool(value)


def convert_to_json(value):
    """converts a value to a json dictionary."""
    if isinstance(value, str):
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            logger.error("failed to decode json: %s", e)
            raise InternalPluginException(f"failed to decode json: {value}") from e
    if not isinstance(value, dict):
        raise InternalPluginException(f"expected dict or json string, got {value}")
    return value

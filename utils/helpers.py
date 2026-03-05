# pylint: disable=no-member
"""
This module defines the helpers functions.
"""

from CTFd.models import db  # type: ignore
from CTFd.plugins.ctfd_chall_manager.models import DynamicIaCChallenge
from CTFd.plugins.ctfd_chall_manager.utils.chall_manager_error import (
    ChallManagerException,
)
from CTFd.plugins.ctfd_chall_manager.utils.challenge_store import query_challenges
from CTFd.plugins.ctfd_chall_manager.utils.instance_manager import query_instance
from CTFd.plugins.ctfd_chall_manager.utils.logger import configure_logger
from CTFd.utils import get_config
from CTFd.utils import user as current_user
from CTFd.utils.config import is_teams_mode
from flask import request
from sqlalchemy import func

logger = configure_logger(__name__)


def retrieve_all_ids(admin=False) -> dict[str, int] | ValueError:
    """
    This function return all ids for AdminInstance calls.

    return: dict of {"user_id", "team_id", "source_id", "challenge_id"}
    """
    team_id = 0
    admin_id = 0

    user = current_user.get_current_user()
    user_id = int(user.id)

    if admin:
        admin_id = user_id

    # If GET
    challenge_id = request.args.get("challengeId")
    source_id = request.args.get("sourceId")

    if challenge_id is None or source_id is None:  # If POST/PATCH/DELETE
        data = request.get_json()
        challenge_id = data.get("challengeId")
        source_id = data.get("sourceId")

    if challenge_id is None or source_id is None:
        raise ValueError("missing challengeId or sourceId")

    challenge_id = int(challenge_id)
    source_id = int(source_id)

    if not admin:
        source_id = user_id
        if is_teams_mode():
            team_id = user.team_id
            if team_id is not None:
                source_id = int(team_id)

    return {
        "admin_id": admin_id,
        "user_id": user_id,
        "team_id": team_id,
        "source_id": source_id,
        "challenge_id": challenge_id,
    }


def calculate_mana_used(source_id: int) -> int | ChallManagerException:
    """
    Calculate the mana used by source_id based on existing instances on Chall-Manager.
    return: mana_used (int)
    """

    # retrieve all challenge_ids for source_id of running instances
    try:
        instances = query_instance(source_id)
    except ChallManagerException as e:
        raise e

    chall_ids = []
    for i in instances:
        chall_ids.append(i["challengeId"])

    logger.debug(
        "source_id %s has %s instances for challenges %s",
        source_id,
        len(chall_ids),
        chall_ids,
    )

    # SQL command to SUM all mana_cost of all challenges_ids from Chall-Manager
    mana_used = (
        db.session.query(func.sum(DynamicIaCChallenge.mana_cost).label("mana"))
        .filter(DynamicIaCChallenge.id.in_(chall_ids))
        .scalar()
    )

    logger.debug("mana_used for source_id %s is %s", source_id, mana_used)

    if mana_used is None:
        return 0

    return int(mana_used)


def calculate_all_mana_used() -> dict | ChallManagerException:
    """
    Retrieve all instances for all source_id, then calculate the amound of mana used.
    return: {"source_id": "mana_used"}
    raise: ChallManagerException
    """

    # find all source_id with running instances
    source_ids = {}
    instances = []
    try:
        challenges = query_challenges()
    except ChallManagerException as e:
        raise e

    for item in challenges:
        instances = instances + list(item["instances"])

    for item in instances:
        source_id = item["sourceId"]

        # calculate the mana_used for this source_id
        # dict prevent calculate multiple times the same source_id
        if source_id not in source_ids:
            source_ids[source_id] = calculate_mana_used(source_id)

    return source_ids


def check_source_can_edit_instance(challenge_id: int, source_id: int) -> bool:
    """
    Check that the source_id can patch/delete an instance of challenge_id.
    False if challenge_id is shared.
    Default: True
    """

    challenge = DynamicIaCChallenge.query.filter_by(id=challenge_id).first()
    # if instance must be shared (admins only can deploy it)
    if challenge.shared:
        logger.warning(
            "unauthorized attempt to edit sharing instance challenge_id: %s, source_id: %s",
            challenge_id,
            source_id,
        )
        return False

    return True


def check_source_can_create_instance(challenge_id: int, source_id: int) -> bool:
    """
    Checks that source_id can create instance of challenge_id.
    - need challenge to be editable (non-shared).
    - source_id can afford the instance (mana)
    """
    if not check_source_can_edit_instance(challenge_id, source_id):
        return False

    challenge = DynamicIaCChallenge.query.filter_by(id=challenge_id).first()

    # if mana feature is not enabled
    cm_mana_total = get_config("chall-manager:chall-manager_mana_total")
    if cm_mana_total <= 0:
        logger.debug(
            "source_id %s can edit an instance of challenge_id %s, reason: mana not enabled",
            source_id,
            challenge_id,
        )
        return True

    # if instance do not define a mana_cost (free)
    if challenge.mana_cost == 0:
        logger.debug(
            "source_id %s can edit an instance of challenge_id %s, reason: challenge is free",
            source_id,
            challenge_id,
        )
        return True

    try:
        mana_used = calculate_mana_used(source_id)
    except ChallManagerException:
        return False  # block create if CM generate an error

    new_mana = mana_used + challenge.mana_cost
    # if source can afford it
    if new_mana <= cm_mana_total:
        logger.debug(
            "source_id %s can create an instance of challenge_id %s, reason: source can afford it",
            source_id,
            challenge_id,
        )
        return True

    # default
    logger.debug(
        "source_id %s cannot create instance of challenge_id %s, reason: source can't afford it",
        source_id,
        challenge_id,
    )
    return False


def check_source_can_patch_instance(challenge_id: int, source_id: int) -> bool:
    """
    Checks that source_id can patch instance of challenge_id.
    """
    if not check_source_can_edit_instance(challenge_id, source_id):
        return False

    challenge = DynamicIaCChallenge.query.filter_by(id=challenge_id).first()
    if not challenge.timeout:
        logger.warning(
            "unauthorized attempt to patch non timeout instance challenge_id: %s, source_id: %s",
            challenge_id,
            source_id,
        )
        return False

    # default
    logger.debug(
        "source_id %s can patch instance of challenge_id %s",
        source_id,
        challenge_id,
    )
    return True

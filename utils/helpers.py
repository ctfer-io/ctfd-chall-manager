# pylint: disable=no-member
"""
This module defines the helpers functions.
"""

import requests
from CTFd.models import db  # type: ignore
from CTFd.plugins.ctfd_chall_manager.models import DynamicIaCChallenge
from CTFd.plugins.ctfd_chall_manager.utils.chall_manager_error import (
    ChallManagerException,
)
from CTFd.plugins.ctfd_chall_manager.utils.challenge_store import query_challenges
from CTFd.plugins.ctfd_chall_manager.utils.instance_manager import query_instance
from CTFd.plugins.ctfd_chall_manager.utils.logger import configure_logger
from CTFd.utils import get_config
from sqlalchemy import func

logger = configure_logger(__name__)


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


def check_chall_manager_healthcheck() -> bool:
    """
    Check that chall-manager api is reachable.
    Performe a GET request on http://chall-manger-url:port/healthcheck
    """
    cm_api_reachable = False

    try:
        logger.debug("getting connection status with chall-manager")
        health_url = f'{get_config("chall-manager:chall-manager_api_url")}/healthcheck'
        requests.get(health_url, timeout=5).raise_for_status()
    except requests.HTTPError as e:
        logger.warning("can communicate with CM, but got error %s", e)
    except requests.RequestException as e:
        logger.warning("cannot communicate with CM, got %s", e)
    else:
        logger.info("communication with CM configured successfully")
        cm_api_reachable = True

    return cm_api_reachable

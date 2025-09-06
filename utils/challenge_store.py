"""
This module contains all functions to use Chall-Manager ChallengeStore group.
"""

import json

import requests
from CTFd.plugins.ctfd_chall_manager.utils.chall_manager_error import (
    ChallManagerException,
)
from CTFd.plugins.ctfd_chall_manager.utils.logger import configure_logger
from CTFd.utils import get_config

logger = configure_logger(__name__)
CM_API_TIMEOUT = get_config("chall-manager_api_timeout")

# pylint: disable=duplicate-code
# pylint detect duplicate-code between challenge_store and intance_manager
# This is false positive


def query_challenges() -> list | ChallManagerException:
    """
    Query all challenges information and their instances running.

    :return list: list of challenges [{ . }, { . }]
    """
    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/api/v1/challenge"
    s = requests.Session()
    result = []

    logger.debug("querying challenges from %s", url)

    try:
        with s.get(url, headers=None, stream=True, timeout=CM_API_TIMEOUT) as resp:
            for line in resp.iter_lines():
                if line:
                    res = line.decode("utf-8")
                    res = json.loads(res)
                    result.append(res["result"])
        logger.debug("successfully queried challenges: %s", result)
    except Exception as e:
        logger.error("error querying challenges: %s", e)
        raise ChallManagerException("error querying challenges") from e

    return result


def create_challenge(
    challenge_id: int, *args
) -> requests.Response | ValueError | ChallManagerException:
    """
    Create challenge on chall-manager

    :param challenge_id: id of challenge to create (e.g: 1)
    :param *args: additional configuration in dictionary format
    (e.g {'timeout': '600', 'updateStrategy': 'update_in_place', 'until': '2024-07-10 15:00:00'})

    :return Response: of chall-manager API
    """
    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/api/v1/challenge"

    headers = {"Content-Type": "application/json"}

    payload = {}

    if len(args) != 0:
        if not isinstance(args[0], dict):
            logger.error(
                "invalid argument, got %s, dict is expected",
                args[0],
            )
            raise ValueError(
                f"invalid argument, got {args[0]} for type {type(args[0])}, dict is expected"
            )

        payload = args[0]

    logger.debug("creating challenge with id=%s", challenge_id)

    payload["id"] = str(challenge_id)

    try:
        r = requests.post(
            url, data=json.dumps(payload), headers=headers, timeout=CM_API_TIMEOUT
        )
        logger.debug("received response: %s %s", r.status_code, r.text)
    except Exception as e:
        logger.error("error creating challenge: %s", e)
        raise ChallManagerException(
            "an exception occurred while communicating with CM"
        ) from e

    if r.status_code != 200:
        logger.error("error from chall-manager: %s", json.loads(r.text))
        raise ChallManagerException(
            f"Chall-manager returned an error: {json.loads(r.text)}"
        )

    return r


def delete_challenge(challenge_id: int) -> requests.Response | ChallManagerException:
    """
    Delete challenge and its instances running.

    :param challenge_id* (int): 1

    :return Response: of chall-manager API
    """
    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/api/v1/challenge/{challenge_id}"

    logger.debug("deleting challenge with id=%s", challenge_id)

    try:
        r = requests.delete(url, timeout=CM_API_TIMEOUT)
        logger.debug("received response: %s %s", r.status_code, r.text)
    except Exception as e:
        logger.error("error deleting challenge: %s", e)
        raise ChallManagerException("error deleting challenge") from e

    return r


def get_challenge(challenge_id: int) -> requests.Response | ChallManagerException:
    """
    Get challenge information and its instances running.

    :param challenge_id* (int): 1
    :return Response: of chall-manager API
    """
    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/api/v1/challenge/{challenge_id}"

    logger.debug("getting challenge information for id=%s", challenge_id)

    try:
        r = requests.get(url, timeout=CM_API_TIMEOUT)
        logger.debug("recieved response: %s %s", r.status_code, r.text)
    except Exception as e:
        logger.error("error getting challenge: %s", e)
        raise ChallManagerException(
            "an exception occurred while communicating with CM"
        ) from e

    if r.status_code != 200:
        logger.error("error from chall-manager: %s", json.loads(r.text))
        raise ChallManagerException(
            f"Chall-manager returned an error: {json.loads(r.text)}"
        )

    return r


def update_challenge(
    challenge_id: int, *args
) -> requests.Response | ValueError | ChallManagerException:
    """
    Update challenge with information provided

    :param challenge_id*: 1
    :param *args: additional configuration in dictionary format
    (e.g {'timeout': '600s', 'updateStrategy': 'update_in_place', 'until': '2024-07-10 15:00:00' })
    :return Response: of chall-manager API
    """
    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/api/v1/challenge/{challenge_id}"

    headers = {"Content-Type": "application/json"}

    payload = {}

    if len(args) != 0:
        if not isinstance(args[0], dict):
            logger.error("invalid arguments provided for updating challenge")
            raise ValueError(f"error updating challenge, invalid inputs, got {args}")

        payload = args[0]

    logger.debug("updating challenge with id=%s", challenge_id)

    payload["updateMask"] = ",".join(
        k for k in ("timeout", "until", "additional", "min", "max") if k in payload
    )

    logger.debug(
        "updating challenge %s with updateMask %s", challenge_id, payload["updateMask"]
    )

    try:
        r = requests.patch(
            url, data=json.dumps(payload), headers=headers, timeout=CM_API_TIMEOUT
        )
        logger.debug("received response: %s %s", r.status_code, r.text)
    except Exception as e:
        logger.error("error updating challenge: %s", e)
        raise ChallManagerException("error while communicating with CM") from e

    if r.status_code != 200:
        logger.error("error from chall-manager: %s", json.loads(r.text))
        raise ChallManagerException(
            f"Chall-manager returned an error: {json.loads(r.text)}"
        )

    return r

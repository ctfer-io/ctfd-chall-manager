"""
This module contains all functions to use Chall-Manager InstanceManager group.
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


def create_instance(
    challenge_id: int, source_id: int
) -> requests.Response | ChallManagerException:
    """
    Spins up a challenge instance, iif the challenge is registered and no instance is yet running.

    :param challenge_id: id of challenge for the instance
    :param source_id: id of source for the instance
    :return Response: of chall-manager API
    :raise ChallManagerException:
    """

    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/api/v1/instance"

    payload = {"challengeId": str(challenge_id), "sourceId": str(source_id)}

    headers = {"Content-Type": "application/json"}

    logger.debug(
        "creating instance for challenge_id=%s, source_id=%s", challenge_id, source_id
    )

    try:
        r = requests.post(
            url, data=json.dumps(payload), headers=headers, timeout=CM_API_TIMEOUT
        )
        logger.debug("received response: %s, %s", r.status_code, r.text)
    except Exception as e:
        logger.error("error creating instance: %s", e)
        raise ChallManagerException(
            "an exception occurred while communicating with CM"
        ) from e

    if r.status_code != 200:
        if r.json()["code"] == 2:
            message = r.json()["message"]
            logger.error("chall-manager return an error: %s", message)
            raise ChallManagerException(message=message) from e

    return r


def delete_instance(
    challenge_id: int, source_id: int
) -> requests.Response | ChallManagerException:
    """
    After completion, the challenge instance is no longer required.
    This spins down the instance and removes if from filesystem.

    :param challenge_id: id of challenge for the instance
    :param source_id: id of source for the instance
    :return Response: of chall-manager API
    :raise ChallManagerException:
    """

    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/api/v1/instance/{challenge_id}/{source_id}"

    logger.debug(
        "deleting instance for challenge_id=%s, source_id=%s", challenge_id, source_id
    )

    try:
        r = requests.delete(url, timeout=CM_API_TIMEOUT)
        logger.debug("received response: %s %s", r.status_code, r.text)
    except Exception as e:
        logger.error("error deleting instance: %s", e)
        raise ChallManagerException(
            "an exception occurred while communicating with CM"
        ) from e

    if r.status_code != 200:
        logger.error("error from chall-manager: %s", json.loads(r.text))
        raise ChallManagerException(
            f"Chall-Manager returned an error: {json.loads(r.text)}"
        ) from e

    return r


def get_instance(
    challenge_id: int, source_id: int
) -> requests.Response | ChallManagerException:
    """
    Once created, you can retrieve the instance information.
    If it has not been created yet, returns an error.

    :param challenge_id: id of challenge for the instance
    :param source_id: id of source for the instance
    :return Response: of chall-manager API
    :raise ChallManagerException:
    """

    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/api/v1/instance/{challenge_id}/{source_id}"

    logger.debug(
        "getting instance information for challenge_id=%s, source_id=%s",
        challenge_id,
        source_id,
    )

    try:
        r = requests.get(url, timeout=CM_API_TIMEOUT)
        logger.debug("received response: %s %s", r.status_code, r.text)
    except Exception as e:
        logger.error("error getting instance: %s", e)
        raise ChallManagerException(
            "an exception occurred while communicating with CM"
        ) from e

    if r.status_code != 200:
        logger.info("no instance on chall-manager: %s", json.loads(r.text))
        raise ChallManagerException(
            f"Chall-manager returned an error: {json.loads(r.text)}"
        ) from e

    return r


def update_instance(
    challenge_id: int, source_id: int
) -> requests.Response | ChallManagerException:
    """
    This will set the until date to the request time more the challenge timeout.

    :param challenge_id: id of challenge for the instance
    :param source_id: id of source for the instance
    :return Response: of chall-manager API
    :raise ChallManagerException:
    """

    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/api/v1/instance/{challenge_id}/{source_id}"

    payload = {}

    headers = {"Content-Type": "application/json"}

    logger.debug(
        "updating instance for challenge_id=%s, source_id=%s", challenge_id, source_id
    )

    try:
        r = requests.patch(
            url, data=json.dumps(payload), headers=headers, timeout=CM_API_TIMEOUT
        )
        logger.debug("received response: %s %s", r.status_code, r.text)
    except Exception as e:
        logger.error("Error updating instance: %s", e)
        raise ChallManagerException(
            "An exception occurred while communicating with CM"
        ) from e

    if r.status_code != 200:
        if r.json()["code"] == 2:
            message = r.json()["message"]
            logger.error("chall-manager return an error: %s", message)
            raise ChallManagerException(message=message) from e

    return r


def query_instance(source_id: int) -> list | ChallManagerException:
    """
    This will return a list with all instances that exists on chall-manager for the source_id given.

    :param source_id: id of source for the instance
    :return list: all instances for the source_id (e.g [{source_id:x, challenge_id, y},..])
    """

    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/api/v1/instance?sourceId={source_id}"

    s = requests.Session()

    result = []

    logger.debug("querying instances for sourceId=%s", source_id)

    try:
        with s.get(url, headers=None, stream=True, timeout=CM_API_TIMEOUT) as resp:
            for line in resp.iter_lines():
                if line:
                    res = line.decode("utf-8")
                    res = json.loads(res)
                    if "result" in res.keys():
                        result.append(res["result"])
        logger.debug("successfully queried instances: %s", result)
    except Exception as e:
        logger.error("connection error: %s", e)
        raise ChallManagerException("connection error") from e

    return result

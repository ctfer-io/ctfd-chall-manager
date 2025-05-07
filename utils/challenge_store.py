import requests
import json

from CTFd.utils import get_config  # type: ignore
from .logger import configure_logger

logger = configure_logger(__name__)

def query_challenges() -> list:
    """
    Query all challenges information and their instances running.

    :return list: list of challenges [{ . }, { . }]
    """
    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/challenge"
    s = requests.Session()
    result = []

    logger.debug(f"Querying challenges from {url}")

    try:
        with s.get(url, headers=None, stream=True, timeout=30) as resp:
            for line in resp.iter_lines():
                if line:
                    res = line.decode("utf-8")
                    res = json.loads(res)
                    result.append(res["result"])
        logger.debug(f"Successfully queried challenges: {result}")
    except Exception as e:
        logger.error(f"Error querying challenges: {e}")
        raise Exception(f"ConnectionError: {e}")

    return result

def create_challenge(id: int, scenario: str, *args) -> requests.Response:
    """
    Create challenge on chall-manager
    
    :param id: id of challenge to create (e.g: 1)
    :param scenario: base64(zip(.)),
    :param *args: additional configuration in dictionary format (e.g {'timeout': '600', 'updateStrategy': 'update_in_place', 'until': '2024-07-10 15:00:00'})
    
    :return Response: of chall-manager API
    """
    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/challenge"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {}

    if len(args) != 0:
        if type(args[0]) is not dict:
            logger.error(f"invalid argument, got {args[0]} for type {type(args[0])}, dict is expected")
            raise Exception(f"invalid argument, got {args[0]} for type {type(args[0])}, dict is expected")

        payload = args[0]

    logger.debug(f"Creating challenge with id={id}")

    payload["id"] = str(id)
    payload["scenario"] = scenario

    try:
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        logger.debug(f"Received response: {r.status_code} {r.text}")
    except Exception as e:
        logger.error(f"Error creating challenge: {e}")
        raise Exception(f"An exception occurred while communicating with CM: {e}")
    else:
        if r.status_code != 200:
            logger.error(f"Error from chall-manager: {json.loads(r.text)}")
            raise Exception(f"Chall-manager returned an error: {json.loads(r.text)}")
    
    return r

def delete_challenge(id: int) -> requests.Response:
    """
    Delete challenge and its instances running.
    
    :param id* (int): 1

    :return Response: of chall-manager API
    """
    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/challenge/{id}"

    logger.debug(f"Deleting challenge with id={id}")

    try:
        r = requests.delete(url)
        logger.debug(f"Received response: {r.status_code} {r.text}")
    except Exception as e:
        logger.error(f"error deleting challenge: {e}")
        raise Exception(f"error deleting challenge: {e}")
    
    return r

def get_challenge(id: int) -> requests.Response:
    """
    Get challenge information and its instances running.
    
    :param id* (int): 1
    :return Response: of chall-manager API
    """
    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/challenge/{id}"

    logger.debug(f"Getting challenge information for id={id}")

    try:
        r = requests.get(url, timeout=30)
        logger.debug(f"Received response: {r.status_code} {r.text}")
    except Exception as e:
        logger.error(f"Error getting challenge: {e}")
        raise Exception(f"An exception occurred while communicating with CM: {e}")
    else:
        if r.status_code != 200:
            logger.error(f"Error from chall-manager: {json.loads(r.text)}")
            raise Exception(f"Chall-manager returned an error: {json.loads(r.text)}")
 
    return r

def update_challenge(id: int, *args) -> requests.Response:
    """
    Update challenge with information provided
    
    :param id*: 1 
    :param *args: additional configuration in dictionary format (e.g {'timeout': '600s', 'updateStrategy': 'update_in_place', 'until': '2024-07-10 15:00:00' })
    :return Response: of chall-manager API
    """
    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/challenge/{id}"

    headers = {
        "Content-Type": "application/json"
    }

    payload = {}

    if len(args) != 0:
        if type(args[0]) is not dict:
            logger.error("Invalid arguments provided for updating challenge")
            raise Exception(f"Error deleting challenge: {e}")

        payload = args[0]

    logger.debug(f"Updating challenge with id={id}")

    updateMask = []

    if "timeout" in payload.keys():
        updateMask.append("timeout")

    if "until" in payload.keys():
        updateMask.append("until")

    if "additional" in payload.keys():
        updateMask.append("additional")

    if "min" in payload.keys():
        updateMask.append("min")
    
    if "max" in payload.keys():
        updateMask.append("max")

    payload["updateMask"] = ",".join(updateMask)

    logger.debug(f"updating challenge {id} with updateMask {payload['updateMask']}")

    try:
        r = requests.patch(url, data=json.dumps(payload), headers=headers)
        logger.debug(f"Received response: {r.status_code} {r.text}")
    except Exception as e:
        logger.error(f"Error updating challenge: {e}")
        raise Exception(f"An exception occurred while communicating with CM: {e}")
    else:
        if r.status_code != 200:
            logger.error(f"Error from chall-manager: {json.loads(r.text)}")
            raise Exception(f"Chall-manager returned an error: {json.loads(r.text)}")
    
    return r

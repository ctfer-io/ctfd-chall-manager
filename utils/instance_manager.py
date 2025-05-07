import requests
import json
from CTFd.utils import get_config  # type: ignore

from .logger import configure_logger
from .chall_manager_error import ChallManagerException

logger = configure_logger(__name__)

def create_instance(challengeId: int, sourceId: int) -> requests.Response | Exception: 
    """
    Spins up a challenge instance, iif the challenge is registered and no instance is yet running.
    
    :param challengeId: id of challenge for the instance
    :param sourceId: id of source for the instance
    :return Response: of chall-manager API
    :raise Exception:
    """

    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/instance"

    payload = {
        "challengeId": challengeId,
        "sourceId": sourceId
    }

    headers = {
        "Content-Type": "application/json"
    }

    logger.debug(f"Creating instance for challengeId={challengeId}, sourceId={sourceId}")

    try:        
        r = requests.post(url, data=json.dumps(payload), headers=headers)
        logger.debug(f"Received response: {r.status_code} {r.text}")
    except Exception as e:
        logger.error(f"Error creating instance: {e}")
        raise Exception(f"An exception occurred while communicating with CM: {e}")
    else:
        if r.status_code != 200:
            if r.json()["code"] == 2:
                message = r.json()["message"]
                logger.error(f"chall-manager return an error: {message}")
                raise ChallManagerException(message=message)
 
    return r

def delete_instance(challengeId: int , sourceId: int) -> requests.Response | Exception:
    """
    After completion, the challenge instance is no longer required. This spins down the instance and removes if from filesystem.
    
    :param challengeId: id of challenge for the instance
    :param sourceId: id of source for the instance
    :return Response: of chall-manager API
    :raise Exception:
    """

    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/instance/{challengeId}/{sourceId}"

    logger.debug(f"Deleting instance for challengeId={challengeId}, sourceId={sourceId}")

    try:        
        r = requests.delete(url)
        logger.debug(f"Received response: {r.status_code} {r.text}")
    except Exception as e:
        logger.error(f"Error deleting instance: {e}")
        raise Exception(f"An exception occurred while communicating with CM: {e}")
    else:
        if r.status_code != 200:
            logger.error(f"Error from chall-manager: {json.loads(r.text)}")
            raise Exception(f"Chall-manager returned an error: {json.loads(r.text)}")
 
    return r

def get_instance(challengeId: int, sourceId: int) -> requests.Response | Exception:
    """
    Once created, you can retrieve the instance information. If it has not been created yet, returns an error.
    
    :param challengeId: id of challenge for the instance
    :param sourceId: id of source for the instance
    :return Response: of chall-manager API
    :raise Exception:
    """

    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/instance/{challengeId}/{sourceId}"

    logger.debug(f"Getting instance information for challengeId={challengeId}, sourceId={sourceId}")

    try:        
        r = requests.get(url, timeout=30)
        logger.debug(f"Received response: {r.status_code} {r.text}")
    except Exception as e:
        logger.error(f"Error getting instance: {e}")
        raise Exception(f"An exception occurred while communicating with CM: {e}")
    else:
        if r.status_code != 200:
            logger.info(f"No instance on chall-manager: {json.loads(r.text)}")
            raise Exception(f"Chall-manager returned an error: {json.loads(r.text)}")
 
    return r

def update_instance(challengeId: int, sourceId: int) -> requests.Response | Exception:
    """
    This will set the until date to the request time more the challenge timeout.
    
    :param challengeId: id of challenge for the instance
    :param sourceId: id of source for the instance
    :return Response: of chall-manager API
    :raise Exception:
    """

    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/instance/{challengeId}/{sourceId}"

    payload = {}

    headers = {
        "Content-Type": "application/json"
    }

    logger.debug(f"Updating instance for challengeId={challengeId}, sourceId={sourceId}")

    try:        
        r = requests.patch(url, data=json.dumps(payload), headers=headers)
        logger.debug(f"Received response: {r.status_code} {r.text}")
    except Exception as e:
        logger.error(f"Error updating instance: {e}")
        raise Exception(f"An exception occurred while communicating with CM: {e}")
    else:
        if r.status_code != 200:
            if r.json()["code"] == 2:
                message = r.json()["message"]
                logger.error(f"chall-manager return an error: {message}")
                raise ChallManagerException(message=message)
 
    return r

def query_instance(sourceId: int) -> list | Exception:
    """
    This will return a list with all instances that exists on chall-manager for the sourceId given.

    :param sourceId: id of source for the instance
    :return list: all instances for the sourceId (e.g [{sourceId:x, challengeId, y},..])
    """
    
    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/instance?sourceId={sourceId}"

    s = requests.Session()

    result = []

    logger.debug(f"Querying instances for sourceId={sourceId}")

    try:
        with s.get(url, headers=None, stream=True, timeout=30) as resp:
            for line in resp.iter_lines():
                if line:
                    res = line.decode("utf-8")
                    res = json.loads(res)
                    if "result" in res.keys():
                        result.append(res["result"])
        logger.debug(f"Successfully queried instances: {result}")
    except Exception as e:
        logger.error(f"ConnectionError: {e}")
        raise Exception(f"ConnectionError: {e}")

    return result

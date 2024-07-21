import requests
import json

from CTFd.utils import get_config # type: ignore

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

    payload = {}
    payload["challengeId"] = challengeId
    payload["sourceId"] = sourceId

    headers = {
        "Content-Type": "application/json"
    }

    try:        
        r = requests.post(url, data = json.dumps(payload), headers=headers)
    except Exception as e :
        raise Exception(f"An exception occured while communicating with CM : {e}")
    else:
        if r.status_code != 200:
            raise Exception(f"Chall-manager return an error : {json.loads(r.text)}")
 
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

    try:        
        r = requests.delete(url)
    except Exception as e :
        raise Exception(f"An exception occured while communicating with CM : {e}")
    else:
        if r.status_code != 200:
            raise Exception(f"Chall-manager return an error : {json.loads(r.text)}")
 
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


    try:        
        r = requests.get(url)
    except Exception as e :
        raise Exception(f"An exception occured while communicating with CM : {e}")
    # else:
    #     if r.status_code != 200:
    #         raise Exception(f"Chall-manager return an error : {json.loads(r.text)}") 
    # TODO 
 
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

    try:        
        r = requests.patch(url, data = json.dumps(payload), headers=headers)
    except Exception as e :
        raise Exception(f"An exception occured while communicating with CM : {e}")
    else:
        if r.status_code != 200:
            raise Exception(f"Chall-manager return an error : {json.loads(r.text)}")
 
    return r


def query_instance(sourceId: int)-> list | Exception:
    """
    This will return a list with all instances that exists on chall-manager for the sourceId given.

    :param sourceId: id of source for the instance
    :return list: all instances for the sourceId (e.g [{sourceId:x, challengeId, y},..])
    """

    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/instance?sourceId={sourceId}"

    s = requests.Session()

    result = []

    try:
        with s.get(url, headers=None, stream=True) as resp:
            for line in resp.iter_lines():
                if line:
                    res = line.decode("utf-8")
                    res = json.loads(res)

                    result.append(res["result"])
    except Exception as e:
        raise Exception(f"ConnectionError: {e}")

    return result


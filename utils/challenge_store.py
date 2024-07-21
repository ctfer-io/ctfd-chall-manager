import requests
import json

from CTFd.utils import get_config # type: ignore

def query_challenges() -> list:
    """
    Query all challenges information and their instances running.

    :return list: list of challenges [{ . }, { . }]
    """
    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/challenge"

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

def create_challenge(id: int, scenario: str, *args) -> requests.Response:
    """
    Create challenge on chall-manager
    
    :param id: id of challenge to create (e.g: 1)
    :param scenario: base64(zip(.)),
    :param *args: additional configuration in dictionnary format (e.g {'timeout': '600', 'updateStrategy': 'update_in_place', 'until': '2024-07-10 15:00:00')}
    
    :return Response: of chall-manager API
    """
    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/challenge"

    headers = {
        "Content-Type": "application/json"
    }

    # init payload 
    payload = {}

    # check if args is provided
    if len(args) != 0:
        # if invalid inputs ça dégage mon salaud
        if type(args[0]) is not dict: 
            return

        payload = args[0] # check if inputs are valid for CM ?

    print(f"plugins debug args[0]: {args[0]}")  # TODO use logging

    # mandatory inputs
    payload["id"] = str(id)
    payload["scenario"] = scenario

    try:    
        r = requests.post(url, data = json.dumps(payload), headers=headers)
    except Exception as e :
        raise Exception(f"An exception occured while communicating with CM : {e}")
    else:
        if r.status_code != 200:
            raise Exception(f"Chall-manager return an error : {json.loads(r.text)}")
    
    return r

def delete_challenge(id: int) -> requests.Response:
    """
    Delete challenge and its instances running.
    
    :param target* (string): url of chall-manager API (e.g http://localhost:9090/api/v1)
    :param id* (int): 1

    :return Response: of chall-manager API
    """

    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/challenge/{id}"

    try:        
        r = requests.delete(url)
    except Exception as e :
        return e 
    
    return r

def get_challenge(id: int) -> requests.Response:
    """
    Get challenge information and its instances running.
    
    : :param id* (int): 1
    :return Response: of chall-manager API
    """

    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/challenge/{id}" 
    
    try: 
        r = requests.get(url)
    except Exception as e :
        raise Exception(f"An exception occured while communicating with CM : {e}")
    else:
        if r.status_code != 200:
            raise Exception(f"Chall-manager return an error : {json.loads(r.text)}")
 
    return r

def update_challenge(id: int, *args)-> requests.Response:
    """
    Update challenge with informations provided
    
    :param id*: 1 
    :param *args: additional configuration in dictionnary format (e.g {'timeout': '600', 'updateStrategy': 'update_in_place', 'until': '2024-07-10 15:00:00' })
    :return Response: of chall-manager API
    """

    cm_api_url = get_config("chall-manager:chall-manager_api_url")
    url = f"{cm_api_url}/challenge/{id}"

    headers = {
        "Content-Type": "application/json"
    } 

    # init payload 
    payload = {}

    # check if args is provided
    if len(args) != 0:
        # if invalid inputs ça dégage mon salaud
        if type(args[0]) is not dict: 
            return

        payload = args[0] # check if inputs are valid for CM ?

    payload["id"] = str(id)

    try:        
        r = requests.patch(url, data = json.dumps(payload), headers=headers)
    except Exception as e :
        raise Exception(f"An exception occured while communicating with CM : {e}")
    else:
        if r.status_code != 200:
            raise Exception(f"Chall-manager return an error : {json.loads(r.text)}")
    
    return r

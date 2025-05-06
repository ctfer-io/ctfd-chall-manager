import requests
import json
import os
import threading

class Config:
    def __init__(self, **kwargs):
        self.ctfd_url = os.getenv("CTFD_URL", "http://localhost:8000")
        self.plugin_url = f"{self.ctfd_url}/api/v1/plugins/ctfd-chall-manager"

        self.ctfd_token_user = os.getenv("CTFD_API_TOKEN_USER")
        self.ctfd_token_admin = os.getenv("CTFD_API_TOKEN_ADMIN")

        if not self.ctfd_token_user or not self.ctfd_token_admin:
            raise AttributeError("missing CTFD_API_TOKEN_USER or CTFD_API_TOKEN_ADMIN")
        
        self.headers_admin = {
            "Accept": "application/json",
            "Authorization": f"Token {self.ctfd_token_admin}",
            "Content-Type": "application/json"
        }

        self.headers_user = {
            "Accept": "application/json",
            "Authorization": f"Token {self.ctfd_token_user}",
            "Content-Type": "application/json"
        }

        self.scenario_path = "./hack/deploy/demo-deploy.zip"
        #self.scenario_id = push_scenario_as_file(self.scenario_path)
        
            
    def __repr__(self):
        return f"<Config {self.__dict__}>"



config = Config()

def create_challenge(shared=False, destroy_on_flag=False, mana_cost=None, timeout=None, until=None, additional={}, min=None, max=None, state="visible"):

    payload = {
        "name": "test",
        "category":"test",
        "description":"test",
        "initial":"500",
        "function":"linear",
        "decay":"10",
        "minimum":"10",
        "type":"dynamic_iac",
        "scenario_id": config.scenario_id,
        "shared": shared,
        "destroy_on_flag": destroy_on_flag,
        "additional": additional,
        "state": state,
    }

    if mana_cost:
        payload["mana_cost"] = mana_cost

    if min:
        payload["min"] = min

    if max:
        payload["max"] = max

    if timeout:
        payload["timeout"] = timeout

    if until:
        payload["until"] = until

    r = requests.post(f"{config.ctfd_url}/api/v1/challenges",  headers=config.headers_admin, data=json.dumps(payload))
    a = json.loads(r.text)
    if a["success"] != True:
        raise Exception("error while setting up the testing environment, do not process") 
    
    # return the chall_id
    return a["data"]["id"]

def delete_challenge(challengeId):
    r = requests.delete(f"{config.ctfd_url}/api/v1/challenges/{challengeId}",  headers=config.headers_admin)
    a = json.loads(r.text)
    if a["success"] != True:
        raise Exception("error while setting up the testing environment, do not process") 

def push_scenario_as_file(path):
    files = {'file': open(path, 'rb')}
    # do not use headers with application/json
    headers = {
        "Authorization": f"Token {config.ctfd_token_admin}",
    }
    r = requests.post(f"{config.ctfd_url}/api/v1/files",  headers=headers, files=files)
    a = json.loads(r.text)

    scenario_id = a["data"][0]["id"]
    return scenario_id


# region /instance
# readable function to manipulate CRUD operation as user on /instance
def post_instance(challengeId: int):
    payload = {
        "challengeId": f"{challengeId}"
    }
    r = requests.post(f"{config.plugin_url}/instance", headers=config.headers_user, data=json.dumps(payload))
    return r

def get_instance(challengeId: int):
    r = requests.get(f"{config.plugin_url}/instance?challengeId={challengeId}",  headers=config.headers_user)
    return r

def get_admin_instance(challengeId: int, sourceId: int):
    r = requests.get(f"{config.plugin_url}/admin/instance?challengeId={challengeId}&sourceId={sourceId}",  headers=config.headers_admin)
    return r

def delete_instance(challengeId: int):
    payload = {
        "challengeId": f"{challengeId}"
    }
    r = requests.delete(f"{config.plugin_url}/instance",  headers=config.headers_user, data=json.dumps(payload))
    return r

def patch_instance(challengeId: int): 
    payload = {
        "challengeId": f"{challengeId}"
    }
    r = requests.patch(f"{config.plugin_url}/instance",  headers=config.headers_user, data=json.dumps(payload))
    return r

# Run post on thread
def run_post_instance(challengeId: int, results: dict, lock: threading.Lock):
    r = post_instance(challengeId)
    with lock:
        # Store the result in a shared dictionary with the challengeId as the key
        results[challengeId] = json.loads(r.text)

def get_source_id():
    r = requests.get(f"{config.ctfd_url}/api/v1/configs/user_mode", headers=config.headers_admin)
    a = json.loads(r.text)

    user_mode = a["data"]["value"]

    r = requests.get(f"{config.ctfd_url}/api/v1/users/me", headers=config.headers_user)
    a = json.loads(r.text)

    sourceId = a["data"]["id"]
    if user_mode == "teams":
        sourceId = a["data"]["team_id"]

    return sourceId

def bypass_ratelimit():
    payload = {
        "value": "99999999999"
    }

    r = requests.patch(f"{config.ctfd_url}/api/v1/configs/incorrect_submissions_per_min", headers=config.headers_admin, data=json.dumps(payload))
    return r

def reset_all_submissions():
    r = requests.get(f"{config.ctfd_url}/api/v1/submissions", headers=config.headers_admin)
    a = json.loads(r.text)

    submissions = []
    for i in a["data"]:
        submissions.append(i["id"])

    for id in submissions:
        r = requests.delete(f"{config.ctfd_url}/api/v1/submissions/{id}", headers=config.headers_admin)

config.scenario_id = push_scenario_as_file(config.scenario_path)


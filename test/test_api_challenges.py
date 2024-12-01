import unittest
import requests
import json
import os 

ctfd_url = os.getenv("CTFD_URL")
base_url = f"{ctfd_url}/api/v1/challenges"
ctfd_token_admin = os.getenv("CTFD_API_TOKEN_ADMIN")
scenario_id = 1 # a scenario must be sent before (e2e cypress tests did it)

headers_admin = {
    "Accept": "application/json",
    "Authorization": f"Token {ctfd_token_admin}",
    "Content-Type": "application/json"
}

base_challenge = {
    "name":"test",
    "category":"test",
    "description":"test",
    "initial":"500",
    "function":"linear",
    "decay":"10",
    "minimum":"10",
    "state":"hidden",
    "type":"dynamic_iac"
}

class Test_F_UserMana(unittest.TestCase):
    def test_create_challenge_with_all_params(self):
        # create a challenge with all params configured
        plugin_attributes = {
            "scope_global":"true",
            "destroy_on_flag":"true",
            "mana_cost":"15",
            "until":"2222-02-22T21:22:00.000Z",
            "timeout":"2222",
            "scenario_id": f"{scenario_id}",
        }

        payload = { **base_challenge, **plugin_attributes}
        r = requests.post(f"{base_url}",  headers=headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True) 

        # check that the challenge has correct params
        chall_id = a["data"]["id"]
        r = requests.get(f"{base_url}/{chall_id}", headers=headers_admin)
        a = json.loads(r.text)

        self.assertEqual(a["success"], True) 
        self.assertEqual(a["data"]["scope_global"], True) 
        self.assertEqual(a["data"]["destroy_on_flag"], True) 
        self.assertEqual(a["data"]["until"], "2222-02-22T21:22:00.000Z") 
        self.assertEqual(a["data"]["timeout"], "2222") 
        self.assertEqual(a["data"]["scenario_id"], scenario_id) 

        # clean testing environment
        r = requests.delete(f"{base_url}/{chall_id}", headers=headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True) 

    def test_create_challenge_with_mandatory_params(self):
        # create a challenge with mandatory params (scenario_id is the only one)
        plugin_attributes = {
            "scenario_id": f"{scenario_id}",
        }

        # create the challenge
        payload = { **base_challenge, **plugin_attributes}
        r = requests.post(f"{base_url}",  headers=headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True) 

        # check that the challenge has correct params
        chall_id = a["data"]["id"]
        r = requests.get(f"{base_url}/{chall_id}", headers=headers_admin)
        a = json.loads(r.text)        
        self.assertEqual(a["success"], True) 
        self.assertEqual(a["data"]["scenario_id"], scenario_id) 

        # check on default values
        self.assertEqual(a["data"]["scope_global"], False)
        self.assertEqual(a["data"]["destroy_on_flag"], False)
        self.assertEqual(a["data"]["until"], None)
        self.assertEqual(a["data"]["timeout"], None)
        
        # clean testing environment
        r = requests.delete(f"{base_url}/{chall_id}", headers=headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True) 

    def test_cannot_create_challenge_if_no_scenario_id(self):
        r = requests.post(f"{base_url}",  headers=headers_admin, data=json.dumps(base_challenge))
        self.assertEqual(r.status_code, 500) # CTFd return internal server error
        # https://github.com/CTFd/CTFd/issues/2674

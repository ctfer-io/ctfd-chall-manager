# This file will test the additional parameters from the plugin itself.
# Tests must follows the CTFd evolution 

import unittest
import requests
import json

from .utils import config, create_challenge, delete_challenge

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

class Test_F_Challenges(unittest.TestCase):
    def test_create_challenge_with_all_params(self):
        chall_id = create_challenge(scope="true", destroy_on_flag="true", until="2222-02-22T21:22:00.000Z", timeout="2222")

        r = requests.get(f"{config.ctfd_url}/api/v1/challenges/{chall_id}", headers=config.headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True) 

        self.assertEqual(a["data"]["scope_global"], True) 
        self.assertEqual(a["data"]["destroy_on_flag"], True) 
        self.assertEqual(a["data"]["until"], "2222-02-22T21:22:00.000Z") 
        self.assertEqual(a["data"]["timeout"], "2222") 
        self.assertEqual(a["data"]["scenario_id"], config.scenario_id) 

        delete_challenge(chall_id)



    def test_create_challenge_with_mandatory_params(self):
        # create a challenge with mandatory params (scenario_id is the only one)
        chall_id = create_challenge()

        r = requests.get(f"{config.ctfd_url}/api/v1/challenges/{chall_id}", headers=config.headers_admin)
        a = json.loads(r.text)        
        self.assertEqual(a["success"], True) 
        self.assertEqual(a["data"]["scenario_id"], config.scenario_id) 

        # check on default values
        self.assertEqual(a["data"]["scope_global"], False)
        self.assertEqual(a["data"]["destroy_on_flag"], False)
        self.assertEqual(a["data"]["until"], None)
        self.assertEqual(a["data"]["timeout"], None)

        payload = {
            "scope_global": "true",
            "destroy_on_flag": "true",
            "until": "2222-02-22T21:22:00.000Z",
            "timeout": "2222",
        }

        r = requests.patch(f"{config.ctfd_url}/api/v1/challenges/{chall_id}", headers=config.headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)        
        self.assertEqual(a["success"], True)

        # check on update params
        self.assertEqual(a["success"], True) 
        self.assertEqual(a["data"]["scope_global"], True) 
        self.assertEqual(a["data"]["destroy_on_flag"], True) 
        self.assertEqual(a["data"]["until"], "2222-02-22T21:22:00.000Z") 
        self.assertEqual(a["data"]["timeout"], "2222") 
        
        # clean testing environment
        delete_challenge(chall_id)

    def test_cannot_create_challenge_if_no_scenario_id(self):
        r = requests.post(f"{config.ctfd_url}/api/v1/challenges",  headers=config.headers_admin, data=json.dumps(base_challenge))
        self.assertEqual(r.status_code, 500) # CTFd return internal server error
        # https://github.com/CTFd/CTFd/issues/2674

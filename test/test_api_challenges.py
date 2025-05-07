# This file will test the additional parameters from the plugin itself.
# Tests must follows the CTFd evolution 

import unittest
import requests
import json

from .utils import (
    config,
    create_challenge,
    delete_challenge,
    post_instance,
    delete_instance,
    get_admin_instance,
    get_source_id,
    reset_all_submissions,
    bypass_ratelimit
    )

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
        chall_id = create_challenge(shared="true", destroy_on_flag="true", until="2222-02-22T21:22:00Z", additional={"test": "test"}, min=1, max=2, timeout=2222)

        r = requests.get(f"{config.ctfd_url}/api/v1/challenges/{chall_id}", headers=config.headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True) 

        self.assertEqual(a["data"]["shared"], True)
        self.assertEqual(a["data"]["destroy_on_flag"], True) 
        self.assertEqual(a["data"]["until"], "2222-02-22T21:22:00Z") 
        self.assertEqual(a["data"]["timeout"], 2222)
        self.assertEqual(a["data"]["scenario_id"], config.scenario_id)
        self.assertEqual(a["data"]["additional"], {"test": "test"})
        self.assertEqual(a["data"]["min"], 1)
        self.assertEqual(a["data"]["max"], 2)

        delete_challenge(chall_id)



    def test_create_challenge_with_mandatory_params(self):
        # create a challenge with mandatory params (scenario_id is the only one)
        chall_id = create_challenge()

        r = requests.get(f"{config.ctfd_url}/api/v1/challenges/{chall_id}", headers=config.headers_admin)
        a = json.loads(r.text)        
        self.assertEqual(a["success"], True) 
        self.assertEqual(a["data"]["scenario_id"], config.scenario_id) 

        # check on default values
        self.assertEqual(a["data"]["shared"], False)
        self.assertEqual(a["data"]["destroy_on_flag"], False)
        self.assertEqual(a["data"]["until"], None)
        self.assertEqual(a["data"]["timeout"], None)
        self.assertEqual(a["data"]["additional"], {})
        self.assertEqual(a["data"]["min"], 0)
        self.assertEqual(a["data"]["max"], 0)

        payload = {
            "shared": "true",
            "destroy_on_flag": "true",
            "until": "2222-02-22T21:22:00Z",
            "timeout": "2222",
            "additional": {"test": "test"},
            "min": 1,
            "max": 2
        }

        r = requests.patch(f"{config.ctfd_url}/api/v1/challenges/{chall_id}", headers=config.headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)        
        self.assertEqual(a["success"], True)

        # check on update params
        self.assertEqual(a["success"], True) 
        self.assertEqual(a["data"]["shared"], True)
        self.assertEqual(a["data"]["destroy_on_flag"], True) 
        self.assertEqual(a["data"]["until"], "2222-02-22T21:22:00Z") 
        self.assertEqual(a["data"]["timeout"], 2222)
        self.assertEqual(a["data"]["additional"], {"test": "test"})
        self.assertEqual(a["data"]["min"], 1)
        self.assertEqual(a["data"]["max"], 2)
        
        # clean testing environment
        delete_challenge(chall_id)

    def test_cannot_create_challenge_if_no_scenario_id(self):
        r = requests.post(f"{config.ctfd_url}/api/v1/challenges",  headers=config.headers_admin, data=json.dumps(base_challenge))
        self.assertEqual(r.status_code, 500) # CTFd return internal server error
        # https://github.com/CTFd/CTFd/issues/2674

    def test_attempt_ctfd_flag(self):
        bypass_ratelimit()

        chall_id = create_challenge()

        ctfd_flag = "fallback"
        payload = {
            "challenge": chall_id,
            "content": ctfd_flag,
            "data": "",
            "type": "static"

        }
        r = requests.post(f"{config.ctfd_url}/api/v1/flags", headers=config.headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        post_instance(chall_id)

        payload = {
            "challenge_id": chall_id,
            "submission": ctfd_flag
        }

        r = requests.post(f"{config.ctfd_url}/api/v1/challenges/attempt", headers=config.headers_user,  data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        self.assertEqual(a["data"]["status"], "correct")

        reset_all_submissions()
        delete_instance(chall_id)
        delete_challenge(chall_id)


    def test_attempt_variate_flag(self):
        bypass_ratelimit()

        chall_id = create_challenge()
        post_instance(chall_id)

        # i can flag with variate flag
        r = get_admin_instance(chall_id, get_source_id())
        a = json.loads(r.text)

        payload = {
            "challenge_id": chall_id,
            "submission": a["data"]["flag"]
        }

        r = requests.post(f"{config.ctfd_url}/api/v1/challenges/attempt", headers=config.headers_user,  data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        self.assertEqual(a["data"]["status"], "correct")

        # clear
        reset_all_submissions()
        delete_instance(chall_id)
        delete_challenge(chall_id)


    def test_attempt_expired(self):
        bypass_ratelimit()
        chall_id = create_challenge()

        payload = {
            "challenge_id": chall_id,
            "submission": "xx"
        }

        r = requests.post(f"{config.ctfd_url}/api/v1/challenges/attempt", headers=config.headers_user,  data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        self.assertEqual(a["data"]["status"], "incorrect")
        self.assertIn("Expired", a["data"]["message"])

        reset_all_submissions()
        delete_challenge(chall_id)
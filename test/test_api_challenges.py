"""
This module defines all tests cases for the CTFd endpoint with plugin extension.
"""

import json
import unittest

import requests

from .utils import (
    config,
    create_challenge,
    delete_challenge,
    delete_instance,
    get_admin_instance,
    get_instance,
    get_source_id,
    post_instance,
    reset_all_submissions,
)

base_challenge = {
    "name": "test",
    "category": "test",
    "description": "test",
    "initial": "500",
    "function": "linear",
    "decay": "10",
    "minimum": "10",
    "state": "hidden",
    "type": "dynamic_iac",
}


# pylint: disable=invalid-name,missing-timeout,duplicate-code
class Test_F_Challenges(unittest.TestCase):
    """
    Test_F_Challenges defines all tests for /challenges endpoint on CTFd.
    """

    def test_create_challenge_with_all_params(self):
        """
        Performs tests with all parameters that the plugins can define.
        """
        chall_id = create_challenge(
            shared=True,
            destroy_on_flag=True,
            until="2222-02-22T21:22:00Z",
            additional={"test": "test"},
            pooler_min=1,
            pooler_max=2,
            timeout=2222,
        )

        r = requests.get(
            f"{config.ctfd_url}/api/v1/challenges/{chall_id}",
            headers=config.headers_admin,
        )
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        self.assertEqual(a["data"]["shared"], True)
        self.assertEqual(a["data"]["destroy_on_flag"], True)
        self.assertEqual(a["data"]["until"], "2222-02-22T21:22:00Z")
        self.assertEqual(a["data"]["timeout"], 2222)
        self.assertEqual(a["data"]["scenario"], config.scenario)
        self.assertEqual(a["data"]["additional"], {"test": "test"})
        self.assertEqual(a["data"]["min"], 1)
        self.assertEqual(a["data"]["max"], 2)

        delete_challenge(chall_id)

    def test_create_challenge_with_mandatory_params(self):
        """
        Performs tests on mandatory parameter.
        """
        # Create a challenge with mandatory params (scenario is the only one)
        chall_id = create_challenge()

        r = requests.get(
            f"{config.ctfd_url}/api/v1/challenges/{chall_id}",
            headers=config.headers_admin,
        )
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        self.assertEqual(a["data"]["scenario"], config.scenario)

        # Check default values
        self.assertEqual(a["data"]["shared"], False)
        self.assertEqual(a["data"]["destroy_on_flag"], False)
        self.assertEqual(a["data"]["until"], None)
        self.assertEqual(a["data"]["timeout"], None)
        self.assertEqual(a["data"]["additional"], {})
        self.assertEqual(a["data"]["min"], 0)
        self.assertEqual(a["data"]["max"], 0)

        # Then set other ones
        payload = {
            "shared": "true",
            "destroy_on_flag": "true",
            "until": "2222-02-22T21:22:00Z",
            "timeout": "2222",
            "additional": {"test": "test"},
            "min": 1,
            "max": 2,
        }

        r = requests.patch(
            f"{config.ctfd_url}/api/v1/challenges/{chall_id}",
            headers=config.headers_admin,
            data=json.dumps(payload),
        )
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        # Check updated values
        self.assertEqual(a["success"], True)
        self.assertEqual(a["data"]["shared"], True)
        self.assertEqual(a["data"]["destroy_on_flag"], True)
        self.assertEqual(a["data"]["until"], "2222-02-22T21:22:00Z")
        self.assertEqual(a["data"]["timeout"], 2222)
        self.assertEqual(a["data"]["additional"], {"test": "test"})
        self.assertEqual(a["data"]["min"], 1)
        self.assertEqual(a["data"]["max"], 2)

        # Then reset date ones (regression of #163)
        payload = {
            "until": None,
            "timeout": None,
        }

        r = requests.patch(
            f"{config.ctfd_url}/api/v1/challenges/{chall_id}",
            headers=config.headers_admin,
            data=json.dumps(payload),
        )
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        # Check updated values
        self.assertEqual(a["data"]["until"], None)
        self.assertEqual(a["data"]["timeout"], None)

        # Finally, clean the testing environment
        delete_challenge(chall_id)

    def test_cannot_create_challenge_if_no_scenario(self):
        """
        Performs tests that CTFd will generate an error if mandatory value is missing.
        """
        r = requests.post(
            f"{config.ctfd_url}/api/v1/challenges",
            headers=config.headers_admin,
            data=json.dumps(base_challenge),
        )
        self.assertEqual(r.status_code, 500)  # CTFd return internal server error
        # https://github.com/CTFd/CTFd/issues/2674

    def test_can_update_scenario(self):
        """
        Check the scenario and the associated instances are updated
        """
        chall_id = create_challenge(timeout=600)

        r = requests.get(
            f"{config.ctfd_url}/api/v1/challenges/{chall_id}",
            headers=config.headers_admin,
        )
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        self.assertEqual(a["data"]["scenario"], config.scenario)

        # create instance
        r = post_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        until1 = a["data"]["until"]

        payload = {
            "scenario": config.scenario2,
            "updateStrategy": "recreate",
            "until": 600,  # FIXME wtf ?
        }

        # update the challenge
        r = requests.patch(
            f"{config.ctfd_url}/api/v1/challenges/{chall_id}",
            headers=config.headers_admin,
            data=json.dumps(payload),
        )
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        self.assertEqual(a["data"]["scenario"], config.scenario2)

        # check that the until has changed (instance recreated)
        r = get_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        print(a)  # TODO remove before PR

        until2 = a["data"]["until"]

        # recreate as updateStrategy must destroy then recreate the instance
        self.assertNotEqual(until1, until2)

        delete_instance(chall_id)
        delete_challenge(chall_id)

    def test_attempt_ctfd_flag(self):
        """
        Performs tests on CTFd flag and check that dynamic flag can be bypassed by CTFd flags.

        """
        chall_id = create_challenge()

        ctfd_flag = "fallback"
        payload = {
            "challenge": chall_id,
            "content": ctfd_flag,
            "data": "",
            "type": "static",
        }
        r = requests.post(
            f"{config.ctfd_url}/api/v1/flags",
            headers=config.headers_admin,
            data=json.dumps(payload),
        )
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        post_instance(chall_id)

        payload = {"challenge_id": chall_id, "submission": ctfd_flag}

        r = requests.post(
            f"{config.ctfd_url}/api/v1/challenges/attempt",
            headers=config.headers_user,
            data=json.dumps(payload),
        )
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        self.assertEqual(a["data"]["status"], "correct")

        reset_all_submissions()
        delete_instance(chall_id)
        delete_challenge(chall_id)

    def test_attempt_variate_flag(self):
        """
        Chekcs that variate flag from Chall-Manager can be used.
        """
        chall_id = create_challenge()
        post_instance(chall_id)

        # i can flag with variate flag
        r = get_admin_instance(chall_id, get_source_id())
        a = json.loads(r.text)

        flags = a["data"]["flags"]
        payload = {"challenge_id": chall_id, "submission": flags[0]}

        r = requests.post(
            f"{config.ctfd_url}/api/v1/challenges/attempt",
            headers=config.headers_user,
            data=json.dumps(payload),
        )
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        self.assertEqual(a["data"]["status"], "correct")  # logic = any

        # clear
        reset_all_submissions()
        delete_instance(chall_id)
        delete_challenge(chall_id)

    def test_attempt_expired(self):
        """
        Check that the plugin return an error if attempt on expired instance.
        """
        chall_id = create_challenge()

        payload = {"challenge_id": chall_id, "submission": "xx"}

        r = requests.post(
            f"{config.ctfd_url}/api/v1/challenges/attempt",
            headers=config.headers_user,
            data=json.dumps(payload),
        )
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        self.assertEqual(a["data"]["status"], "incorrect")
        self.assertIn("Expired", a["data"]["message"])

        reset_all_submissions()
        delete_challenge(chall_id)

    def test_attempt_logic_any(self):
        """
        Check that the plugin can be used with the logic=any feature.
        """
        chall_id = create_challenge(logic="any")
        post_instance(chall_id)

        # i can flag with variate flag
        r = get_admin_instance(chall_id, get_source_id())
        a = json.loads(r.text)

        flags = a["data"]["flags"]
        payload = {"challenge_id": chall_id, "submission": flags[0]}

        r = requests.post(
            f"{config.ctfd_url}/api/v1/challenges/attempt",
            headers=config.headers_user,
            data=json.dumps(payload),
        )
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        self.assertEqual(a["data"]["status"], "correct")

        # clear
        reset_all_submissions()
        delete_instance(chall_id)
        delete_challenge(chall_id)

    def test_attempt_logic_all(self):
        """
        Check that the plugin can be used with the logic=all feature.
        """
        chall_id = create_challenge(logic="all")
        post_instance(chall_id)

        # create ctfd flag
        ctfd_flag = "fallback"
        payload = {
            "challenge": chall_id,
            "content": ctfd_flag,
            "data": "",
            "type": "static",
        }
        r = requests.post(
            f"{config.ctfd_url}/api/v1/flags",
            headers=config.headers_admin,
            data=json.dumps(payload),
        )
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        # provide the first flag (ctfd side)
        payload = {"challenge_id": chall_id, "submission": ctfd_flag}
        r = requests.post(
            f"{config.ctfd_url}/api/v1/challenges/attempt",
            headers=config.headers_user,
            data=json.dumps(payload),
        )
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        self.assertEqual(a["data"]["status"], "partial")

        r = get_admin_instance(chall_id, get_source_id())
        a = json.loads(r.text)
        flags = a["data"]["flags"]

        # provide the other flags provided by Chall-Manager
        for f in flags:
            payload = {"challenge_id": chall_id, "submission": f}
            r = requests.post(
                f"{config.ctfd_url}/api/v1/challenges/attempt",
                headers=config.headers_user,
                data=json.dumps(payload),
            )
            a = json.loads(r.text)
            self.assertEqual(a["success"], True)
            self.assertIn(a["data"]["status"], ["partial", "correct"])

        # clear
        reset_all_submissions()
        delete_instance(chall_id)
        delete_challenge(chall_id)

    def test_attempt_logic_team(self):
        """
        Check that the plugin can be used with the logic=team feature.
        """
        chall_id = create_challenge(logic="team")
        post_instance(chall_id)

        r = requests.get(
            f"{config.ctfd_url}/api/v1/configs/user_mode", headers=config.headers_admin
        )
        a = json.loads(r.text)
        user_mode = a["data"]["value"]

        # provide the second flag provided by Chall-Manager
        r = get_admin_instance(chall_id, get_source_id())
        a = json.loads(r.text)
        flags = a["data"]["flags"]

        payload = {"challenge_id": chall_id, "submission": flags[0]}
        r = requests.post(
            f"{config.ctfd_url}/api/v1/challenges/attempt",
            headers=config.headers_user,
            data=json.dumps(payload),
        )
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        # if partial is returned, then logic=mode is enabled
        if user_mode == "teams":
            self.assertEqual(a["data"]["status"], "partial")
        else:
            self.assertEqual(a["data"]["status"], "correct")

        # clear
        reset_all_submissions()
        delete_instance(chall_id)
        delete_challenge(chall_id)

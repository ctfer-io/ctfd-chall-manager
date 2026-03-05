"""
This module defines all tests cases for the /instance endpoint.
"""

import datetime
import json
import threading
import time
import unittest

import requests

from .utils import (
    config,
    create_challenge,
    delete_challenge,
    delete_instance,
    get_instance,
    patch_instance,
    post_instance,
    run_post_instance,
)


# pylint: disable=invalid-name,missing-timeout,duplicate-code
class Test_F_UserInstance(unittest.TestCase):
    """
    Test_F_UserInstance defines all tests for /instance.
    """

    def test_create_patch_delete_visible_challenge(self):
        """
        Checks all basic behavior of instance usage.
        """
        chall_id = create_challenge(timeout=99)

        r = get_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = post_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        self.assertEqual("connectionInfo" in a["data"].keys(), True)

        r = get_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        self.assertEqual("connectionInfo" in a["data"].keys(), True)

        r = patch_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = delete_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        delete_challenge(chall_id)

    def test_create_invalid_challenge(self):
        """
        Checks that user cannot create instance of challenge that NOT exists.
        """
        r = post_instance(9999)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

    def test_delete_invalid_challenge(self):
        """
        Checks that user cannot delete an instance of challenge that NOT exists.
        """
        r = delete_instance(9999)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

    def test_delete_valid_challenge_but_no_instance(self):
        """
        Checks that user cannot delete an instance that NOT exists.
        """
        chall_id = create_challenge()

        r = delete_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

        delete_challenge(chall_id)

    def test_patch_valid_challenge_but_no_instance(self):
        """
        Checks that user cannot renew an instance that NOT exists.
        """
        chall_id = create_challenge()

        r = patch_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

        delete_challenge(chall_id)

    def test_get_missing_arg(self):
        """
        Checks that plugin return an error if challengeId is not define on GET.
        """
        r = requests.get(f"{config.plugin_url}/instance", headers=config.headers_user)
        self.assertEqual(r.status_code, 400)

    def test_post_missing_arg(self):
        """
        Checks that plugin return an error if challengeId is not define on POST.
        """
        r = requests.post(f"{config.plugin_url}/instance", headers=config.headers_user)
        self.assertEqual(r.status_code, 400)

    def test_patch_missing_arg(self):
        """
        Checks that plugin return an error if challengeId is not define on PATCH.
        """
        r = requests.patch(f"{config.plugin_url}/instance", headers=config.headers_user)
        self.assertEqual(r.status_code, 400)

    def test_delete_missing_arg(self):
        """
        Checks that plugin return an error if challengeId is not define on DELETE.
        """
        r = requests.delete(
            f"{config.plugin_url}/instance", headers=config.headers_user
        )
        self.assertEqual(r.status_code, 400)

    def test_cannot_create_same_chall_twice(self):
        """
        Checks that user cannot create an instance twice.
        """
        chall_id = create_challenge()

        r = post_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        self.assertEqual("connectionInfo" in a["data"].keys(), True)

        r = post_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

        r = delete_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        delete_challenge(chall_id)

    def test_create_multi_instances(self):
        """
        Tests concurrent creation of 3 instances, ensuring only 1 or 2 is approved.
        The other requests should be rate-limited (HTTP 429).
        If thread1 completes before thread2 starts, mana limitation may approve 2.
        """
        results = {}
        lock = threading.Lock()

        # testing setup has 10 mana max
        chall_id1 = create_challenge(mana_cost=5)
        chall_id2 = create_challenge(mana_cost=5)
        chall_id3 = create_challenge(mana_cost=5)

        # Create threads for each instance
        thread1 = threading.Thread(
            target=run_post_instance, args=(chall_id1, results, lock)
        )
        thread2 = threading.Thread(
            target=run_post_instance, args=(chall_id2, results, lock)
        )
        thread3 = threading.Thread(
            target=run_post_instance, args=(chall_id3, results, lock)
        )

        # Start all threads
        thread1.start()
        thread2.start()
        thread3.start()

        # Wait for all threads to complete
        thread1.join()
        thread2.join()
        thread3.join()

        # Initialize the result dictionary
        formatted_result = {"success": [], "failure": []}

        # Iterate through the results and categorize the IDs based on success
        for instance_id, result in results.items():
            if result["success"]:
                formatted_result["success"].append(instance_id)
            else:
                formatted_result["failure"].append(instance_id)

        self.assertEqual(len(formatted_result["success"]), 1)
        self.assertEqual(len(formatted_result["failure"]), 2)

        self.assertTrue(
            len(formatted_result["success"]) <= 2
        )  # can be 2 if the thread1 in completed before thread2 start
        self.assertTrue(
            len(formatted_result["failure"]) >= 1
        )  # at least one cannot be done (mana limitation)

        # Clean test environment
        for i in formatted_result["success"]:
            delete_instance(i)

        delete_challenge(chall_id1)
        delete_challenge(chall_id2)
        delete_challenge(chall_id3)

    def test_hidden_challenge(self):
        """
        This test try to deploy an instance on hidden challenge.
        User cannot deploy an instance if the challenge is hidden.
        """
        # create a hidden challenge
        chall_id = create_challenge(state="hidden")

        r = post_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)  # user cannot deploy instance

        r = get_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)  # user cannot deploy instance

        # remove
        delete_challenge(chall_id)

    def test_cannot_renew_until_instance(self):
        """
        This test try to renew an instance with params until only.
        User cannot renew an instance if a timeout is not defined.
        """
        # create a challenge
        chall_id = create_challenge(until="2222-12-22T22:22:22Z")

        r = post_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = patch_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

        # remove
        delete_challenge(chall_id)

    def test_renew_until_timeout_instance_ok(self):
        """
        This test try to renew an instance with until and timeout define.
        User can deploy an instance if a timeout is defined and now+timeout is less than until.
        """
        # create a challenge
        chall_id = create_challenge(until="2222-12-22T22:22:22Z", timeout=90)

        r = post_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = patch_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        # remove
        delete_challenge(chall_id)

    def test_renew_until_timeout_instance_ko(self):
        """
        This test try to renew an instance with until and timeout define.
        User cannot deploy an instance if a timeout is defined and now+timeout
        is greater than until.
        """
        # create a challenge

        # get the current date
        now = datetime.datetime.now()
        # add 10 minutes to the current date
        until = now + datetime.timedelta(minutes=30)
        # format the date to string
        formated_until = until.strftime("%Y-%m-%dT%H:%M:%SZ")

        chall_id = create_challenge(until=formated_until, timeout=999999999)
        r = post_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = get_instance(chall_id)
        a = json.loads(r.text)
        before = a["data"]["until"]
        self.assertEqual(before, formated_until)

        r = patch_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = get_instance(chall_id)
        a = json.loads(r.text)
        after = a["data"]["until"]
        self.assertEqual(after, before)

        # remove
        delete_challenge(chall_id)

    def test_create_instance_with_additional(self):
        """
        Checks that user can create an instance where additional is defined.
        """
        chall_id = create_challenge(additional={"test": "test"})
        r = post_instance(chall_id)

        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = get_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        # self.assertEqual(a["data"]["additional"]["test"], "test") # check that is not empty ?

        delete_challenge(chall_id)

    def test_create_instance_pooled(self):
        """
        Checks that user can get an instance immediately from the Pool.
        """
        chall_id = create_challenge(pooler_min=1, pooler_max=1)

        time.sleep(10)  # wait the pooler

        before = datetime.datetime.now()
        r = post_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        after = datetime.datetime.now()

        delai = abs((after - before).total_seconds())
        if delai > 0.5:
            raise TimeoutError("too slow bro")

        r = get_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        delete_challenge(chall_id)

import datetime
import unittest
import requests
import json
import threading
import time

from .utils import config, get_instance, post_instance, patch_instance, delete_instance, run_post_instance, create_challenge, delete_challenge

class Test_F_UserInstance(unittest.TestCase):
    def test_create_patch_delete_visible_challenge(self):
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
        r = post_instance(9999)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

    def test_delete_invalid_challenge(self):
        r = delete_instance(9999)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

    def test_delete_valid_challenge_but_no_instance(self):
        chall_id = create_challenge()

        r = delete_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

        delete_challenge(chall_id)

    def test_patch_valid_challenge_but_no_instance(self):
        chall_id = create_challenge()

        r = patch_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

        delete_challenge(chall_id)

    def test_get_missing_arg(self):
        r = requests.get(f"{config.plugin_url}/instance",  headers=config.headers_user)
        self.assertEqual(r.status_code, 400)

    def test_post_missing_arg(self):
        r = requests.post(f"{config.plugin_url}/instance",  headers=config.headers_user)
        self.assertEqual(r.status_code, 400)

    def test_patch_missing_arg(self):
        r = requests.patch(f"{config.plugin_url}/instance",  headers=config.headers_user)
        self.assertEqual(r.status_code, 400)

    def test_delete_missing_arg(self):
        r = requests.delete(f"{config.plugin_url}/instance",  headers=config.headers_user)
        self.assertEqual(r.status_code, 400)

    def test_cannot_create_same_chall_twice(self):
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
        This test perform 3 creation requests in parallel but only 2 must be approved.
        """
        results = {}
        lock = threading.Lock()

        chall_id1 = create_challenge(mana_cost=5)
        chall_id2 = create_challenge(mana_cost=5)
        chall_id3 = create_challenge(mana_cost=5)

        # Create threads for each instance
        thread1 = threading.Thread(target=run_post_instance, args=(chall_id1, results, lock))
        thread2 = threading.Thread(target=run_post_instance, args=(chall_id2, results, lock))
        thread3 = threading.Thread(target=run_post_instance, args=(chall_id3, results, lock))

        # Start all threads
        thread1.start()
        thread2.start()
        thread3.start()

        # Wait for all threads to complete
        thread1.join()
        thread2.join()
        thread3.join()

        # Initialize the result dictionary
        formatted_result = {'success': [], 'failure': []}

        # Iterate through the results and categorize the IDs based on success
        for instance_id, result in results.items():
            if result['success']:
                formatted_result['success'].append(instance_id)
            else:
                formatted_result['failure'].append(instance_id)


        self.assertEqual(len(formatted_result['success']), 2)
        self.assertEqual(len(formatted_result['failure']), 1)

        # Clean test environment
        for i in formatted_result['success']:
            delete_instance(i)

        delete_challenge(chall_id1)
        delete_challenge(chall_id2)
        delete_challenge(chall_id3)

    def test_hidden_challenge(self):
        '''
        This test try to deploy an instance on hidden challenge. 
        User cannot deploy an instance if the challenge is hidden.
        '''
        # create a hidden challenge
        chall_id = create_challenge(state="hidden")

        r = post_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False) # user cannot deploy instance 

        r = get_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False) # user cannot deploy instance 

        # remove 
        delete_challenge(chall_id)


    def test_cannot_renew_until_instance(self):
        '''
        This test try to renew an instance until the instance is deployed.
        User cannot renew an instance if a timeout is not defined.
        '''
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
        '''
        This test try to renew an instance until the instance is deployed.
        User can deploy an instance if a timeout is defined and now+timeout is less than until.
        '''
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
        '''
        This test try to renew an instance until the instance is deployed.
        User cannot deploy an instance if a timeout is defined and now+timeout is greater than until.
        '''
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
        chall_id = create_challenge(min=1, max=1)

        time.sleep(10) # wait the pooler

        before = datetime.datetime.now()
        r = post_instance(chall_id)   
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        after = datetime.datetime.now()

        delai = abs((after - before).total_seconds())
        if delai > 0.5:
            raise Exception("too slow bro")
        
        r = get_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        delete_challenge(chall_id)

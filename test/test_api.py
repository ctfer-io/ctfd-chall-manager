import unittest
import requests
import json
import os 
import threading

ctfd_url = os.getenv("CTFD_URL")
base_url = f"{ctfd_url}/api/v1/plugins/ctfd-chall-manager"
ctfd_token_user = os.getenv("CTFD_API_TOKEN_USER")
ctfd_token_admin = os.getenv("CTFD_API_TOKEN_ADMIN")

headers_user = {
    "Accept": "application/json",
    "Authorization": f"Token {ctfd_token_user}",
    "Content-Type": "application/json"
}

headers_admin = {
    "Accept": "application/json",
    "Authorization": f"Token {ctfd_token_admin}",
    "Content-Type": "application/json"
}

def post_instance(challengeId: int):
    payload = {
        "challengeId": f"{challengeId}"
    }
    r = requests.post(f"{base_url}/instance", headers=headers_user, data=json.dumps(payload))
    return r

def get_instance(challengeId: int):
    r = requests.get(f"{base_url}/instance?challengeId={challengeId}",  headers=headers_user)
    return r

def delete_instance(challengeId: int):
    r = requests.delete(f"{base_url}/instance?challengeId={challengeId}",  headers=headers_user)
    return r

def patch_instance(challengeId: int): 
    r = requests.patch(f"{base_url}/instance?challengeId={challengeId}",  headers=headers_user)
    return r


def run_post_instance(challengeId: int, results: dict, lock: threading.Lock):
    r = post_instance(challengeId)
    with lock:
        # Store the result in a shared dictionary with the challengeId as the key
        results[challengeId] = json.loads(r.text)

class Test_F_UserMana(unittest.TestCase):
    def test_valid_get(self):
        r = requests.get(f"{base_url}/mana",  headers=headers_user)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

class Test_F_UserInstance(unittest.TestCase):
    def test_create_patch_delete_visible_challenge(self):
        r = get_instance(1)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = post_instance(1)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)        
        self.assertEqual("connectionInfo" in a["data"]["message"].keys(), True)

        r = get_instance(1)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        self.assertEqual("connectionInfo" in a["data"]["message"].keys(), True)

        r = patch_instance(1)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = delete_instance(1)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

    def test_create_invalid_challenge(self):
        r = post_instance(9999)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

    def test_delete_invalid_challenge(self):
        r = delete_instance(9999)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

    def test_delete_valid_challenge_but_no_instance(self):
        r = delete_instance(1)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

    def test_patch_valid_challenge_but_no_instance(self):
        r = patch_instance(1)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

    def test_get_missing_arg(self):
        r = requests.get(f"{base_url}/instance",  headers=headers_user)
        self.assertEqual(r.status_code, 400)

    def test_post_missing_arg(self):
        r = requests.post(f"{base_url}/instance",  headers=headers_user)
        self.assertEqual(r.status_code, 400)

    def test_patch_missing_arg(self):
        r = requests.patch(f"{base_url}/instance",  headers=headers_user)
        self.assertEqual(r.status_code, 400)

    def test_delete_missing_arg(self):
        r = requests.delete(f"{base_url}/instance",  headers=headers_user)
        self.assertEqual(r.status_code, 400)

    def test_cannot_create_same_chall_twice(self):
        r = post_instance(1)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)        
        self.assertEqual("connectionInfo" in a["data"]["message"].keys(), True)

        r = post_instance(1)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)   

        r = delete_instance(1)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

    def test_create_multi_instances(self):
        """
        This test perform 3 creation requests in parallel but only 2 must be approved.
        """
        results = {}
        lock = threading.Lock()

        # Create threads for each instance
        thread1 = threading.Thread(target=run_post_instance, args=(1, results, lock))
        thread2 = threading.Thread(target=run_post_instance, args=(2, results, lock))
        thread3 = threading.Thread(target=run_post_instance, args=(3, results, lock))

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


        # Clean test environment
        for i in formatted_result['success']:
            delete_instance(i)

        self.assertEqual(len(formatted_result['success']), 2)
        self.assertEqual(len(formatted_result['failure']), 1)

    def test_hidden_challenge(self):
        '''
        This test try to deploy an instance on hidden challenge. 
        User cannot deploy an instance if the challenge is hidden.
        '''
        # create a hidden challenge
        payload = {
            "name":"test",
            "category":"test",
            "description":"test",
            "initial":"500",
            "function":"linear",
            "decay":"10",
            "minimum":"10",
            "state":"hidden",
            "type":"dynamic_iac",
            "scenario_id": "1" # already push files
        }
        r = requests.post(f"{ctfd_url}/api/v1/challenges",  headers=headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True) 

        chall_id = a["data"]["id"]

        payload = {
            "challengeId": f"{chall_id}",
        }
        r = post_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False) # user cannot deploy instance 

        r = get_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False) # user cannot deploy instance 

        # remove 
        r = requests.delete(f"{ctfd_url}/api/v1/challenges/{chall_id}",  headers=headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True) 

class Test_F_AdminInstance(unittest.TestCase):
    def test_user_connection_is_denied(self):
        r = requests.get(f"{base_url}/admin/instance",  headers=headers_user)
        self.assertEqual(r.status_code, 403)
        r = requests.post(f"{base_url}/admin/instance",  headers=headers_user)
        self.assertEqual(r.status_code, 403)
        r = requests.patch(f"{base_url}/admin/instance",  headers=headers_user)
        self.assertEqual(r.status_code, 403)
        r = requests.delete(f"{base_url}/admin/instance",  headers=headers_user)
        self.assertEqual(r.status_code, 403)

    def test_valid_challenge_valid_source(self):
        challengeId = 1
        sourceId = 1

        r = requests.get(f"{base_url}/admin/instance?challengeId={challengeId}&sourceId={sourceId}",  headers=headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        payload = {
            "challengeId": f"{challengeId}",
            "sourceId": f"{sourceId}"
        }
        r = requests.post(f"{base_url}/admin/instance",  headers=headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = requests.get(f"{base_url}/admin/instance?challengeId={challengeId}&sourceId={sourceId}",  headers=headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        self.assertEqual("connectionInfo" in a["data"]["message"].keys(), True)

        r = requests.patch(f"{base_url}/admin/instance?challengeId={challengeId}&sourceId={sourceId}",  headers=headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = requests.delete(f"{base_url}/admin/instance?challengeId={challengeId}&sourceId={sourceId}",  headers=headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

    def test_invalid_challenge_valid_source(self):
        challengeId = 999999
        sourceId = 1

        r = requests.get(f"{base_url}/admin/instance?challengeId={challengeId}&sourceId={sourceId}",  headers=headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True) 

        payload = {
            "challengeId": f"{challengeId}",
            "sourceId": f"{sourceId}"
        }
        r = requests.post(f"{base_url}/admin/instance",  headers=headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

        r = requests.patch(f"{base_url}/admin/instance?challengeId={challengeId}&sourceId={sourceId}",  headers=headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

        r = requests.delete(f"{base_url}/admin/instance?challengeId={challengeId}&sourceId={sourceId}",  headers=headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

    def test_valid_challenge_unknown_source(self):
        challengeId = 1
        sourceId = 999999

        r = requests.get(f"{base_url}/admin/instance?challengeId={challengeId}&sourceId={sourceId}",  headers=headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True) 
        
        payload = {
            "challengeId": f"{challengeId}",
            "sourceId": f"{sourceId}"
        }
        r = requests.post(f"{base_url}/admin/instance",  headers=headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = requests.patch(f"{base_url}/admin/instance?challengeId={challengeId}&sourceId={sourceId}",  headers=headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = requests.delete(f"{base_url}/admin/instance?challengeId={challengeId}&sourceId={sourceId}",  headers=headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

    def test_delete_valid_challenge_but_no_instance(self):
        challengeId = 1
        sourceId = 999999
        r = requests.delete(f"{base_url}/admin/instance?challengeId={challengeId}&sourceId={sourceId}",  headers=headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

    def test_patch_valid_challenge_but_no_instance(self):
        challengeId = 1
        sourceId = 999999
        r = requests.patch(f"{base_url}/admin/instance?challengeId={challengeId}&sourceId={sourceId}",  headers=headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)
  
    def test_hidden_challenge(self):
        '''
        This test try to deploy an instance on hidden challenge. 
        Admin can deploy an instance event if the challenge is hidden.
        '''                
        # create a hidden challenge
        payload = {
            "name":"test",
            "category":"test",
            "description":"test",
            "initial":"500",
            "function":"linear",
            "decay":"10",
            "minimum":"10",
            "state":"hidden",
            "type":"dynamic_iac",
            "scenario_id": "1"
        }
        r = requests.post(f"{ctfd_url}/api/v1/challenges",  headers=headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True) 

        chall_id = a["data"]["id"]
        sourceId = 1

        payload = {
            "challengeId": f"{chall_id}",
            "sourceId": f"{sourceId}"
        }
        r = requests.post(f"{base_url}/admin/instance",  headers=headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True) # admin can deploy instance 

        r = requests.get(f"{base_url}/admin/instance?challengeId={chall_id}&sourceId={sourceId}",  headers=headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True) # admin can deploy instance 

        r = requests.delete(f"{ctfd_url}/api/v1/challenges/{chall_id}",  headers=headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True) 

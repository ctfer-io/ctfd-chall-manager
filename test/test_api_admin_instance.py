import requests
import json
import unittest

from .utils import config, create_challenge, delete_challenge

class Test_F_AdminInstance(unittest.TestCase):

    def test_user_connection_is_denied(self):
        r = requests.get(f"{config.plugin_url}/admin/instance",  headers=config.headers_user)
        self.assertEqual(r.status_code, 403)
        r = requests.post(f"{config.plugin_url}/admin/instance",  headers=config.headers_user)
        self.assertEqual(r.status_code, 403)
        r = requests.patch(f"{config.plugin_url}/admin/instance",  headers=config.headers_user)
        self.assertEqual(r.status_code, 403)
        r = requests.delete(f"{config.plugin_url}/admin/instance",  headers=config.headers_user)
        self.assertEqual(r.status_code, 403)

    def test_valid_challenge_valid_source(self):

        challengeId = create_challenge(timeout=9999)
        sourceId = 1 

        r = requests.get(f"{config.plugin_url}/admin/instance?challengeId={challengeId}&sourceId={sourceId}",  headers=config.headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        payload = {
            "challengeId": f"{challengeId}",
            "sourceId": f"{sourceId}"
        }
        r = requests.post(f"{config.plugin_url}/admin/instance",  headers=config.headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = requests.get(f"{config.plugin_url}/admin/instance?challengeId={challengeId}&sourceId={sourceId}",  headers=config.headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        self.assertEqual("connectionInfo" in a["data"].keys(), True)

        r = requests.patch(f"{config.plugin_url}/admin/instance",  headers=config.headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = requests.delete(f"{config.plugin_url}/admin/instance",  headers=config.headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        delete_challenge(challengeId)

    def test_invalid_challenge_valid_source(self):
        challengeId = 999999
        sourceId = 1 # TODO config

        r = requests.get(f"{config.plugin_url}/admin/instance?challengeId={challengeId}&sourceId={sourceId}",  headers=config.headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], False) 

        payload = {
            "challengeId": f"{challengeId}",
            "sourceId": f"{sourceId}"
        }
        r = requests.post(f"{config.plugin_url}/admin/instance",  headers=config.headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

        r = requests.patch(f"{config.plugin_url}/admin/instance",  headers=config.headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

        r = requests.delete(f"{config.plugin_url}/admin/instance",  headers=config.headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

    def test_valid_challenge_unknown_source(self):
        challengeId = create_challenge(timeout=9999)
        sourceId = 999999

        r = requests.get(f"{config.plugin_url}/admin/instance?challengeId={challengeId}&sourceId={sourceId}",  headers=config.headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True) 
        
        payload = {
            "challengeId": f"{challengeId}",
            "sourceId": f"{sourceId}"
        }
        r = requests.post(f"{config.plugin_url}/admin/instance",  headers=config.headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = requests.patch(f"{config.plugin_url}/admin/instance",  headers=config.headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = requests.delete(f"{config.plugin_url}/admin/instance",  headers=config.headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)
        
        delete_challenge(challengeId)

    def test_delete_valid_challenge_but_no_instance(self):
        challengeId = create_challenge()
        sourceId = 999999
        payload = {
            "challengeId": f"{challengeId}",
            "sourceId": f"{sourceId}"
        }

        r = requests.delete(f"{config.plugin_url}/admin/instance",  headers=config.headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)
        delete_challenge(challengeId)

    def test_patch_valid_challenge_but_no_instance(self):
        challengeId = create_challenge(timeout=9999)
        sourceId = 999999
        payload = {
            "challengeId": f"{challengeId}",
            "sourceId": f"{sourceId}"
        }

        r = requests.patch(f"{config.plugin_url}/admin/instance",  headers=config.headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], False)

        delete_challenge(challengeId)
  
    def test_hidden_challenge(self):
        '''
        This test try to deploy an instance on hidden challenge. 
        Admin can deploy an instance event if the challenge is hidden.
        '''                

        chall_id = create_challenge(state="hidden")
        sourceId = 1 # TODO config

        payload = {
            "challengeId": f"{chall_id}",
            "sourceId": f"{sourceId}"
        }
        r = requests.post(f"{config.plugin_url}/admin/instance",  headers=config.headers_admin, data=json.dumps(payload))
        a = json.loads(r.text)
        self.assertEqual(a["success"], True) # admin can deploy instance 

        r = requests.get(f"{config.plugin_url}/admin/instance?challengeId={chall_id}&sourceId={sourceId}",  headers=config.headers_admin)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True) # admin can deploy instance 

        delete_challenge(chall_id)
import unittest
import requests
import json
import os 

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

# TODO add test_hidden_challenge()
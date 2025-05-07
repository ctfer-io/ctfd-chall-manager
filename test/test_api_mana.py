import requests
import json
import unittest

from .utils import config, create_challenge, post_instance, delete_challenge, delete_instance

class Test_F_UserMana(unittest.TestCase):
    def test_valid_get(self):
        r = requests.get(f"{config.plugin_url}/mana",  headers=config.headers_user)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)


    def test_mana_is_consum(self):
        mana_cost = 5
        chall_id = create_challenge(mana_cost=mana_cost)

        r = requests.get(f"{config.plugin_url}/mana",  headers=config.headers_user)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = post_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = requests.get(f"{config.plugin_url}/mana",  headers=config.headers_user)
        a = json.loads(r.text)
        self.assertEqual(a["data"]["used"], str(mana_cost))

        r = delete_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        delete_challenge(chall_id)

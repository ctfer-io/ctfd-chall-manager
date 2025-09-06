"""
This module defines tests cases on /mana
"""

import json
import unittest

import requests

from .utils import (config, create_challenge, delete_challenge,
                    delete_instance, post_instance)


# pylint: disable=invalid-name,missing-timeout,duplicate-code
class Test_F_UserMana(unittest.TestCase):
    """
    Test_F_UserMana defines tests cases on /mana
    """

    def test_valid_get(self):
        """
        Checks that user can retrieve its mana used.
        """
        r = requests.get(f"{config.plugin_url}/mana", headers=config.headers_user)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

    def test_mana_is_consum(self):
        """
        Checks that mana is consum if user deploy instance..
        """
        mana_cost = 5
        chall_id = create_challenge(mana_cost=mana_cost)

        r = requests.get(f"{config.plugin_url}/mana", headers=config.headers_user)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = post_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        r = requests.get(f"{config.plugin_url}/mana", headers=config.headers_user)
        a = json.loads(r.text)
        self.assertEqual(a["data"]["used"], mana_cost)

        r = delete_instance(chall_id)
        a = json.loads(r.text)
        self.assertEqual(a["success"], True)

        delete_challenge(chall_id)

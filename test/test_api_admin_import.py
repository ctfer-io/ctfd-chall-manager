"""
This module defines all tests cases for the /admin/import endpoint.
"""

import json
import unittest

import requests

from .utils import config, create_challenge


# pylint: disable=invalid-name,missing-timeout,duplicate-code
class Test_F_AdminInstance(unittest.TestCase):
    """
    Test_F_AdminInstance defines all tests cases for the /admin/import endpoint.
    """

    def test_user_connection_is_denied(self):
        """
        Performs calls on admin endpoint with user account.
        Must be denied on all.
        """
        r = requests.post(
            f"{config.plugin_url}/admin/import", headers=config.headers_user
        )
        self.assertEqual(r.status_code, 403)


    def test_import_missing_challenge(self):
        """
        Performs test to create an instance for a challenge that exists
        and for a source that exists.
        """

        challengeId = create_challenge()

        # delete it in chall-manager
        r = requests.delete(f"http://localhost:8080/api/v1/challenge/{challengeId}") # chall-manager 
        self.assertEqual(r.status_code, 200)

        payload = {
            "challengeId": challengeId
        }

        r = requests.post(
            f"{config.plugin_url}/admin/import", 
            headers=config.headers_admin,
            data=json.dumps(payload),
        )
        self.assertEqual(r.status_code, 200)

    def test_import_existing_challenge(self):
        """
        Performs test to create an instance for a challenge that exists
        and for a source that exists.
        """

        challengeId = create_challenge()

        payload = {
            "challengeId": challengeId
        }

        r = requests.post(
            f"{config.plugin_url}/admin/import", 
            headers=config.headers_admin,
            data=json.dumps(payload),
        )
        self.assertEqual(r.status_code, 409) # already exists


    def test_import_wihtout_challenge_id(self):
        r = requests.post(
            f"{config.plugin_url}/admin/import", 
            headers=config.headers_admin,
        )
        self.assertEqual(r.status_code, 400)
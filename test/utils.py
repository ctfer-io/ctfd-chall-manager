# pylint: disable=missing-timeout
"""
This module defines the Config to use to tests cases and
helper functions inside tests cases.
"""

import json
import os
import threading

import requests


class Config:  # pylint: disable=too-few-public-methods,too-many-instance-attributes
    """
    Config class purpose is to configure testing environemnt.
    """

    def __init__(self):
        self.ctfd_url = os.getenv("CTFD_URL", "http://localhost:8000")
        self.plugin_url = f"{self.ctfd_url}/api/v1/plugins/ctfd-chall-manager"

        self.ctfd_token_user = os.getenv("CTFD_API_TOKEN_USER")
        self.ctfd_token_admin = os.getenv("CTFD_API_TOKEN_ADMIN")

        if not self.ctfd_token_user or not self.ctfd_token_admin:
            raise AttributeError("missing CTFD_API_TOKEN_USER or CTFD_API_TOKEN_ADMIN")

        self.headers_admin = {
            "Accept": "application/json",
            "Authorization": f"Token {self.ctfd_token_admin}",
            "Content-Type": "application/json",
        }

        self.headers_user = {
            "Accept": "application/json",
            "Authorization": f"Token {self.ctfd_token_user}",
            "Content-Type": "application/json",
        }

        # This ref need to be pushed before start testing
        self.scenario = "registry:5000/examples/deploy:latest"
        self.scenario2 = "registry:5000/examples/deploy:v2"

    def __repr__(self):
        return f"<Config {self.__dict__}>"


config = Config()


# pylint: disable=dangerous-default-value,too-many-arguments,too-many-positional-arguments,duplicate-code
# skipping linting for tests only function (will be fix later)
def create_challenge(
    shared=False,
    destroy_on_flag=False,
    mana_cost=None,
    timeout=None,
    until=None,
    additional={},
    pooler_min=None,
    pooler_max=None,
    logic=None,
    state="visible",
):
    """
    Create challenge based on arguments.
    """

    payload = {
        "name": "test",
        "category": "test",
        "description": "test",
        "initial": "500",
        "function": "linear",
        "decay": "10",
        "minimum": "10",
        "type": "dynamic_iac",
        "scenario": config.scenario,
        "shared": shared,
        "destroy_on_flag": destroy_on_flag,
        "additional": additional,
        "state": state,
    }

    if mana_cost:
        payload["mana_cost"] = mana_cost

    if pooler_min:
        payload["min"] = pooler_min

    if pooler_max:
        payload["max"] = pooler_max

    if timeout:
        payload["timeout"] = timeout

    if until:
        payload["until"] = until

    # CTFd 3.8.0 new feature
    if logic in ["any", "all", "team"]:
        payload["logic"] = logic

    r = requests.post(
        f"{config.ctfd_url}/api/v1/challenges",
        headers=config.headers_admin,
        data=json.dumps(payload),
    )
    a = json.loads(r.text)
    if a["success"] is not True:
        raise ValueError(
            f"error while setting up the testing environment, do not process: {a}"
        )

    # return the chall_id
    return a["data"]["id"]


def delete_challenge(challenge_id: int):
    """
    Delete challenge based on challenge_id using user account.
    """
    r = requests.delete(
        f"{config.ctfd_url}/api/v1/challenges/{challenge_id}",
        headers=config.headers_admin,
    )
    a = json.loads(r.text)
    if a["success"] is not True:
        raise ValueError(
            f"error while setting up the testing environment, do not process: {a}"
        )


# region /instance
# readable function to manipulate CRUD operation as user on /instance
def post_instance(challenge_id: int):
    """
    Create an instance of challenge_id using user account.
    """
    payload = {"challengeId": f"{challenge_id}"}
    r = requests.post(
        f"{config.plugin_url}/instance",
        headers=config.headers_user,
        data=json.dumps(payload),
    )
    return r


def get_instance(challenge_id: int):
    """
    Retrieve informations on given challenge_id using user account.
    """
    r = requests.get(
        f"{config.plugin_url}/instance?challengeId={challenge_id}",
        headers=config.headers_user,
    )
    return r


def get_admin_instance(challenge_id: int, source_id: int):
    """
    Retrieve instance information from the challenge_id and source_id using admin account.
    """
    r = requests.get(
        f"{config.plugin_url}/admin/instance?challengeId={challenge_id}&sourceId={source_id}",
        headers=config.headers_admin,
    )
    return r


def delete_instance(challenge_id: int):
    """
    Delete instance of challenge_id using user account.
    """
    payload = {"challengeId": f"{challenge_id}"}
    r = requests.delete(
        f"{config.plugin_url}/instance",
        headers=config.headers_user,
        data=json.dumps(payload),
    )
    return r


def patch_instance(challenge_id: int):
    """
    Renew instance of challenge_id using user account.
    """
    payload = {"challengeId": f"{challenge_id}"}
    r = requests.patch(
        f"{config.plugin_url}/instance",
        headers=config.headers_user,
        data=json.dumps(payload),
    )
    return r


# Run post on thread
def run_post_instance(challenge_id: int, results: dict, lock: threading.Lock):
    """
    Runs post_instance function in parallel.
    """
    r = post_instance(challenge_id)
    with lock:
        # Store the result in a shared dictionary with the challengeId as the key
        results[challenge_id] = json.loads(r.text)


def get_source_id():
    """
    Retrieve source_id of the current user based on user_mode configured.
    """
    r = requests.get(
        f"{config.ctfd_url}/api/v1/configs/user_mode", headers=config.headers_admin
    )
    a = json.loads(r.text)

    user_mode = a["data"]["value"]

    r = requests.get(f"{config.ctfd_url}/api/v1/users/me", headers=config.headers_user)
    a = json.loads(r.text)

    source_id = a["data"]["id"]
    if user_mode == "teams":
        source_id = a["data"]["team_id"]

    return source_id


def reset_all_submissions():
    """
    Reset all submissions on CTFd.
    """
    r = requests.get(
        f"{config.ctfd_url}/api/v1/submissions", headers=config.headers_admin
    )
    a = json.loads(r.text)

    submissions = []
    for i in a["data"]:
        submissions.append(i["id"])

    for item in submissions:
        r = requests.delete(
            f"{config.ctfd_url}/api/v1/submissions/{item}", headers=config.headers_admin
        )

"""
This module defines the helpers functions.
"""

from CTFd.utils import user as current_user
from CTFd.utils.config import is_teams_mode
from flask import request


def retrieve_all_ids(admin=False) -> dict[str, int] | ValueError:
    """
    This function return all ids for AdminInstance calls.

    return: dict of {"user_id", "team_id", "source_id", "challenge_id"}
    """
    team_id = 0
    admin_id = 0

    user = current_user.get_current_user()
    user_id = int(user.id)

    if admin:
        admin_id = user_id

    # If GET
    challenge_id = request.args.get("challengeId")
    source_id = request.args.get("sourceId")

    if challenge_id is None or source_id is None:  # If POST/PATCH/DELETE
        data = request.get_json()
        challenge_id = data.get("challengeId")
        source_id = data.get("sourceId")

    if challenge_id is None or source_id is None:
        raise ValueError("missing challengeId or sourceId")

    challenge_id = int(challenge_id)
    source_id = int(source_id)

    if not admin:
        source_id = user_id
        if is_teams_mode():
            team_id = user.team_id
            if team_id is not None:
                source_id = int(team_id)

    return {
        "admin_id": admin_id,
        "user_id": user_id,
        "team_id": team_id,
        "source_id": source_id,
        "challenge_id": challenge_id,
    }

"""
This module defines decorators used by API endpoints.
"""

import functools

from CTFd.models import Challenges
from CTFd.utils.user import is_admin
from flask import request
from flask_restx import abort
from sqlalchemy.sql import and_


def challenge_visible(func):
    """
    This decorator abort the request if the challenge is not visible.
    The request is NOT abort if the user is admin.
    """

    @functools.wraps(func)
    def _challenge_visible(*args, **kwargs):
        # Get challengeId from query string
        challenge_id = request.args.get("challengeId")

        if not challenge_id:
            data = request.get_json()
            if data:
                challenge_id = data.get("challengeId")

        if not challenge_id:
            abort(400, "missing args", success=False)

        if is_admin():
            if not Challenges.query.filter(Challenges.id == challenge_id).first():
                abort(404, "no such challenge", success=False)
        else:
            if not Challenges.query.filter(
                Challenges.id == challenge_id,
                and_(Challenges.state != "hidden", Challenges.state != "locked"),
            ).first():
                abort(403, "challenge not visible", success=False)
        return func(*args, **kwargs)

    return _challenge_visible

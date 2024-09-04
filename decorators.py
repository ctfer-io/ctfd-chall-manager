import functools
import time
from flask import request, current_app, session
from flask_restx import abort
from sqlalchemy.sql import and_

from CTFd.models import Challenges # type: ignore
from CTFd.utils.user import is_admin # type: ignore

def challenge_visible(func):
    @functools.wraps(func)
    def _challenge_visible(*args, **kwargs):
        # Get challengeId from query string
        challengeId = request.args.get('challengeId')

        if not challengeId :
            data = request.get_json()
            if data:
                challengeId = data.get('challengeId')

        if not challengeId:
            abort(400, 'missing args', success=False)

        if is_admin():
            if not Challenges.query.filter(
                Challenges.id == challengeId
            ).first():
                abort(404, 'no such challenge', success=False)
        else:
            if not Challenges.query.filter(
                Challenges.id == challengeId,
                and_(Challenges.state != "hidden", Challenges.state != "locked"),
            ).first():
                abort(403, 'challenge not visible', success=False)
        return func(*args, **kwargs)

    return _challenge_visible

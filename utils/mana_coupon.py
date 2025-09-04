# pylint: disable=no-member
"""
This module contains all functions for mana resources.
"""

from sqlalchemy import func

from CTFd.models import db  # type: ignore
from CTFd.utils import get_config

from CTFd.plugins.ctfd_chall_manager.models import DynamicIaCChallenge
from CTFd.plugins.ctfd_chall_manager.utils.instance_manager import query_instance
from CTFd.plugins.ctfd_chall_manager.utils.logger import configure_logger

# Configure logger for this module
logger = configure_logger(__name__)


class ManaCoupon(db.Model):
    """
    ManaCoupon class contains the metadata for a coupons to associate source_id and challenge_id.
    """

    id = db.Column(db.Integer, primary_key=True)

    challenge_id = db.Column(db.Integer)
    source_id = db.Column(db.Integer)
    mana_used = db.Column(db.Integer)

    def __repr__(self):
        return f"<ManaCoupon challenge_id: {self.challenge_id} source_id: {self.source_id} ManaCost:{self.mana_used}>"


def create_coupon(challenge_id: int, source_id: int):
    """
    Create a new coupon for the transaction for challenge_id and source_id

    :param challenge_id: ID of the challenge
    :param source_id: ID of the source (team_id or user_id based on user_mode)
    """
    challenge = DynamicIaCChallenge.query.filter_by(id=challenge_id).first()
    if not challenge:
        logger.error("challenge with ID %s not found.", challenge_id)
        return

    coupon = ManaCoupon(
        challenge_id=challenge_id, source_id=source_id, mana_used=challenge.mana_cost
    )
    logger.debug("creating coupon: %s", coupon)
    db.session.add(coupon)
    db.session.commit()


def delete_coupon(challenge_id: int, source_id: int):
    """
    Search and delete a coupon based on challenge_id and source_id

    :param challenge_id: ID of the challenge
    :param source_id: ID of the source (team_id or user_id based on user_mode)
    """
    coupon = ManaCoupon.query.filter_by(
        challenge_id=challenge_id, source_id=source_id
    ).first()
    if coupon:
        logger.debug("deleting coupon: %s", coupon)
        db.session.delete(coupon)
        db.session.commit()
    else:
        logger.warning(
            "no coupon found for challenge_id %s and source_id %s",
            challenge_id,
            source_id,
        )


def get_source_mana(source_id: int) -> int:
    """
    Calculate all mana used by source_id, this will also update coupons based on CM records.

    :param source_id: ID of the source (team_id or user_id based on user_mode)
    :return: Sum of mana used
    """
    # get all coupons that exist
    coupons = ManaCoupon.query.filter_by(source_id=source_id).all()

    # get all instances that exist on CM
    # TODO handle exception here
    instances = query_instance(source_id)
    logger.info("instances found: %s", instances)

    for c in coupons:
        exists = False
        for i in instances:
            if int(i["challengeId"]) == int(c.challenge_id):
                exists = True
                break

        if not exists:
            logger.info(
                "coupon %s does not match any existing instance, deleting it.", c
            )
            delete_coupon(c.challenge_id, source_id)

    result = (
        db.session.query(func.sum(ManaCoupon.mana_used).label("mana"))
        .filter_by(source_id=source_id)
        .first()
    )

    if result["mana"] is None:
        return 0

    return result["mana"]


def get_all_mana() -> list:
    """
    Calculate all mana used by all source_id based on existing coupons

    :return: list(map) [{ source_id: x, mana: y, remaining: z}, ..]
    """
    data = (
        db.session.query(
            ManaCoupon.source_id.label("id"),
            func.sum(ManaCoupon.mana_used).label("mana"),
        )
        .group_by(ManaCoupon.source_id)
        .all()
    )

    mana_total = get_config("chall-manager:chall-manager_mana_total")

    result = []
    for item in data:
        data = {}
        data["source_id"] = item[0]
        data["mana"] = item[1]
        data["remaining"] = f"{mana_total-item[1]}"
        result.append(data)

    logger.debug("mana usage data: %s", result)
    return result

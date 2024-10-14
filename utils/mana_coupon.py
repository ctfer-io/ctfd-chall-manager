from ..models import DynamicIaCChallenge

from CTFd.models import db  # type: ignore
from CTFd.utils import get_config  # type: ignore
from sqlalchemy import func

from .instance_manager import query_instance
from .logger import configure_logger

# Configure logger for this module
logger = configure_logger(__name__)

class ManaCoupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    challengeId = db.Column(db.Integer)
    sourceId = db.Column(db.Integer)
    mana_used = db.Column(db.Integer)
    
    def __repr__(self):
        return f"<ManaCoupon challengeId: {self.challengeId} sourceId: {self.sourceId} ManaCost:{self.mana_used}>"

def create_coupon(challengeId: int, sourceId: int):
    """
    Create a new coupon for the transaction for challengeId and sourceId

    :param challengeId: ID of the challenge 
    :param sourceId: ID of the source (team_id or user_id based on user_mode)
    """
    challenge = DynamicIaCChallenge.query.filter_by(id=challengeId).first()
    if not challenge:
        logger.error(f"Challenge with ID {challengeId} not found.")
        return

    coupon = ManaCoupon(challengeId=challengeId, sourceId=sourceId, mana_used=challenge.mana_cost)
    logger.debug(f"Creating coupon: {coupon}")
    db.session.add(coupon)
    db.session.commit()

def delete_coupon(challengeId: int, sourceId: int):
    """
    Search and delete a coupon based on challengeId and sourceId

    :param challengeId: ID of the challenge 
    :param sourceId: ID of the source (team_id or user_id based on user_mode)
    """
    coupon = ManaCoupon.query.filter_by(challengeId=challengeId, sourceId=sourceId).first()
    if coupon:
        logger.debug(f"Deleting coupon: {coupon}")
        db.session.delete(coupon)
        db.session.commit()
    else:
        logger.warning(f"No coupon found for challengeId {challengeId} and sourceId {sourceId}.")

def get_source_mana(sourceId: int) -> int:
    """
    Calculate all mana used by sourceId, this will also update coupons based on CM records.

    :param sourceId: ID of the source (team_id or user_id based on user_mode)
    :return: Sum of mana used 
    """
    # get all coupons that exist 
    coupons = ManaCoupon.query.filter_by(sourceId=sourceId).all()

    # get all instances that exist on CM
    instances = query_instance(sourceId)
    logger.info(f"Instances {instances}")

    for c in coupons:
        exists = False
        for i in instances:
            if int(i['challengeId']) == int(c.challengeId):
                exists = True
                break
    
        if not exists:
            logger.info(f"Coupon {c} does not match any existing instance, deleting it.")
            delete_coupon(c.challengeId, sourceId)

    result = db.session.query(
        func.sum(ManaCoupon.mana_used).label("mana")
    ).filter_by(sourceId=sourceId
    ).first()

    if result['mana'] is None:
        return 0 

    return result['mana']

def get_all_mana() -> list:
    """
    Calculate all mana used by all sourceId based on existing coupons

    :return: list(map) [{ sourceId: x, mana: y, remaining: z}, ..]
    """
    data = db.session.query(
        ManaCoupon.sourceId.label("id"),
        func.sum(ManaCoupon.mana_used).label("mana")
    ).group_by(ManaCoupon.sourceId
    ).all()

    mana_total = get_config('chall-manager:chall-manager_mana_total')

    result = []
    for item in data:
        data = {}
        data["sourceId"] = item[0]
        data["mana"] = item[1]
        data["remaining"] = f"{mana_total-item[1]}"
        result.append(data)

    logger.debug(f"Mana usage data: {result}")
    return result

from ..models import DynamicIaCChallenge

from CTFd.models import ( # type: ignore
    db,
)
from CTFd.utils import get_config # type: ignore
from sqlalchemy import func

from .instance_manager import query_instance


class ManaCoupon(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    challengeId = db.Column(db.Integer)
    sourceId = db.Column(db.Integer)
    mana_used = db.Column(db.Integer)
    
    @classmethod
    def __repr__(self):
        return f"<ManaCoupon {self.id} {self.challengeId} {self.sourceId} {self.mana_used}"


def create_coupon(challengeId: int, sourceId: int):
    """
    Create a new coupon for the transaction for challengeId and sourceId

    :param challengeId: ID of the challenge 
    :param sourceId: ID of the source (team_id or user_id based on user_mode)
    """
    challenge = DynamicIaCChallenge.query.filter_by(id=challengeId).first()  
    coupon = ManaCoupon(challengeId=challengeId, sourceId=sourceId, mana_used=challenge.mana_cost)
    print(f" creating {coupon}")  # TODO use logging
    db.session.add(coupon)
    db.session.commit()

def delete_coupon(challengeId: int, sourceId: int):
    """
    Search and delete a coupon based on challengeId and sourceId

    :param challengeId: ID of the challenge 
    :param sourceId: ID of the source (team_id or user_id based on user_mode)
    """
    coupon = ManaCoupon.query.filter_by(challengeId=challengeId, sourceId=sourceId).first()
    print(f" deleting {coupon}")  # TODO use logging
    db.session.delete(coupon)
    db.session.commit()


def get_source_mana(sourceId: int) -> int:
    """
    Calculate all mana used by sourceId, this will also update coupons based on CM records.

    :param sourceId: ID of the source (team_id or user_id based on user_mode)
    :return: Sum of mana used 
    """
    # get all coupons that exists 
    coupons = ManaCoupon.query.filter_by(sourceId=sourceId).all()

    # get all instances that exists on CM
    instances = query_instance(sourceId)

    for c in coupons:
        exists = False
        for i in instances:
            if int(i['challengeId']) == int(c.challengeId):
                exists = True
                break
    
        if not exists:
            delete_coupon(c.challengeId, sourceId)

    result = db.session.query(
        func.sum(ManaCoupon.mana_used).label("mana")
    ).filter_by(sourceId=sourceId
    ).first()

    if result['mana'] == None:
        return 0 

    return result['mana']

def get_all_mana() -> list:
    """
    Calculate all mana used by all sourceId based on existing coupons

    :return: list(map) [{ sourceId: x, mana: y, remaining: z}, ..]
    """
    # select u.id as id, COALESCE(SUM(t.mana_used),0) AS mana from mana_coupon t right join users u on t.sourceId = u.id group by u.id;
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

    return result
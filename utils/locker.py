import redis
import os
from redis.exceptions import LockError
import redis.lock

from .logger import configure_logger

logger = configure_logger(__name__)

# Get the Redis connection URL from the environment variable
REDIS_URL = os.getenv('REDIS_URL')
if REDIS_URL == None:
    logger.error(f"REDIS_URL not found, quitting")
    raise Exception("REDIS_URL not found, quitting")

logger.debug(f"REDIS_URL is {REDIS_URL}")

# Connect to the Redis server using the URL
redis_client = redis.Redis.from_url(REDIS_URL)
logger.debug(f"redis client configured succesfully")

class RWLock():
    def __init__(self, name):
        self.name = name

        # https://dl.acm.org/doi/pdf/10.1145/362759.362813

        self.m1 = redis_client.lock(name=f"{name}_m1")
        self.m2 = redis_client.lock(name=f"{name}_m2")

        self.r = redis_client.lock(name=f"{name}_r")
        self.w = redis_client.lock(name=f"{name}_w")

        self.g = redis_client.lock(name=f"{name}_g") # no concurrency reader


    def r_lock(self):
        logger.debug(f"{self.name}_r locked")
        logger.debug(f"{redis_client.get(f'{self.name}_readcount')}")
        try:

            self.r.acquire()
            self.m1.acquire()

            redis_client.incr(f"{self.name}_readcount")

            if redis_client.get(f"{self.name}_readcount") == 1:
                self.w.acquire()

            self.m1.release()
            self.r.release()

            self.g.acquire()

        except LockError as e:
            logger.warning(f"Failed to acquire lock due to error: {str(e)}")


    def r_unlock(self):
        logger.debug(f"{self.name}_r unlocked")
        try:
            self.g.release()

            self.m1.acquire()

            redis_client.decr(f"{self.name}_readcount")

            if redis_client.get(f"{self.name}_readcount") == 0:
                self.w.release()

            self.m1.release()

        except LockError as e:
            logger.warning(f"Failed to acquire lock due to error: {str(e)}")

    def rw_lock(self):
        logger.debug(f"{self.name}_rw locked")
        try:
            self.m2.acquire()

            redis_client.incr(f"{self.name}_writecount")

            if redis_client.get(f"{self.name}_writecount") == 1:
                self.r.acquire()

            self.m2.release()
            self.w.acquire()

        except LockError as e:
            logger.warning(f"Failed to acquire lock due to error: {str(e)}")

    def rw_unlock(self):
        logger.debug(f"{self.name}_rw unlocked")
        try:
            self.w.release()
            self.m2.acquire()

            redis_client.decr(f"{self.name}_writecount")
            if redis_client.get(f"{self.name}_writecount") == 0:
                self.r.release()

            self.m2.release()

        except LockError as e:
            logger.warning(f"Failed to acquire lock due to error: {str(e)}")

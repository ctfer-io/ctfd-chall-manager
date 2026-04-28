"""
This module implements the generic class used by the plugin to maintain synchronization
inside the plugin (i.e mana)
"""

import os
import threading

import redis
from CTFd.plugins.ctfd_chall_manager.utils.logger import configure_logger

logger = configure_logger(__name__)

# https://github.com/ctfer-io/ctfd-chall-manager/issues/141
lockers = {}
lockers_lock = threading.Lock()


REDIS_URL = os.getenv("REDIS_URL")
REDIS_CLIENT = None
if REDIS_URL:
    REDIS_CLIENT = redis.Redis.from_url(REDIS_URL)
    logger.info("redis lock configured successfully")
else:
    logger.info("local lock configured successfully")

lock_is_local = REDIS_CLIENT is None
logger.debug("distributed redis lock configured: %s", (not lock_is_local))


class Lock:
    """
    A class used to manage internal locks for synchronization.

    Attributes:
        name (str): The name of the lock.
        gr (threading.Lock or redis_client.lock): A lock object for global locking.
    """

    # <name>_gr is a lock made to block concurrency calls to chall-manager instances.
    # rw_lock system is an optional (and experimental) feature
    # that priorise the access of the <name>_gr lock.

    def __init__(self, name: str):
        """
        Initializes a new instance of the ManaLock class.

        Args:
            name (str): The name of the lock.
        """
        self.name = name
        self.gr = threading.Lock()
        if REDIS_CLIENT is not None:
            logger.debug("redis client found, use distributed cache")
            self.gr = REDIS_CLIENT.lock(name=f"{name}_gr", thread_local=False)

    def __repr__(self):
        return f"Lock name={self.name}"

    def is_locked(self) -> bool:
        """
        Returns True if this key is locked by any process, otherwise False.
        """
        return self.gr.locked()

    def lock(self):
        """
        Acquires the lock.
        """
        self.gr.acquire()

    def unlock(self):
        """
        Releases the lock.
        """
        self.gr.release()


def load_or_store(name: str) -> Lock:
    """
    Loads an existing lock or creates a new one if it doesn't exist.

    ``name`` (str): The name of the lock to be loaded or created.

    Return Lock: The loaded or newly created lock.

    Notes:
        - If the distributed lock system is activated, it returns a new ManaLock instance.
        - If the distributed lock system is not activated, it uses a local lock system.
        - The function ensures thread safety by acquiring and releasing a lock on the
        lockers dictionary.
    """

    if not lock_is_local:
        return Lock(name)

    try:

        logger.debug("distributed locking system not found, use local lock")
        # https://github.com/ctfer-io/ctfd-chall-manager/issues/179
        lockers_lock.acquire()  # pylint: disable=consider-using-with

        if name in lockers.keys():  # pylint: disable=consider-iterating-dictionary
            logger.debug("previous lock found in lockers, use previous")
            return lockers[name]

        logger.debug("previous lock NOT found, create new one")
        lock = Lock(name)
        lockers[name] = lock
    finally:
        lockers_lock.release()

    return lock

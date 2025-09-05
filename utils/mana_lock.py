"""
This module implements the generic class used by the plugin to maintain synchronization
on ManaCoupon.
"""

import os
import threading

from CTFd.plugins.ctfd_chall_manager.utils.locker import REDIS_CLIENT, create_rw_lock
from CTFd.plugins.ctfd_chall_manager.utils.logger import configure_logger

logger = configure_logger(__name__)

# https://github.com/ctfer-io/ctfd-chall-manager/issues/141
lockers = {}
lockers_lock = threading.Lock()
lock_is_local = os.getenv("REDIS_URL") is None
rw_lock_enabled = (
    os.getenv("PLUGIN_SETTINGS_CM_EXPERIMENTAL_RWLOCK", "false").lower() == "true"
)


class ManaLock:
    """
    A class used to manage locks for ManaCoupon synchronization.

    Attributes:
        name (str): The name of the lock.
        rw (RWLock): An instance of RWLock for read-write locking.
        gr (threading.Lock or redis_client.lock): A lock object for general locking.
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

        if rw_lock_enabled:
            logger.debug("experimental rwlock configured")
            self.rw = create_rw_lock(name)

        self.gr = threading.Lock()
        if REDIS_CLIENT is not None:
            logger.debug("redis client found, use distributed cache")
            self.gr = REDIS_CLIENT.lock(name=f"{name}_gr", thread_local=False)

    def __repr__(self):
        return f"ManaLock name={self.name}"

    def player_lock(self):
        """
        Acquires the lock for a player.
        """
        if rw_lock_enabled:
            self.rw.r_lock()

        self.gr.acquire()

    def player_unlock(self):
        """
        Releases the lock for a player.
        """
        self.gr.release()

        if rw_lock_enabled:
            self.rw.r_unlock()

    def admin_lock(self):
        """
        Acquires the lock for an admin.
        """
        if rw_lock_enabled:
            self.rw.rw_lock()
        self.gr.acquire()

    def admin_unlock(self):
        """
        Releases the lock for an admin.
        """
        self.gr.release()

        if rw_lock_enabled:
            self.rw.rw_unlock()


def load_or_store(name: str) -> ManaLock:
    """
    Loads an existing lock or creates a new one if it doesn't exist.

    ``name`` (str): The name of the lock to be loaded or created.

    Return ManaLock: The loaded or newly created lock.

    Notes:
        - If the distributed lock system is activated, it returns a new ManaLock instance.
        - If the distributed lock system is not activated, it uses a local lock system.
        - The function ensures thread safety by acquiring and releasing a lock on the lockers dictionary.
    """

    if not lock_is_local:
        logger.debug("distributed lock activated, use redis remote lock")
        return ManaLock(name)

    try:

        logger.debug("distributed locking system not found, use local lock")
        lockers_lock.acquire()

        if name in lockers.keys():
            logger.debug("previous lock found in lockers, use previous")
            return lockers[name]

        logger.debug("previous lock NOT found, create new one")
        lock = ManaLock(name)
        lockers[name] = lock
    finally:
        lockers_lock.release()

    return lock

import os
import threading

from .locker import RWLock, redis_client
from .logger import configure_logger

logger = configure_logger(__name__)

# https://github.com/ctfer-io/ctfd-chall-manager/issues/141
lockers = {}
lockers_lock  = threading.Lock()
lock_is_local = os.getenv('REDIS_URL') == None
rw_lock = os.getenv("PLUGIN_SETTINGS_CM_EXPERIMENTAL_RWLOCK") != None

class ManaLock():
    # <name>_gr is a lock made to block concurrency calls to chall-manager instances and mana coupons.
    # rw_lock system is an optional (and experimental) feature that priorise the access of the <name>_gr lock.

    def __init__(self, name: str):
        self.name = name

        self.rw = None
        if rw_lock:
            logger.debug("experimental rwlock configured")
            self.rw = RWLock(name)

        self.gr = threading.Lock()
        if redis_client != None:
            logger.debug("redis client found, use distributed cache")
            self.gr = redis_client.lock(name=f"{name}_gr", thread_local=False)
        

    def player_lock(self):
        if rw_lock:
            self.rw.r_lock()

        self.gr.acquire()

    def player_unlock(self):
        self.gr.release()

        if rw_lock:
            self.rw.r_unlock()

    def admin_lock(self):
        if rw_lock:
            self.rw.rw_lock()
        self.gr.acquire()

    def admin_unlock(self):
        self.gr.release()

        if rw_lock:
            self.rw.rw_unlock()


def load_or_store(name: str) -> ManaLock:
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

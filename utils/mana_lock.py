import threading

from .locker import RWLock, redis_client
from .logger import configure_logger

logger = configure_logger(__name__)

class ManaLock():
    def __init__(self, name: str):
        self.name = name

        self.rw = RWLock(name)

        self.gr = threading.Lock()
        if redis_client != None:
            self.gr = redis_client.lock(name=f"{name}_gr", thread_local=False)
        

    def player_lock(self):
        self.rw.r_lock()
        self.gr.acquire()

    def player_unlock(self):
        self.gr.release()
        self.rw.r_unlock()

    def admin_lock(self):
        self.rw.rw_lock()

    def admin_unlock(self):
        self.rw.rw_unlock()

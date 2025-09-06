"""
This modules implements RWLock with Writer preference system based
on https://dl.acm.org/doi/pdf/10.1145/362759.362813 (Problem 2).

Classes:
    RWLockInterface: An abstract base class for read-write lock interfaces.
    ThreadingRWLock: A concrete implementation of RWLockInterface using threading locks.
    RedisRWLock: A concrete implementation of RWLockInterface using Redis locks.

Functions:
    RWLock: A factory function that returns an instance of either ThreadingRWLock or RedisRWLock
            based on the availability of a Redis URL.
"""

import os
import threading
from abc import ABC, abstractmethod

import redis
from CTFd.plugins.ctfd_chall_manager.utils.logger import configure_logger
from redis.exceptions import LockError

logger = configure_logger(__name__)

REDIS_URL = os.getenv("REDIS_URL")
REDIS_CLIENT = None
if REDIS_URL:
    REDIS_CLIENT = redis.Redis.from_url(REDIS_URL)
    logger.info("redis lock configured successfully")
else:
    logger.info("local lock configured successfully")


# pylint: disable=consider-using-with
# see https://github.com/ctfer-io/ctfd-chall-manager/issues/179


class RWLockInterface(ABC):
    """
    An abstract base class for read-write lock interfaces.
    """

    @abstractmethod
    def r_lock(self) -> None:
        """
        Acquire a read lock.
        """

    @abstractmethod
    def r_unlock(self) -> None:
        """
        Release a read lock.
        """

    @abstractmethod
    def rw_lock(self) -> None:
        """
        Acquire a read-write lock.
        """

    @abstractmethod
    def rw_unlock(self) -> None:
        """
        Release a read-write lock.
        """


# pylint: disable=too-many-instance-attributes
class ThreadingRWLock(RWLockInterface):
    """
    A concrete implementation of RWLockInterface using threading locks.
    This class must be used **only** on a standalone CTFd instance.
    """

    def __init__(self, name: str):
        """
        Initialize the ThreadingRWLock with a name.

        ``name`` (str): The name of the lock.
        """
        self.name = name

        self.m1 = threading.Lock()
        self.m2 = threading.Lock()
        self.m3 = threading.Lock()

        self.r = threading.Lock()
        self.w = threading.Lock()

        self.rcounter = int(0)
        self.wcounter = int(0)

    def r_lock(self) -> None:
        try:
            self.m3.acquire()
            self.r.acquire()
            self.m1.acquire()

            self.rcounter = self.rcounter + 1

            if self.rcounter == 1:
                self.w.acquire()

        finally:
            self.m1.release()
            self.r.release()
            self.m3.release()

    def r_unlock(self) -> None:
        try:
            self.m1.acquire()

            self.rcounter = self.rcounter - 1

            if self.rcounter == 0:
                self.w.release()

        finally:
            self.m1.release()

    def rw_lock(self) -> None:
        try:
            self.m2.acquire()

            self.wcounter = self.wcounter + 1

            if self.wcounter == 1:
                self.r.acquire()

        finally:
            self.m2.release()
            self.w.acquire()

    def rw_unlock(self) -> None:
        try:
            self.w.release()
            self.m2.acquire()

            self.wcounter = self.wcounter - 1

            if self.wcounter == 0:
                self.r.release()

        finally:
            self.m2.release()


# pylint: disable=too-many-instance-attributes
class RedisRWLock(RWLockInterface):
    """
    A concrete implementation of RWLockInterface using Redis locks.
    This class can be used for standalone or multiple CTFd instances for
    synchronization among instances.
    """

    def __init__(self, name: str):
        """
        Initialize the RedisRWLock with a name.

        ``name`` (str): The name of the lock.
        """
        self.name = name

        # https://dl.acm.org/doi/pdf/10.1145/362759.362813

        self.m1 = REDIS_CLIENT.lock(name=f"{name}_m1", thread_local=False)
        self.m2 = REDIS_CLIENT.lock(name=f"{name}_m2", thread_local=False)
        self.m3 = REDIS_CLIENT.lock(name=f"{name}_m3", thread_local=False)

        self.r = REDIS_CLIENT.lock(name=f"{name}_r", thread_local=False)
        self.w = REDIS_CLIENT.lock(name=f"{name}_w", thread_local=False)

        if REDIS_CLIENT.get(f"{self.name}_readcount") is None:
            REDIS_CLIENT.set(f"{self.name}_readcount", 0)

        if REDIS_CLIENT.get(f"{self.name}_writecount") is None:
            REDIS_CLIENT.set(f"{self.name}_writecount", 0)

    def r_lock(self) -> None:
        try:
            self.m3.acquire()
            self.r.acquire()
            self.m1.acquire()

            REDIS_CLIENT.incr(f"{self.name}_readcount")

            if int(REDIS_CLIENT.get(f"{self.name}_readcount")) == 1:
                self.w.acquire()

        except LockError as e:
            logger.warning("failed to acquire lock due to error: %s", e)

        finally:
            self.m1.release()
            self.r.release()
            self.m3.release()

    def r_unlock(self) -> None:
        try:
            self.m1.acquire()

            REDIS_CLIENT.decr(f"{self.name}_readcount")

            if int(REDIS_CLIENT.get(f"{self.name}_readcount")) == 0:
                REDIS_CLIENT.delete(f"{self.name}_w")

        except LockError as e:
            logger.warning("failed to release lock due to error: %s", e)

        finally:
            self.m1.release()

    def rw_lock(self) -> None:
        try:
            self.m2.acquire()

            REDIS_CLIENT.incr(f"{self.name}_writecount")

            if int(REDIS_CLIENT.get(f"{self.name}_writecount")) == 1:
                self.r.acquire()

        except LockError as e:
            logger.warning("failed to acquire lock due to error: %s", e)

        finally:
            self.m2.release()
            self.w.acquire()

    def rw_unlock(self) -> None:
        logger.debug("%s_rw unlocked", self.name)
        try:
            REDIS_CLIENT.delete(f"{self.name}_w")
            self.m2.acquire()

            REDIS_CLIENT.decr(f"{self.name}_writecount")
            if int(REDIS_CLIENT.get(f"{self.name}_writecount")) == 0:
                REDIS_CLIENT.delete(f"{self.name}_r")

        except LockError as e:
            logger.warning("failed to release lock due to error: %s", e)

        finally:
            self.m2.release()


def create_rw_lock(name: str) -> RWLockInterface:
    """
    A factory function that returns an instance of either ThreadingRWLock or RedisRWLock
    based on the availability of a Redis URL.

    ``name`` (str): The name of the lock.

    Return an instance of either ThreadingRWLock or RedisRWLock.
    """
    if REDIS_URL:
        logger.debug("initiate RedisRWLock for %s", name)
        return RedisRWLock(name)

    logger.debug("initiate ThreadingRWLock for %s", name)
    return ThreadingRWLock(name)

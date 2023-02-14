# -*- coding: utf-8 -*-

"""
Submit base class
"""
import abc
import threading

from src import util
from src.core.reentrant_timer import ReentrantTimer
from src.logger import Logger


class SubmitBase(object, metaclass=abc.ABCMeta):
    def __init__(self, capacity: int = 20, timeout: float = 10.0, queue_capacity=20):
        self.capacity = capacity
        self.timeout = timeout
        self.buf = []
        self.mutex = threading.Lock()
        self.submit_mutex = threading.Lock()

        # self.timer = threading.Timer(self.timeout, self._timerEvent)
        self.timer = ReentrantTimer(self.timeout, self._timerEvent)

        self.logger = Logger().getLogger(__name__)

    def __del__(self):
        if isinstance(self.timer, ReentrantTimer) and self.timer.is_alive():
            self.timer.cancel()

    @abc.abstractmethod
    def _send(self) -> bool:
        raise NotImplementedError()

    def doSend(self):
        if self.mutex.locked():
            return
        if self.mutex.acquire(blocking=False):
            self.logger.debug("Ready to send result")
            try:
                result = self._send()
                if result:
                    self.logger.debug("Result submitted")
                    self.buf = []
            finally:
                self.mutex.release()

    def _checkBuf(self):
        if len(self.buf) >= self.capacity:
            self.doSend()

    def _timerEvent(self):
        if len(self.buf) == 0:
            self.logger.debug("Submit timer trigger with no buffer data")
            return
        self.doSend()

    def timerStop(self):
        if self.timer.is_active():
            self.timer.stop_timer()
            self.logger.debug("Submit timer stopped")

    def timerStart(self):
        if not self.timer.is_active():
            self.logger.debug("Submit timer start")
            self.timer.start_timer()

    def submit(self, data: dict):
        self.submit_mutex.acquire()
        try:
            if "submit_time" not in data:
                data['submit_time'] = util.now()
            self.buf.append(data)
            self.timerStop()
            self._checkBuf()
            self.timerStart()
        finally:
            self.submit_mutex.release()

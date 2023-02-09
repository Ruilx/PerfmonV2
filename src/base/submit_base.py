# -*- coding: utf-8 -*-

"""
Submit base class
"""
import abc
import threading
from multiprocessing import Queue

from src import util
from src.logger import Logger


class SubmitQuit(BaseException):
    ...


class SubmitBase(object, metaclass=abc.ABCMeta):
    def __init__(self, capacity: int = 20, timeout: float = 10.0, queue_capacity=20):
        self.capacity = capacity
        self.timeout = timeout
        self.buf = []
        self.mutex = threading.Lock()
        self.queue = Queue(queue_capacity)

        self.timer = threading.Timer(self.timeout, self._timerEvent)

        self.running = True

        self.logger = Logger().getLogger(__name__)

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
        if self.timer.is_alive():
            self.timer.cancel()
            self.timer.finished.clear()
            self.logger.debug("Submit timer stopped")

    def timerStart(self):
        if not self.timer.is_alive():
            self.logger.debug("Submit timer start")
            self.timer.run()

    def submit(self, data: dict):
        # Multi process calling funtion needs Lock! here
        if "submit_time" not in data:
            data['submit_time'] = util.now()
        self.buf.append(data)
        self.timerStop()
        self._checkBuf()
        self.timerStart()
        # Unlock here

    def daemon(self):
        self.logger.info(f"Submit thread deamon is running...")
        while self.running:
            try:
                result = self.queue.get()
                assert isinstance(result, dict)
                assert "cmd" in result
                match result['cmd']:
                    case "quit":
                        self.running = False
                        self.logger.info(f"queue task received quit command, thread will exit")
                        raise SubmitQuit
                    case "result" | "error":
                        self.submit(result)
            except SubmitQuit:
                self.logger.info(f"Submit finished.")
                self.running = False
            except AssertionError as e:
                self.logger.error(f"Submit has a assertion error: {e!r}")
                util.printTraceback(e, self.logger.error)
                continue
            except BaseException as e:
                self.logger.error(f"Submit has a base exception occurred: {e!r}")
                util.printTraceback(e, self.logger.error)
                self.running = False

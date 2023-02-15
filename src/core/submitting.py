# -*- coding: utf-8 -*-

"""
Submitting 线程管理器类
可以注册多个submit模块
"""
import gc
from multiprocessing import Queue
from threading import Thread, ThreadError

from src import util
from src.base.submit_base import SubmitBase
from src.logger import Logger


class SubmitQuit(BaseException):
    ...


class SubmitEntity(object):
    def __init__(self, queue_in: Queue, submitters: list, name: str):
        self.logger = Logger().getLogger(__name__)
        self.name = name
        self.queue_in = queue_in
        self.submitters = submitters

        self.running = True

    def set_running(self, r):
        self.running = r

    def daemon(self):
        self.logger.info(f"SubmitEntity '{self.name}' daemon is running...")
        while self.running:
            try:
                result = self.queue_in.get()
                assert isinstance(result, dict)
                assert "cmd" in result
                match result['cmd']:
                    case "quit":
                        self.running = False
                        self.logger.info(f"queue task received quit command, submit entity will exit.")
                        raise SubmitQuit
                    case "result" | "error":
                        # result struct
                        try:
                            for index, submitter in enumerate(self.submitters):
                                if not isinstance(submitter, SubmitBase):
                                    raise ValueError(f"Submitter [{index}] is not a submit class")
                                submitter.submit(result)
                        except ValueError as e:
                            self.logger.error(str(e))
                            util.printTraceback(e, self.logger.error)
                            continue
                        except BaseException as e:
                            self.logger.error(str(e))
                            util.printTraceback(e, self.logger.error)
            except SubmitQuit:
                self.logger.info(f"Submit finished")
                self.running = False
            except AssertionError as e:
                self.logger.error(f"Submit has a assertion error: {e!r}")
                util.printTraceback(e, self.logger.error)
                continue
            except ThreadError as e:
                self.logger.error(f"Submit has a thread exception: {e!r}")
                util.printTraceback(e, self.logger.error)
                self.running = False
            except BaseException as e:
                self.logger.error(f"Submit has a base exception occurred: {e!r}")
                util.printTraceback(e, self.logger.error)
                self.running = False
        self.logger.info(f"SubmitEntity '{self.name}' leave daemon <-------")


class Submitting(object):
    def __init__(self, submit_count: int, submit_queue_size: int = 20):
        self.submit_count = submit_count
        self.submitters = []
        self.submit_threads = {}
        self.queue = Queue(submit_queue_size)

        self.logger = Logger().getLogger(__name__)

        self._setup_threads()

    def __del__(self):
        self._reset_threads()
        self.logger.debug("SUBMIT QUEUE JOINING...")
        self.queue.close()
        self.queue.join_thread()
        self.logger.debug("SUBMIT QUEUE JOINED.")
        for submitter in self.submitters:
            if isinstance(submitter, SubmitBase):
                self.logger.debug(f"SUBMIT BASE INSTANCE: '{submitter.__name__}' will delete...")
                del submitter
                self.logger.debug("SUBMIT BASE INSTANCE deleted.")

    def get_queue(self):
        return self.queue

    def register_submit(self, submit: SubmitBase):
        if submit not in self.submitters:
            self.submitters.append(submit)
        else:
            raise ValueError(f"SubmitBase duplicated.")

    def _reset_threads(self):
        if self.submit_threads:
            for name, item in self.submit_threads.items():
                thread = item['thread']
                entity = item['entity']
                if isinstance(thread, Thread):
                    if thread.is_alive():
                        if isinstance(entity, SubmitEntity):
                            entity.set_running(False)
                        self.logger.info(f"Thread '{thread.name}' joining...")
                        self.queue.put({'cmd': "quit"})
                        thread.join()
                        self.logger.info(f"Thread '{thread.name}' joined.")
            self.submit_threads = {}
            gc.collect()
        self.logger.debug("Threads Reset.")

    def _setup_threads(self):
        self._reset_threads()
        for i in range(self.submit_count):
            name = "_".join(("submit", str(i)))
            entity = SubmitEntity(self.queue, self.submitters, name)
            thread = Thread(None, entity.daemon, name)
            self.submit_threads[name] = {
                'entity': entity,
                'thread': thread,
            }
            self.logger.info(f"Submit thread '{name}' has been setup.")

    def start(self):
        self.logger.info("Ready to start submit threads...")
        for name, item in self.submit_threads.items():
            if not isinstance(item['thread'], Thread):
                self.logger.error(f"Thread name '{name}' has a non Thread instance! Skipped.")
                continue
            item['thread'].start()
            self.logger.info(f"Thread name '{name}' started.")

    def stop(self):
        self.logger.info("Ready to stop threads...")
        self._reset_threads()

# -*- coding: utf-8 -*-

"""
Processing 进程管理器类
可以开启指定个进程进行管理
并在进程异常退出时杀掉重启
"""
import gc
import signal
import sys, os
from multiprocessing import Queue, Process, ProcessError

from src.core.perfmon import Perfmon
from src.logger import Logger

from src import util


class ProcessFinished(BaseException):
    ...


class ProcessEntity(object):
    def __init__(self, queue_in: Queue, queue_out: Queue, name: str, perfmon_set):
        self.logger = Logger().getLogger(__name__)
        self.name = name
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.perfmon_set = perfmon_set

        self.running = True

        self._setup()

    def _setup(self):
        def _signalHandle(sig, var2):
            if sig == signal.SIGINT:
                self.logger.info(f"Receive signal SIGINT, stopping process...")
                self.running = False
                raise ProcessFinished()

        signal.signal(signal.SIGINT, _signalHandle)

    def daemon(self):
        while self.running:
            try:
                task = self.queue_in.get()
                assert isinstance(task, dict)
                assert "cmd" in task
                match task['cmd']:
                    case "quit":
                        self.running = False
                        self.logger.info(f"queue task receive quit command, process will exit.")
                        raise ProcessFinished
                    case "task":
                        # task struct:
                        # "perfmon": perfmon name, will find in perfmon list and do task.
                        assert "perfmon" in task
                        perfmon = task['perfmon']
                        assert isinstance(perfmon, Perfmon)
                        perfmon.run_task(perfmon.generate_params())
            except ProcessFinished:
                self.logger.info(f"process finished.")
                break
            except ProcessError as e:
                self.logger.info(f"process occurred an error: {e!r}")
                util.printTraceback(e, self.logger.error)
                continue
            except AssertionError as e:
                self.logger.info(f"processing has a assertion error: {e!r}")
                util.printTraceback(e, self.logger.error)
                continue
            except BaseException as e:
                self.logger.info(f"base exception occurred: {e!r}")
                util.printTraceback(e, self.logger.error)


class Processing(object):
    def __init__(self, process_count, queue_size=50):
        self.process_count = process_count
        self.processes = {}  # name => Process
        self.queue = Queue(queue_size)

        self._setup_processes()

    def _reset_processes(self):
        if self.processes:
            for process in self.processes:
                if isinstance(process, Process):
                    if process.is_alive():
                        process.kill()
                        process.terminate()
                    process.join()
                    process.close()
            self.processes = {}
            gc.collect()

    def _setup_processes(self):
        self._reset_processes()
        for i in range(self.process_count):
            name = "_".join(("process", str(i)))
            entity = ProcessEntity
            self.processes[name] = Process(None, )

# -*- coding: utf-8 -*-

"""
Processing 进程管理器类
可以开启指定个进程进行管理
并在进程异常退出时杀掉重启
"""

import gc
import signal
from multiprocessing import Process, ProcessError, Queue

from src import util
from src.core.perfmon import Perfmon
from src.logger import Logger


class ProcessFinished(BaseException):
    ...


class ProcessEntity(object):
    def __init__(self, queue_in: Queue, name: str):
        self.logger = Logger().getLogger(__name__)
        self.name = name
        self.queue_in = queue_in

        self.running = True

        self._setup()

    def _setup(self):
        def _signalHandle(sig, var2):
            match sig:
                case signal.SIGINT:
                    self.logger.info(f"Receive signal SIGINT, stopping process...")
                    self.running = False
                    raise ProcessFinished()

        signal.signal(signal.SIGINT, _signalHandle)

    def daemon(self):
        self.logger.info(f"ProcessEntity '{self.name}' daemon is running...")
        while self.running:
            try:
                task = self.queue_in.get()
                assert isinstance(task, dict)
                assert "cmd" in task
                match task['cmd']:
                    case "quit":
                        self.running = False
                        self.logger.info(f"queue task received quit command, process will exit.")
                        raise ProcessFinished
                    case "task":
                        # task struct:
                        # "perfmon": perfmon name, will find in perfmon list and do task.
                        assert "perfmon" in task
                        perfmon = task['perfmon']
                        assert isinstance(perfmon, Perfmon)
                        perfmon.run_task(perfmon.generate_params())
            except ProcessFinished:
                self.logger.info(f"Processing finished.")
                self.running = False
            except ProcessError as e:
                self.logger.error(f"Processing occurred an error: {e!r}")
                util.printTraceback(e, self.logger.error)
                self.running = False
            except AssertionError as e:
                self.logger.error(f"Processing has a assertion error: {e!r}")
                util.printTraceback(e, self.logger.error)
                continue
            except KeyboardInterrupt:
                self.logger.error("Processing has a keyboard interrupt")
                self.running = False
                self.queue_in.put({'cmd': 'quit'})
            except BaseException as e:
                self.logger.error(f"Processing has a base exception occurred: {e!r}")
                util.printTraceback(e, self.logger.error)
                self.running = False
        self.logger.info(f"ProcessEntity '{self.name}' leave daemon <------")


class Processing(object):
    def __init__(self, process_count: int, task_queue_size: int = 50):
        self.process_count = process_count
        self.processes = {}  # name => {'entity': ProcessEntity, 'process': Process}
        self.queue = Queue(task_queue_size)

        self.logger = Logger().getLogger(__name__)

        self._setup_processes()

    def __del__(self):
        self._reset_processes()
        self.logger.debug(f"PROCESS QUEUE JOINING...")
        self.queue.close()
        self.queue.join_thread()
        self.logger.debug(f"PROCESS QUEUE JOINED.")

    def get_queue(self):
        return self.queue

    def _reset_processes(self):
        if self.processes:
            queue = self.get_queue()
            for name, item in self.processes.items():
                process = item['process']
                if isinstance(process, Process):
                    if process.is_alive():
                        queue.put({"cmd": "quit"})
                        process.terminate()
                        process.join(5)
                        process.kill()
                        process.join()
                    process.close()
                    self.logger.debug(f"Process '{process.name}' terminated.")
            self.processes = {}
            gc.collect()
        self.logger.debug("Process Reset.")

    def _setup_processes(self):
        self._reset_processes()
        for i in range(self.process_count):
            name = "_".join(("process", str(i)))
            entity = ProcessEntity(self.queue, name)
            process = Process(None, entity.daemon, name)
            self.processes[name] = {
                'entity': entity,
                'process': process,
            }
            self.logger.info(f"Process '{name}' has been setup.")

    def start(self):
        self.logger.info("Ready to start processes...")
        for name, item in self.processes.items():
            if not isinstance(item['process'], Process):
                self.logger.error(f"Process name '{name}' has a non Process instance! Skipped.")
                continue
            item['process'].start()
            self.logger.info(f"Process name '{name}' started.")

    def stop(self):
        self.logger.info("Ready to stop processes...")
        self._reset_processes()

# -*- coding: utf-8 -*-

"""
Perfmon sector

@Ruilx
"""
import types
from src import util
from multiprocessing import Queue

from src.base import task_base
from src.base.task_base import TaskBase
from src.logger import Logger


class Perfmon(object):
    def __init__(self, agent_name: str, config: dict, queue: Queue):
        self.agent_name = agent_name
        self.name = None,
        self.type = None,
        self.delay = None,
        self.queue = queue
        self.tasks = []

        self.logger = Logger().getLogger(__name__)

    def _parsePerfmon(self, config: dict):
        self.name = util.checkKey("name", config, str, "perfmon")
        self.type = util.checkKey("type", config, str, "perfmon")
        self.delay = util.checkKey("delay", config, (float, int), "perfmon")
        tasks = util.checkKey("tasks", config, (list, dict), "perfmon")
        if isinstance(tasks, dict):
            self._parse_task(tasks)
        elif isinstance(tasks, list):
            for task in tasks:
                self._parse_task(task)

    def _parse_task(self, task: dict):
        method = util.checkKey("method", task, str, "task")
        g = globals()
        classObj = None
        match method:
            case "readfile":
                if "ReadFile" not in g:
                    pass
                classObj = g['ReadFile']
            case default:
                raise ValueError(f"Method '{method}' has no class instance to start with, maybe this version is not "
                                 "supported.")
        if not isinstance(classObj, types.MethodType):
            raise RuntimeError(f"Task classobj has no class structure handled.")

        try:
            self.register_task(classObj(self.name, task))
        except TypeError as e:
            raise RuntimeError from e

    def register_task(self, task: TaskBase):
        self.tasks.append(task)

    def run_task(self, params: dict):
        taskCount = len(self.tasks)
        self.logger.debug(f"Perfmon '{self.name}' start running...")
        self.logger.debug(f"Perfmon '{self.name}' has {taskCount} task{'s' if taskCount != 1 else ''}.")
        result = None
        for task in self.tasks:
            if not isinstance(task, task_base.TaskBase):
                self.logger.error(f"Task '{task!r}' is not a valid task, skipped")
                continue
            task.task_run(params)
            result = task.getResult()
            if "_step" not in params or not isinstance(params['_step'], dict):
                params['_step'] = {}
            r_step = result.copy()
            del r_step['params']
            params['_step'][task.getName()] = r_step
        if result is None:
            self.logger.warning(f"Perfmon '{self.name}' returns None result")
        self.submit(result)

    def submit(self, result):
        self.logger.debug(f"Perfmon '{self.name}' result:")
        self.logger.debug(f"{result!r}")
        self.queue.put(result)

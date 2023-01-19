# -*- coding: utf-8 -*-

from sched import scheduler

from src.base.task_base import TaskBase


class Scheduler(object):
    def __init__(self):
        self.scheduler = scheduler()

    def register_scheduler(self, task: TaskBase):
        ...

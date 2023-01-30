# -*- coding: utf-8 -*-

from sched import scheduler

from src.base.task_base import TaskBase
from src.core.perfmon import Perfmon


class Scheduler(object):
    def __init__(self):
        self.scheduler = scheduler()
        self.scheduler_table = {}

    def register_scheduler(self, perfmon: Perfmon):
        event_id = perfmon.register_schedule(self.scheduler)
        self.scheduler_table[perfmon.name] = event_id

    def start(self, blocking=True):
        self.scheduler.run(blocking)

    def stop(self, event_id=None):
        if event_id is None:
            for event in self.scheduler.queue:
                self.scheduler.cancel(event)
        else:
            self.scheduler.cancel(event_id)

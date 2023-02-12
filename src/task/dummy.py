# -*- coding: utf-8 -*-

from src import util
from src.base.task_base import TaskBase

"""
Dummy task instance
@ Ruilx

configs:
'method': <for TaskBase use> Fixed: "dummy"
'format': <for TaskBase use>
'except': <for TaskBase use>
'timeout': <for TaskBase use>

'text': returning text (required)
"""

class Dummy(TaskBase):
    def __init__(self, name: str, config: dict):
        if self.method != "dummy":
            raise TypeError(f"Dummy class need a dummy-type config, but find '{self.method}' type.")

        self.text = util.checkKey("text", config, str, "config")

        super().__init__(name, config)

    def _checkProcess(self):
        ...

    def _setup(self):
        ...

    def _run(self, params: dict):
        self.value = self.text

    def _join(self):
        ...

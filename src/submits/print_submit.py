# -*- coding: utf-8 -*-

import io
import json
import sys

from src import util
from src.base.submit_base import SubmitBase
from src.core.agent_config import AgentConfig

"""
PrintSubmit
打印屏幕提交类
"""


class PrintSubmit(SubmitBase):

    def __init__(self, config: AgentConfig, capacity: int = 20, timeout: float = 10):
        super().__init__(capacity, timeout)
        self.submit_config = config.getSubmitConfig()
        self.type = util.checkKey("type", self.submit_config, str, "submit")
        self.device = util.checkKey("device", self.submit_config, str, "submit")
        self.device = util.checkValueEnum(self.device, ("stdout", "stderr"))

        self.format = util.checkKey("format", self.submit_config, str, "submit")
        self.format = util.checkValueEnum(self.format, ("JsonEachRow", "PythonRepr"))

        self.fd = {"stdout": sys.stdout, "stderr": sys.stderr}[self.device]
        self.print_func = {"JsonEachRow": self.print_JsonEachRow, "PythonRepr": self.print_PythonRepr}[self.format]

    def __del__(self):
        ...

    def print_JsonEachRow(self, data: dict):
        print(json.dumps(data, ensure_ascii=False, indent=None), file=self.fd)

    def print_PythonRepr(self, data: dict):
        print(data.__repr__(), file=self.fd)

    def _send(self) -> bool:
        count = len(self.buf)
        if count <= 0:
            return False
        for item in self.buf:
            self.print_func(item)
        self.logger.debug(f"data has been write, total: {count} line{'s' if count != 1 else ''}.")
        return True

# -*- coding: utf-8 -*-

import io
import json

from pathlib import Path

from src import util
from src.base.submit_base import SubmitBase
from src.core.agent_config import AgentConfig

"""
FileSubmit
通过FILE提交数据类
"""


class FileSubmit(SubmitBase):
    Encoding = "utf-8"

    def __init__(self, config: AgentConfig, capacity: int = 20, timeout: float = 10):
        super(FileSubmit, self).__init__(capacity, timeout)
        self.config = config
        self.filepath = self.config.getReportUrl()  # will fix next

        self.path = Path(self.filepath)
        self.fd = self.path.open("a", encoding=FileSubmit.Encoding)

    def __del__(self):
        if isinstance(self.fd, io.TextIOWrapper):
            if not self.fd.closed:
                self.fd.close()

    def _send(self) -> bool:
        count = len(self.buf)
        if count <= 0:
            return False
        if self.fd.closed:
            raise RuntimeError(f"Submit: file: {self.path!s} closed.")
        for item in self.buf:
            self.fd.write(json.dumps(item))
            self.fd.write('\n')
        self.logger.debug(f"data has been write, total: {count} line{'s' if count != 1 else ''}.")
        return True

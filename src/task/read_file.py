# -*- coding: utf-8 -*-
import io
from pathlib import Path
from src import util
from src.base.task_base import TaskBase

"""
ReadFile task instance
@ Ruilx

configs:
'method':  <for TaskBase use> Fixed: "readfile"
'format':  <for TaskBase use>
'expect':  <for TaskBase use>
'timeout': <for TaskBase use>

'path'  : the path to file (required)
'length': every read length (default: 4096)
'close' : close policy: (choice: "always", "never", "on_exception")
          "always": close file every read
          "never":  never close file, only use seek to reset pointer, except file closed unexpectedly, 
                    will try open it in next time.
          "on_exception": file will close while on read exception, will try open it in next time.
"""


class ReadFile(TaskBase):
    def __init__(self, name: str, config: dict):
        if self.method != "readfile":
            raise TypeError(f"ReadFile class need a readfile-type config, but find '{self.method}' type")

        self.path = Path(util.checkKey("path", config, str, "config"))

        try:
            self.length = util.checkKey("length", config, int, "config")
        except ValueError as e:
            self.length = 4096
        if self.length <= 0:
            raise ValueError(f"'readfile' task length cannot be zero or negative like '{length}'")

        try:
            self.close = util.checkKey("close", config, str, "config")
        except ValueError as e:
            self.close = "never"
        self.close = util.checkValueEnum(self.close, ("always", "never", "on_exception"), False, "close")

        super().__init__(name, config)
        self.fd = None

    def _checkProcess(self):
        if not self.path.is_absolute():
            raise ValueError(f"Readfile class file path '{self.path!r}' need a absolute path.")

        if not self.path.is_file():
            raise ValueError(f"Readfile class file path '{self.path!r}' must be a regular file.")

    def openFile(self, reset: bool = False):
        if reset and (isinstance(self.fd, io.TextIOWrapper) or not self.fd.closed):
            self.fd.close()
        if not isinstance(self.fd, io.TextIOWrapper) and self.fd.closed:
            self.fd = self.path.open("r", encoding="utf-8")

    def closeFile(self):
        if isinstance(self.fd, io.TextIOWrapper) or not self.fd.closed:
            self.fd.close()

    def _setup(self):
        if not isinstance(self.path, Path):
            raise RuntimeError(f"Perfmon item {self.name} with readfile method has no valid path: '{self.path!r}'")
        self.openFile()

    def _run(self, params: dict):
        self.openFile(self.close == "always")
        self.fd.seek(0)
        self.value = self.fd.read(self.length)
        if self.close == "always":
            self.closeFile()

    def _join(self):
        self.closeFile()

# -*- coding: utf-8 -*-

import subprocess

from src import util
from src.base.task_base import TaskBase

"""
Execute task instance
@ Ruilx

configs:
'method':  <for TaskBase use> Fixed "execute"
'format':  <for TaskBase use>
'expect':  <for TaskBase use>
'timeout': <for TaskBase use>

'exec'  : command or shell execute (required)
'params': list for command params (required)
'stdin' : write to stdin when program started
"""


class Execute(TaskBase):
    ProgramExitCode_OK = 0

    def __init__(self, name: str, config: dict):
        self.exec = util.checkKey("exec", config, str, "config")
        self.params = util.checkKey("params", config, (list, tuple), "config")

        try:
            self.stdin = util.checkKey("stdin", config, str, "config")
        except ValueError as e:
            self.stdin = ""

        if not self.exec:
            raise ValueError(f"'execute' task param 'exec' required.")

        for param in self.params:
            if not isinstance(param, str):
                raise ValueError("'execute' task param 'param' each list item should be string type, but one of it "
                                 f"founded '{type(param)}'")

        super().__init__(name, config)
        self.program = None
        self.status_code = None

    def _checkProcess(self):
        if self.method != "execute":
            raise TypeError(f"Execute class need a execute-type config, but find '{self.method}' type")
        if not exec:
            raise ValueError(f"Execute class exec command is empty")

    def _setup(self):
        self.timeoutType = Execute.TimeoutTypeEnum.CustomType

    def _run(self, params: dict):
        command = [self.exec]
        command.extend(self.params)
        self.program = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        encoding="utf-8")
        if not self.program.stdin.closed:
            if self.stdin:
                self.program.stdin.write(self.stdin)
            self.program.stdin.close()
        else:
            self.logger.warning("program STDIN closed, stdin data not send to program.")

        try:
            self.program.wait(timeout=self.wait)
        except subprocess.TimeoutExpired:
            self.program.terminate()
            self.program.kill()

        exitcode = self.program.returncode
        params['_returncode'] = exitcode
        self.value = self.program.stdout.read(4096)
        params['_stderr'] = self.program.stderr.read(4096)

        if exitcode != Execute.ProgramExitCode_OK:
            self.error = f"Program '{self.exec}' exited with code '{exitcode}'"

    def _join(self):
        if isinstance(self.program, subprocess.Popen):
            if self.program.poll() is None:
                self.program.terminate()
                self.program.kill()
                self.program.wait(10)

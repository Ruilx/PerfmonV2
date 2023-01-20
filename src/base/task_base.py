# -*- coding: utf-8 -*-

"""
Task base class


"""
import abc
import enum
import signal
import gc
from threading import Timer

from src import util
from src.core.expect import Expect
from src.logger import Logger
from src.formats.format import FormatFactory


class TaskBase(object, metaclass=abc.ABCMeta):
    ValidExceptEnum = ('int', 'intOrNull', 'real', 'realOrNull', 'string', 'stringOrNull', 'null')

    class TimeoutTypeEnum(enum.Enum):
        KeyboardInterruptType = 0
        CustomType = 1

    def __init__(self, name, config: dict):
        self.name = name
        self.config = config

        self.logger = Logger().getLogger(__name__)

        self.timeoutType = TaskBase.TimeoutTypeEnum.KeyboardInterruptType

        self.method = util.checkKey("method", config, str, "task")
        self.format = util.checkKey("format", config, (str, list), "task")
        self.expect = util.checkKey("expect", config, str, "task")
        self.timeout = util.checkKey("timeout", config, float, "task")

        try:
            self.wait = util.checkKey("wait", config, str, "task")
        except ValueError:
            self.wait = 10

        try:
            self.retry = util.checkKey("retry", config, int, "task")
        except ValueError:
            self.retry = 3

        util.checkValueEnum(self.expect, TaskBase.ValidExceptEnum, valueName="expect")
        self.params = {}
        self.value = None
        self.error = None

        self.timer = None

        self._checkProcess()
        self._setup()

        match self.timeoutType:
            case TaskBase.TimeoutTypeEnum.KeyboardInterruptType:
                self._setupTimer()
            case default:
                ...

    def __del__(self):
        if isinstance(self.timer, Timer):
            if self.timer.is_alive():
                self.timer.cancel()
                self.logger.debug(f"Task '{self.name}' internal timer stopped.")
        self._join()
        gc.collect()

    def _setupTimer(self):
        def _signalEvent(s, var2):
            if s == signal.SIGINT:
                raise TimeoutError(f"Task '{self.name}' running time exceeded in {self.timeout} second"
                                   f"{'s' if self.timeout != 1 else ''}.")

        if not isinstance(self.timer, Timer):
            self.timer = Timer(self.timeout, _signalEvent)

    def getName(self):
        return self.name

    def _doFormat(self):
        """
        从format工厂处理得到的值
        :return:
        :rtype:
        """
        def __doFormat(cur):
            if isinstance(cur, str):
                return FormatFactory()[cur](self.value)
            elif isinstance(cur, list):
                currentValue = self.value
                for c in cur:
                    currentValue = __doFormat(c)
                    if not currentValue:
                        return None
                return currentValue
            elif cur is None:
                return self.value
            else:
                raise ValueError(f"format name type need str, but '{type(cur)}' found")

        self.value = __doFormat(self.format)

    def _doExpect(self):
        self.value = Expect.expect(self.expect, self.value)

    @abc.abstractmethod
    def _checkProcess(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _setup(self):
        raise NotImplementedError()

    @abc.abstractmethod
    def _run(self, params: dict):
        raise NotImplementedError()

    @abc.abstractmethod
    def _join(self):
        raise NotImplementedError()

    def task_run(self, params: dict):
        self.error = None
        self.params = params
        for attempt in range(self.retry):
            if isinstance(self.timer, Timer):
                if self.timer.is_alive():
                    self.timer.cancel()
                self.timer.finished.clear()
                self.timer.run()
            try:
                self._run(params)
                self._doFormat()
                self._doExpect()
                self.error = None
                break
            except TimeoutError as e:
                self.error = e
                util.printTraceback(e, self.logger.error)
                continue
            except BaseException as e:
                self.logger.error(f"Task '{self.name}' exception occurred while processing: {e!r}")
                util.printTraceback(e, self.logger.error)
                self.error = e
                continue
        if isinstance(self.timer, Timer):
            if self.timer.is_alive():
                self.timer.cancel()
                self.logger.debug(f"Task '{self.name}' has a timer cancelled.")
        gc.collect()

    def getValue(self):
        return self.value

    def getError(self):
        return self.error

    def getResult(self):
        return {
            'cmd': "result" if self.error is None else "error",
            'name': self.name,
            'params': self.params,
            'except': self.expect,
            'value': self.value,
            'errno': 0 if self.error is None else 1,
            'error': "{}: {}".format(self.error.__class__.__name__, self.error.__repr__()) if isinstance(self.error, BaseException) else "",
            'timestamp': util.timestamp(),
        }

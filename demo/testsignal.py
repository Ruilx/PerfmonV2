#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
本文介绍了如何打断一个Python中函数调用的同步等待问题
使用SIGINT中断触发一个KeyboardInterrupt异常退出同步等待的过程, 可以自由设置超时时间.
"""

import sys, os, signal
import time
from threading import Timer
import datetime

now = lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def timerEvent():
    print(now(), "RAISE SIGNAL...")
    signal.raise_signal(signal.SIGINT)


def delay(during: float):
    time.sleep(during)


def signalEvent(sig, var2):
    if sig == signal.SIGINT:
        print(now(), "RAISING RUNTIME ERROR...")
        raise RuntimeError


def main():
    timer = Timer(5, timerEvent)
    signal.signal(signal.SIGINT, signalEvent)
    print(now(), "TIMER STARTED.")
    timer.start()
    try:
        delay(20)
        print(now(), "DELAY FINISHED.")
    except KeyboardInterrupt as e:
        print(now(), "INTERRUPTED!")
    except RuntimeError as e:
        print(now(), "INTERRUPTED! BY USER SIGNAL.")
    if timer.is_alive():
        timer.cancel()
        print(now(), "TIMER CANCELLED.")


if __name__ == "__main__":
    main()

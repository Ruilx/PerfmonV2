#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
from datetime import datetime
from typing import Callable
from threading import Timer, Event


class ReentrantTimer(Timer):
    """
    Call a function after a specified number of seconds
    and can reentrant start
    always need a thread to run timer.

    t = Timer(30.0, f, args=None, kwargs=None)
    t.start_timer()
    ...
    t.start_timer()  # <- reentrant for reset
    ...
    t.stop_timer()
    t.start_timer()  # <- also reentrant
    ...
    t.cancel()       # <- exit thread
    """

    def __init__(self, interval: float | int, function: Callable, args=None, kwargs=None):
        Timer.__init__(self, interval, function, args, kwargs)
        self.idling = Event()
        self.running = True

    def start_timer(self):
        self.finished.clear()
        self.idling.set()
        if not self.is_alive():
            self.start()

    def stop_timer(self):
        self.idling.clear()
        self.finished.set()

    def is_active(self):
        return self.idling.is_set()

    def cancel(self):
        self.running = False
        self.finished.set()
        self.idling.set()

    def run(self):
        while self.running:
            self.idling.wait()
            super().run()
            self.idling.clear()


def now():
    return datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")


def printIt(*args, **kwargs):
    print(now(), *args, **kwargs)


def timer_event():
    printIt("Timer Event Here!")


def main():
    timer = ReentrantTimer(5, timer_event)
    printIt("Timer start.")
    timer.start_timer()
    printIt("Sleep 2s.")
    printIt("ACTIVE:", timer.is_active())
    time.sleep(2)
    printIt("Timer stop.")
    timer.stop_timer()
    printIt("Sleep 2s.")
    printIt("ACTIVE:", timer.is_active())
    time.sleep(2)
    printIt("Timer start.")
    timer.start_timer()
    printIt("Sleep 6s.")
    time.sleep(6)
    printIt("ACTIVE:", timer.is_active())
    printIt("Timer stop. (it already stopped)")
    timer.stop_timer()
    printIt("Sleep 6s.")
    time.sleep(6)
    printIt("ACTIVE:", timer.is_active())
    printIt("Timer Start.")
    timer.start_timer()
    printIt("Sleep 2s.")
    time.sleep(2)
    printIt("Timer Cancelled.")
    timer.cancel()
    printIt("Reached end.")
    printIt("Alive? ", timer.is_alive())


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
import signal
from threading import Timer
from datetime import datetime

running = True

def now():
    return datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S")

def printIt(*args, **kwargs):
    print(now(), *args, **kwargs)

def timer_event(timer: Timer):
    global running
    printIt("Timer Event Here!")
    timer_reload(timer)

def timer_reload(timer: Timer):
    timer.finished.clear()
    timer.run()

def main():

    def _single_handler(sig, _):
        global running
        if sig in (signal.SIGINT, ):
            running = False
            printIt("Receive SIGINT")

    signal.signal(signal.SIGINT, _single_handler)

    timer = Timer(5, timer_event)
    timer.args.append(timer)
    timer.start()

    global running
    while running:
        printIt("Do Normal Work...")
        time.sleep(1)

    timer.cancel()
    printIt("Finished Bye~")

if __name__ == "__main__":
    main()

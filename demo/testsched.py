#!/usr/bin/env python3
# =*= coding: utf-8 =*=

"""
本代码介绍sched.scheduler带循环启动的样例
"""

import os, sys, sched
import time, datetime
import traceback

now = lambda: datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

scheduler = sched.scheduler()


def worker(name, config):
    print(f"Worker: '{name}', @{now()}")
    print(scheduler.queue)
    reload_job(config)


def reload_job(config):
    scheduler.enter(config['delay'],
                    config['priority'],
                    worker,
                    (config['name'], config))
    print(f"Job '{config['name']}' reloaded.")


def main():
    task1_config = {
        'name': "task1",
        'delay': 5,
        'priority': 10,
    }

    task2_config = {
        'name': "task2",
        'delay': 10,
        'priority': 5,
    }

    reload_job(task1_config)
    reload_job(task2_config)

    scheduler.run()

    print(f"{now()}, finished")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Perfmon V2
@ Ruilx

"""

import argparse
import os
import platform
import sys
import signal
import threading

from core.agent_config import AgentConfig
from logger import Logger
from src import util
from src.core.submitting import Submitting
from src.core.scheduler import Scheduler
from src.core.processing import Processing
from src.core.perfmon import Perfmon
from src.submits.print_submit import PrintSubmit


def argBuilder():
    argparser = argparse.ArgumentParser(sys.argv[0], description="Perfmon agent")
    argparser.add_argument("-c", "--config", type=str, required=True, help="config file", dest="config")
    return argparser.parse_args()


def main():
    logger = Logger().getLogger(__name__)
    args = argBuilder()
    config = AgentConfig(args.config)
    print(config.getAgentName())
    print(config.getReportUrl())
    process_count = config.getProcessCount()
    if not process_count:
        process_count = os.cpu_count()
        logger.info(f"Worker count is set to '{process_count}' as CPU count.")

    submitting = Submitting(1)
    submit = PrintSubmit(config)
    submitting.register_submit(submit)

    scheduler = Scheduler()

    processing = Processing(process_count)

    def signal_handle(sig, _):
        signals = [signal.SIGINT, signal.SIGTERM]
        if sig in signals:
            scheduler.stop()
            processing.stop()
            submitting.stop()

    signal.signal(signal.SIGINT, signal_handle)
    signal.signal(signal.SIGTERM, signal_handle)

    for item in config.getPerfmonItems():
        perfmon = Perfmon(config.getAgentName(), item, submitting.get_queue())
        scheduler.register_scheduler(perfmon)

    try:
        submitting.start()
        processing.start()
        scheduler.start()
    except BaseException as e:
        logger.error(f"BaseException: {e!r}")
        util.printTraceback(e, logger.error)
    finally:
        scheduler.stop()
        processing.stop()
        submitting.stop()

    del processing
    del submitting

    logger.info("Stopped, bye.")


if __name__ == "__main__":
    main()

    print("Active count: ", threading.active_count())

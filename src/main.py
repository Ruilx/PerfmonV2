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

from core.agent_config import AgentConfig
from logger import Logger
from src.submits.file_submit import FileSubmit
from src.core.submitting import Submitting
from src.core.scheduler import Scheduler
from src.core.processing import Processing
from src.core.perfmon import Perfmon


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
    submit = FileSubmit(config)
    submitting.register_submit(submit)

    scheduler = Scheduler()

    processing = Processing(process_count)

    def signal_handle(sig, _):
        signals = [signal.SIGINT, signal.SIGTERM]
        if platform.system() != 'Windows':
            signals.append(signal.SIGKILL)
        if sig in signals:
            scheduler.stop()
            processing.stop()
            submitting.stop()

    signal.signal(signal.SIGINT, signal_handle)
    signal.signal(signal.SIGTERM, signal_handle)
    if platform.system() != 'Windows':
        signal.signal(signal.SIGKILL, signal_handle)

    submitting.start()
    processing.start()

    for item in config.getPrefmonItems():
        perfmon = Perfmon(config.getAgentName(), item, submitting.get_queue())
        scheduler.register_scheduler(perfmon)

    scheduler.start()

    logger.info("Stopped, bye.")


if __name__ == "__main__":
    main()

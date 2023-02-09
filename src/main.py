#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Perfmon V2
@ Ruilx

"""

import argparse
import os
import sys

from core.agent_config import AgentConfig
from logger import Logger
from src.core.http_submit import HttpSubmit


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

    submit = HttpSubmit(config)


if __name__ == "__main__":
    main()

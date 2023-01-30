#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Perfmon V2
@ Ruilx

"""

import sys, os
import argparse

from core.agent_config import AgentConfig
from logger import Logger


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

    print(process_count)


if __name__ == "__main__":
    main()

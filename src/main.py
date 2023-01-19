#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Perfmon V2
@ Ruilx

"""

import sys, os
import argparse

from core.agent_config import AgentConfig


def argBuilder():
    argparser = argparse.ArgumentParser(sys.argv[0], description="Perfmon agent")
    argparser.add_argument("-c", "--config", type=str, required=True, help="config file", dest="config")
    return argparser.parse_args()


def main():
    args = argBuilder()
    config = AgentConfig(args.config)
    print(config.getAgentName())
    print(config.getReportUrl())


if __name__ == "__main__":
    main()

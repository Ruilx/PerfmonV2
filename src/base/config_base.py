# -*- coding: utf-8 -*-

"""
ConfigBase Class

Base class for any config type
"""

import os.path
import json


class ConfigBase(object):
    def __init__(self, filePath):
        self.filePath = ""
        self.cfg = {}
        self.setConfigPath(filePath)

    def setConfigPath(self, filePath):
        self.filePath = filePath
        self.__loadConfig()

    def __loadConfig(self):
        if not self.filePath:
            raise ValueError(f"file path '{self.filePath}' not set.")
        if not os.path.exists(self.filePath):
            raise ValueError(f"file path '{self.filePath}' not exist.")
        with open(self.filePath, "r") as fd:
            self.cfg = json.load(fd)

    def _findKey(self, *keys):
        currentNode = self.cfg
        for key in keys:
            if isinstance(currentNode, dict):
                if key in currentNode:
                    currentNode = currentNode[key]
                else:
                    return None
            elif isinstance(currentNode, (list, tuple)):
                if isinstance(key, int):
                    if key < len(currentNode):
                        currentNode = currentNode[key]
                    else:
                        currentNode = None
                        break
                elif isinstance(key, str):
                    result = []
                    for current in currentNode:
                        if isinstance(current, dict):
                            if key in current:
                                result.append(current[key])
                    currentNode = result
            else:
                return currentNode
        return currentNode

# -*- config: utf-8 -*-

from src.base import config_base


class AgentConfig(config_base.ConfigBase):
    def __init__(self, filePath):
        super().__init__(filePath)
        assert self.getAgentName(), "Config need 'agent_name' key"
        assert self.getReportUrl(), "Config need 'report' key"
        assert self.getPrefmonItems(), "Config need 'perfmon' items"

    def getAgentName(self):
        return self._findKey("agent_name")

    def getReportUrl(self):
        return self._findKey("report")

    def getPrefmonItems(self):
        return self._findKey("perfmon")

    def getProcessCount(self):
        return self._findKey("process")

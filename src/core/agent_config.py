# -*- config: utf-8 -*-

from src.base import config_base


class AgentConfig(config_base.ConfigBase):
    def __init__(self, filePath):
        super().__init__(filePath)
        assert self.getAgentName(), "Config need 'agent_name' key"
        # assert self.getReportUrl(), "Config need 'report' key"
        assert self.getPrefmonItems(), "Config need 'perfmon' items"

    def getAgentName(self):
        """
        获得配置文件中Agent名称
        :return:
        :rtype: str
        """
        return self._findKey("agent_name")

    def getReportUrl(self):
        """
        获得配置文件中报告资源的URL
        :TODO: 更新结构体
        :return:
        :rtype: str
        """
        return self._findKey("report")

    def getSubmitConfig(self):
        return self._findKey("submit")

    def getPrefmonItems(self):
        """
        获得配置文件Perfmon项目
        :return:
        :rtype: dict
        """
        return self._findKey("perfmon")

    def getProcessCount(self):
        """
        获得配置文件中指定的进程数
        :return:
        :rtype:
        """
        return self._findKey("process")

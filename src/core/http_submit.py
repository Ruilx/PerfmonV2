# -*- coding: utf-8 -*-

import requests

from src import util
from src.base.submit_base import SubmitBase
from src.core.agent_config import AgentConfig


class HttpSubmit(SubmitBase):
    Headers = {
        'Accept': "application/json;q=0.9;charset=utf-8",
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36 Perfmon/1.0 (Client 1.0) Trust-Agent/1.0"
    }

    def __init__(self, config: AgentConfig, retry: int = 3, capacity: int = 20, timeout: float = 10):
        super().__init__(capacity, timeout)
        self.retry = retry
        self.session = requests.Session()
        self.config = config
        util.checkUrl(self.config.getReportUrl())

    def checkResponse(self, response: requests.Response):
        assert response.status_code == 200, f"report server response status code '{response.status_code}'"
        json_t = response.json()
        assert "errno" in json_t, "report server response json has no 'errno' key"
        if json_t['errno'] != 0:
            raise RuntimeError("report server reponse error({ERRNO}){ERROR}".format(
                ERRNO=json_t['errno'], ERROR=f": {json_t['error']}" if "error" in json_t else ""
            ))
        return json_t

    def send(self) -> bool:
        if len(self.buf) <= 0:
            return False
        errmsg = []
        result = ""
        for i in range(self.retry):
            try:
                res = self.session.post(self.config.getReportUrl(), json=self.buf, headers=HttpSubmit.Headers)
                self.checkResponse(res)
                result = res.content
                break
            except BaseException as e:
                errmsg.append(str(e))
        if result:
            self.logger.debug("data has been sent")
            return True
        else:
            self.logger.debug("data send failure")
            for index, content in enumerate(errmsg):
                self.logger.debug(f"==> (try {index + 1}): {content}")
            return False

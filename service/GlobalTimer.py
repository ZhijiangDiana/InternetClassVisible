import asyncio
import threading
from time import sleep
from config import INTERNAL_REQUEST_TOKEN, SERVER_IP, SERVER_PORT

import requests

from service.MemberFinishStatistic import CalculateRateService


class GlobalTimer:
    __instance = None
    __instance_lock = threading.Lock()

    _timer_thread = None

    def __new__(cls):
        with cls.__instance_lock:
            if cls.__instance is None:
                # 实例化对象
                cls.__instance = super().__new__(cls)
                self = cls.__instance

                # 初始化定时器线程
                self._timer_thread = threading.Thread(target=self._timer_func, daemon=True,
                                                      name="GlobalTimer")
                self._timer_thread.start()

        return cls.__instance

    # 当前周期是60s
    def _timer_func(self):
        while True:
            # 0s
            requests.put(url=f"http://{SERVER_IP}:{SERVER_PORT}/internal/statistic/member_finish_rate",
                         params={'token': INTERNAL_REQUEST_TOKEN})
            sleep(60)
            # 60s

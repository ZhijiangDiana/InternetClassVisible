import asyncio
import threading
from time import sleep
from config import INTERNAL_REQUEST_TOKEN, SERVER_IP, SERVER_PORT

import requests

from service.TotalCourseFinishStatistic import CalculateRateService


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
        # 单次任务
        # 初始化正在进行的课程
        requests.post(url=f"http://{SERVER_IP}:{SERVER_PORT}/internal/record/initialize_running",
                      params={'token': INTERNAL_REQUEST_TOKEN})
        # 更新课程完成率名单
        requests.put(url=f"http://{SERVER_IP}:{SERVER_PORT}/internal/statistic/course/finish_rate",
                     params={'token': INTERNAL_REQUEST_TOKEN})
        # 更新总体完成率名单
        requests.put(url=f"http://{SERVER_IP}:{SERVER_PORT}/internal/statistic/finish_rate",
                     params={'token': INTERNAL_REQUEST_TOKEN})

        # 多次任务
        cnt = 0
        while True:
            if cnt % 30 == 0:
                # 刷新正在进行的学习
                requests.post(url=f"http://{SERVER_IP}:{SERVER_PORT}/internal/record/refresh_running",
                              params={'token': INTERNAL_REQUEST_TOKEN})
            sleep(1)
            if cnt == 60:
                cnt = 0
            else:
                cnt += 1

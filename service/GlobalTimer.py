import threading
from time import sleep
from controller.internal import *


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
    async def _timer_func(self):
        # 单次任务
        # 初始化正在进行的课程
        await initialize_running()
        # 更新课程完成率名单
        await update_statistic_course_finish_rate()
        # 更新总体完成率名单
        await update_statistic_member_finish_rate()

        # 多次任务
        cnt = 0
        while True:
            if cnt % 30 == 0:
                # 刷新正在进行的学习
                await refresh_running()
            sleep(1)
            if cnt == 60:
                cnt = 0
            else:
                cnt += 1

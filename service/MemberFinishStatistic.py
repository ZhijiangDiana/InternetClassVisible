import asyncio
import copy
import threading
from datetime import datetime

import pytz
from tqdm.auto import tqdm

from config import TIMEZONE
from dao import record_dao
from entity.db_entity import *


class CalculateRateService:
    __instance = None
    __instance_lock = threading.Lock()

    def __new__(cls):
        with cls.__instance_lock:
            if cls.__instance is None:
                # 实例化对象
                cls.__instance = super().__new__(cls)
        return cls.__instance

    # 完成率名单对象
    _finish_rate = {
        # 初始化为时间戳原点
        "refresh_time": datetime(1970, 1, 1),
        # 所有人的完成率
        "member_rate": {int(): float()}
    }
    # 给变量加锁以防止读-写锁
    _finish_rate_lock = asyncio.Lock()

    # 获取某人完成情况原始数据
    async def _get_mem_course(self, mem_id):
        need_finish = await record_dao.get_courses_should_finish(mem_id)
        finished = await record_dao.get_courses_finished(mem_id)

        return {
            "need_finish": need_finish,
            "finished": finished
        }

    # 更新完成率名单对象，定时任务60s执行一次
    async def update_finish_rate(self):
        # 初始化完成率表
        finish_rate = {
            # 更新名单的更新时间
            "refresh_time": datetime.now(),
            # 所有人的完成率
            "member_rate": {int(): float()}
        }

        members = await Member.all()
        # 依次计算每个人的完成率并存入表中
        for member in tqdm(members):
            status = await self._get_mem_course(member.id)
            need_finish = status["need_finish"]
            finished = status["finished"]

            # 防止除数为0
            rate = 0.0
            if len(need_finish) != 0:
                rate = len(finished) * 1.0 / len(need_finish)
            finish_rate["member_rate"][member.id] = rate
        # 新名单取代旧名单
        async with self._finish_rate_lock:
            self._finish_rate = finish_rate
        print(f"{id(self)}已在{self._finish_rate["refresh_time"]}更新完成率名单")

    # 获取完成率名单对象
    async def get_all_finish_rate(self):
        # async with self._finish_rate_lock:
        #     # 如果上次更新时间距离现在超过60s，则更新名单
        #     if (datetime.now() - self._finish_rate["refresh_time"]).seconds >= 60:
        #         await self._update_finish_rate()

        async with self._finish_rate_lock:
            finish_rate = copy.deepcopy(self._finish_rate)

        return finish_rate

    # 获取某人的完成率
    async def get_member_finish_rate(self, mem_id):
        finish_rate = await self.get_all_finish_rate()
        return {
            "refresh_time": finish_rate["refresh_time"],
            mem_id: finish_rate["member_rate"][mem_id]
        }

    async def get_finish_status(self, mem_id):
        status = await self._get_mem_course(mem_id)
        need_finish = status["need_finish"]
        finished = status["finished"]

        for course in need_finish:
            course["is_finished"] = finished.__contains__(course)

        return finished

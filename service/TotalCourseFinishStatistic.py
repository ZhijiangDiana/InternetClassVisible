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
        "member_rate": {int(): float()},
        # 支部的完成率
        "organization_rate": {str(): float()},
        # 学院的完成率
        "p_org_rate": 0.0
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

    async def _update_member_rate(self, finish_rate):
        members = await Member.all()
        # 依次计算每个人的完成率并存入表中
        for member in members:
            status = await self._get_mem_course(member.id)
            need_finish = status["need_finish"]
            finished = status["finished"]

            # 防止除数为0
            rate = 0.0
            if len(need_finish) != 0:
                rate = len(finished) * 1.0 / len(need_finish)
            finish_rate["member_rate"][member.id] = rate
        print(f"{id(self)}已在{datetime.now()}更新成员完成率名单")

        return finish_rate

    async def _update_org_rate(self, finish_rate):
        orgs = await Organization.all()
        # 依次计算每个支部的完成率并存入表中
        for org in orgs:
            org_members = await Member.filter(organization_id=org.id)
            # 计算支部的总完成率
            rate = 0.0
            mem_cnt = 0
            for member in org_members:
                rate += finish_rate["member_rate"][member.id]
                mem_cnt += 1
            # 防止除数为0
            if mem_cnt > 0:
                rate /= mem_cnt
            finish_rate["organization_rate"][org.id] = rate

        print(f"{id(self)}已在{datetime.now()}更新支部完成率名单")

        return finish_rate

    async def _update_p_rate(self, finish_rate):
        # 计算光电学院总完成率并存入表中
        rate = 0.0
        org_cnt = 0
        for key, value in finish_rate["organization_rate"].items():
            rate += value
            org_cnt += 1
        if org_cnt > 0:
            rate /= org_cnt
        finish_rate["p_org_rate"] = rate
        print(f"{id(self)}已在{datetime.now()}更新支部完成率名单")

        return finish_rate

    # 更新完成率名单对象，定时任务60s执行一次
    async def update_finish_rate(self):
        # 初始化完成率表
        finish_rate = {
            # 更新名单的更新时间
            "refresh_time": datetime.now(),
            # 所有人的完成率
            "member_rate": {int(): float()},
            # 支部的完成率
            "organization_rate": {str(): float()},
            # 学院的完成率
            "p_org_rate": float()
        }

        # 更新成员统计信息
        finish_rate = await self._update_member_rate(finish_rate)
        # 更新支部统计信息
        finish_rate = await self._update_org_rate(finish_rate)
        # 更新学院统计信息
        finish_rate = await self._update_p_rate(finish_rate)

        # 新名单取代旧名单
        async with self._finish_rate_lock:
            self._finish_rate = finish_rate

    # 获取完成率名单对象
    async def get_all_finish_rate(self):
        async with self._finish_rate_lock:
            finish_rate = copy.deepcopy(self._finish_rate)

        return finish_rate

    async def get_all_member_finish_rate(self):
        async with self._finish_rate_lock:
            refresh_time = copy.deepcopy(self._finish_rate["refresh_time"])
            mems_finish_rate = copy.deepcopy(self._finish_rate["member_rate"])
            return {
                "refresh_time": refresh_time,
                "member_rate": mems_finish_rate
            }

    async def get_all_org_finish_rate(self):
        async with self._finish_rate_lock:
            refresh_time = copy.deepcopy(self._finish_rate["refresh_time"])
            orgs_finish_rate = copy.deepcopy(self._finish_rate["organization_rate"])
            return {
                "refresh_time": refresh_time,
                "organization_rate": orgs_finish_rate
            }

    # 获取某人的完成率
    async def get_member_finish_rate(self, mem_id):
        async with self._finish_rate_lock:
            refresh_time = copy.deepcopy(self._finish_rate["refresh_time"])
            mem_rate = copy.deepcopy(self._finish_rate["member_rate"][mem_id])
            return {
                "refresh_time": refresh_time,
                "member_rate": mem_rate
            }

    async def get_org_finish_rate(self, org_id):
        async with self._finish_rate_lock:
            refresh_time = copy.deepcopy(self._finish_rate["refresh_time"])
            org_rate = copy.deepcopy(self._finish_rate["organization_rate"][org_id])
            return {
                "refresh_time": refresh_time,
                "organization_rate": org_rate
            }

    async def get_p_finish_rate(self):
        async with self._finish_rate_lock:
            refresh_time = copy.deepcopy(self._finish_rate["refresh_time"])
            p_rate = copy.deepcopy(self._finish_rate["p_org_rate"])
            return {
                "refresh_time": refresh_time,
                "p_finish_rate": p_rate
            }

    async def get_finish_status(self, mem_id):
        status = await self._get_mem_course(mem_id)
        need_finish = status["need_finish"]
        finished = status["finished"]

        for course in need_finish:
            course["is_finished"] = finished.__contains__(course)

        return finished


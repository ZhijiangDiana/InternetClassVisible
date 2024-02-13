import asyncio
import copy
import threading
from datetime import datetime

import pytz
from tqdm.auto import tqdm

from config import TIMEZONE
from dao import record_dao
from entity.db_entity import *


# 计算所有课程中个人和支部的完成率及完成率排名
class CalculateRateService:
    # 完成率名单对象
    _finish_rate = {
        # 初始化为时间戳原点
        "refresh_time": datetime(1970, 1, 1),
        # 所有人的完成率
        "member_rate": {},
        # 支部的完成率
        "organization_rate": {},
        # 学院的完成率
        "p_org_rate": 0.0
    }
    # 给变量加锁以防止读-写锁
    _finish_rate_lock = asyncio.Lock()

    # 完成率排名名单
    _finish_rate_rank = {
        "refresh_time": datetime(1970, 1, 1),
        "member_rank": {},
        "org_rank": {},
        "member_rank_list": [],
        "organization_rank_list": []
    }
    # 给变量加锁防止读写冲突
    _finish_rate_rank_lock = asyncio.Lock()

    # 获取某人完成情况原始数据
    @staticmethod
    async def _get_mem_course(mem_id):
        need_finish = await record_dao.get_courses_should_finish(mem_id)
        finished = await record_dao.get_courses_finished(mem_id)

        return {
            "need_finish": need_finish,
            "finished": finished
        }

    @staticmethod
    async def _update_member_rate(finish_rate):
        members = await Member.all()
        # 依次计算每个人的完成率并存入表中
        for member in members:
            status = await CalculateRateService._get_mem_course(member.id)
            need_finish = status["need_finish"]
            finished = status["finished"]

            # 防止除数为0
            rate = 0.0
            if len(need_finish) != 0:
                rate = len(finished) * 1.0 / len(need_finish)
            finish_rate["member_rate"][member.id] = rate
        print(f"已在{datetime.now()}更新成员完成率名单")

        return finish_rate

    @staticmethod
    async def _update_org_rate(finish_rate):
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

        print(f"已在{datetime.now()}更新支部完成率名单")

        return finish_rate

    @staticmethod
    async def _update_p_rate(finish_rate):
        # 计算光电学院总完成率并存入表中
        rate = 0.0
        org_cnt = 0
        for key, value in finish_rate["organization_rate"].items():
            rate += value
            org_cnt += 1
        if org_cnt > 0:
            rate /= org_cnt
        finish_rate["p_org_rate"] = rate
        print(f"已在{datetime.now()}更新学院完成率名单")

        return finish_rate

    @classmethod
    async def _update_finish_rate(cls):
        # 初始化完成率表
        finish_rate = {
            # 更新名单的更新时间
            "refresh_time": datetime.now(),
            # 所有人的完成率
            "member_rate": {},
            # 支部的完成率
            "organization_rate": {},
            # 学院的完成率
            "p_org_rate": float()
        }

        # 更新成员统计信息
        finish_rate = await cls._update_member_rate(finish_rate)
        # 更新支部统计信息
        finish_rate = await cls._update_org_rate(finish_rate)
        # 更新学院统计信息
        finish_rate = await cls._update_p_rate(finish_rate)

        # 新名单取代旧名单
        async with cls._finish_rate_lock:
            cls._finish_rate = finish_rate

    @staticmethod
    async def _update_member_rank(finish_rate_rank, finish_rate):
        # 个人在学院的排名
        # 使用sorted函数和lambda表达式按值排序，返回一个包含元组的列表
        finish_rate_sorted = sorted(finish_rate["member_rate"].items(), key=lambda x: x[1], reverse=True)
        # 存储排名榜
        finish_rate_rank["member_rank_list"] = finish_rate_sorted
        # 更新个人在学院的排名
        for index, member in enumerate(finish_rate_sorted):
            mem_id = member[0]
            rate = member[1]
            rank = index + 1
            finish_rate_rank["member_rank"][mem_id]["finish_rate"] = rate
            finish_rate_rank["member_rank"][mem_id]["rank_in_p_org"] = rank

        # 个人在支部的排名
        orgs = await Organization.all()  # 获取所有支部信息
        for org in orgs:
            members = await Member.filter(organization_id=org.id)  # 获取支部中每个人
            org_finish_rate = {}  # 支部人员及其完成率字典
            # 将支部成员及其完成率加入字典
            for member in members:
                org_finish_rate[member.id] = finish_rate["member_rate"][member.id]
            # 排序
            finish_rate_sorted = sorted(org_finish_rate.items(), key=lambda x: x[1], reverse=True)
            # 更新个人在支部的排名
            for index, member in enumerate(finish_rate_sorted):
                mem_id = member[0]
                rank = index + 1
                finish_rate_rank["member_rank"][mem_id]["rank_in_org"] = rank

        # print(finish_rate_rank)

        return finish_rate_rank

    @staticmethod
    async def _update_org_rank(finish_rate_rank, finish_rate):
        # 使用sorted函数和lambda表达式按值排序，返回一个包含元组的列表
        finish_rate_sorted = sorted(finish_rate["organization_rate"].items(), key=lambda x: x[1], reverse=True)
        # 存储排名榜
        finish_rate_rank["organization_rank_list"] = finish_rate_sorted
        # 存储排名信息
        for index, org in enumerate(finish_rate_sorted):
            mem_id = org[0]
            rate = org[1]
            rank = index + 1
            finish_rate_rank["org_rank"][mem_id]["finish_rate"] = rate
            finish_rate_rank["org_rank"][mem_id]["rank_in_p_org"] = rank

        return finish_rate_rank

    @classmethod
    async def _update_rate_rank(cls, finish_rate):
        # 初始化排名表
        finish_rate_rank = {
            "refresh_time": datetime.now(),
            "member_rank": {},
            "org_rank": {},
            "member_rank_list": [],
            "organization_rank_list": []
        }
        members = await Member.all()
        for member in members:
            finish_rate_rank["member_rank"][member.id] = {}
        orgs = await Organization.all()
        for org in orgs:
            finish_rate_rank["org_rank"][org.id] = {}

        # 更新个人在支部、在学院的排名
        finish_rate_rank = await cls._update_member_rank(finish_rate_rank, finish_rate)
        # 更新支部在学院的排名
        finish_rate_rank = await cls._update_org_rank(finish_rate_rank, finish_rate)

        async with cls._finish_rate_rank_lock:
            cls._finish_rate_rank = finish_rate_rank

    # 更新完成率名单对象和排名名单对象，定时任务60s执行一次
    @classmethod
    async def update_statistic(cls):
        await cls._update_finish_rate()
        async with cls._finish_rate_lock:
            finish_rate = copy.deepcopy(cls._finish_rate)
        await cls._update_rate_rank(finish_rate)

    # -----------
    # 对外接口部分
    # -----------

    @classmethod
    async def get_all_member_finish_rate(cls):
        async with cls._finish_rate_lock:
            refresh_time = copy.deepcopy(cls._finish_rate["refresh_time"])
            mems_finish_rate = copy.deepcopy(cls._finish_rate["member_rate"])
        return {
            "refresh_time": refresh_time,
            "member_rate": mems_finish_rate
        }

    @classmethod
    async def get_all_org_finish_rate(cls):
        async with cls._finish_rate_lock:
            refresh_time = copy.deepcopy(cls._finish_rate["refresh_time"])
            orgs_finish_rate = copy.deepcopy(cls._finish_rate["organization_rate"])
        return {
            "refresh_time": refresh_time,
            "organization_rate": orgs_finish_rate
        }

    # 获取个人所有课程的完成率
    @classmethod
    async def get_member_finish_rate(cls, mem_id):
        async with cls._finish_rate_lock:
            refresh_time = copy.deepcopy(cls._finish_rate["refresh_time"])
            mem_rate = copy.deepcopy(cls._finish_rate["member_rate"][mem_id])
        return {
            "refresh_time": refresh_time,
            "member_rate": mem_rate
        }

    # 获取支部所有课程的完成率
    @classmethod
    async def get_org_finish_rate(cls, org_id):
        print(cls._finish_rate)
        async with cls._finish_rate_lock:
            refresh_time = copy.deepcopy(cls._finish_rate["refresh_time"])
            org_rate = copy.deepcopy(cls._finish_rate["organization_rate"][org_id])
        return {
            "refresh_time": refresh_time,
            "organization_rate": org_rate
        }

    # 获取学院所有课程的完成率
    @classmethod
    async def get_p_finish_rate(cls):
        async with cls._finish_rate_lock:
            refresh_time = copy.deepcopy(cls._finish_rate["refresh_time"])
            p_rate = copy.deepcopy(cls._finish_rate["p_org_rate"])
        return {
            "refresh_time": refresh_time,
            "p_finish_rate": p_rate
        }

    # 获取个人所有课程的完成情况
    @classmethod
    async def get_finish_status(cls, mem_id):
        status = await cls._get_mem_course(mem_id)
        need_finish = status["need_finish"]
        finished = status["finished"]
        # print(len(need_finish), need_finish)
        # print(len(finished), finished)

        for course in need_finish:
            course["is_finished"] = finished.__contains__(course)

        return need_finish

    # 获取个人全部课程中在学院和支部的排名
    @classmethod
    async def get_member_rate_rank(cls, mem_id):
        async with cls._finish_rate_rank_lock:
            refresh_time = copy.deepcopy(cls._finish_rate_rank["refresh_time"])
            rank_in_org = copy.deepcopy(cls._finish_rate_rank["member_rank"][mem_id]["rank_in_org"])
            rank_in_p_org = copy.deepcopy(cls._finish_rate_rank["member_rank"][mem_id]["rank_in_p_org"])
        return {
            "refresh_time": refresh_time,
            "rank_in_org": rank_in_org,
            "rank_in_p_org": rank_in_p_org
        }

    # 获取支部全部课程中在学院的排名
    @classmethod
    async def get_org_rate_rank(cls, org_id):
        async with cls._finish_rate_rank_lock:
            refresh_time = copy.deepcopy(cls._finish_rate_rank["refresh_time"])
            rank_in_p_org = copy.deepcopy(cls._finish_rate_rank["org_rank"][org_id]["rank_in_p_org"])
        return {
            "refresh_time": refresh_time,
            "rank_in_p_org": rank_in_p_org
        }

    # 获取支部内个人排名列表
    @classmethod
    async def get_org_member_rank_list(cls, org_id):
        members = await Member.filter(organization_id=org_id)
        async with cls._finish_rate_rank_lock:
            rank_dict = {}
            refresh_time = copy.deepcopy(cls._finish_rate["refresh_time"])
            for member in members:
                rank_dict[member.id] = copy.deepcopy(cls._finish_rate["member_rate"][member.id])
        rank = sorted(rank_dict.items(), key=lambda x: x[1], reverse=True)
        # print(rank)

        rank_with_mem_info = []
        for entry in rank:
            # print(entry)
            rank_with_mem_info.append({
                "member": await Member.get(id=entry[0]),
                "rate": entry[1]
            })
        # print(rank_with_mem_info)

        return {
            "refresh_time": refresh_time,
            "rank": rank_with_mem_info
        }

    # 获取学院内个人排名列表
    @classmethod
    async def get_p_member_rank_list(cls):
        async with cls._finish_rate_rank_lock:
            refresh_time = copy.deepcopy(cls._finish_rate["refresh_time"])
            rank_list = copy.deepcopy(cls._finish_rate_rank["member_rank_list"])

        rank_with_mem_info = []
        for entry in rank_list:
            # print(entry)
            rank_with_mem_info.append({
                "member": await Member.get(id=entry[0]),
                "rate": entry[1]
            })

        return {
            "refresh_time": refresh_time,
            "rank": rank_with_mem_info
        }

    # 获取学院内支部排名列表
    @classmethod
    async def get_p_org_rank_list(cls):
        async with cls._finish_rate_rank_lock:
            refresh_time = copy.deepcopy(cls._finish_rate["refresh_time"])
            rank_list = copy.deepcopy(cls._finish_rate_rank["organization_rank_list"])

        rank_with_mem_info = []
        for entry in rank_list:
            rank_with_mem_info.append({
                "organization": await Organization.get(id=entry[0]),
                "rate": entry[1]
            })

        return {
            "refresh_time": refresh_time,
            "rank": rank_with_mem_info
        }

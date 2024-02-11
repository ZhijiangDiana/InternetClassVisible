import asyncio
import threading
from datetime import datetime

from dao.record_dao import get_org_records
from entity.db_entity import *


class CourseRateCalculateService:
    __instance = None
    __instance_lock = threading.Lock()

    def __new__(cls):
        with cls.__instance_lock:
            if cls.__instance is None:
                # 实例化对象
                cls.__instance = super().__new__(cls)
        return cls.__instance

    _finish_rate = {
        "org_rate": {
            # 支部编号: {课程号: 完成率}
            str(): {str(): float()}
        },
        "p_org_rate": {
            # 课程号: 完成率
            str(): float()
        }
    }
    _finish_rate_lock = asyncio.Lock()

    _finish_rate_rank = {
        # 支部编号: {课程号: 排名}
        str(): {str(): int()}
    }
    _finish_rate_rank_lock = asyncio.Lock()

    _finish_rate_rank_list = {
        # 课程号: 排名榜
        str(): []
    }
    _finish_rate_rank_list_lock = asyncio.Lock()

    # 正在进行的课程不参与学院总统计，也不对其完成率进行记录，仅在请求数据使时现场计算

    # 初始化排名名单
    async def update_statistic(self):
        async with self._finish_rate_lock:
            self._finish_rate = await self._calculate_past_rate()
        async with self._finish_rate_rank_lock:
            self._finish_rate_rank = await self._calculate_past_rank()

    # 计算往期课程的完成率及排名
    async def _calculate_past_rate(self):
        # 初始化变量
        finish_rate = {
            "org_rate": {},
            "p_org_rate": {}
        }
        # 计算支部的某次课程完成率
        orgs = await Organization.all()
        for org in orgs:
            past_courses = await Course.filter(end_datetime__lte=datetime.now(), start_datetime__gte=org.create_time)
            finish_rate["org_rate"][org.id] = {}
            for course in past_courses:
                # print(course.id, course.title)
                finish_record = await get_org_records(org_id=org.id, course_id=course.id)
                members_cnt = await Member.filter(organization_id=org.id).count()
                rate = 0.0
                if members_cnt > 0:
                    rate = 1.0 * len(finish_record) / members_cnt
                finish_rate["org_rate"][org.id][course.id] = rate
            # print(org.id, finish_rate["org_rate"][org.id])
        # 计算学院某次课程的完成率
        courses = await Course.all()
        for course in courses:
            finish_record = await MemberCourse.filter(course_id=course.id)
            members_cnt = await Member.filter(join_datetime__lte=course.start_datetime).count()
            rate = 0.0
            if members_cnt > 0:
                rate = 1.0 * len(finish_record) / members_cnt
            finish_rate["p_org_rate"][course.id] = rate
        # print(finish_rate["p_org_rate"])

        return finish_rate

    async def _calculate_past_rank(self):
        finish_rank = {}
        # 计算某次课程的排名
        past_courses = await Course.filter(end_datetime__lte=datetime.now())
        for course in past_courses:
            # 获取某课程所有支部完成率，并排序
            rates = {}
            for key, value in self._finish_rate["org_rate"].items():
                if value.__contains__(course.id):
                    rates[key] = value[course.id]
            rank_list = sorted(rates.items(), key=lambda x: x[1], reverse=True)
            # 将排名名单写入排名榜
            async with self._finish_rate_rank_list_lock:
                self._finish_rate_rank_list[course.id] = rank_list
            # 将支部排名写入字典中
            for index, rank in enumerate(rank_list):
                org_id = rank[0]
                finish_rank[org_id] = {}
                finish_rank[org_id][course.id] = index + 1
        async with self._finish_rate_rank_lock:
            self._finish_rate_rank_list = finish_rank

    # 获取某次课程中支部完成率
    async def get_org_course_rate(self, org_id, course_id):
        return {
            "org": await Organization.get(id=org_id),
            "rate": self._finish_rate["org_rate"][org_id][course_id],
            "rank": self._finish_rate_rank[org_id][course_id]
        }

    # 获取某支部所有课程的完成率
    async def get_org_records(self, org_id):
        return {
            "org": await Organization.get(id=org_id),
            "rates": self._finish_rate["org_rate"][org_id],
            "ranks": self._finish_rate_rank[org_id]
        }

    # 获取某次课程中学院完成率
    async def get_p_org_course_rate(self, course_id):
        return self._finish_rate["p_org_rate"][course_id]

    # 获取某次课程中支部完成率排名列表
    async def get_org_rate_list(self, course_id):
        return self._finish_rate_rank[course_id]
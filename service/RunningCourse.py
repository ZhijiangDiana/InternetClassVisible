import asyncio
from datetime import datetime

from entity.db_entity import *
from service.DataIn.InterfacePraparation import YouthBigLearning


class RunningCourseService:
    _running_course = {}

    # 获取最新一期课程
    @classmethod
    async def get_running_course(cls):
        youth_big_learning = YouthBigLearning()
        courses = youth_big_learning.get_all_courses()
        now = datetime.now()
        for course in courses:
            if now > datetime.strptime(course["endTime"], "%Y-%m-%d %H:%M:%S"):
                break
            start_time = min(course["startTime"], course["createTime"])
            added_course = await Course.create(id=course["id"], type=course["type"], title=course["title"],
                                               start_datetime=start_time, end_datetime=course["endTime"],
                                               cover=course["cover"], uri=course["uri"])
            cls._running_course[course["id"]] = added_course

    # 30s爬取一次正在进行的课程的完成情况，需要添加到定时器业务中
    @classmethod
    async def refresh_running_course_finish_status(cls):
        youth_big_learning = YouthBigLearning()
        # TODO 爬取某一课程的完成信息并存入数据库，插入前需要先判断是否存在

    # 课程结束时的回调，需要添加到计划任务中
    @classmethod
    async def handle_running_course_end(cls, course_id):
        # 最后一次刷新该课程的完成情况
        await cls.refresh_running_course_finish_status()
        # 在名单中删除该课程
        cls._running_course.__delitem__(course_id)
        # TODO 通知CourseFinishStatistic业务更新完成率列表

    # 60s计算正在进行课程的完成率
    @classmethod
    async def get_running_course_rate(cls):
        # TODO 计算正在进行的完成率
        var = 114514

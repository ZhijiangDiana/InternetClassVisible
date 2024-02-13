import asyncio
import threading
from datetime import datetime

from entity.db_entity import *
from service.DataIn.InterfacePraparation import YouthBigLearning


class RunningCourseService:
    __instance = None
    __instance_lock = threading.Lock()

    def __new__(cls):
        with cls.__instance_lock:
            if cls.__instance is None:
                # 实例化对象
                cls.__instance = super().__new__(cls)
        return cls.__instance

    _running_course = {}

    _running_course_statistic = {
        str(): {
            # 支部编号: 完成率
            "rate": {str(): float()},
            # 总体完成率
            "p_org_rate": float(),
            # 支部编号: 排名
            "rank": {str(): int()},
            # 支部编号: 完成率
            "rank_list": [{str(): float()}]
        }
    }

    # 获取最新一期课程
    async def get_running_course(self):
        youth_big_learning = YouthBigLearning()
        courses = await youth_big_learning.get_all_courses()
        now = datetime.now()
        for course in courses:
            # 判断过期学习
            if now > datetime.strptime(course["endTime"], "%Y-%m-%d %H:%M:%S"):
                continue
            # 检查数据库中是否有该课程，若没有则添加
            if not await Course.exists(course["id"]):
                start_time = min(course["startTime"], course["createTime"])
                added_course = await Course.create(id=course["id"], type=course["type"], title=course["title"],
                                                   start_datetime=start_time, end_datetime=course["endTime"],
                                                   cover=course["cover"], uri=course["uri"])
            else:
                added_course = await Course.filter(id=course["id"])
            self._running_course[course["id"]] = added_course

    # 本业务的所有定时项目，30s
    async def update_running_course(self):
        await self._update_running_course_finish_status()
        await self._update_running_course_statistic()


    # 爬取一次正在进行的课程的完成情况，需要添加到定时器业务中
    async def _update_running_course_finish_status(self):
        youth_big_learning = YouthBigLearning()
        for course in self._running_course.values():
            # {
            #     "id": "38718",
            #     "openid": null,
            #     "createTime": "2022-09-06 23:10:40",
            #     "cardNo": "李林兴",
            #     "userType": "团员",
            #     "isStudy": true,
            #     "course": "2023年第22期",
            #     "branchs": [
            #         "高校系统",
            #         "上海理工大学",
            #         "上海理工大学光电信息与计算机工程学院",
            #         "2021级测控1班",
            #         "2021级测控1班"
            #     ]
            # }
            records = await youth_big_learning.get_course_record(course.id)
            for record in records:
                # 判断此人是否存在
                if await Member.exists(id=record["id"]):
                    if not await MemberCourse.exists(course_id=course.id, member_id=record["id"]):
                        await MemberCourse.create(course_id=course.id, member_id=record["id"])
                        print(f"{record["cardNo"]}同学（{record["id"]}）学习了{record["course"]}（{course.id}）课程")
                else:
                    print(f"不存在{record["cardNo"]}同学（{record["id"]}）")
            print(f"更新了{len(self._running_course)}个正在进行课程的学习记录")

    # 刷新完成率和排名
    async def _update_running_course_statistic(self):
        statistic = {}
        orgs = await Organization.all()
        for course in self._running_course.values():
            statistic[course.id] = {}
            # 完成率
            statistic[course.id]["rate"] = {}
            for org in orgs:
                mem_cnt = await Member.filter(organization_id=org.id).count()
                finish_cnt = await MemberCourse.filter(course_id=course.id, member_id=org.id).count()
                rate = 0.0
                if mem_cnt > 0:
                    rate = 1.0 * finish_cnt / mem_cnt
                statistic[course.id]["rate"][org.id] = rate

            # 学院完成率
            mem_cnt = await Member.all().count()
            finish_cnt = await MemberCourse.filter(course_id=course.id).count()
            statistic[course.id]["p_org_rate"] = 1.0 * finish_cnt / mem_cnt

            # 排名榜
            rank_list = sorted(statistic[course.id]["rate"].items(), key=lambda x: x[1], reverse=True)
            statistic[course.id]["rank_list"] = rank_list
            # 排名
            statistic[course.id]["rank"] = {}
            for index, item in enumerate(rank_list):
                statistic["rank"][item[0]] = item[1]

        # 回写并覆盖原有数据
        self._running_course_statistic = statistic


    # 课程结束时的回调
    # TODO 需要添加到计划任务中
    async def handle_running_course_end(self, course_id):
        await asyncio.sleep(5)
        # 最后一次刷新该课程的完成情况
        await self.update_running_course()
        # 在名单中删除该课程
        self._running_course.__delitem__(course_id)
        self._running_course_statistic.__delitem__(course_id)
        # TODO 通知CourseFinishStatistic和TotalCourseFinishStatistic业务更新完成率列表

    # 获取支部完成率
    async def get_org_statistic(self, org_id, course_id):
        return {
            "org_id": org_id,
            "rate": self._running_course_statistic[course_id]["rate"][org_id],
            "rank": self._running_course_statistic[course_id]["rank"][org_id]
        }

    # 获取完成率排名榜
    async def get_rank_list(self, course_id):
        return self._running_course_statistic[course_id]["rank_list"]

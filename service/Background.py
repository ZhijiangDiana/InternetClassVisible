import asyncio

from service.CourseFinishStatistic import CourseRateCalculateService
from service.RunningCourse import RunningCourseService
from service.TotalCourseFinishStatistic import TotalCourseRateService
from service.SemesterStatistic import SemesterStatistic


async def update_statistic_member_finish_rate():
    await TotalCourseRateService.update_statistic()


async def update_statistic_course_finish_rate():
    await CourseRateCalculateService.update_statistic()


async def refresh_running():
    await RunningCourseService.update_running_course()
    await SemesterStatistic.updateweekStatistic()


async def initialize_running():
    # 启动时获取正在进行的课程
    await RunningCourseService.get_running_course()

from service.CourseFinishStatistic import CourseRateCalculateService
from service.RunningCourse import RunningCourseService
from service.TotalCourseFinishStatistic import CalculateRateService


async def update_statistic_member_finish_rate():
    await CalculateRateService().update_statistic()


async def update_statistic_course_finish_rate():
    await CourseRateCalculateService().update_statistic()


async def refresh_running():
    await RunningCourseService().refresh_running_course_finish_status()


async def initialize_running():
    # 启动时获取正在进行的课程，只需调用一次
    await RunningCourseService().get_running_course()

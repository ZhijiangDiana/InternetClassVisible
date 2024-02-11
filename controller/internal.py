from fastapi import APIRouter

from entity.response import normal_resp
from service.CourseFinishStatistic import CourseRateCalculateService
from service.RunningCourse import RunningCourseService
from service.TotalCourseFinishStatistic import CalculateRateService
from config import INTERNAL_REQUEST_TOKEN

internal = APIRouter()


@internal.put("/statistic/finish_rate")
async def update_statistic_member_finish_rate(token: str):
    if token == INTERNAL_REQUEST_TOKEN:
        await CalculateRateService().update_statistic()
        resp = normal_resp()
    else:
        resp = normal_resp(
            status=403,
            message="不允许调用内部接口"
        )

    return resp


@internal.put("/statistic/course/finish_rate")
async def update_statistic_course_finish_rate(token: str):
    if token == INTERNAL_REQUEST_TOKEN:
        await CourseRateCalculateService().update_statistic()
        resp = normal_resp()
    else:
        resp = normal_resp(
            status=403,
            message="不允许调用内部接口"
        )

    return resp


@internal.post("/record/refresh_running")
async def refresh_running(token: str):
    if token == INTERNAL_REQUEST_TOKEN:
        await RunningCourseService().refresh_running_course_finish_status()
        resp = normal_resp()
    else:
        resp = normal_resp(
            status=403,
            message="不允许调用内部接口"
        )

    return resp


@internal.post("/record/initialize_running")
async def initialize_running(token: str):
    # 启动时获取正在进行的课程，只需调用一次
    if token == INTERNAL_REQUEST_TOKEN:
        await RunningCourseService().get_running_course()
        resp = normal_resp()
    else:
        resp = normal_resp(
            status=403,
            message="不允许调用内部接口"
        )

    return resp

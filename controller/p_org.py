from fastapi import APIRouter

from entity.db_entity import Organization
from entity.response import normal_resp
from service.CourseFinishStatistic import CourseRateCalculateService
from service.TotalCourseFinishStatistic import TotalCourseRateService

p_org = APIRouter()


@p_org.get("/statistic/record")
async def get_statistic_record():
    rate = await TotalCourseRateService.get_p_finish_rate()
    resp = normal_resp.success(result={
        "refresh_time": rate["refresh_time"],
        "p_finish_rate": rate["p_finish_rate"]
    })

    return resp


@p_org.get("/statistic/rank_list/all/member")
async def get_member_rank_list():
    rank = await TotalCourseRateService.get_p_member_rank_list()

    return normal_resp.success(result={
        "refresh_time": rank["refresh_time"],
        "rank_list": rank["rank"]
    })


@p_org.get("/statistic/rank_list/all/org")
async def get_all_org_rank_list():
    rank = await TotalCourseRateService.get_p_org_rank_list()

    return normal_resp.success(result={
        "refresh_time": rank["refresh_time"],
        "rank_list": rank["rank"]
    })


@p_org.get("/statistic/rank_list/course/{courseId}")
async def get_course_rank_list(courseId: str):
    res = await CourseRateCalculateService.get_org_rate_list(course_id=courseId)
    result = []
    for item in res:
        if item[1] != 0:
            result.append({
                "organization": await Organization.get(id=item[0]),
                "rate": item[1]
            })
    return normal_resp.success(result=result)

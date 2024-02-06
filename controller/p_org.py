from fastapi import APIRouter

from entity.response import normal_resp
from service.TotalCourseFinishStatistic import CalculateRateService

p_org = APIRouter()


@p_org.get("/statistic/record")
async def get_statistic_record():
    cal = CalculateRateService()
    rate = await cal.get_p_finish_rate()
    resp = normal_resp(result={
        "refresh_time": rate["refresh_time"],
        "p_finish_rate": rate["p_finish_rate"]
    })

    return resp


@p_org.get("/statistic/rank_list/all/member")
async def get_member_rank_list():
    cal = CalculateRateService()
    rank = await cal.get_p_member_rank_list()

    return normal_resp(result={
        "refresh_time": rank["refresh_time"],
        "rank_list": rank["rank"]
    })


@p_org.get("/statistic/rank_list/all/org")
async def get_all_org_rank_list():
    cal = CalculateRateService()
    rank = await cal.get_p_org_rank_list()

    return normal_resp(result={
        "refresh_time": rank["refresh_time"],
        "rank_list": rank["rank"]
    })
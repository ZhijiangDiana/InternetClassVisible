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

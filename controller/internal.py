from fastapi import APIRouter

from entity.response import normal_resp
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



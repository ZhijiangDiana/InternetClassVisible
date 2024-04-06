from fastapi import APIRouter

from entity.db_entity import *
from entity.response import normal_resp
from entity.input_model import OrgValidator
from service.TotalCourseFinishStatistic import TotalCourseRateService

organization = APIRouter()


# @organization.post("/add_all")
# async def add_all():
#     with open(f"all_organization.json", "r", encoding="utf-8") as all_organization:
#         all_organization = json.load(all_organization)
#         for one_org in all_organization["result"]:
#             added_org = await Organization.create(id=one_org["id"], pid=one_org["pid"], title=one_org["title"],
#                                                   qr_code=one_org["qrCode"])
#             print(added_org)
#
#     return True


@organization.get("")
async def get_all():
    orgs = await Organization.all().order_by("-create_time")
    return normal_resp.success(result={
        "cnt": len(orgs),
        "organizations": orgs
    })


@organization.get("/{org_id}")
async def get_by_id(org_id: str):
    org_id = await OrgValidator(org_id)
    org = await Organization.get(id=org_id)

    return normal_resp.success(result=org)


@organization.get("/statistic/record/{org_id}")
async def get_course_finish_statistic(org_id: str):
    org_id = await OrgValidator(org_id)
    rate = await TotalCourseRateService.get_org_finish_rate(org_id)

    return normal_resp.success(result={
        "refresh_time": rate["refresh_time"],
        "org_id": org_id,
        "finished_rate": rate["organization_rate"],
    })


@organization.get("/statistic/rank/all/{org_id}", description="获取支部全部课程中在学院内的排名")
async def get_rank_statistic(org_id: str):
    org_id = await OrgValidator(org_id)
    rate = await TotalCourseRateService.get_org_finish_rate(org_id)
    rank = await TotalCourseRateService.get_org_rate_rank(org_id)

    return normal_resp.success(result={
        "refresh_time": rate["refresh_time"],
        "org_id": org_id,
        "finished_rate": rate["organization_rate"],
        "rank": rank
    })


@organization.get("/statistic/rank_list/all/{org_id}", description="获取支部成员全部课程中在支部内的排名列表")
async def get_rank_statistic_member(org_id: str):
    org_id = await OrgValidator(org_id)
    rank = await TotalCourseRateService.get_org_member_rank_list(org_id)

    return normal_resp.success(result={
        "refresh_time": rank["refresh_time"],
        "rank_list": rank["rank"]
    })



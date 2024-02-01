import json

from fastapi import APIRouter
from pydantic import BaseModel, validator

from entity.db_entity import *
from dao import org_dao
from entity.response import normal_resp

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


@organization.get("/search/all")
async def get_all():
    orgs = await Organization.all()
    resp = normal_resp(result={
        "cnt": len(orgs),
        "organizations": orgs
    })

    return resp


@organization.get("/search/{org_id}")
async def get_by_id(org_id: str):
    is_exist = Organization.exists(id=org_id)
    if not is_exist:
        return normal_resp(
            message="查询结果为空"
        )
    org = await Organization.get(id=org_id)
    resp = normal_resp(result=org)

    return resp



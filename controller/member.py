import json

from fastapi import APIRouter
from pydantic import BaseModel, validator
from tortoise.exceptions import DoesNotExist

from dao import record_dao
from entity.response import normal_resp
from entity.db_entity import *
from service.DataIn.InterfacePraparation import YouthBigLearning

member = APIRouter()


# @member.post("/add_all")
# async def add_all():
#     youth_learning = YouthBigLearning()
#     all_member = youth_learning.getAllMember("N000100110001")
#
#     print("写入数据库进度：")
#     for entry in all_member:
#         print(f'\r正在写入{entry}', end='  ')
#
#         # 依次查找支部
#         org = None
#         for branch in entry["branchs"]:
#             try:
#                 org = await Organization.get(title=branch)
#                 break
#             except DoesNotExist as e:
#                 int(1)
#         if org is None:
#             print("实体不合法")
#             continue
#
#         await Member.create(id=entry["id"], join_datetime=entry["createTime"],
#                             name=entry["cardNo"], user_type=entry["userType"], organization_id=org.id)
#
#     return normal_resp()


# 列出所有成员
@member.get("/search/all")
async def get_all():
    members = await Member.all()
    resp = normal_resp(result={
        "cnt": len(members),
        "members": members
    })
    return resp


# 根据支部列出其下属的所有成员
@member.get("/search/org/{org_id}")
async def get_by_org(org_id: str):
    is_exist = await Organization.exists(id=org_id)
    if not is_exist:
        return normal_resp(
            message="查询结果为空"
        )

    members = await Member.filter(organization_id=org_id)
    org = await Organization.get(id=org_id)
    resp = normal_resp(result={
        "organization": org,
        "cnt": len(members),
        "members": members
    })
    return resp


# 根据id查找成员
@member.get("/search/{mem_id}")
async def get_by_id(mem_id: int):
    is_exist = await Member.exists(id=mem_id)
    if not is_exist:
        return normal_resp(
            message="查询结果为空"
        )

    mem = await Member.get(id=mem_id)
    org = await mem.organization.get()
    resp = normal_resp(result={
        "member": mem,
        "organization": org
    })

    return resp


# 统计某个成员的学习情况，返回其id，完成率，详细完成情况
@member.get("/statistic/record/{mem_id}")
async def get_course_finish_statistic(mem_id: int):
    need_finish = await record_dao.get_courses_should_finish(mem_id)
    finished = await record_dao.get_courses_finished(mem_id)

    for course in need_finish:
        course["is_finished"] = finished.__contains__(course)

    return normal_resp(result={
        "mem_id": mem_id,
        "finished_rate": len(finished) * 1.0 / len(need_finish),
        "course_stat": need_finish
    })

import json

from fastapi import APIRouter
from pydantic import BaseModel, validator
from tortoise.exceptions import DoesNotExist

from entity.response import normal_resp
from entity.db_entity import *
from service.DataIn.InterfacePraparation import YouthBigLearning

member = APIRouter()


@member.post("/add_all")
async def add_all():
    youth_learning = YouthBigLearning()
    all_member = youth_learning.getAllMember("N000100110001")

    print("写入数据库进度：")
    for entry in all_member:
        print(f'\r正在写入{entry}', end='  ')

        # 依次查找支部
        org = None
        for branch in entry["branchs"]:
            try:
                org = await Organization.get(title=branch)
                break
            except DoesNotExist as e:
                int(1)
        if org is None:
            print("实体不合法")
            continue

        await Member.create(id=entry["id"], join_datetime=entry["createTime"],
                            name=entry["cardNo"], user_type=entry["userType"], organization_id=org.id)

    return normal_resp()


@member.get("/{id}")
async def get_member(mem_id: int):
    mem = await Member.get(id=mem_id)
    org = await mem.organization.get()

    resp = normal_resp(result={
        "member": mem,
        "organization": org
    })

    return resp


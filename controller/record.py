import json

from fastapi import APIRouter
from pydantic import BaseModel, validator
from tortoise.exceptions import DoesNotExist

from entity.response import normal_resp
from entity.db_entity import *
from service.DataIn.InterfacePraparation import YouthBigLearning

record = APIRouter()


@record.post("/add_all/{start}/{end}")
async def add_all(start: int, end: int):
    youth_learning = YouthBigLearning()

    print("写入数据库进度：")
    all_member = await Member.filter(id__gt=start, id__lte=end)  # 38800  39000  227000
    cnt = 1
    for mem_entry in all_member:
        # 多表查询学生的所在的支部
        org = await mem_entry.organization.get()

        # 获取所有学生的学习记录
        mem_record = youth_learning.get_member_record(org_id=org.id, mem_name=mem_entry.name)
        print(f"\r正在写入第{cnt}条学习记录，共{len(all_member)}条", end='  ')

        # 将爬到的结果存入数据库
        for record_entry in mem_record:
            course = None
            try:
                course = await Course.get(title=record_entry["course"], start_datetime__lte=record_entry["createTime"],
                                          end_datetime__gte=record_entry["createTime"])
            except DoesNotExist:
                continue

            await MemberCourse.create(finish_datetime=record_entry["createTime"], course_id=course.id,
                                      member_id=mem_entry.id)

        cnt += 1

    return normal_resp()

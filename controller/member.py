from fastapi import APIRouter

from entity.input_model import *
from entity.output_model import *
from entity.response import normal_resp
from entity.db_entity import *
from service.TotalCourseFinishStatistic import TotalCourseRateService

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


# @member.put("/modify_year")
# async def modify_year():
#     orgs = await Organization.all()
#     for org in orgs:
#         members = await Member.filter(organization_id=org.id)
#         join_date = datetime(year=int(org.title[:4]), day=1, month=9)
#         for mem in members:
#             # 修改join_datetime字段
#             mem.join_datetime = join_date
#             # 保存更改
#             await mem.save()


# 列出所有成员
@member.get("/")
async def get_all():
    members = await Member.all()
    return normal_resp.success(result={"cnt": len(members),"members": members})


# 根据支部列出其下属的所有成员
@member.get("/org/{org_id}")
async def get_by_org(org_id: str):
    org_id = await OrgValidator(org_id)
    # 查询并返回
    result={
        "cnt": 0,
        "members": []
    }
    members = await Member.filter(organization_id=org_id)
    for member in members:
        result["cnt"] += 1
        result["members"].append(member.id)
    return normal_resp.success(result)


# 根据id查找成员
@member.get("/{mem_id}")
async def get_by_id(mem_id: int):
    # 检查成员是否存在
    mem_id = await MemberValidator(mem_id)

    mem = await Member.get(id=mem_id)
    org = await mem.organization.get()
    return normal_resp.success(result={"member": mem, "organization": org})


# 统计某个成员的学习情况，返回其id，完成率，详细完成情况
@member.get("/statistic/record/{mem_id}")
async def get_course_finish_statistic(mem_id: int):
    # 检查成员是否存在
    mem_id = await MemberValidator(mem_id)

    rate = await TotalCourseRateService.get_member_finish_rate(mem_id)
    status = await TotalCourseRateService.get_finish_status(mem_id)

    return normal_resp.success(result={
        "refresh_time": rate["refresh_time"],
        "mem_id": mem_id,
        "finished_rate": rate["member_rate"],
        "course_stat": status
    })


# 统计某个成员的总完成率和排名
@member.get("/statistic/rank/all/{mem_id}")
async def get_member_rank(mem_id: int):
    # 检查成员是否存在
    mem_id = await MemberValidator(mem_id)

    rate = await TotalCourseRateService.get_member_finish_rate(mem_id)
    rank = await TotalCourseRateService.get_member_rate_rank(mem_id)

    return normal_resp.success(result={
        "refresh_time": rate["refresh_time"],
        "mem_id": mem_id,
        "finished_rate": rate["member_rate"],
        "org_rank": rank["rank_in_org"],
        "p_org_rank": rank["rank_in_p_org"],
    })

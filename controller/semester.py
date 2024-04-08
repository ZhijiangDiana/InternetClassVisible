import re
import datetime
from fastapi import APIRouter

from entity.db_entity import Organization, Member
from entity.response import normal_resp
from entity.input_model import MemberValidator, OrgValidator
from middleware.ExceptionHandler import ValidatorError
from service.SemesterStatistic import SemesterStatistic

semester = APIRouter()


# 202320241 2023-2024学年第一学期
def semester_parser(semester: str):
    m = re.match(r"^(20[0-9]{2})(20[0-9]{2})([12])$", semester)
    if m is None:
        raise ValidatorError("学期格式错误")
    m = list(m.groups())
    if int(m[1]) - int(m[0]) != 1 or m[2] not in ['1', '2']:
        raise ValidatorError("学期格式错误")
    
    m[2] = "一" if m[2] == "1" else "二"
    sem = f"{m[0]}-{m[1]}学年第{m[2]}学期"

    # if sem not in SemesterStatistic._orgFinishRate.keys():
    #     raise ValidatorError("学期不存在")
    return sem


@semester.get("")
async def get_all_semesters():
    semester_str = ["202020212", "202120221", "202120222", "202220231", "202220232", "202320241"]
    res = []
    for sem in semester_str:
        res.append({
            "id": sem,
            "name": semester_parser(sem),
        })
    res.reverse()
    return normal_resp.success(result=res)


@semester.get("/{semester}/member")
async def all_member(semester: str):
    semester = semester_parser(semester)
    res = await SemesterStatistic.get_all_stu_rank(semester)
    res = {key: value for key, value in res.items() if value != 0}
    sorted_data = sorted(res.items(), key=lambda x: x[1], reverse=True)
    result_list = list(sorted_data)[:50]
    result = []
    for item in result_list:
        mem = await Member.get(id=item[0])
        result.append({
            "member": mem,
            "organization": await mem.organization.get(),
            "rate": item[1],
        })

    return normal_resp.success(result=result)


@semester.get("/{semester}/member/{member_id}")
async def get_member(semester: str, member_id: int):
    semester = semester_parser(semester)
    member_id = await MemberValidator(member_id)
    rate, rank = await SemesterStatistic.get_stu_rank(semester, member_id)
    resp = normal_resp.success(result={'rate': rate, 'rank': rank})
    return resp


@semester.get("/{semester}/org")
async def all_org(semester: str):
    semester = semester_parser(semester)
    res = await SemesterStatistic.get_all_org_rank(semester)
    sorted_data = sorted(res.items(), key=lambda x: x[1], reverse=True)
    result_list = list(sorted_data)
    result = []
    for item in result_list:
        result.append({
            "organization": await Organization.get(id=item[0]),
            "rate": item[1],
        })

    return normal_resp.success(result=result)


@semester.get("/{semester}/org/{org_id}")
async def get_org(semester: str, org_id: str):
    semester = semester_parser(semester)
    org_id = await OrgValidator(org_id)
    rate, rank = await SemesterStatistic.get_org_rank(semester, org_id)
    resp = normal_resp.success(result={'rate': rate, 'rank': rank})
    return resp


@semester.get("/{semester}/org/{org_id}/detail")
async def get_org_detail(semester: str, org_id: str):
    semester = semester_parser(semester)
    org_id = await OrgValidator(org_id)
    resp = normal_resp.success(result=(await SemesterStatistic.get_org_stu_rank(semester, org_id)))
    return resp

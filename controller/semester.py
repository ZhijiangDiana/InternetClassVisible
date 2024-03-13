import re
import datetime
from fastapi import APIRouter
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

    if sem not in SemesterStatistic._orgFinishRate.keys():
        raise ValidatorError("学期不存在")
    return sem


@semester.get("/{semester}/member")
async def all_member(semester: str):
    semester = semester_parser(semester)
    resp = normal_resp.success(result=(await SemesterStatistic.get_all_stu_rank(semester)))
    return resp


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
    resp = normal_resp.success(result=(await SemesterStatistic.get_all_org_rank(semester)))
    return resp


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

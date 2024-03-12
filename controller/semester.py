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
    if re.match(r"^(20\d{2})(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])$", semester) is None:
        raise ValidatorError("学期格式错误")
    return SemesterStatistic._date2semester(datetime.datetime.strptime(semester, "%Y%m%d"))


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

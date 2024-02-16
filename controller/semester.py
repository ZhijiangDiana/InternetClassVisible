from fastapi import APIRouter
from entity.response import normal_resp
from service.SemesterStatistic import SemesterStatistic

semester = APIRouter()


# 202320241 2023-2024学年第一学期
def semester_parser(semester: str):
    if semester[-1] not in ["1", "2"]:
        raise ValueError("学期格式错误")
    return (
        semester[:4] + "-" + semester[4:8] + "学年第" + "一"
        if semester[-1] == "1"
        else "二" + "学期"
    )


@semester.get("/{semester}/member")
async def all_member(semester: str):
    semester = semester_parser(semester)
    resp = normal_resp(result={semester: await SemesterStatistic.get_all_stu_rank(semester)})
    return resp


@semester.get("/{semester}/member/{member_id}")
async def get_member(semester: str, member_id: int):
    semester = semester_parser(semester)
    rate, rank = await SemesterStatistic.get_stu_rank(semester, member_id)
    resp = normal_resp(result={'rate': rate, 'rank': rank})
    return resp


@semester.get("/{semester}/org")
async def all_org(semester: str):
    semester = semester_parser(semester)
    resp = normal_resp(result={semester: await SemesterStatistic.get_all_org_rank(semester)})
    return resp


@semester.get("/{semester}/org/{org_id}")
async def get_org(semester: str, org_id: int):
    semester = semester_parser(semester)
    rate, rank = await SemesterStatistic.get_org_rank(semester, org_id)
    resp = normal_resp(result={'rate': rate, 'rank': rank})
    return resp


@semester.get("/{semester}/org/{org_id}/detail")
async def get_org_detail(semester: str, org_id: int):
    semester = semester_parser(semester)
    resp = normal_resp(result={semester: await SemesterStatistic.get_org_stu_rank(semester, org_id)})
    return resp

from fastapi import APIRouter

from ai import probaPredModel
from entity.db_entity import *
from entity.response import normal_resp
from entity.input_model import OrgValidator
from controller.semester import semester_parser
from service.CourseFinishStatistic import CourseRateCalculateService
from service.SendEmail import EmailService
from service.TotalCourseFinishStatistic import TotalCourseRateService
from service.SemesterStatistic import SemesterStatistic
from middleware.ExceptionHandler import ValidatorError
import numpy as np
from collections import Counter
import random

demand = APIRouter()

@demand.get("/userOverview")
async def userOverview():
    classNum = len(await Organization.all().values_list("id"))
    courseNum = len(await Course.all().values_list("id"))
    totalRate = np.mean(list(TotalCourseRateService._finish_rate["organization_rate"].values()))*100
    memberNum = len(TotalCourseRateService._finish_rate["member_rate"].keys())
    return normal_resp.success({"classNum": classNum, "courseNum": courseNum, "totalRate": totalRate, "memberNum": memberNum})


@demand.get("/org_rate/total", description="所有支部的总的完成率")
async def get_total_rate():
    rate = TotalCourseRateService._finish_rate["organization_rate"]
    all_org = {k:v for k,v in await Organization.filter(id__in=rate.keys()).values_list("id", "title")}
    rate = [{"name":all_org[k], "value":int(v*100)} for k,v in rate.items()]
    return normal_resp.success(result=rate)


@demand.get("/course/{course_id}")
async def get_by_id(course_id: str):
    barData = Counter([i[0] for i in await MemberCourse.filter(course_id=course_id).prefetch_related("member").values_list("member__organization_id")])
    lineData = Counter([i[0] for i in await Member.filter(join_datetime__lte=(await Course.get(id=course_id).values_list("start_datetime"))).values_list("organization_id")])
    lineData = {k:lineData[k] for k in barData.keys()}
    category = [(await Organization.get(id=i).values_list("title"))[0] for i in barData.keys()]
    rateData = [int(v/lineData[k] * 100) for k,v in barData.items()]
    barData = list(barData.values())
    lineData = list(lineData.values())
    return normal_resp.success(result={"category":category, "barData":barData, "lineData":lineData, "rateData":rateData})


@demand.get("/org_rate/semester/{semester}")
async def all_org(semester: str):
    semester = semester_parser(semester)
    result = await SemesterStatistic.get_all_org_rank(semester)
    result = [{"name":(await Organization.get(id=k).values_list("title"))[0], "value":int(v*100)} for k,v in result.items()]
    return normal_resp.success(result=result)


@demand.get("/topKproba/all/{k}", description="获取所有人中不做下一期课程概率最高的k个人\n调用此api可能会超级超级耗时,十七秒左右,但是添加了缓存,一定时间内(这里是1个小时)再次调用就会很快")
async def topKproba_all(k: int):
    if k <= 0:
        raise ValidatorError("查询数量不能小于0!")
    all_stu_id = [i[0] for i in await Member.all().values_list("id")]
    if k > len(all_stu_id):
        raise ValidatorError("查询数量不能大于学生总数!")
    all_stu_proba = sorted([[x, await probaPredModel.proba_pred(x)] for x in all_stu_id], reverse=True, key=lambda x: x[1])[:k]
    result = []
    for x in all_stu_proba:
        mem = await Member.get(id=x[0])
        org = await mem.organization.get()
        result.append({
            "member": mem,
            "organization": org,
            "rate": x[1]
        })
    return normal_resp.success(result=result)

@demand.get("/topKproba/org/{org_id}/{k}", description="获取指定支部中不做下一期课程概率最高的k个人")
async def topKproba(org_id:str, k: int):
    org_id = await OrgValidator(org_id)
    if k <= 0:
        raise ValidatorError("查询数量不能小于0!")
    org_stu_id = [i[0] for i in await Member.filter(organization_id=org_id).values_list("id")]
    if k > len(org_stu_id):
        raise ValidatorError("查询数量不能大于支部学生总数!")
    org_stu_proba = sorted([[x, await probaPredModel.proba_pred(x)] for x in org_stu_id], reverse=True, key=lambda x: x[1])[:k]
    result = []
    for x in org_stu_proba:
        mem = await Member.get(id=x[0])
        org = await mem.organization.get()
        result.append({
            "member": mem,
            "organization": org,
            "rate": x[1]
        })
    return normal_resp.success(result=result)


@demand.get("/courseOverView/{course}")
async def courseOverview(course: str):
    return normal_resp.success(result={
        "currentCourse": course.replace("C", ""),
        "finish_rate": await CourseRateCalculateService.get_p_org_course_rate(course),
        "count": EmailService().cnt,
    })


@demand.get("/semesterOverView/{semester}")
async def semesterOverView(semester: str):
    # 第二学期按第一学期算，不然数据就为0了
    semester = semester[:-1]+"1" if semester[-1]=="2" else semester
    semester = semester_parser(semester)
    sem_start_date, sem_end_date = SemesterStatistic._semester2date(semester)
    course_num = len(await Course.filter(start_datetime__gt=sem_start_date, start_datetime__lt=sem_end_date).values_list("id"))
    # 支部最高完成率，平均完成率，新增团员数
    if type(SemesterStatistic._orgFinishRate[semester]) is dict:
        orgRates = [org_data[1]/((await Member.filter(organization_id=org_data[0]).count())*course_num) for org_data in SemesterStatistic._orgFinishRate[semester].items()]
    else:
        orgRates = list(SemesterStatistic._orgFinishRate[semester].values())
    if semester.startswith("2023"):
        newMemberNum = 955
    else:
        newMemberNum = await Member.filter(join_datetime__gt=sem_start_date, join_datetime__lt=sem_end_date).count()
    return normal_resp.success(result={
        "highestRate": max(orgRates),
        "averageRate": float(np.mean(orgRates)),
        "newMemberNum": newMemberNum
    })


@demand.get("/unfinish")
async def unfinish():
    latest_course = (await Course.all().order_by("start_datetime").values())[-1]
    finished_member = [i[0] for i in await MemberCourse.filter(course_id=latest_course["id"]).values_list("member_id")]
    unfinished_member = (await Member.filter(id__not_in=finished_member).prefetch_related("organization").values("join_datetime", "name", "organization__title"))
    random.shuffle(unfinished_member)
    unfinished_member = unfinished_member[:50]
    return normal_resp.success(result=[{"member":{"join_datetime":i["join_datetime"], "name":i["name"]},
                                        "organization":{"title":i["organization__title"]}} for i in unfinished_member])
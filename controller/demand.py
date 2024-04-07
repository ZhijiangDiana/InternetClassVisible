from fastapi import APIRouter

from ai import probaPredModel
from entity.db_entity import *
from entity.response import normal_resp
from entity.input_model import OrgValidator
from controller.semester import semester_parser
from service.TotalCourseFinishStatistic import TotalCourseRateService
from service.SemesterStatistic import SemesterStatistic
from middleware.ExceptionHandler import ValidatorError
import numpy as np
from collections import Counter

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
    return normal_resp.success(result=[{"name":(await Member.get(id=x[0]).values_list("name"))[0], "value":x[1]} for x in all_stu_proba])

@demand.get("/topKproba/org/{org_id}/{k}", description="获取指定支部中不做下一期课程概率最高的k个人")
async def topKproba(org_id:str, k: int):
    org_id = await OrgValidator(org_id)
    if k <= 0:
        raise ValidatorError("查询数量不能小于0!")
    org_stu_id = [i[0] for i in await Member.filter(organization_id=org_id).values_list("id")]
    if k > len(org_stu_id):
        raise ValidatorError("查询数量不能大于支部学生总数!")
    org_stu_proba = sorted([[x, await probaPredModel.proba_pred(x)] for x in org_stu_id], reverse=True, key=lambda x: x[1])[:k]
    return normal_resp.success(result=[{"name":(await Member.get(id=x[0]).values_list("name"))[0], "value":x[1]} for x in org_stu_proba])
from fastapi import APIRouter
from tortoise.expressions import Q

from entity.db_entity import *
from entity.input_model import CourseValidator
from entity.response import normal_resp
from service.SendEmail import EmailService

course = APIRouter()


# @course.post("/add_all")
# async def add_all():
#     with open(f"all_course.json", "r", encoding="utf-8") as all_course:
#         all_course = json.load(all_course)
#         for one_course in all_course["result"]["list"]:
#             start_time = min(one_course["startTime"], one_course["createTime"])
#             added_course = await Course.create(id=one_course["id"], type=one_course["type"], title=one_course["title"],
#                                 start_datetime=start_time, end_datetime=one_course["endTime"],
#                                 cover=one_course["cover"], uri=one_course["uri"])
#             print(added_course)
#
#     return True


@course.get("")
async def get_all():
    courses = await Course.all().order_by("-start_datetime")
    return normal_resp.success(result={
        "cnt": len(courses),
        "courses": courses
    })


@course.get("/{course_id}")
async def get_by_id(course_id: str):
    course_id = await CourseValidator(course_id)
    cou = await Course.get(id=course_id)
    return normal_resp.success(result=cou)


@course.post("/sendEmails")
async def send_email():
    EmailService().cnt += 1
    cnt = EmailService().cnt

    course = await Course.filter().order_by('-start_datetime').first()
    finished_member = await MemberCourse.filter(course_id=course.id).values_list('member_id', flat=True)
    mems = await Member.filter(~Q(id__in=finished_member)).filter(email__isnull=False)

    # print(mems.__len__())
    for mem in mems:
        await EmailService().send_email(mem.email)
    return normal_resp.success(result=cnt)

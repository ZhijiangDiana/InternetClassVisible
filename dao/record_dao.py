from entity.db_entity import *
from tortoise.expressions import Q


async def get_courses_should_finish(mem_id):
    join_datetime = (await Member.get(id=mem_id).values("join_datetime"))["join_datetime"]
    return await Course.filter(start_datetime__lte=join_datetime).\
                        values("id, type, title, start_datetime, end_datetime, cover, uri")


async def get_courses_finished(mem_id):
    return await Course.filter(finish_member__member_id=mem_id).prefetch_related("finish_member__course_id").\
                        values("id, type, title, start_datetime, end_datetime, cover, uri")


async def get_org_records(org_id, course_id):
    # List[Dict{"id":xxx}] -> List[xxx]
    member_ids = [i["id"] for i in (await Member.filter(organization_id=org_id).values("id"))]
    return await MemberCourse.filter(Q(member_id__in=member_ids) & Q(course_id=course_id))
from entity.db_entity import *


'''
可以在此处自定义返回字典的字段名:
在 values 之前插入 annotate 方法, 传入**kwargs以修改返回的参数名字, 同时values里面也要对应修改

annotates = {"id":"course_id", "type":"course__type", ...}
MemberCourse.filter().prefetch_related().annotate(annotates).values("id", "type", ...)
'''

async def get_courses_should_finish(mem_id):
    join_datetime = (await Member.get(id=mem_id).values("join_datetime"))["join_datetime"]
    return await Course.filter(start_datetime__gte=join_datetime).\
                        values("id", "type", "title", "start_datetime", "end_datetime", "cover", "uri")


async def get_courses_finished(mem_id):
    return await MemberCourse.filter(member_id=mem_id).prefetch_related("member", "course").\
                    values("course_id", "course__type", "course__title", "course__start_datetime", "course__end_datetime", "course__cover", "course__uri")


async def get_org_records(org_id, course_id):
    # List[Dict{"id":xxx}] -> List[xxx]
    member_ids = [i["id"] for i in (await Member.filter(organization_id=org_id).values("id"))]
    return await MemberCourse.filter(member_id__in=member_ids, course_id=course_id).values()